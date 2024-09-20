# data_manager.py

class DataManager:
    """管理数据的类"""

    def __init__(self):
        self.data = {}

    def get_data(self, key):
        """获取数据"""
        return self.data.get(key, None)

    def set_data(self, key, value):
        """设置数据"""
        self.data[key] = value

    def delete_data(self, key):
        """删除数据"""
        if key in self.data:
            del self.data[key]

# 测试DataManager
if __name__ == "__main__":
    dm = DataManager()
    dm.set_data('api_key', 'your_api_key_here')
    print(dm.get_data('api_key'))
    dm.delete_data('api_key')
    print(dm.get_data('api_key'))
