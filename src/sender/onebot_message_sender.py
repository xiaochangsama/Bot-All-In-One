import json
import time

from src.config_manager import ConfigManager
from src.data_manager import DataManager


class OneBotMessageSender:
    def __init__(self, websocket_url='ws://127.0.0.1:8070'):
        """
        初始化消息发送器类，仅支持 WebSocket 方式
        :param websocket_url: WebSocket URL
        """
        self.websocket_url = websocket_url
        self.config_manager = ConfigManager()  # 初始化 ConfigManager
        self.data_manager = DataManager(config_manager=self.config_manager)  # 初始化 DataManager

    async def send_message(self, message,msg_data, websocket):
        """通过传入的 WebSocket 发送消息"""
        try:
            # 发送消息并接收响应
            await websocket.send(message)


        except Exception as e:
            # 记录错误日志
            print(f"通过 WebSocket 发送消息失败: {e}")
            return None

        print(msg_data)
        # 记录响应并处理
        message_id = msg_data.get('message_id', 'unknown')  # 获取消息ID
        user_id = msg_data.get('user_id', 'unknown')  # 获取用户ID
        bot_name = self.config_manager.get_default('bot_name', 'YourBot')  # 从配置文件获取 bot 名称

        # 准备 message_data
        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 获取当前时间戳
        message_data = f"[{timestamp_str}] {bot_name}: {message}"  # 格式化 message_data

        # 更新缓存
        self.data_manager.set_latest_message_id(user_id, message_id, message_data)
