def handle_message(message):
    """插件处理消息的入口"""
    if "你好" in message:
        return {
            "type": "回复",
            "message": "你好！我是插件1，已处理你的消息。"
        }
    elif "跳过" in message:
        return {
            "type": "跳出"
        }
    elif "取消" in message:
        return {
            "type": "取消"
        }
    return {
        "type": "继续"
    }
