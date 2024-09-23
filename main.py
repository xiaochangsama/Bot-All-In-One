import asyncio

from src.config_manager import ConfigManager
from src.database.database_manager import DatabaseManager
from src.database.message_handler import MessageHandler
from src.dify_ai_interaction.dify_handler import DifyHandler
from src.logger import setup_logger
from src.plugin.plugin_handler import PluginHandler
from src.plugin.plugin_manager import PluginManager
from src.websocket.message_listener import MessageListener
from src.websocket.qq_websocket_sender import QQWebSocketSender
from src.websocket.websocket_handler import WebSocketHandler


async def main():
    # 加载配置
    config_manager = ConfigManager(config_file='config/config.json')

    # 获取配置中的 WebSocket URL
    websocket_url = config_manager.get('websocket_url', 'ws://localhost:8070')

    # 初始化日志记录器
    logger = setup_logger('main')

    # 初始化数据库管理器
    db_manager = DatabaseManager(config_manager)

    # 初始化 QQ 消息发送器
    qq_sender = QQWebSocketSender(config_manager, db_manager, logger)

    # 初始化 Dify 处理器
    dify_handler = DifyHandler(logger,qq_sender)

    # 初始化插件管理器
    plugin_manager = PluginManager()  # 假设你有一个 PluginManager 类
    plugin_handler = PluginHandler(plugin_manager, logger)

    message_handler = MessageHandler(config_manager)  # 确保已导入并初始化

    # 初始化 WebSocket 处理器
    websocket_handler = WebSocketHandler(plugin_handler, dify_handler, db_manager, qq_sender, message_handler, logger)

    # 初始化消息监听器
    message_listener = MessageListener(config_manager, websocket_handler, logger)


    # 启动 WebSocket 服务器
    await message_listener.start()


if __name__ == "__main__":
    asyncio.run(main())
