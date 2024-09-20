# message_listener.py

import asyncio
import websockets
import json
from logger import setup_logger
from heartbeat_handler import HeartbeatHandler

class MessageListener:
    """作为 WebSocket 服务器，等待 OneBot 的连接"""

    def __init__(self, host, port, path, logger=None):
        self.host = host
        self.port = port
        self.path = path
        self.logger = logger or setup_logger('MessageListener')
        self.heartbeat_handler = None

    async def handler(self, websocket, path):
        """处理收到的消息"""
        if path == self.path:
            self.logger.info(f'OneBot 已连接：{path}')
            try:
                async for message in websocket:
                    msg_data = json.loads(message)
                    # 判断是否是心跳消息
                    if msg_data.get('post_type') == 'meta_event' and msg_data.get('meta_event_type') == 'heartbeat':
                        # 处理心跳消息
                        self.heartbeat_handler.add_heartbeat(msg_data)
                    elif msg_data.get('post_type') == 'message' and msg_data.get('message_type') == 'private':
                        # 收到私聊消息，处理它
                        await self.process_private_message(websocket, msg_data)
                    else:
                        # 记录其他消息
                        self.logger.info(f'收到消息：{message}')
            except websockets.exceptions.ConnectionClosed as e:
                self.logger.info('连接已关闭')
        else:
            self.logger.warning(f'收到未知路径的连接：{path}')
            await websocket.close()

    async def process_private_message(self, websocket, msg_data):
        """处理 QQ 用户发送的私聊消息"""
        user_id = msg_data['sender']['user_id']
        message_text = msg_data.get('raw_message', '')
        self.logger.info(f'收到来自 {user_id} 的私聊消息：{message_text}')

        # 发送消息到 Dify，传递用户 ID
        response = self.dify_client.send_request(message_text, user_id)
        answer = self.dify_receiver.process_response(response)

        if answer:
            reply = {
                "action": "send_private_msg",
                "params": {
                    "user_id": user_id,
                    "message": answer
                },
                "echo": "send_private_msg"
            }
            await websocket.send(json.dumps(reply))
            self.logger.debug(f'已向 {user_id} 发送回复')
        else:
            self.logger.error('未能从 Dify 获取有效响应')

    async def start(self, dify_client, dify_receiver):
        """启动 WebSocket 服务器"""
        self.dify_client = dify_client
        self.dify_receiver = dify_receiver
        self.heartbeat_handler = HeartbeatHandler(self.logger, interval=300)

        # 使用自定义的处理函数来处理路径
        async def ws_handler(websocket, path):
            await self.handler(websocket, path)

        server = await websockets.serve(ws_handler, self.host, self.port)
        self.logger.info(f'WebSocket 服务器已启动，监听 {self.host}:{self.port}{self.path}')
        await server.wait_closed()
