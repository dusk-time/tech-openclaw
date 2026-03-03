from browser_use import *
import inspect

# 打印 browser_use 模块的文件位置
print(f"browser_use module file: {inspect.getfile(browser_use)}")

# 尝试查看 browser 子模块
import browser_use.browser
print(f"\nbrowser_use.browser module contents:")
print(dir(browser_use.browser))
