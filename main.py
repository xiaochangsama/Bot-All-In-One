# main.py

import asyncio
from logger import setup_logger
from dify_client import DifyClient
from dify_receiver import DifyReceiver
from message_listener import MessageListener

async def main():
    # 设置日志
    logger = setup_logger('Main')

    # 初始化 DifyClient
    dify_client = DifyClient(logger)

    # 初始化 DifyReceiver
    dify_receiver = DifyReceiver(logger)

    # 初始化 MessageListener
    listener = MessageListener('127.0.0.1', 8070, '/ws', logger)

    # 启动监听
    await listener.start(dify_client, dify_receiver)

if __name__ == "__main__":
    asyncio.run(main())
