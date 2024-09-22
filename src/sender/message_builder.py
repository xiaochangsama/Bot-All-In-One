import json

class MessageBuilder:
    @staticmethod
    def build_message(target_id, message, is_group):
        """构建用于发送的QQ消息"""
        reply_action = "send_group_msg" if is_group else "send_private_msg"
        reply = {
            "action": reply_action,
            "params": {
                "group_id" if is_group else "user_id": target_id,
                "message": message
            },
            "echo": reply_action
        }
        return json.dumps(reply)
