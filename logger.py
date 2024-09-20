# logger.py

import logging
import os
from datetime import datetime

def setup_logger(name, level=logging.INFO):
    """设置并返回一个日志记录器"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建日志目录
    log_directory = os.path.join('run', 'log')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # 以当前日期时间命名日志文件
    log_filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log')
    log_file = os.path.join(log_directory, log_filename)

    # 文件处理器
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setFormatter(formatter)
    fh.setLevel(level)

    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(level)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # 避免重复添加处理器
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
