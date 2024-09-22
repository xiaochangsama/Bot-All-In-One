import json
import os
import shutil

class ConfigManager:
    """管理配置文件的类，使用 JSON 格式"""

    def __init__(self, config_file='config/config.json', default_file='config/default/default_config.json'):
        self.config_file = config_file
        self.default_file = default_file
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件，如果不存在则从默认配置文件复制"""
        if not os.path.exists(self.config_file):
            self.create_default_config()  # 如果 config.json 不存在，从默认文件复制
        with open(self.config_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def create_default_config(self):
        """从默认配置文件复制 config.json"""
        if os.path.exists(self.default_file):
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            shutil.copy(self.default_file, self.config_file)
            print(f"配置文件 {self.config_file} 不存在，已从默认配置 {self.default_file} 复制")
        else:
            raise FileNotFoundError(f"默认配置文件 {self.default_file} 不存在，无法创建 {self.config_file}")

    def get_default(self, key, default=None):
        """从配置文件中获取默认配置"""
        return self.config.get("chat_setting", {}).get("default", {}).get(key, default)

    def get_all(self, key, default=None):
        """从配置文件中获取全部配置"""
        return self.config.get(key, default)

    def get_group_chat_setting(self, group_id):
        """获取群聊的配置，优先读取群聊特定配置"""
        group_chats = self.config.get("chat_setting", {}).get("group_chat", {})
        group_config = group_chats.get(str(group_id), None)
        if group_config is not None:
            return group_config
        # 使用默认配置
        return self.config.get("chat_setting", {}).get("default", {"enabled": False})

    def get_private_chat_setting(self, user_id):
        """获取个人聊天的配置，优先读取个人特定配置"""
        private_chats = self.config.get("chat_setting", {}).get("private_chat", {})
        private_config = private_chats.get(str(user_id), None)
        if private_config is not None:
            return private_config
        # 使用默认配置
        return self.config.get("chat_setting", {}).get("default", {"enabled": False})

    def validate_config(self):
        """验证配置文件是否包含所有必需字段"""
        required_fields = ['api_key', 'dify_url', 'response_mode', 'user_id']
        missing_fields = [field for field in required_fields if field not in self.config]
        if missing_fields:
            raise ValueError(f"配置文件中缺少必要字段: {', '.join(missing_fields)}")

    def get_db_idle_timeout(self):
        """获取数据库关闭倒计时（秒数）"""
        return self.config.get("db_idle_timeout", 300)  # 默认300秒（5分钟）

    def get_onebot_config(self):
        """获取 OneBot 的相关配置"""
        return self.config.get("onebot_config", {})

    def get_transport_type(self):
        """获取消息发送的传输方式（WebSocket或HTTP）"""
        return self.get_onebot_config().get("transport_type", "websocket")

    def get_websocket_url(self):
        """获取 OneBot WebSocket URL"""
        return self.get_onebot_config().get("websocket_url", "ws://127.0.0.1:8070")

    def get_http_api_url(self):
        """获取 OneBot HTTP API URL"""
        return self.get_onebot_config().get("http_api_url", "http://127.0.0.1:8070")

    def get_cache_message_limit(self, user_id):
        """获取特定用户的消息缓存限制"""
        private_config = self.get_private_chat_setting(user_id)
        return private_config.get("message_cache_limit", 20)  # 默认缓存20条

    def get_cache_settings(self, key, default=None):
        """从配置文件中获取缓存相关的全局设置"""
        return self.config.get("cache_settings", {}).get(key, default)