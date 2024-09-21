import requests
import json
from logger import setup_logger
from config_manager import ConfigManager
from data_manager import DataManager


class DifyClient:
    """用于与 Dify 通信的客户端"""

    def __init__(self, logger=None):
        self.logger = logger or setup_logger('DifyClient')
        config_manager = ConfigManager()
        self.api_key = config_manager.get_default('api_key')
        self.dify_url = config_manager.get_default('dify_url', 'http://localhost/v1/chat-messages')
        self.response_mode = config_manager.get_default('response_mode', 'blocking')
        self.user_id = config_manager.get_default('user_id', 'abc-123')
        self.conversation_mode = config_manager.get_default('conversation_mode', 'single')
        self.data_manager = DataManager()  # 用于管理会话 ID

        if not self.api_key or self.api_key == 'your_api_key_here':
            self.logger.error('API Key 未在配置文件中设置，请修改配置文件后重新运行程序。')
            raise ValueError('API Key 未在配置文件中设置')

    async def send_request(self, query, identifier, is_group=False, files=None):
        """
        发送请求到 Dify，根据 `identifier` 和是否为群聊来决定会话
        :param identifier: 用户 ID 或 群聊 ID
        :param is_group: 是否为群聊
        """
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

        # 根据会话模式选择处理方式
        if self.conversation_mode == 'single':
            if is_group:
                # 使用群聊 ID 管理会话
                conversation_id = self.data_manager.get_conversation_id(f"group_{identifier}")
            else:
                # 使用用户 ID 管理会话
                conversation_id = self.data_manager.get_conversation_id(identifier)

            if conversation_id:
                data["conversation_id"] = conversation_id  # 使用已有会话 ID
            else:
                self.logger.info(f'未找到 {identifier} 的会话 ID，等待从 Dify 响应中获取')

        elif self.conversation_mode == 'multi':
            # 多会话模式，不使用会话 ID，每次请求新建对话
            data["conversation_id"] = ""

        self.logger.info(f'发送请求到 Dify，查询：{query}，会话模式：{self.conversation_mode}')

        try:
            # 处理非流式响应
            if self.response_mode == 'blocking':
                response = requests.post(url, headers=headers, data=json.dumps(data))
                self.logger.debug(f'响应状态码：{response.status_code}')
                self.logger.debug(f'响应内容：{response.text}')

                if response.status_code == 200:
                    response_data = response.json()

                    # 检查是否有 conversation_id，并保存到 DataManager
                    conversation_id = response_data.get("conversation_id")
                    if conversation_id and self.conversation_mode == 'single':
                        key = f"group_{identifier}" if is_group else identifier
                        self.data_manager.set_conversation_id(key, conversation_id)
                        self.logger.info(f'获取到 {identifier} 的新会话 ID：{conversation_id}')

                    return response_data
                else:
                    self.logger.error(f'请求失败，状态码：{response.status_code}')
                    self.logger.error(f'响应内容：{response.text}')
                    return None

        except Exception as e:
            self.logger.error(f'发送请求到 Dify 时发生异常：{e}')
            return None
