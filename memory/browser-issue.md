# 浏览器控制问题记录

**日期:** 2026-02-23

## 问题描述

OpenClaw 浏览器控制功能无法正常工作，无论是扩展模式还是独立浏览器模式都失败。

## 已尝试的解决方案

### 扩展模式 (chrome profile)
- ✅ 网关正常运行 (端口 18789)
- ✅ 扩展中继服务监听中 (端口 18792)
- ✅ Chrome 扩展已安装并启用
- ✅ 扩展徽章显示 ON
- ❌ 浏览器工具调用超时 (15000ms)
- ❌ 错误：`Chrome extension relay for profile "chrome" is not reachable`

### 独立浏览器模式 (openclaw profile)
- ✅ 配置已添加 (端口 18800)
- ❌ Chrome CDP 启动失败
- ❌ 错误：`Failed to start Chrome CDP on port 18800`

## 当前配置

```json
{
  "browser": {
    "enabled": true,
    "defaultProfile": "openclaw",
    "executablePath": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "profiles": {
      "openclaw": { "cdpPort": 18800, "color": "#FF4500" },
      "chrome": { "cdpUrl": "http://127.0.0.1:18792", "driver": "extension", "color": "#00AA00" }
    }
  },
  "gateway": {
    "port": 18789,
    "auth": { "mode": "token", "token": "4eb78b2aeddf52cc46f6f256b3d0cf2768ccb4e5a826e569" }
  }
}
```

## 待排查事项

1. **扩展 Token 配置** — 需要在 Chrome 扩展选项中设置 Gateway token
2. **Chrome 进程冲突** — 可能有多个 Chrome 实例占用端口
3. **扩展中继服务** — 检查是否正确启动
4. **独立浏览器用户数据目录** — 可能需要指定独立的 userDataDir

## 临时方案

使用 `Start-Process` 命令手动打开网页：
```powershell
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -ArgumentList "https://www.bilibili.com"
```

## 下一步

- [ ] 在 Chrome 扩展选项中配置 Gateway token
- [ ] 彻底关闭所有 Chrome 进程后重试
- [ ] 检查扩展中继服务日志
- [ ] 尝试指定独立 userDataDir 启动 openclaw 浏览器
