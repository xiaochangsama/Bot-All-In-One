import json
import time
import logging

class QQWebSocketSender:
    def __init__(self, config_manager, data_manager, logger=None):
        """
        初始化 QQ WebSocket 消息发送器类
        :param config_manager: 配置管理器实例
        :param data_manager: 数据管理器实例
        :param logger: 日志记录器实例
        """
        self.config_manager = config_manager
        self.data_manager = data_manager
        self.logger = logger or logging.getLogger(__name__)

    async def send_message(self, message, msg_data, websocket):
        """通过 WebSocket 发送 QQ 消息"""
        try:
            # 发送消息
            await websocket.send(message)
            self.logger.info(f"成功发送消息: {message}")
        except Exception as e:
            # 记录错误日志
            self.logger.error(f"通过 WebSocket 发送消息失败: {e}")
            return None

        # 处理消息并更新缓存
        self._log_and_cache_message(message, msg_data)

    def _log_and_cache_message(self, message, msg_data):
        """记录消息日志并更新缓存"""
        message_id = msg_data.get('message_id', 'unknown')  # 获取消息ID
        user_id = msg_data.get('user_id', 'unknown')  # 获取用户ID
        bot_name = self.config_manager.get('bot_name', 'YourBot')  # 从配置文件获取 bot 名称

        # 准备 message_data
        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        message_data = f"[{timestamp_str}] {bot_name}: {message}"

        # 更新缓存
        self.data_manager.set_latest_message_id(user_id, message_id, message_data)
        self.logger.info(f"缓存更新：{message_data}")
