import aiohttp  # 使用 aiohttp 处理异步请求
from config_manager import ConfigManager
from data_manager import DataManager
from logger import setup_logger


class DifyClient:
    """用于与 Dify 通信的异步客户端"""

    def __init__(self, logger=None):
        self.logger = logger or setup_logger('DifyClient')
        config_manager = ConfigManager()  # 使用配置管理器
        self.api_key = config_manager.get_default('api_key')
        self.dify_url = config_manager.get_default('dify_url', 'http://localhost/v1/chat-messages')
        self.response_mode = config_manager.get_default('response_mode', 'blocking')
        self.user_id = config_manager.get_default('user_id', 'abc-123')
        self.conversation_mode = config_manager.get_default('conversation_mode', 'multi')
        self.data_manager = DataManager()  # 管理会话 ID

        if not self.api_key:
            self.logger.error('API Key 未在配置文件中设置，请修改配置文件后重新运行程序。')
            raise ValueError('API Key 未在配置文件中设置')

    async def send_request(self, query, user_id):
        """发送请求到 Dify (异步)"""
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

        if self.conversation_mode == 'single':
            conversation_id = self.data_manager.get_conversation_id(user_id)
            if conversation_id:
                data["conversation_id"] = conversation_id
            else:
                self.logger.info(f'未找到 {user_id} 的会话 ID，等待从 Dify 响应中获取')
        else:
            data["conversation_id"] = ""  # 多会话模式

        self.logger.info(f'发送请求到 Dify，查询：{query}，会话模式：{self.conversation_mode}')

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.dify_url, json=data, headers=headers) as response:
                    if response.status == 200:
                        response_data = await response.json()

                        # 检查是否有 conversation_id，并保存到 DataManager
                        conversation_id = response_data.get("conversation_id")
                        if conversation_id and self.conversation_mode == 'single':
                            self.data_manager.set_conversation_id(user_id, conversation_id)
                            self.logger.info(f'获取到 {user_id} 的新会话 ID：{conversation_id}')

                        return response_data
                    else:
                        self.logger.error(f'请求失败，状态码：{response.status}')
                        self.logger.error(f'响应内容：{await response.text()}')
                        return None
            except Exception as e:
                self.logger.error(f'发送请求到 Dify 时发生异常：{e}')
                return None
