import json


class DifyHandler:
    def __init__(self, dify_client, dify_receiver, logger):
        self.dify_client = dify_client
        self.dify_receiver = dify_receiver
        self.logger = logger

    async def send_dify_response(self, websocket, msg_data, target_id, is_group):
        """调用 DifyClient 发送 AI 响应"""
        message_text = msg_data.get('raw_message', '')
        response = await self.dify_client.send_request(message_text, target_id, is_group)
        answer = self.dify_receiver.process_response(response)

        if answer:
            reply_action = "send_group_msg" if is_group else "send_private_msg"
            reply = {
                "action": reply_action,
                "params": {
                    "group_id" if is_group else "user_id": target_id,
                    "message": answer
                },
                "echo": reply_action
            }
            await websocket.send(json.dumps(reply))
            self.logger.debug(f'已向 {"群" if is_group else "用户"} {target_id} 发送 AI 回复')
        else:
            self.logger.error('未能从 Dify 获取有效响应')
