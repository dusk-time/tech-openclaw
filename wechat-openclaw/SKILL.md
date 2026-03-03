---
name: wechat
description: Send and receive WeChat messages via the OpenClaw WeChat channel (Windows PC automation via wxauto). Use the `message` tool with `channel: "wechat"` to communicate with WeChat contacts and groups.
metadata: { "openclaw": { "emoji": "💬", "requires": { "config": ["channels.wechat"] } } }
---

# WeChat Channel Actions

## Overview

WeChat channel enables OpenClaw to automate a personal WeChat account on Windows PC using wxauto. Use the `message` tool with `channel: "wechat"` to send messages, manage conversations, and interact with contacts and groups.

## Important Prerequisites

- **Platform**: Windows PC with WeChat installed and logged in
- **Requirements**: WeChat window must be open (minimized is OK)
- **Note**: This is unofficial automation - use at your own risk

## Inputs to collect

- `target`: Contact name, group name, or "文件传输助手" (File Transfer Assistant)
- `message`: Text content for send/edit operations
- For media: local file `path` for attachments

## Actions

### Send a message

```json
{
  "action": "send",
  "channel": "wechat",
  "to": "张三",
  "message": "你好！最近怎么样？"
}
```

### Send to group

```json
{
  "action": "send",
  "channel": "wechat",
  "to": "Family Group",
  "message": "周末有空吗？"
}
```

### Send image

```json
{
  "action": "send",
  "channel": "wechat",
  "to": "张三",
  "path": "C:/Users/username/Pictures/photo.jpg"
}
```

### Send file attachment

```json
{
  "action": "send",
  "channel": "wechat",
  "to": "张三",
  "path": "C:/Users/username/Documents/report.pdf"
}
```

### Broadcast to multiple recipients

```json
{
  "action": "send",
  "channel": "wechat",
  "to": ["张三", "李四", "王五"],
  "message": "会议改到下午3点"
}
```

### Send voice note

```json
{
  "action": "send",
  "channel": "wechat",
  "to": "张三",
  "path": "C:/Users/username/voice.amr"
}
```

### Simulate reaction (emoji)

WeChat PC doesn't support native reactions. Sending an emoji as a message is the closest equivalent:

```json
{
  "action": "send",
  "channel": "wechat",
  "to": "张三",
  "message": "👍"
}
```

## Group Chat Behavior

Groups require mention by default (`requireMention: true` in config). To trigger a response:

1. **@mention the bot** - e.g., "@小助手 在吗？"
2. **Trigger keywords** - if configured in group settings
3. **Open group policy** - set `groupPolicy: "open"` for auto-respond

### Group message example

```json
{
  "action": "send",
  "channel": "wechat",
  "to": "开发讨论群",
  "message": "@所有人 今天的会议几点开始？"
}
```

## Channel Configuration

The WeChat channel supports the following config in `openclaw.json`:

```json5
{
  "channels": {
    "wechat": {
      "enabled": true,
      "dmPolicy": "pairing",        // pairing | allowlist | open | disabled
      "allowFrom": ["张三", "李四"],
      "groupPolicy": "allowlist",   // open | allowlist | disabled
      "requireMention": true,
      "listenList": [
        "文件传输助手",
        "Family Group",
        "开发讨论群"
      ],
      "avatarDir": "avatars/wechat-bot",
      "memoryEnabled": true
    }
  }
}
```

## Special Contacts

- **文件传输助手** - File Transfer Assistant (often used for self-testing)
- **自己** - Your own account (for testing DM functionality)

## Notes

- WeChat must remain logged in and the window must be open
- Message rate limits apply (avoid sending too fast)
- Voice notes must be in AMB/AMR format or WeChat-compatible
- Media files are sent directly from the local path
- Group names must match exactly as they appear in WeChat

## Ideas to try

- Test with "文件传输助手" first to verify functionality
- Create a group for testing group features
- Set up different avatars for different chat contexts
- Enable memory to have contextual conversations

## Troubleshooting

- **No messages received**: Check if WeChat window is open and listenList is correct
- **Send failed**: Verify the contact/group exists and WeChat is responsive
- **Not triggering in groups**: Ensure you're @mentioning the bot or check group policy settings
