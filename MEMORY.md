# MEMORY.md - 长期记忆

## 2026-02-27 重要记录

### 🌐 Browser-Use 浏览器自动化配置

**用途**: 负责搜索、浏览网页、执行浏览器自动化任务

**配置位置**: `F:\OpenClawProjects\browser-use\`

**关键配置**:
```python
# ⭐ 必须设置代理绕过规则（Windows）
os.environ['no_proxy'] = '127.0.0.1,localhost,::1'
os.environ['NO_PROXY'] = '127.0.0.1,localhost,::1'

# API 配置
os.environ['OPENAI_API_KEY'] = 'sk-c140291135b749cb89573b706e2a91cf'

# 初始化
from browser_use import Agent, Browser, ChatOpenAI

browser = Browser(headless=True)
llm = ChatOpenAI(
    model='qwen3.5-plus',
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
)

agent = Agent(
    task='任务描述',
    llm=llm,
    browser=browser,
    use_vision=False,
    generate_gif=False,
)
await agent.run()
```

**测试脚本**:
- `test_fixed.py` - 基础测试（已验证通过）
- `test_ai_agent_search.py` - B 站搜索测试（已验证通过）

**成功案例**:
- ✅ B 站搜索 "openclaw" - 找到 99+ 相关视频
- ✅ B 站搜索 "AI Agent" - 按最新发布排序并总结

**注意事项**:
1. Windows 系统必须设置 `NO_PROXY` 环境变量
2. 如果仍有 CDP 连接问题，检查系统代理设置
3. 使用 `headless=True` 提高速度

---

## 🏢 多 Agent 协作"AI 公司"想法 (2026-02-27)

### 用户需求
- **目标**: 组建全能型多 Agent 协作团队
- **工作模式**: 用户把控大方向，Agent 团队负责完善和执行
- **场景**: 复杂任务自动拆解、分工协作、结果汇总

### 调研的框架
| 框架 | 链接 | 特点 |
|------|------|------|
| ChatDev 2.0 | https://github.com/OpenBMB/ChatDev | 零代码配置，虚拟公司模式（CEO/CTO/程序员） |
| MassGen | https://github.com/massgen/MassGen | 迭代优化 + 投票共识机制 |
| Microsoft Agent Framework | https://github.com/microsoft/agent-framework | 微软官方，图编排，稳定可靠 |
| CrewAI | https://github.com/crewAIInc/crewAI | 角色扮演，任务导向 |
| MetaGPT | https://github.com/geekan/MetaGPT | 需求转代码，软件工程流程 |

### OpenClaw 现状分析
**已有能力**:
- ✅ 多 Agent 协作 (`sessions_spawn`)
- ✅ 任务分工和结果汇总
- ✅ 工具调用（浏览器、搜索、文件、命令）

**缺少**:
- ❌ 角色配置模板
- ❌ 可视化编排界面
- ❌ 预定义工作流
- ❌ 零代码配置

### 下一步
- 用户正在考虑方向
- 可能方案：OpenClaw 自建 / 安装 ChatDev 2.0 / 混合模式
- 等待用户进一步指示
4. 禁用 `use_vision` 和 `generate_gif` 减少错误

**官方 Issue 参考**: https://github.com/browser-use/browser-use/issues/2819

---

## 项目位置

- **Nebula Chat**: `F:\OpenClawProjects\nebula-chat\` (P2P 聊天项目，85% 完成)
- **Browser-Use**: `F:\OpenClawProjects\browser-use\` (浏览器自动化，已配置完成)

---

## 🛠️ 工程最佳实践

### 不要重复造轮子

**核心原则**: 我们想做的东西，别人可能已经有半成品或可用的模块

**优先级**:
1. 找现有库/框架 (2 小时调研)
2. 评估质量和适用性 (30 分钟)
3. 集成使用 (2-4 小时)
4. 只有自己实现更好时才自己写

**案例**:
- Browser automation → browser-use (2 小时 vs 自己写 7 天)
- P2P 通信 → libp2p (3 天 vs 自己写 3 周+)

**找轮子的地方**:
- GitHub (搜索 stars>1000 的项目)
- PyPI / npm / Maven (官方包仓库)
- Awesome 列表 (精选库集合)
- 官方文档推荐

**评估标准**:
- ⭐ Stars >1000
- 📦 下载量 >10k/月
- 🔄 最近更新 (<3 个月)
- 📖 文档完善
- ✅ 测试覆盖 >80%
