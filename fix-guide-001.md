# 🛠️ 修复方案 #001 - 命令行与 Memory 系统

> 针对诊断结果中的问题

---

## 📋 问题确认

| 问题 | 严重程度 | 影响 |
|------|---------|------|
| `openclaw status` 返回 code 1 | 🔴 高 | 无法诊断系统状态 |
| Memory 插件状态未知 | 🟡 中 | 可能无法记住对话 |
| 缺少 embedding provider | 🟡 中 | 无法语义搜索记忆 |

---

## 🔧 修复步骤

### Step 1: 修复命令行工具

**症状**: `openclaw status` 返回 code 1 无输出

**可能原因**:
1. Gateway 未运行
2. 配置损坏
3. 环境变量问题

**修复命令** (Windows PowerShell):
```powershell
# 1. 检查环境变量
$env:PATH

# 2. 手动启动 Gateway
openclaw gateway start

# 3. 等待 5 秒后重试
Start-Sleep 5
openclaw status

# 4. 如果还失败，查看日志
openclaw logs --follow
```

**如果 Gateway 启动失败**:
```powershell
# 检查端口占用
netstat -ano | findstr 18789

# 重置 Gateway
openclaw gateway stop
openclaw gateway start --force
```

---

### Step 2: 验证 Memory 插件

**测试命令**:
```powershell
# 检查 memory 命令是否存在
openclaw memory --help

# 检查 memory 状态
openclaw memory status

# 测试写入记忆
echo "测试记忆" > memory/2026-03-03-test.md

# 测试搜索（会报错，但能看到错误信息）
openclaw memory search "测试"
```

**预期结果**:
- ✅ `memory --help` 显示帮助 → 插件已加载
- ❌ `memory status` 报错关于 API key → 需要配置 embedding

---

### Step 3: 配置 Embedding（关键！）

**方案 A: 使用 DashScope（你已配置 Qwen，同一家）**

```powershell
# 检查 DashScope key 是否可用
$env:DASHSCOPE_API_KEY

# 在 models.json 中添加 embedding 配置
```

**编辑文件**: `%USERPROFILE%\.openclaw\agents\main\agent\models.json`

**添加内容**:
```json
{
  "mode": "merge",
  "providers": {
    "bailian": {
      "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
      "apiKey": "sk-你的key",
      "models": [
        {
          "id": "text-embedding-v3",
          "name": "Embedding V3",
          "kind": "embedding"
        }
      ]
    }
  }
}
```

**方案 B: 使用 OpenAI（更稳定）**

如果你有 OpenAI API key:
```json
{
  "providers": {
    "openai": {
      "baseUrl": "https://api.openai.com/v1",
      "apiKey": "sk-xxx",
      "models": [
        {
          "id": "text-embedding-3-small",
          "name": "Embedding 3 Small",
          "kind": "embedding"
        }
      ]
    }
  }
}
```

---

## ✅ 验证清单

修复后执行：
```powershell
# 1. Gateway 运行
openclaw status

# 2. Memory 可用
openclaw memory status

# 3. 搜索功能
openclaw memory search "关键词"

# 4. 重启生效
openclaw gateway restart
```

---

## 🎯 优先级

1. **最高**: 修复 `openclaw status`（影响所有诊断）
2. **高**: 配置 embedding（让记忆可用）
3. **中**: 测试 memory 功能

---

## 📝 反馈格式

执行后更新 `feedback.md`:
```markdown
## 修复 #001 反馈

### 执行结果
- [ ] openclaw status: 正常 / 仍报错
- [ ] memory status: 正常 / 仍报错
- [ ] embedding 配置: 已配置 / 跳过

### 遇到的问题
（如有报错，贴完整错误信息）

### 下一步
（需要进一步帮助吗？）
```

---

*Kimi Claw*  
*2026-03-03 21:35*
