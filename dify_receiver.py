# dify_receiver.py

from logger import setup_logger

class DifyReceiver:
    """处理从 Dify 接收到的反馈信息"""

    def __init__(self, logger=None):
        self.logger = logger or setup_logger('DifyReceiver')

    def process_response(self, response):
        """处理 Dify 的响应"""
        if response:
            self.logger.debug('处理 Dify 的响应')
            answer = response.get('answer')
            if answer:
                self.logger.info(f'答案：{answer}')
                return answer
            else:
                self.logger.error('响应中不包含答案')
                self.logger.debug(f'完整响应：{response}')
                return None
        else:
            self.logger.error('没有收到有效的响应')
            return None
