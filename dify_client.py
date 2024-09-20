# dify_client.py

import requests
import json
from logger import setup_logger

class DifyClient:
    """用于与Dify通信的客户端"""

    def __init__(self, api_key, logger=None):
        self.api_key = api_key
        self.logger = logger or setup_logger('DifyClient', 'dify_client.log')

    def send_request(self, query, files=None):
        """发送请求到Dify"""

        url = 'http://localhost/v1/chat-messages'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            "inputs": {},
            "query": query,
            "response_mode": "streaming",
            "conversation_id": "",
            "user": "abc-123",
            "files": files or []
        }

        self.logger.info('发送请求到Dify')
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            self.logger.info('请求成功')
            return response.json()
        else:
            self.logger.error(f'请求失败，状态码：{response.status_code}')
            return None

# 测试DifyClient
if __name__ == "__main__":
    client = DifyClient('your_api_key_here')
    response = client.send_request('What are the specs of the iPhone 13 Pro Max?')
    print(response)
