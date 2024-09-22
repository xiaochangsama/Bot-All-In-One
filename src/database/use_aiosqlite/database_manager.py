import asyncio
import aiosqlite


class DatabaseManager:
    def __init__(self, config_manager):
        self.connections = {}
        self.config_manager = config_manager
        self.idle_timeout = config_manager.get_db_idle_timeout()
        self.timers = {}

    async def get_connection(self, db_id, is_group=True):
        if db_id not in self.connections:
            # 初始化数据库
            if is_group:
                self.connections[db_id] = await self.init_group_db(db_id)
            else:
                self.connections[db_id] = await self.init_private_db(db_id)

        # 重置倒计时
        self.reset_timer(db_id)
        return self.connections[db_id]

    async def init_group_db(self, group_id):
        db_path = f"./data/{group_id}.db"
        conn = await aiosqlite.connect(db_path)
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

    async def init_private_db(self, user_id):
        db_path = f"./data/{user_id}.db"
        conn = await aiosqlite.connect(db_path)
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

    def reset_timer(self, db_id):
        if db_id in self.timers:
            self.timers[db_id].cancel()  # 取消现有的定时任务
        self.timers[db_id] = asyncio.create_task(self.close_db_after_timeout(db_id))

    async def close_db_after_timeout(self, db_id):
        await asyncio.sleep(self.idle_timeout)  # 等待指定的超时时间
        await self.close_connection(db_id)

    async def close_connection(self, db_id):
        if db_id in self.connections:
            await self.connections[db_id].close()  # 关闭数据库连接
            del self.connections[db_id]  # 从连接池中移除
            print(f"数据库 {db_id} 连接已关闭")

    async def close_all_connections(self):
        """关闭所有数据库连接"""
        for db_id in list(self.connections.keys()):
            await self.close_connection(db_id)
