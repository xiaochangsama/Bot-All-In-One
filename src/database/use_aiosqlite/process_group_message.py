import time

import aiosqlite

from src import config_manager
from src.config_manager import ConfigManager
from src.data_manager import DataManager
from src.database.use_aiosqlite.tools import format_timestamp

# 异步创建/打开数据库并创建表
async def init_group_db(group_id):
    db_path = f"./data/{group_id}.db"
    conn = await aiosqlite.connect(db_path)

    # 创建表 (如果不存在)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS group_messages (
            message_id INTEGER PRIMARY KEY,
            time TEXT,
            user_id INTEGER,
            nickname TEXT,
            role TEXT,
            message TEXT
        )
    ''')
    await conn.commit()
    return conn


# 异步存储群聊消息到数据库
async def store_group_message(msg_data, conn):
    # 初始化 ConfigManager 实例
    config_manager = ConfigManager()

    group_id = msg_data['group_id']
    message_id = msg_data['message_id']
    user_id = msg_data['sender']['user_id']
    nickname = msg_data['sender']['nickname']  # 直接获取昵称，不进行 encode 和 decode
    role = msg_data['sender']['role']
    message = msg_data['raw_message']
    timestamp = format_timestamp(msg_data['time'])

    # 插入消息记录
    await conn.execute('''
        INSERT INTO group_messages (message_id, time, user_id, nickname, role, message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (message_id, timestamp, user_id, nickname, role, message))

    await conn.commit()

    # 准备message_data
    timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # 获取当前时间戳
    message_data = f"[{timestamp_str}] {nickname}: {message}"  # 格式化message_data

    # 在存储消息后更新缓存
    data_manager = DataManager(config_manager=config_manager)  # 传入 ConfigManager 实例
    data_manager.set_latest_message_id(user_id, message_id, message_data)
