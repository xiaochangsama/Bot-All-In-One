# config_manager.py

import configparser
import os
import shutil

class ConfigManager:
    """配置管理器，用于读取配置文件中的参数"""

    def __init__(self, config_file='config/config.ini'):
        self.config_file = config_file
        self.default_config_file = 'config/default/config.default.ini'

        if not os.path.exists(self.config_file):
            self.create_default_config()

        self.config = configparser.ConfigParser()
        self.config.read(self.config_file, encoding='utf-8')

    def create_default_config(self):
        """创建默认的配置文件"""
        if not os.path.exists(self.default_config_file):
            raise FileNotFoundError(f'参考配置文件不存在：{self.default_config_file}')

        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 复制参考配置文件到配置文件位置，保留注释
        shutil.copyfile(self.default_config_file, self.config_file)
        print(f'配置文件不存在，已创建默认配置文件：{self.config_file}')
        print('请修改配置文件中的参数，然后重新运行程序。')
        exit(0)

    def get(self, section, option, fallback=None):
        """获取指定 section 下的 option 值"""
        return self.config.get(section, option, fallback=fallback)

    def get_default(self, option, fallback=None):
        """获取 DEFAULT section 下的 option 值"""
        return self.get('DEFAULT', option, fallback)

# 测试 ConfigManager
if __name__ == "__main__":
    config_manager = ConfigManager()
    api_key = config_manager.get_default('api_key')
    print(f'API Key: {api_key}')
