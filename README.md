# Bot-All-In-One

**更新日期：2024.9.21**

## 项目概述

为了解决现有机器人功能臃肿和配置繁琐的问题，开发了一个多平台接入的机器人控制器，未来将集成更高级的拟真机器人功能。

## 功能特性

- **接入QQ**：实现QQ基本功能接入。
- **接入Dify**：异步处理发送到Dify的请求，支持单会话和多会话模式，工作流可在Dify中配置。
- **插件系统**：支持自定义插件代理处理QQ消息，扩展功能。

## 安装

### 环境要求

- Python 3.0+
- WebSockets
- Requests

### 安装步骤

1. **克隆仓库：**
   ```bash
   git clone https://github.com/xiaochangsama/Bot-All-In-One
   cd Bot-All-In-One
   ```

2. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置机器人：**
   - 首次运行将自动生成模板配置文件。示例配置：
   ```json
   {
     "api_key": "your_dify_api_key",
     "dify_url": "http://localhost/v1/chat-messages",
     "response_mode": "blocking",
     "user_id": "test",
     "conversation_mode": "single",
     "enabled_plugins": [],
     "chat_setting": {
       "default": {
         "enabled": false
       },
       "group_chat": {
         "834013534": {
           "enabled": true
         }
       },
       "private_chat": {
         "1354281282": {
           "enabled": true
         }
       }
     }
   }
   ```

4. **运行机器人：**
   ```bash
   python main.py
   ```

## 使用说明

### 接入QQ

使用Lagrange进行配置，默认设置即可。详细文档见：[Lagrange Documentation](https://lagrangedev.github.io/Lagrange.Doc/Lagrange.OneBot/)

### Dify 集成

需要Dify的URL或本地部署，详细信息见：[Dify GitHub](https://github.com/langgenius/dify)

- **API 密钥**：在配置文件的`"api_key"`项下设置。
- **单会话模式 vs 多会话模式**：
  - **单会话模式**：为每个用户或群组保存会话状态。
  - **多会话模式**：每次交互启动新对话。

### 插件系统

#### 插件结构

每个插件应放置在`plugins/`目录下，包含`plugin.py`文件，需实现`handle_message()`函数，返回四种操作之一：

- **回复**：直接回复用户/群聊。
- **取消**：取消消息回复。
- **继续**：将消息传递给下一个插件或Dify。
- **跳出**：跳过插件处理，由主程序处理消息。

#### 插件目录示例

```bash
plugins/
  MyPlugin/
    plugin.py
```

#### 插件`plugin.py`示例

```python
def handle_message(message):
    if "你好" in message:
        return {"type": "reply", "message": "你好！有什么我可以帮忙的吗？"}
    return {"type": "跳出"}
```

## 配置文件说明

- **`api_key`**：Dify API密钥（必填，字符串）。
- **`dify_url`**：Dify API URL（字符串）。
- **`response_mode`**：响应模式（可选：`blocking`、`streaming`）。
- **`enabled_plugins`**：启用插件列表（数组）。
- **`chat_setting`**：消息处理设置，包括：
  - **`default`**：默认自动回复设置。
  - **`group_chat`**：启用的群聊列表。
  - **`private_chat`**：启用的私聊用户列表。

## 常见问题

目前没有。

## 项目展望

目前项目结构相对混乱，虽然已实现基本功能，但在可扩展性方面存在不足。为了解决这一问题，我们正在积极尝试采用新的架构设计，以提高系统的清晰度和可维护性。

### 未来发展方向：

1. **架构优化**：
   - 采用模块化设计，以提升代码的可读性和可维护性。
   - 实现灵活的功能扩展机制，以便在未来快速集成新功能。

2. **多平台接入**：
   - 计划未来接入多个聊天平台，包括QQ和微信，提供统一的机器人管理接口。
   - 设计多种工作流触发方式，以满足不同场景下的需求，提升用户交互体验。

3. **可配置控制界面**：
   - 通过简单的浏览器控制台页面，提供高度可配置的设计，使用户能够灵活调整机器人设置，满足个性化需求。

4. **大模型适配**：
   - 除了现有的Dify集成，未来还将提供其他可配置的大模型，以简化部署过程，减少系统资源占用，提升整体性能。

通过以上优化与拓展，我们致力于打造一个更加灵活、高效的机器人控制平台，以满足日益增长的用户需求和技术挑战。

## 许可证

本项目基于MIT许可证发布，详细信息见[LICENSE](./LICENSE)文件。
