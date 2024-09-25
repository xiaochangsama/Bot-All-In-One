# config.py
# 文件路径: /config/config.py
# 默认配置文件路径: /config/default/default_config.json
# 配置文件路径: /config/config.json

import os
import json
import shutil
from common.log import get_logger

logger = get_logger()

"""
使用方式:
1. 创建配置文件（如不存在）：create_config()
2. 加载配置：load_config()
3. 保存配置：save_config(config_data)

例：获取 Dify API 的 URL:
config = load_config()
dify_url = config["bot_dify"]["dify_url"]
print(f"Dify URL: {dify_url}")
"""

# 创建配置文件夹路径
config_folder = os.path.join(os.getcwd(), 'config')
default_config_folder = os.path.join(config_folder, 'default')
default_config_file = os.path.join(default_config_folder, 'default_config.json')
config_file = os.path.join(config_folder, 'config.json')


# 检查并创建config.json文件
def create_config():
    if not os.path.exists(config_file):
        if os.path.exists(default_config_file):
            # 复制default_config.json作为config.json
            shutil.copy(default_config_file, config_file)
            logger.info("已从 default_config.json 创建 config.json 文件。")
        else:
            logger.error("未找到 default_config.json 文件！")
    else:
        logger.info("config.json 文件已存在。")


# 加载配置文件内容
def load_config():
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        logger.debug("成功加载配置文件。")
        return config_data
    except Exception as e:
        logger.error(f"加载配置文件时出错：{e}")
        return None


# 保存配置文件内容
def save_config(config_data):
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        logger.info("配置文件已成功保存。")
    except Exception as e:
        logger.error(f"保存配置文件时出错：{e}")


# 使用示例
if __name__ == "__main__":
    # 创建config.json文件（如果尚不存在）
    create_config()

    # 加载配置
    config = load_config()
    if config:
        logger.info(f"当前配置: {config}")

    # 可以根据需要修改config
    # config['new_key'] = 'new_value'
    # save_config(config)
