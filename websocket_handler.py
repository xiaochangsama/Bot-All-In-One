from database.use_aiosqlite.process_group_message import store_group_message
from database.use_aiosqlite.process_private_message import store_private_message


class WebSocketHandler:
    def __init__(self, plugin_handler, dify_handler, db_manager, config_manager, logger):
        self.plugin_handler = plugin_handler
        self.dify_handler = dify_handler
        self.db_manager = db_manager
        self.config_manager = config_manager
        self.logger = logger

    async def process_private_message(self, websocket, msg_data):
        """处理 QQ 用户发送的私聊消息"""
        user_id = msg_data['sender']['user_id']
        self.logger.info(f'收到来自 {user_id} 的私聊消息')

        # 获取数据库连接并存储私聊消息
        conn = await self.db_manager.get_connection(user_id, is_group=False)
        await store_private_message(msg_data, conn)

        # 处理插件消息
        if not await self.plugin_handler.handle_plugin_message(websocket, msg_data, user_id, is_group=False):
            # 插件未处理，发送 AI 回复
            await self.dify_handler.send_dify_response(websocket, msg_data, user_id, is_group=False)

    async def process_group_message(self, websocket, msg_data):
        """处理 QQ 群聊消息"""
        group_id = msg_data['group_id']
        user_id = msg_data['sender']['user_id']
        self.logger.info(f'收到来自群 {group_id} 的消息')

        # 获取数据库连接并存储群聊消息
        conn = await self.db_manager.get_connection(group_id, is_group=True)
        await store_group_message(msg_data, conn)

        # 检查是否允许回复
        group_setting = self.config_manager.get_group_chat_setting(group_id)
        if not group_setting.get('enabled', True):
            self.logger.debug(f'群 {group_id} 已被配置为不回复消息')
            return

        # 处理插件消息
        if not await self.plugin_handler.handle_plugin_message(websocket, msg_data, group_id, is_group=True):
            # 插件未处理，发送 AI 回复
            await self.dify_handler.send_dify_response(websocket, msg_data, group_id, is_group=True)
