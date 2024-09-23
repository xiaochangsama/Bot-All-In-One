# handler.py
from src.dify_ai_interaction.dify_client import DifyClient
from src.dify_ai_interaction.dify_sender import DifySender


class DifyHandler:
    """负责会话管理和处理AI交互流程"""

    def __init__(self, logger,qq_sender):
        self.client = DifyClient(logger)
        self.sender = DifySender(logger, qq_sender)  # 传递 qq_sender 实例
        self.logger = logger

    async def send_dify_response(self, websocket, msg_data, target_id, is_group):
        """处理消息，调用 DifyClient 获取 AI 回复，并使用 sender 发送"""
        message_text = msg_data.get('raw_message', '')
        self.logger.debug(f'准备处理消息: {message_text}')

        # 获取 AI 的回复
        response = await self.client.send_request(message_text, target_id, is_group)
        if response:
            answer = response.get('answer', '')
            if answer:
                self.logger.debug(f'AI 回复: {answer}')
                await self.sender.send_message(answer, target_id, websocket, is_group, msg_data)  # 传递 msg_data
            else:
                self.logger.error('未能从 Dify 获取有效答案')
        else:
            self.logger.error('Dify API 响应无效')
