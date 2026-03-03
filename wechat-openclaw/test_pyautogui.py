#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test if pyautogui can type
"""

import time
import pyautogui

print("=== pyautogui 输入测试 ===\n")

print("步骤：")
print("1. 打开一个可以输入的地方（比如记事本、浏览器地址栏）")
print("2. 确保光标在输入框里闪烁")
print("3. 10秒后会自动输入 'hello123'\n")

print("10秒准备时间...")
time.sleep(10)

print("\n正在输入 'hello123' ...")
pyautogui.write('hello123', interval=0.1)

print("\n✓ 如果记事本里出现 'hello123'，说明 pyautogui 工作正常")
print("\n如果没有，请检查：")
print("- Python 是否有管理员权限？")
print("- 是否有其他程序拦截了键盘输入？")
