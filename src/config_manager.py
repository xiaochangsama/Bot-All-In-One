import json
import os
import shutil

class ConfigManager:
    """通用配置管理类，使用 JSON 文件管理配置"""

    def __init__(self, config_file='config/config.json', default_file='config/default/default_config.json'):
        self.config_file = config_file
        self.default_file = default_file
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件，如果不存在则从默认配置文件复制"""
        if not os.path.exists(self.config_file):
            self.create_default_config()
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

    def get(self, key, default=None):
        """通用获取配置的函数"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is default:
                break
        return value

    def set(self, key, value):
        """通用设置配置的函数"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save_config()

    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as file:
            json.dump(self.config, file, ensure_ascii=False, indent=4)

    def validate_config(self):
        """验证配置文件是否包含所有必需字段"""
        required_fields = ['api_key', 'dify_url', 'response_mode', 'user_id']
        missing_fields = [field for field in required_fields if not self.get(field)]
        if missing_fields:
            raise ValueError(f"配置文件中缺少必要字段: {', '.join(missing_fields)}")

    def get_chat_setting(self, chat_type, chat_id):
        """获取群聊或私聊的配置，优先读取特定聊天配置"""
        chat_settings = self.get(f'chat_setting.{chat_type}_chat', {})
        return chat_settings.get(str(chat_id), self.get('chat_setting.default', {}))

    def get_cache_settings(self, key, default=None):
        """从缓存设置中获取配置"""
        return self.get(f'cache_settings.{key}', default)

    def get_db_idle_timeout(self):
        """获取数据库闲置超时时间"""
        return self.get('db_idle_timeout', 300)

    def get_onebot_config(self, key, default=None):
        """获取 OneBot 相关配置"""
        return self.get(f'onebot_config.{key}', default)
    def get_cache_message_limit(self, chat_type, chat_id, default_limit=50):
        """获取指定聊天的消息缓存限制，支持私聊和群聊"""
        chat_settings = self.get(f'chat_setting.{chat_type}_chat.{chat_id}', None)
        if chat_settings and 'message_cache_limit' in chat_settings:
            return chat_settings['message_cache_limit']
        return self.get('chat_setting.default.message_cache_limit', default_limit)