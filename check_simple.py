import inspect
import browser_use

# 打印模块位置
print(f"browser_use location: {inspect.getfile(browser_use)}")
print(f"\nAvailable in browser_use:")
print([x for x in dir(browser_use) if not x.startswith('_')])
