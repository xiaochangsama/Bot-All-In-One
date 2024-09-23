import importlib
from src.config_manager import ConfigManager

class PluginManager:
    """插件管理器"""

    def __init__(self, plugin_dir='plugins', logger=None):
        self.plugin_dir = plugin_dir
        self.enabled_plugins = []
        self.loaded_plugins = {}
        self.logger = logger  # 注入 logger
        self.config_manager = ConfigManager()

    def load_plugins(self):
        """根据配置文件加载启用的插件"""
        # 通过 config_manager 获取启用的插件列表
        plugins = self.config_manager.get('enabled_plugins', [])
        self.enabled_plugins = [plugin.strip() for plugin in plugins if plugin.strip()]

        for plugin_name in self.enabled_plugins:
            try:
                plugin_module = self._load_plugin(plugin_name)
                if plugin_module:
                    self.loaded_plugins[plugin_name] = plugin_module
                    self.logger.info(f"插件 {plugin_name} 已加载")
            except Exception as e:
                self.logger.error(f"加载插件 {plugin_name} 时出错: {e}")

    def _load_plugin(self, plugin_name):
        """动态加载插件"""
        try:
            plugin_path = f"{self.plugin_dir}.{plugin_name}.plugin"
            plugin_module = importlib.import_module(plugin_path)
            return plugin_module
        except ModuleNotFoundError as e:
            self.logger.error(f"插件 {plugin_name} 不存在: {e}")
            return None

    def handle_message(self, msg_data):
        """将完整的原消息传递给插件处理"""
        for plugin_name, plugin_module in self.loaded_plugins.items():
            try:
                result = plugin_module.handle_message(msg_data)
                if result["type"] == "回复":
                    return {"handled": True, "reply": result["message"]}
                elif result["type"] == "取消":
                    return {"handled": True, "reply": None}
                elif result["type"] == "跳出":
                    return {"handled": False, "reply": None}
            except Exception as e:
                self.logger.error(f"插件 {plugin_name} 处理消息时出错: {e}")
        return {"handled": False, "reply": None}
