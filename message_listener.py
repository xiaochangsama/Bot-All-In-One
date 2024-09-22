import asyncio
import websockets
import json

from database.use_aiosqlite.database_manager import DatabaseManager
from database.use_aiosqlite.process_group_message import store_group_message
from database.use_aiosqlite.process_private_message import store_private_message
from logger import setup_logger
from heartbeat_handler import HeartbeatHandler
from plugin_manager import PluginManager
from config_manager import ConfigManager
from plugin_handler import PluginHandler
from dify_handler import DifyHandler
from websocket_handler import WebSocketHandler


class MessageListener:
    """WebSocket 服务器，等待 OneBot 的连接"""

    def __init__(self, host, port, path, logger=None):
        self.host = host
        self.port = port
        self.path = path
        self.logger = logger or setup_logger('MessageListener')
        self.config_manager = ConfigManager()
        self.db_manager = DatabaseManager(self.config_manager)
        self.plugin_manager = PluginManager()

        # 初始化 Plugin 和 Dify 处理器
        self.plugin_handler = PluginHandler(self.plugin_manager, self.logger)
        self.dify_handler = DifyHandler(None, None, self.logger)  # DifyClient 后续传入
        self.websocket_handler = WebSocketHandler(self.plugin_handler, self.dify_handler,
                                                  self.db_manager, self.config_manager, self.logger)

    async def handler(self, websocket, path):
        """处理收到的消息"""
        if path == self.path:
            self.logger.info(f'OneBot 已连接：{path}')
            self.plugin_manager.load_plugins()
            try:
                async for message in websocket:
                    msg_data = json.loads(message)
                    if msg_data.get('post_type') == 'meta_event' and msg_data.get('meta_event_type') == 'heartbeat':
                        self.heartbeat_handler.add_heartbeat(msg_data)
                    elif msg_data.get('post_type') == 'message':
                        if msg_data.get('message_type') == 'private':
                            await self.websocket_handler.process_private_message(websocket, msg_data)
                        elif msg_data.get('message_type') == 'group':
                            await self.websocket_handler.process_group_message(websocket, msg_data)
            except websockets.exceptions.ConnectionClosed:
                self.logger.info('连接已关闭')

    async def start(self, dify_client, dify_receiver):
        """启动 WebSocket 服务器"""
        self.dify_handler.dify_client = dify_client
        self.dify_handler.dify_receiver = dify_receiver
        self.heartbeat_handler = HeartbeatHandler(self.logger, interval=300)

        async def ws_handler(websocket, path):
            await self.handler(websocket, path)

        server = await websockets.serve(ws_handler, self.host, self.port)
        self.logger.info(f'WebSocket 服务器已启动，监听 {self.host}:{self.port}{self.path}')
        await server.wait_closed()

    async def shutdown(self):
        """关闭时，关闭所有数据库连接"""
        await self.db_manager.close_all_connections()
