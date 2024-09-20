import importlib
import os
from config_manager import ConfigManager


class PluginManager:
    """插件管理器"""

    def __init__(self, plugin_dir='plugins'):
        self.plugin_dir = plugin_dir
        self.enabled_plugins = []
        self.loaded_plugins = {}

    def load_plugins(self):
        """根据配置文件加载启用的插件"""
        config_manager = ConfigManager()
        plugins = config_manager.get_default('enabled_plugins', '').split(',')
        self.enabled_plugins = [plugin.strip() for plugin in plugins if plugin.strip()]

        for plugin_name in self.enabled_plugins:
            try:
                plugin_module = self._load_plugin(plugin_name)
                if plugin_module:
                    self.loaded_plugins[plugin_name] = plugin_module
                    print(f"插件 {plugin_name} 已加载")
            except Exception as e:
                print(f"加载插件 {plugin_name} 时出错: {e}")

    def _load_plugin(self, plugin_name):
        """动态加载插件"""
        try:
            plugin_path = f"{self.plugin_dir}.{plugin_name}.plugin"
            plugin_module = importlib.import_module(plugin_path)
            return plugin_module
        except ModuleNotFoundError as e:
            print(f"插件 {plugin_name} 不存在: {e}")
            return None

    def handle_message(self, message):
        """将消息传递给插件处理"""
        for plugin_name, plugin_module in self.loaded_plugins.items():
            try:
                result = plugin_module.handle_message(message)
                if result["type"] == "回复":
                    return {"handled": True, "reply": result["message"]}
                elif result["type"] == "取消":
                    return {"handled": True, "reply": None}  # 取消回复
                elif result["type"] == "跳出":
                    return {"handled": False, "reply": None}  # 跳出，主程序继续处理
                # 如果是 "继续"，继续执行下一个插件
            except Exception as e:
                print(f"插件 {plugin_name} 处理消息时出错: {e}")
        return {"handled": False, "reply": None}  # 所有插件处理完后没有处理消息
