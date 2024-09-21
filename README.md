
# Bot-All-In-One

更新日期2024.9.21

## 项目概述

- 因为很多机器人比较臃肿，包含一些麻烦无用的功能或者配置麻烦，因此决定自己开发一个能够接入多个聊天平台的机器人控制器，未来会集成一些拟真机器人功能。

## 功能特性

- **接入QQ**：可以接入QQ实现基本的功能
- **接入Dify**：异步处理发送到 Dify 的请求，支持单会话和多会话模式，针对消息的工作流可以在dify中配置
- **插件系统**：可以自定义插件代理处理QQ消息实现更多功能

## 安装

### 环境要求

- Python 3.0+
- WebSockets
- Requests

### 安装步骤

1. **克隆仓库：**
   ```bash
   git clone https://github.com/xiaochangsama/Bot-All-In-One
   cd QQBotWithDify
   ```

2. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置机器人：**
   - 首次运行可以自动生成模板配置文件
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
使用Lagrange，默认配置即可
https://lagrangedev.github.io/Lagrange.Doc/Lagrange.OneBot/

### Dify 集成
需要由Dify的URL或者本地部署Dify
https://github.com/langgenius/dify

- **API 密钥**：在配置文件的 `"api_key"` 项下设置你的 Dify API 密钥。
- **单会话模式 vs 多会话模式**：
  - **单会话模式**：机器人为每个用户或群组保存会话状态，保持对话的上下文。
  - **多会话模式**：每次交互都会启动一个新对话。

### 插件系统

#### 插件结构

每个插件都放置在 `plugins/` 目录下。插件必须包含一个 `plugin.py` 文件，并实现 `handle_message()` 函数，该函数返回以下四种操作之一：

- **回复**：直接回复用户/群聊。
- **取消**：取消消息回复。
- **继续**：将消息传递给下一个插件或 Dify。
- **跳出**：跳过插件处理，由主程序处理消息。

#### 插件目录示例

```bash
plugins/
  MyPlugin/
    plugin.py
```

#### 插件 `plugin.py` 示例

```python
def handle_message(message):
    if "你好" in message:
        return {"type": "reply", "message": "你好！有什么我可以帮忙的吗？"}
    return {"type": "跳出"}
```

## 配置文件说明

### `api_key`：
- **类型**：字符串
- **描述**：Dify 平台的 API 密钥，必须设置。

### `dify_url`：
- **类型**：字符串
- **描述**：Dify API 的 URL。

### `response_mode`：
- **类型**：字符串
- **可选值**：`blocking`、`streaming`
- **描述**：设置 Dify API 的响应模式。

### `enabled_plugins`：
- **类型**：数组
- **描述**：启用的插件列表。

### `chat_setting`：
- **描述**：群聊和私聊消息处理的设置。
- **`default`**：设置是否默认启用自动回复。
- **`group_chat`**：指定启用的群聊列表。
- **`private_chat`**：指定启用的私聊用户列表。

## 常见问题

目前没有



## 许可证

本项目基于 MIT 许可证发布。请查看 [LICENSE](./LICENSE) 文件了解更多信息。

