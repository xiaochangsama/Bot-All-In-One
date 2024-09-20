# message_listener.py

import asyncio
import websockets
import json
from logger import setup_logger

class MessageListener:
    """作为 WebSocket 服务器，等待 OneBot 的连接"""

    def __init__(self, host, port, path, logger=None):
        self.host = host
        self.port = port
        self.path = path
        self.logger = logger or setup_logger('MessageListener', 'message_listener.log')

    async def handler(self, websocket, path):
        """处理收到的消息"""
        self.logger.info(f'OneBot 已连接：{path}')
        try:
            async for message in websocket:
                self.logger.info(f'收到消息：{message}')
                # 处理消息的逻辑
                msg_data = json.loads(message)
                # 检查消息类型，这里只是示例
                if msg_data.get('message_type') == 'private':
                    query = msg_data.get('raw_message')
                    # 发送请求到 Dify
                    response = self.dify_client.send_request(query)
                    # 处理 Dify 的响应
                    answer = self.dify_receiver.process_response(response)
                    # 构建回复消息
                    reply = {
                        "action": "send_private_msg",
                        "params": {
                            "user_id": msg_data['sender']['user_id'],
                            "message": answer
                        },
                        "echo": "send_private_msg"
                    }
                    await websocket.send(json.dumps(reply))
        except websockets.exceptions.ConnectionClosed as e:
            self.logger.info('连接已关闭')

    def start(self, dify_client, dify_receiver):
        """启动 WebSocket 服务器"""
        self.dify_client = dify_client
        self.dify_receiver = dify_receiver
        start_server = websockets.serve(self.handler, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        self.logger.info(f'WebSocket 服务器已启动，监听 {self.host}:{self.port}{self.path}')
        asyncio.get_event_loop().run_forever()

# 测试 MessageListener
if __name__ == "__main__":
    listener = MessageListener('127.0.0.1', 8070, '/ws')
    # 需要初始化 dify_client 和 dify_receiver
    listener.start(dify_client, dify_receiver)
