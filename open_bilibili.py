from browser_use import Agent
from browser_use.browser import Browser, BrowserConfig

# 创建浏览器配置
config = BrowserConfig(
    headless=False,  # 使用有头模式可以看到浏览器
    chrome_instance_path=None,  # 使用内置 Chromium
)

# 创建浏览器实例
browser = Browser(config=config)

# 创建 Agent 并执行任务
agent = Agent(
    task="Open https://www.bilibili.com and wait for page to load",
    browser=browser,
)

# 运行
result = agent.run()
print(f"Result: {result}")

# 关闭浏览器
browser.close()
