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
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('conversation_id')
            except (json.JSONDecodeError, IOError) as e:
                print(f"读取会话 ID 时出错: {e}")
                return None
        return None

    def set_conversation_id(self, user_id, conversation_id):
        """保存用户的会话 ID"""
        filepath = os.path.join(self.data_dir, f'{user_id}.json')
        data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"读取用户数据时出错: {e}")

        # 更新 conversation_id，不影响其他字段
        data['conversation_id'] = conversation_id

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"保存会话 ID 时出错: {e}")

    def set_latest_message_id(self, user_id, message_id):
        """保存最新的消息 ID"""
        filepath = os.path.join(self.data_dir, f'{user_id}.json')
        data = {}
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"读取用户数据时出错: {e}")

        # 更新 latest_message_id，不影响其他字段
        data['latest_message_id'] = message_id

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"保存最新消息 ID 时出错: {e}")
