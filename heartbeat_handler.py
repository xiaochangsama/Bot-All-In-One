# heartbeat_handler.py

import asyncio
from collections import deque

class HeartbeatHandler:
    """心跳消息处理器"""

    def __init__(self, logger, interval=300):
        """
        初始化心跳处理器
        :param logger: 日志记录器
        :param interval: 处理心跳消息的时间间隔，单位：秒
        """
        self.logger = logger
        self.heartbeat_messages = deque()
        self.interval = interval
        # 启动心跳消息处理任务
        asyncio.create_task(self.process_heartbeats())

    async def process_heartbeats(self):
        """定期处理心跳消息"""
        while True:
            await asyncio.sleep(self.interval)
            if self.heartbeat_messages:
                count = len(self.heartbeat_messages)
                self.logger.info(f'在过去的{self.interval}秒内收到{count}条心跳消息')
                # 清空队列
                self.heartbeat_messages.clear()

    def add_heartbeat(self, msg_data):
        """添加心跳消息到队列"""
        self.heartbeat_messages.append(msg_data)
        # 不记录详细的心跳消息日志，只在简化输出时记录
        self.logger.debug('收到心跳消息')
