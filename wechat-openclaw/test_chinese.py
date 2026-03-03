#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test if pyautogui can type Chinese
"""

import time
import pyautogui

print("=== pyautogui 中文输入测试 ===\n")

print("步骤：")
print("1. 打开记事本或微信输入框")
print("2. 确保光标在输入框里")
print("3. 15秒后会自动输入中文\n")

print("15秒准备时间...")
time.sleep(15)

print("\n正在输入英文: hello123 ...")
pyautogui.write('hello123', interval=0.1)
time.sleep(1)

print("\n正在输入中文: 你好世界 ...")
pyautogui.write('你好世界', interval=0.2)
time.sleep(1)

print("\n正在输入中文: 测试消息 ...")
pyautogui.write('测试消息', interval=0.2)

print("\n✓ 测试完成！")
print("\n检查结果：")
print("- 英文 'hello123' 出现了吗？")
print("- 中文 '你好世界' 出现了吗？")
print("- 中文 '测试消息' 出现了吗？")
