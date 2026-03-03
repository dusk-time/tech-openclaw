import os
from browser_use import Agent

# 设置硅基流动 API
os.environ["OPENAI_API_KEY"] = "sk-goqqjpnhjaccxkjrxbuibairtckvrnzlytcjzlctjcnbgjjr"
os.environ["OPENAI_BASE_URL"] = "https://api.siliconcloud.cn/v1"

print("Starting browser automation...")

# 使用 Agent
agent = Agent(
    task="Open https://www.bilibili.com and tell me the page title",
)

# 运行
result = agent.run()
print(f"Result: {result}")
