import os
import json

class DataManager:
    """管理用户数据的类"""

    def __init__(self, config_manager=None):
        # 从配置管理器中获取数据存储目录，如果没有提供则使用默认的 'data'
        self.data_dir = './data'
        self.config_manager = config_manager

        # 检查数据目录是否存在，如果不存在则创建
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

    def _get_cache_limit(self, user_id, is_group=False):
        """获取消息缓存限制，基于聊天类型"""
        chat_type = 'group' if is_group else 'private'
        return self.config_manager.get_cache_message_limit(chat_type, user_id)

    def _get_cache_threshold_percentage(self):
        """获取缓存阈值百分比"""
        return self.config_manager.get_cache_settings('cache_threshold_percentage', 50)

    def _load_user_data(self, user_id):
        """加载用户的 JSON 数据"""
        filepath = os.path.join(self.data_dir, f'{user_id}.json')
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"读取用户数据时出错: {e}")
        return {}

    def _save_user_data(self, user_id, data):
        """保存用户的 JSON 数据，确保使用 UTF-8 编码"""
        filepath = os.path.join(self.data_dir, f'{user_id}.json')
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)  # ensure_ascii=False 防止中文被转义
        except IOError as e:
            print(f"保存用户数据时出错: {e}")

    def set_latest_message_id(self, user_id, message_id, message_data, is_group=False):
        """保存最新的消息，并检查缓存是否需要清理"""
        data = self._load_user_data(user_id)

        # 获取或初始化消息缓存
        if 'messages' not in data:
            data['messages'] = []

        # 添加新的消息
        data['messages'].append({
            'message_id': message_id,
            'message_data': message_data
        })

        # 获取缓存限制和阈值
        cache_limit = self._get_cache_limit(user_id, is_group)
        threshold_percentage = self._get_cache_threshold_percentage() / 100
        max_cache_size = cache_limit * 2

        # 检查缓存是否超出阈值
        if len(data['messages']) > max_cache_size * threshold_percentage:
            # 超出阈值，删除最早的 cache_limit 条数据
            data['messages'] = data['messages'][cache_limit:]

        # 保存更新后的数据，确保UTF-8编码并避免中文转义
        self._save_user_data(user_id, data)
