import aiosqlite

from src.data_manager import DataManager
from src.database.use_aiosqlite.tools import format_timestamp

# 异步创建/打开数据库并创建表
async def init_private_db(user_id):
    db_path = f"./data/{user_id}.db"
    conn = await aiosqlite.connect(db_path)

    # 创建表 (如果不存在)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS private_messages (
            message_id INTEGER PRIMARY KEY,
            time TEXT,
            user_id INTEGER,
            nickname TEXT,
            sub_type TEXT,
            message TEXT,
            raw_message TEXT,
            post_type TEXT
        )
    ''')
    await conn.commit()
    return conn


# 异步存储私聊消息到数据库
async def store_private_message(msg_data, conn):
    message_id = msg_data['message_id']
    user_id = msg_data['sender']['user_id']
    nickname = msg_data['sender']['nickname'].encode().decode('unicode_escape')
    sub_type = msg_data['sub_type']
    message = msg_data['message'][0]['data']['text'].encode().decode('unicode_escape')
    raw_message = msg_data['raw_message'].encode().decode('unicode_escape')
    post_type = msg_data['post_type']
    timestamp = format_timestamp(msg_data['time'])

    # 插入消息记录
    await conn.execute('''
        INSERT INTO private_messages (message_id, time, user_id, nickname, sub_type, message, raw_message, post_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (message_id, timestamp, user_id, nickname, sub_type, message, raw_message, post_type))

    await conn.commit()

    # 更新DataManager中的最新消息ID
    data_manager = DataManager()
    data_manager.set_latest_message_id(user_id, message_id)
