import configparser
import os

class ConfigManager:
    """管理配置文件的类"""

    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
        else:
            raise FileNotFoundError(f"配置文件 {self.config_file} 不存在")
        return config

    def get_default(self, key, default=None):
        """从配置文件中获取默认配置"""
        return self.config['DEFAULT'].get(key, default)

    def validate_config(self):
        """验证配置文件是否包含所有必需字段"""
        required_fields = ['api_key', 'dify_url', 'response_mode', 'user_id']
        missing_fields = [field for field in required_fields if field not in self.config['DEFAULT']]
        if missing_fields:
            raise ValueError(f"配置文件中缺少必要字段: {', '.join(missing_fields)}")

# 测试 ConfigManager
if __name__ == "__main__":
    config_manager = ConfigManager()
    print(config_manager.get_default('api_key'))  # 打印 api_key
    config_manager.validate_config()  # 验证配置文件
