import re
import json
from datetime import datetime  # 新增导入

from src.dify_ai_interaction.dify_client import DifyClient
from src.dify_ai_interaction.dify_sender import DifySender


class DifyHandler:
    """负责会话管理和处理AI交互流程"""

    def __init__(self, logger, qq_sender):
        self.client = DifyClient(logger)
        self.sender = DifySender(logger, qq_sender)  # 传递 qq_sender 实例
        self.logger = logger

    async def send_dify_response(self, websocket, msg_data, target_id, is_group):
        """处理消息，调用 DifyClient 获取 AI 回复，并使用 sender 发送"""
        message_text = msg_data.get('raw_message', '')
        self.logger.debug(f'原始消息: {msg_data}')

        # 提取用户ID和昵称
        user_id = msg_data.get('sender', {}).get('user_id', '')
        nickname = msg_data.get('sender', {}).get('nickname', '')

        # 获取当前的日期和时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 替换图片、语音和其他类型的CQ码为提示信息
        message_text = self.replace_cq_message(message_text)

        # 查找CQ码并保留name中的@称呼，去掉其他内容
        def replace_cq(match):
            cq_text = match.group(0)
            # 提取name=@xxx部分并保留xxx
            name_match = re.search(r'name=(@\S+)', cq_text)
            if name_match:
                result = name_match.group(1)  # 保留@称呼
                # 去除可能存在的反方括号
                return result.replace(']', '')
            return ''

        # 如果消息中包含CQ码，处理CQ码，否则保留原消息
        if '[CQ:at,' in message_text:
            cleaned_message = re.sub(r'\[CQ:at,.*?\]', replace_cq, message_text).strip()
            self.logger.debug(f'清理后的消息: {cleaned_message}')
        else:
            cleaned_message = message_text  # 不包含CQ码，原样使用消息
            self.logger.debug(f'消息中不包含CQ码，使用原消息: {cleaned_message}')

        # 构建发送给AI的json格式，加入time字段
        ai_request = {
            "user_id": user_id,
            "nickname": nickname,
            "message": cleaned_message,
            "time": current_time  # 添加时间字段
        }

        # 将请求数据转换为json字符串
        ai_request_json = json.dumps(ai_request, ensure_ascii=False)
        self.logger.debug(f'发送给AI的消息: {ai_request_json}')

        # 获取 AI 的回复
        response = await self.client.send_request(ai_request_json, target_id, is_group)
        if response:
            answer = response.get('answer', '')
            if answer:
                self.logger.debug(f'AI 回复: {answer}')
                await self.sender.send_message(answer, target_id, websocket, is_group, msg_data)  # 传递 msg_data
            else:
                self.logger.error('未能从 Dify 获取有效答案')
        else:
            self.logger.error('Dify API 响应无效')

    def replace_cq_message(self, message_text):
        """替换图片、语音、转发、回复等CQ码为提示信息"""
        # 替换图片CQ码为提示信息
        message_text = re.sub(r'\[CQ:image,.*?\]', '图片消息，你使用的是旧版QQ，无法查看', message_text)

        # 替换语音CQ码为提示信息
        message_text = re.sub(r'\[CQ:record,.*?\]', '语音消息，你使用的是旧版QQ，无法查看', message_text)

        # 替换回复CQ码为提示信息
        message_text = re.sub(r'\[CQ:reply,.*?\]', '回复消息，你使用的是旧版QQ，无法查看', message_text)

        # 替换转发CQ码为提示信息
        message_text = re.sub(r'\[CQ:forward,.*?\]', '合并转发消息，你使用的是旧版QQ，无法查看', message_text)

        return message_text
