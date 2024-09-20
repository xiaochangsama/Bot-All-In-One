# data_manager.py

import os
import json

class DataManager:
    """管理用户数据的类"""

    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_conversation_id(self, user_id):
        """获取指定用户的会话 ID"""
        filepath = os.path.join(self.data_dir, f'{user_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            return data.get('conversation_id')
        return None

    def set_conversation_id(self, user_id, conversation_id):
        """保存用户的会话 ID"""
        filepath = os.path.join(self.data_dir, f'{user_id}.json')
        data = {'conversation_id': conversation_id}
        with open(filepath, 'w') as f:
            json.dump(data, f)

# 测试 DataManager
if __name__ == "__main__":
    dm = DataManager()
    dm.set_conversation_id('user123', 'conv-001')
    print(dm.get_conversation_id('user123'))  # 应该输出 'conv-001'

