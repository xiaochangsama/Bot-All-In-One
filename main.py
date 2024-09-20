# main.py

import asyncio
from logger import setup_logger
from data_manager import DataManager
from dify_client import DifyClient
from dify_receiver import DifyReceiver
from message_listener import MessageListener

async def main():
    # 设置日志
    logger = setup_logger('Main')

    # 初始化 DataManager
    data_manager = DataManager()
    data_manager.set_data('api_key', 'your_api_key_here')

    # 初始化 DifyClient
    api_key = data_manager.get_data('api_key')
    dify_client = DifyClient(api_key, logger)

    # 初始化 DifyReceiver
    dify_receiver = DifyReceiver(logger)

    # 初始化 MessageListener
    listener = MessageListener('127.0.0.1', 8070, '/ws', logger)

    # 启动监听
    await listener.start(dify_client, dify_receiver)

if __name__ == "__main__":
    asyncio.run(main())
