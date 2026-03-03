# OpenClaw EvoMap Integration Scripts

跨会话记忆和 HTTP 重试机制集成脚本

## 📦 已集成的 EvoMap 胶囊

### 1. 跨会话记忆连续性
- **Capsule ID**: `sha256:def136049c982ed785117dff00bb3238ed71d11cf77c019b3db2a8f65b476f06`
- **GDI Score**: 69.15
- **效果**: 消除跨会话失忆，自动加载/保存记忆

### 2. HTTP 重试机制
- **Capsule ID**: `sha256:6c8b2bef4652d5113cc802b6995a8e9f5da8b5b1ffe3d6bc639e2ca8ce27edec`
- **GDI Score**: 70.9
- **效果**: API 调用成功率提升 ~30%

---

## 🚀 使用方法

### 方法 1: 在会话开始时加载记忆

```bash
# PowerShell
node ~/.openclaw/workspace/scripts/load-memory.js

# 或在 Node.js 中
const { loadAllMemory } = require('./scripts/load-memory');
const memory = loadAllMemory({ isMainSession: true });
```

### 方法 2: 在会话结束时保存事件

```javascript
const { saveSessionExitEvent } = require('./scripts/save-exit');

// 保存重要事件
saveSessionExitEvent('Completed Task', 'Finished Nebula Chat MVP');
```

### 方法 3: 使用 HTTP 重试包装器

```javascript
const { fetchWithRetry, webSearchWithRetry } = require('./scripts/http-retry');

// 普通 fetch 带重试
const response = await fetchWithRetry('https://api.example.com/data');

// web_search 带重试
const searchResults = await webSearchWithRetry('your query');
```

---

## 📁 文件结构

```
scripts/
├── load-memory.js      # 记忆加载器
├── http-retry.js       # HTTP 重试包装器
├── save-exit.js        # 退出钩子
└── README.md           # 本文档
```

---

## 🔧 配置选项

### load-memory.js 选项

```javascript
loadAllMemory({
  isMainSession: true,    // 是否为主会话（加载 MEMORY.md）
  includeRecent: true,    // 加载 RECENT_EVENTS.md (24h)
  includeDaily: true,     // 加载 memory/YYYY-MM-DD.md
  includeLongTerm: true   // 加载 MEMORY.md
})
```

### http-retry.js 配置

```javascript
fetchWithRetry(url, options, {
  maxRetries: 5,          // 最大重试次数
  initialDelay: 1000,     // 初始延迟 (ms)
  maxDelay: 30000,        // 最大延迟 (ms)
  timeout: 60000,         // 请求超时 (ms)
  retryableStatusCodes: [408, 429, 500, 502, 503, 504],
  retryableErrors: ['ECONNRESET', 'ECONNREFUSED', 'ETIMEDOUT']
})
```

---

## 📊 记忆文件说明

### RECENT_EVENTS.md
- **位置**: `~/.openclaw/workspace/RECENT_EVENTS.md`
- **作用**: 24 小时滚动事件源
- **格式**: Markdown，按时间戳组织

### memory/YYYY-MM-DD.md
- **位置**: `~/.openclaw/workspace/memory/`
- **作用**: 每日原始日志
- **格式**: Markdown，自由格式

### MEMORY.md
- **位置**: `~/.openclaw/workspace/MEMORY.md`
- **作用**: 长期 curated 记忆
- **格式**: Markdown，结构化

---

## 🔍 故障排除

### 问题：记忆没有加载

**检查**:
1. 文件路径是否正确
2. 是否有读取权限
3. 文件是否存在

```bash
# 检查文件
ls ~/.openclaw/workspace/memory/
cat ~/.openclaw/workspace/RECENT_EVENTS.md
```

### 问题：HTTP 重试不工作

**检查**:
1. 错误是否在 retryableErrors 列表中
2. 状态码是否在 retryableStatusCodes 列表中
3. 查看控制台日志 `[HTTPRetry]` 前缀

---

## 📈 效果追踪

### 记忆连续性
- ✅ 会话重启后保留上下文
- ✅ 跨会话任务连续执行
- ✅ 减少重复信息输入

### HTTP 重试
- ✅ 网络故障自动恢复
- ✅ API 限流自动规避
- ✅ 成功率提升 ~30%

---

## 🎯 下一步

### 待集成胶囊
1. **AI 自省调试** (GDI: 70.2) - 自动错误修复
2. **智能错误恢复** (GDI: 66) - 断路器模式

### 改进方向
1. 自动检测主会话 vs 共享会话
2. 记忆压缩和归档
3. HTTP/2 支持
4. 分布式连接池

---

## 📚 参考

- EvoMap Protocol: https://evomap.ai/skill.md
- GEP-A2A Protocol: https://evomap.ai/wiki?doc=gep-a2a
- OpenClaw Docs: `C:\Users\28054\AppData\Roaming\npm\node_modules\openclaw\docs`
