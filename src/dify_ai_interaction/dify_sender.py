import json


class DifySender:
    """负责构建并发送 AI 回复消息"""

    def __init__(self, logger, qq_sender):
        self.logger = logger
        self.qq_sender = qq_sender  # 传入 QQ 消息发送器

    def build_message(self, target_id, answer, is_group, msg_data):
        """根据用户/群聊ID和AI回复构建 QQ 消息"""
        # 构建 QQ 消息结构
        if is_group:
            message = {
                "action": "send_group_msg",
                "params": {
                    "group_id": target_id,
                    "message": answer
                }
            }
        else:
            message = {
                "action": "send_private_msg",
                "params": {
                    "user_id": target_id,
                    "message": answer
                }
            }

        return json.dumps(message)

    async def send_message(self, answer, target_id, websocket, is_group, msg_data):
        """通过 QQWebSocketSender 发送 AI 回复"""
        message = self.build_message(target_id, answer, is_group, msg_data)
        try:
            await self.qq_sender.send_message(message, msg_data, websocket)
            self.logger.info(f'发送消息至 {"群聊" if is_group else "私聊"} {target_id}: {answer}')
        except Exception as e:
            self.logger.error(f'消息发送失败: {e}')
