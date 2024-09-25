# common/log.py

import logging
import os
from datetime import datetime

'''
使用方式
from common.log import get_logger

logger = get_logger()

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.error("This is an error message")
'''
# 创建log文件夹路径
log_folder = os.path.join(os.getcwd(), 'run', 'log')
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# 创建日志文件名，使用当前时间戳
log_file_name = datetime.now().strftime("debug_%Y-%m-%d_%H-%M-%S.log")
log_file = os.path.join(log_folder, log_file_name)

# 创建Logger对象
logger = logging.getLogger('BotLogger')
logger.setLevel(logging.DEBUG)  # 设置最低日志级别为DEBUG

# 创建FileHandler，用于记录DEBUG级别的日志到文件
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# 创建StreamHandler，用于INFO级别的日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加处理器到Logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_logger():
    return logger
