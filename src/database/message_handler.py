# message_handler.py
import time
from src.data_manager import DataManager
from src.database.tools import format_timestamp


class MessageHandler:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.data_manager = DataManager(config_manager=self.config_manager)

    async def store_message(self, msg_data, conn, is_group=True):
        """通用存储消息到数据库的函数"""
        message_id = msg_data['message_id']
        user_id = msg_data['sender']['user_id']
        nickname = msg_data['sender']['nickname']
        message = msg_data['raw_message']
        timestamp = format_timestamp(msg_data['time'])

        # 构建 SQL 插入语句
        if is_group:
            role = msg_data['sender']['role']
            await conn.execute('''
                INSERT INTO group_messages (message_id, time, user_id, nickname, role, message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (message_id, timestamp, user_id, nickname, role, message))
        else:
            sub_type = msg_data['sub_type']
            raw_message = msg_data['raw_message']
            post_type = msg_data['post_type']
            await conn.execute('''
                INSERT INTO private_messages (message_id, time, user_id, nickname, sub_type, message, raw_message, post_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (message_id, timestamp, user_id, nickname, sub_type, message, raw_message, post_type))

        await conn.commit()

        # 更新缓存
        self.update_cache(user_id, message_id, nickname, message)

    def update_cache(self, user_id, message_id, nickname, message):
        """更新缓存中的最新消息"""
        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        message_data = f"[{timestamp_str}] {nickname}: {message}"
        self.data_manager.set_latest_message_id(user_id, message_id, message_data)
