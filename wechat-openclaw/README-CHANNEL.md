# WeChat Channel 集成指南

## 架构

```
OpenClaw Agent → wechat_tool.js → HTTP API → wechat_server.py → pyautogui → 微信窗口
```

## 快速开始

### 1. 安装依赖

```bash
cd C:\Users\28054\.openclaw\workspace\wechat-openclaw

pip install pyautogui pygetwindow pillow opencv-python
```

### 2. 启动服务

```bash
python wechat_server.py
```

服务将在 `http://127.0.0.1:18788` 运行。

### 3. 测试发送

```bash
# 发送消息
node wechat_tool.js send "文件传输助手" "Hello from OpenClaw!"

# 查看状态
node wechat_tool.js status
```

## 在 OpenClaw Agent 中使用

### 方式 1: 使用 exec 调用

```typescript
// 发送微信消息
const result = await exec({
  command: "node",
  args: [
    "C:\\Users\\28054\\.openclaw\\workspace\\wechat-openclaw\\wechat_tool.js",
    "send",
    "文件传输助手",
    "Hello from OpenClaw!"
  ]
});
```

### 方式 2: 使用 HTTP API

```bash
# 发送消息
curl -X POST http://127.0.0.1:18788/send \
  -H "Content-Type: application/json" \
  -d '{"to": "文件传输助手", "message": "Hello!"}'
```

## 校准位置

如果发送位置不准确，需要校准：

### 自动校准

1. 启动服务：
```bash
python wechat_server.py
```

2. 在 OpenClaw 中校准：

```typescript
// 记录点击位置
await exec({
  command: "python",
  args: ["wechat_server.py", "--calibrate"],
  workdir: "C:\\Users\\28054\\.openclaw\\workspace\\wechat-openclaw"
});
```

### 手动校准

编辑 `positions.json` 文件：

```json
{
  "chat_list": {"x": 80, "y": 150},
  "input_box": {"x_pct": 50, "y_pct": 85},
  "send_btn": {"x_pct": 90, "y_pct": 90}
}
```

- `x`, `y`: 绝对坐标（像素）
- `x_pct`, `y_pct`: 窗口内百分比位置

## 配置 OpenClaw

在 `openclaw.json` 中添加：

```json5
{
  "channels": {
    "wechat": {
      "enabled": true,
      "serverUrl": "http://127.0.0.1:18788",
      "dmPolicy": "pairing",
      "groupPolicy": "allowlist",
      "requireMention": true
    }
  },
  "agents": {
    "list": [{
      "name": "wechat-assistant",
      "channel": "wechat",
      "description": "微信助手"
    }]
  }
}
```

## API 端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/status` | 获取服务状态 |
| GET | `/window` | 查找微信窗口 |
| POST | `/send` | 发送消息 |
| POST | `/calibrate/chat` | 校准聊天列表位置 |
| POST | `/calibrate/input` | 校准输入框位置 |
| POST | `/calibrate/send` | 校准发送按钮位置 |

## 故障排除

### 微信窗口找不到

1. 确保微信已打开并完全加载
2. 检查窗口标题是否为 "微信"
3. 尝试激活窗口：
```bash
python -c "
import pygetwindow as gw
wins = gw.getWindowsWithTitle('微信')
print(wins)
```

### 坐标不准确

1. 关闭微信服务
2. 调整 `positions.json` 中的坐标
3. 重新启动服务

### 发送失败

1. 检查微信窗口是否在最前台
2. 确保没有其他程序遮挡微信
3. 增加 `messageDelay` 配置

## 注意事项

⚠️ **重要**：
- 微信窗口必须保持打开（可以最小化）
- 发送消息时微信窗口需要在前台
- 避免同时操作微信
- 建议在消息之间添加延迟

## 文件结构

```
wechat-openclaw/
├── wechat_server.py      # HTTP 服务（Python）
├── wechat_tool.js        # Node.js 工具
├── channel.js            # Channel 实现
├── positions.json        # 校准位置（自动生成）
├── image_wechat.py       # 独立测试脚本
└── README-CHANNEL.md    # 本文档
```
