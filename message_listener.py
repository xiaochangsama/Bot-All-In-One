import asyncio
import websockets
import json

from database.use_aiosqlite.database_manager import DatabaseManager
from database.use_aiosqlite.process_group_message import store_group_message
from database.use_aiosqlite.process_private_message import store_private_message
from logger import setup_logger
from heartbeat_handler import HeartbeatHandler
from plugin_manager import PluginManager  # 导入插件管理器
from config_manager import ConfigManager  # 导入配置管理器


class MessageListener:
    """WebSocket 服务器，等待 OneBot 的连接"""

    def __init__(self, host, port, path, logger=None):
        self.host = host
        self.port = port
        self.path = path
        self.logger = logger or setup_logger('MessageListener')
        self.config_manager = ConfigManager()  # 初始化配置管理器
        self.db_manager = DatabaseManager(self.config_manager)  # 初始化数据库管理器
        self.plugin_manager = PluginManager()

    async def handler(self, websocket, path):
        """处理收到的消息"""
        if path != self.path:
            self.logger.warning(f'收到未知路径的连接：{path}')
            await websocket.close()
            return

        self.logger.info(f'OneBot 已连接：{path}')
        self.plugin_manager.load_plugins()  # 加载启用的插件

        try:
            async for message in websocket:
                msg_data = json.loads(message)
                if msg_data.get('post_type') == 'meta_event' and msg_data.get('meta_event_type') == 'heartbeat':
                    self.heartbeat_handler.add_heartbeat(msg_data)
                elif msg_data.get('post_type') == 'message':
                    self.logger.debug(f'收到原始QQ消息：{message}')  # 记录非心跳消息
                    await self.process_message(websocket, msg_data)
        except websockets.exceptions.ConnectionClosed:
            self.logger.info('连接已关闭')

    async def process_message(self, websocket, msg_data):
        """根据消息类型处理私聊和群聊消息"""
        try:
            if msg_data.get('message_type') == 'private':
                await self.process_private_message(websocket, msg_data)
            elif msg_data.get('message_type') == 'group':
                await self.process_group_message(websocket, msg_data)
        except Exception as e:
            self.logger.error(f"消息处理时出错: {e}")

    async def process_private_message(self, websocket, msg_data):
        """处理 QQ 用户发送的私聊消息"""
        user_id = msg_data['sender']['user_id']
        message_text = msg_data.get('raw_message', '')
        self.logger.info(f'收到来自 {user_id} 的私聊消息：{message_text}')

        # 获取数据库连接并存储私聊消息
        conn = await self.db_manager.get_connection(user_id, is_group=False)
        try:
            await store_private_message(msg_data, conn)
        except Exception as e:
            self.logger.error(f"私聊消息存储失败: {e}")
            return

        # 优先使用插件管理器处理消息
        await self.handle_plugin_message(websocket, msg_data, user_id, is_group=False)

    async def process_group_message(self, websocket, msg_data):
        """处理 QQ 群聊消息"""
        group_id = msg_data['group_id']
        user_id = msg_data['sender']['user_id']
        message_text = msg_data.get('raw_message', '')
        self.logger.info(f'收到来自群 {group_id} 用户 {user_id} 的群聊消息：{message_text}')

        # 获取数据库连接并存储群聊消息
        conn = await self.db_manager.get_connection(group_id, is_group=True)
        try:
            await store_group_message(msg_data, conn)
        except Exception as e:
            self.logger.error(f"群聊消息存储失败: {e}")
            return

        # 从配置文件中检查是否允许回复该群聊消息
        group_setting = self.config_manager.get_group_chat_setting(group_id)
        if not group_setting.get('enabled', True):
            self.logger.debug(f'群 {group_id} 已被配置为不回复消息')
            return  # 群聊未启用回复，跳过处理

        # 使用插件管理器处理群聊消息
        await self.handle_plugin_message(websocket, msg_data, group_id, is_group=True)

    async def handle_plugin_message(self, websocket, msg_data, target_id, is_group):
        """统一处理插件消息"""
        plugin_result = self.plugin_manager.handle_message(msg_data)

        if plugin_result["handled"]:
            if plugin_result["reply"] is not None:
                reply_action = "send_group_msg" if is_group else "send_private_msg"
                reply = {
                    "action": reply_action,
                    "params": {
                        "group_id" if is_group else "user_id": target_id,
                        "message": plugin_result["reply"]
                    },
                    "echo": reply_action
                }
                await websocket.send(json.dumps(reply))
                self.logger.debug(f'已向 {"群" if is_group else "用户"} {target_id} 发送插件回复')
            else:
                self.logger.debug('插件处理后取消回复')
            return  # 插件已处理消息，跳过后续处理

        # 如果插件没有处理，使用 DifyClient 发送请求
        await self.send_dify_response(websocket, msg_data, target_id, is_group)

    async def send_dify_response(self, websocket, msg_data, target_id, is_group):
        """调用 DifyClient 发送 AI 响应"""
        message_text = msg_data.get('raw_message', '')
        response = await self.dify_client.send_request(message_text, target_id, is_group)
        answer = self.dify_receiver.process_response(response)

        if answer:
            reply_action = "send_group_msg" if is_group else "send_private_msg"
            reply = {
                "action": reply_action,
                "params": {
                    "group_id" if is_group else "user_id": target_id,
                    "message": answer
                },
                "echo": reply_action
            }
            await websocket.send(json.dumps(reply))
            self.logger.debug(f'已向 {"群" if is_group else "用户"} {target_id} 发送回复')
        else:
            self.logger.error('未能从 Dify 获取有效响应')

    async def start(self, dify_client, dify_receiver):
        """启动 WebSocket 服务器"""
        self.dify_client = dify_client
        self.dify_receiver = dify_receiver
        self.heartbeat_handler = HeartbeatHandler(self.logger, interval=300)

        async def ws_handler(websocket, path):
            await self.handler(websocket, path)

        server = await websockets.serve(ws_handler, self.host, self.port)
        self.logger.info(f'WebSocket 服务器已启动，监听 {self.host}:{self.port}{self.path}')
        await server.wait_closed()

    async def shutdown(self):
        """关闭时，关闭所有数据库连接"""
        await self.db_manager.close_all_connections()
