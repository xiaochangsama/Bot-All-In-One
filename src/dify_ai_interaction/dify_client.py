# client.py
import aiohttp
import json
from src.config_manager import ConfigManager
from src.data_manager import DataManager

class DifyClient:
    """负责与 Dify API 交互，发送请求并获取结果"""

    def __init__(self, logger):
        self.logger = logger
        config_manager = ConfigManager()
        self.api_key = config_manager.get('api_key')
        self.dify_url = config_manager.get('dify_url')
        self.response_mode = config_manager.get('response_mode', 'blocking')
        self.user_id = config_manager.get('user_id')
        self.conversation_mode = config_manager.get('conversation_mode', 'single')
        self.data_manager = DataManager(config_manager)

    async def send_request(self, query, identifier, is_group=False):
        """发送请求至 Dify，并获取 AI 返回的结果"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            "query": query,
            "inputs": {},  # 根据API文档可以填写具体内容
            "response_mode": self.response_mode,
            "user": self.user_id
        }

        # 根据会话模式选择处理方式
        if self.conversation_mode == 'single':
            # 从 DataManager 获取会话 ID
            conversation_id = self.data_manager.get_conversation_id(identifier)
            if conversation_id:
                data["conversation_id"] = conversation_id  # 如果有会话 ID，使用它
            else:
                self.logger.info(f"未找到 {identifier} 的会话 ID，将创建新会话")

        self.logger.info(f'发送请求至 Dify: {query}')
        self.logger.debug(f'请求数据: {json.dumps(data, indent=4)}')

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.dify_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        self.logger.debug(f'AI 响应: {response_data}')

                        # 检查是否有新的会话 ID，并保存
                        new_conversation_id = response_data.get("conversation_id")
                        if new_conversation_id and not conversation_id:
                            self.data_manager.set_conversation_id(identifier, new_conversation_id)
                            self.logger.info(f"已保存新的会话 ID: {new_conversation_id} 对应 {identifier}")

                        return response_data
                    else:
                        error_message = await response.text()  # 获取错误信息
                        self.logger.error(f'请求失败，状态码: {response.status}, 错误信息: {error_message}')
                        return None
        except Exception as e:
            self.logger.error(f'发送请求时发生错误: {e}')
            return None
