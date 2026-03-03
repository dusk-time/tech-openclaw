import os
from browser_use import Agent
from browser_use.browser import Browser, BrowserConfig
from langchain_openai import ChatOpenAI

# 配置硅基流动 API
os.environ["OPENAI_API_KEY"] = "sk-goqqjpnhjaccxkjrxbuibairtckvrnzlytcjzlctjcnbgjjr"
os.environ["OPENAI_BASE_URL"] = "https://api.siliconcloud.cn/v1"

# 创建模型（使用硅基流动支持的模型）
llm = ChatOpenAI(
    model="Qwen/Qwen2.5-72B-Instruct",  # 硅基流动的模型名称
    base_url="https://api.siliconcloud.cn/v1",
    api_key="sk-goqqjpnhjaccxkjrxbuibairtckvrnzlytcjzlctjcnbgjjr",
)

# 创建浏览器配置
config = BrowserConfig(
    headless=False,  # 显示浏览器窗口
)

# 创建浏览器
browser = Browser(config=config)

# 创建 Agent
agent = Agent(
    task="Open https://www.bilibili.com and tell me the page title",
    llm=llm,
    browser=browser,
)

# 运行
result = agent.run()
print(f"Result: {result}")

# 关闭浏览器
browser.close()
