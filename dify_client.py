# dify_client.py

import requests
import json
from logger import setup_logger
from config_manager import ConfigManager

class DifyClient:
    """用于与 Dify 通信的客户端"""

    def __init__(self, logger=None):
        self.logger = logger or setup_logger('DifyClient')
        # 加载配置
        config_manager = ConfigManager()
        self.api_key = config_manager.get_default('api_key')
        self.dify_url = config_manager.get_default('dify_url', 'http://localhost/v1/chat-messages')
        self.response_mode = config_manager.get_default('response_mode', 'blocking')  # 默认值为 'blocking'
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
            "user": self.user_id
        }

        self.logger.info(f'发送请求到 Dify，查询：{query}')
        try:
            if self.response_mode == 'blocking':
                # 非流式响应处理
                response = requests.post(url, headers=headers, data=json.dumps(data))
                self.logger.debug(f'响应状态码：{response.status_code}')
                self.logger.debug(f'响应内容：{response.text}')
                if response.status_code == 200:
                    self.logger.debug('请求 Dify 成功')
                    try:
                        return response.json()
                    except json.JSONDecodeError as e:
                        self.logger.error(f'解析 Dify 响应时发生 JSONDecodeError: {e}')
                        self.logger.error(f'响应内容：{response.text}')
                        return None
                else:
                    self.logger.error(f'请求失败，状态码：{response.status_code}')
                    self.logger.error(f'响应内容：{response.text}')
                    return None
            elif self.response_mode == 'streaming':
                # 流式响应处理
                with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
                    self.logger.debug(f'响应状态码：{response.status_code}')
                    if response.status_code == 200:
                        self.logger.debug('请求 Dify 成功，开始处理流式响应')
                        # 处理流式响应
                        answer = ''
                        for line in response.iter_lines():
                            if line:
                                line_str = line.decode('utf-8').strip()
                                self.logger.debug(f'接收到流数据：{line_str}')
                                if line_str.startswith('data:'):
                                    json_str = line_str[5:].strip()
                                    try:
                                        json_data = json.loads(json_str)
                                        if json_data.get('event') == 'message':
                                            answer += json_data.get('answer', '')
                                        elif json_data.get('event') == 'message_end':
                                            self.logger.debug('消息接收完毕')
                                            break
                                    except json.JSONDecodeError as e:
                                        self.logger.error(f'解析流数据时发生 JSONDecodeError: {e}')
                        return {'answer': answer}
                    else:
                        self.logger.error(f'请求失败，状态码：{response.status_code}')
                        self.logger.error(f'响应内容：{response.text}')
                        return None
            else:
                self.logger.error(f'无效的 response_mode：{self.response_mode}')
                return None
        except Exception as e:
            self.logger.error(f'发送请求到 Dify 时发生异常：{e}')
            return None
