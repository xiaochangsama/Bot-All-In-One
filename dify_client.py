# dify_client.py

import requests
import json
from logger import setup_logger
from config_manager import ConfigManager

class DifyClient:
    """用于与 Dify 通信的客户端"""

    def __init__(self, logger=None):
        self.logger = logger or setup_logger('DifyClient')
        # 从配置文件中读取配置参数
        config_manager = ConfigManager()
        self.api_key = config_manager.get_default('api_key')
        self.dify_url = config_manager.get_default('dify_url', 'http://localhost/v1/chat-messages')
        self.response_mode = config_manager.get_default('response_mode', 'streaming')
        self.user_id = config_manager.get_default('user_id', 'abc-123')

        if not self.api_key or self.api_key == 'your_api_key_here':
            self.logger.error('API Key 未在配置文件中设置，请修改配置文件后重新运行程序。')
            raise ValueError('API Key 未在配置文件中设置')

    def send_request(self, query, files=None):
        """发送请求到 Dify"""

        url = self.dify_url
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            "inputs": {},
            "query": query,
            "response_mode": self.response_mode,
            "conversation_id": "",
            "user": self.user_id,
            "files": files or []
        }

        self.logger.info('发送请求到 Dify')
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            self.logger.info('请求成功')
            return response.json()
        else:
            self.logger.error(f'请求失败，状态码：{response.status_code}')
            return None

# 测试 DifyClient
if __name__ == "__main__":
    client = DifyClient()
    response = client.send_request('What are the specs of the iPhone 13 Pro Max?')
    print(response)
