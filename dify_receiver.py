# dify_receiver.py

class DifyReceiver:
    """处理从Dify接收到的反馈信息"""

    def __init__(self, logger=None):
        self.logger = logger or setup_logger('DifyReceiver', 'dify_receiver.log')

    def process_response(self, response):
        """处理Dify的响应"""
        if response:
            self.logger.info('处理Dify的响应')
            answer = response.get('answer', '')
            # 可以在这里添加更多的处理逻辑
            self.logger.info(f'答案：{answer}')
            return answer
        else:
            self.logger.error('没有收到有效的响应')
            return None

# 测试DifyReceiver
if __name__ == "__main__":
    receiver = DifyReceiver()
    sample_response = {
        "answer": "iPhone 13 Pro Max specs are listed here:..."
    }
    receiver.process_response(sample_response)
