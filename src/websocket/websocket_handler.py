class WebSocketHandler:
    """处理消息的存储、插件调用、Dify响应、QQ消息发送"""

    def __init__(self, plugin_handler, dify_handler, db_manager, qq_sender, message_handler, logger):
        self.plugin_handler = plugin_handler
        self.dify_handler = dify_handler
        self.db_manager = db_manager
        self.qq_sender = qq_sender
        self.message_handler = message_handler  # 新增的 message_handler 作为消息存储处理器
        self.logger = logger

    async def process_private_message(self, websocket, msg_data):
        """处理 QQ 私聊消息"""
        user_id = msg_data['sender']['user_id']
        self.logger.info(f'收到私聊消息来自 {user_id}')

        # 获取数据库连接
        conn = await self.db_manager.get_connection(user_id, is_group=False)

        # 存储私聊消息
        await self.message_handler.store_message(msg_data, conn, is_group=False)

        # 传递给插件处理
        if not await self.plugin_handler.handle_plugin_message(websocket, msg_data, user_id, is_group=False):
            # 插件未处理，调用 Dify AI 回复
            response = await self.dify_handler.send_dify_response(websocket, msg_data, user_id, is_group=False)
            if response:
                # 通过 QQWebSocketSender 发送消息
                await self.qq_sender.send_message(response, msg_data, websocket)

    async def process_group_message(self, websocket, msg_data):
        """处理 QQ 群聊消息"""
        group_id = msg_data['group_id']
        user_id = msg_data['sender']['user_id']
        self.logger.info(f'收到群聊消息来自群 {group_id} 的用户 {user_id}')

        # 获取数据库连接
        conn = await self.db_manager.get_connection(group_id, is_group=True)

        # 存储群聊消息
        await self.message_handler.store_message(msg_data, conn, is_group=True)

        # 传递给插件处理
        if not await self.plugin_handler.handle_plugin_message(websocket, msg_data, group_id, is_group=True):
            # 插件未处理，调用 Dify AI 回复
            response = await self.dify_handler.send_dify_response(websocket, msg_data, group_id, is_group=True)
            if response:
                # 通过 QQWebSocketSender 发送消息
                await self.qq_sender.send_message(response, msg_data, websocket)
