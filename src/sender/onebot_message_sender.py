import json
import requests
import websockets

class OneBotMessageSender:
    def __init__(self, transport="websocket", websocket_url=None, api_url=None):
        """
        初始化消息发送器类
        :param transport: 通信方式，支持 "websocket" 或 "http"
        :param websocket_url: WebSocket URL
        :param api_url: HTTP API URL
        """
        self.transport = transport
        self.websocket_url = websocket_url
        self.api_url = api_url

    async def send_via_websocket(self, message):
        """通过 WebSocket 发送消息"""
        async with websockets.connect(self.websocket_url) as websocket:
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            return response

    def send_via_http(self, message):
        """通过 HTTP 发送消息"""
        response = requests.post(self.api_url, json=message)
        return response.json()

    async def send_message(self, message):
        """发送消息，根据选择的传输方式（WebSocket或HTTP）"""
        if self.transport == "websocket":
            return await self.send_via_websocket(message)
        elif self.transport == "http":
            return self.send_via_http(message)
        else:
            raise ValueError("Unsupported transport method. Use 'websocket' or 'http'.")

