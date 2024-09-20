import configparser
import os
import shutil

class ConfigManager:
    """管理配置文件的类"""

    def __init__(self, config_file='config/config.ini', default_file='config/default/default_config.ini'):
        self.config_file = config_file
        self.default_file = default_file
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件，如果不存在则从默认配置文件复制"""
        if not os.path.exists(self.config_file):
            self.create_default_config()  # 如果 config.ini 不存在，从默认文件复制
        config = configparser.ConfigParser()
        # 使用 UTF-8 编码读取配置文件
        with open(self.config_file, 'r', encoding='utf-8') as file:
            config.read_file(file)
        return config

    def create_default_config(self):
        """从默认配置文件复制 config.ini"""
        if os.path.exists(self.default_file):
            # 确保 config 目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            shutil.copy(self.default_file, self.config_file)
            print(f"配置文件 {self.config_file} 不存在，已从默认配置 {self.default_file} 复制")
        else:
            raise FileNotFoundError(f"默认配置文件 {self.default_file} 不存在，无法创建 {self.config_file}")

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
    config_manager.validate_config()
    print(config_manager.get_default('api_key'))
