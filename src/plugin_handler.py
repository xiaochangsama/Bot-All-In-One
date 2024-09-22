import json


class PluginHandler:
    def __init__(self, plugin_manager, logger):
        self.plugin_manager = plugin_manager
        self.logger = logger

    async def handle_plugin_message(self, websocket, msg_data, target_id, is_group):
        """处理插件消息"""
        plugin_result = self.plugin_manager.handle_message(msg_data)

        if plugin_result["handled"]:
            if plugin_result["reply"] is not None:
                reply_action = "send_group_msg" if is_group else "send_private_msg"
                reply = {
                    "action": reply_action,
                    "params": {
                        "group_id" if is_group else "user_id": target_id,
                        "message": plugin_result["reply"]
                    },
                    "echo": reply_action
                }
                await websocket.send(json.dumps(reply))
                self.logger.debug(f'已向 {"群" if is_group else "用户"} {target_id} 发送插件回复')
            else:
                self.logger.debug('插件处理后取消回复')
            return True
        return False
