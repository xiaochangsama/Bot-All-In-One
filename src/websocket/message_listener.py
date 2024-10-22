import websockets
import json
from src.logger import setup_logger
from src.websocket.heartbeat_handler import HeartbeatHandler


class MessageListener:
    def __init__(self, config_manager, websocket_handler, logger=None):
        # 从配置文件获取 WebSocket 服务器配置
        self.host = config_manager.get('websocket_host', 'localhost')
        self.port = config_manager.get('websocket_port', 8070)
        self.path = config_manager.get('websocket_path', '/ws')
        self.logger = logger or setup_logger('MessageListener')
        self.websocket_handler = websocket_handler
        self.heartbeat_handler = HeartbeatHandler(self.logger)
        self.config_manager = config_manager  # 添加配置管理器

    async def handler(self, websocket, path):
        """处理接收到的消息"""
        if path == self.path:
            self.logger.info(f'WebSocket 已连接：{path}')
            try:
                async for message in websocket:
                    msg_data = json.loads(message)

                    # 获取聊天类型和ID
                    chat_type = msg_data.get('message_type')
                    chat_id = msg_data.get('group_id') if chat_type == 'group' else msg_data.get('user_id')

                    # 获取对应的聊天配置
                    chat_config = self.config_manager.get_chat_setting(chat_type, chat_id)

                    # 检查聊天是否启用
                    if chat_config.get('enabled', False):
                        # 处理心跳消息
                        if msg_data.get('post_type') == 'meta_event' and msg_data.get('meta_event_type') == 'heartbeat':
                            self.heartbeat_handler.add_heartbeat(msg_data)

                        # 处理普通消息
                        elif msg_data.get('post_type') == 'message':
                            if msg_data.get('message_type') == 'private':
                                await self.websocket_handler.process_private_message(websocket, msg_data)
                            elif msg_data.get('message_type') == 'group':
                                await self.websocket_handler.process_group_message(websocket, msg_data)
                    else:
                        self.logger.debug(f'聊天 {chat_id} 被禁用，忽略消息')

            except websockets.exceptions.ConnectionClosed:
                self.logger.info('WebSocket 连接已关闭')

    async def start(self):
        """启动 WebSocket 服务器"""
        server = await websockets.serve(self.handler, self.host, self.port)
        self.logger.info(f'WebSocket 服务器启动，监听 {self.host}:{self.port}{self.path}')
        await server.wait_closed()

    async def shutdown(self):
        """关闭 WebSocket 服务器"""
        self.logger.info('WebSocket 服务器即将关闭...')
