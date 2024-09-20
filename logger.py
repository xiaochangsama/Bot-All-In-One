# logger.py

import logging

def setup_logger(name, log_file, level=logging.INFO):
    """设置并返回一个日志记录器"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 文件处理器
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)

    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

# 测试日志模块
if __name__ == "__main__":
    test_logger = setup_logger('test_logger', 'test.log')
    test_logger.info('这是一个信息日志')
    test_logger.error('这是一个错误日志')
