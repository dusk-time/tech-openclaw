import os
from browser_use import Agent
from browser_use.browser import BrowserConfig

# 设置硅基流动 API
os.environ["OPENAI_API_KEY"] = "sk-goqqjpnhjaccxkjrxbuibairtckvrnzlytcjzlctjcnbgjjr"
os.environ["OPENAI_BASE_URL"] = "https://api.siliconcloud.cn/v1"

# 使用 Agent（自动使用环境变量配置的 LLM）
agent = Agent(
    task="Open https://www.bilibili.com and tell me the page title",
)

# 运行
result = agent.run()
print(f"Result: {result}")
