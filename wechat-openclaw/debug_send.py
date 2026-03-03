#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed debug script
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pyautogui
    import pygetwindow as gw
except ImportError:
    print("pip install pyautogui pygetwindow")
    sys.exit(1)


def get_window():
    windows = gw.getWindowsWithTitle("微信")
    if not windows:
        print("✗ 没找到微信")
        return None
    return windows[0]


def main():
    if len(sys.argv) < 3:
        print("Usage: python debug_send.py <chat> <message>")
        return
    
    chat = sys.argv[1]
    message = sys.argv[2]
    
    # Load config
    config_file = os.path.join(os.path.dirname(__file__), "positions.json")
    if not os.path.exists(config_file):
        print("✗ 没找到 positions.json")
        return
    
    with open(config_file, 'r') as f:
        pos = json.load(f)
    
    # Get window
    win = get_window()
    if not win:
        return
    
    # Activate window
    print("激活微信窗口...")
    win.activate()
    time.sleep(1)
    
    left, top, right, bottom = win.left, win.top, win.right, win.bottom
    width = right - left
    height = bottom - top
    
    print(f"窗口: {width}x{height} at ({left}, {top})")
    
    # Calculate
    input_x = int(left + width * pos['input_box']['x_pct'] / 100)
    input_y = int(top + height * pos['input_box']['y_pct'] / 100)
    send_x = int(left + width * pos['send_btn']['x_pct'] / 100)
    send_y = int(top + height * pos['send_btn']['y_pct'] / 100)
    
    print(f"输入框位置: ({input_x}, {input_y})")
    print(f"发送按钮位置: ({send_x}, {send_y})")
    
    input("\n\n按 Enter 开始测试（确保微信在最前台）...")
    
    # Step 1: Click input
    print("\n[1/3] 点击输入框...")
    pyautogui.moveTo(input_x, input_y, duration=0.3)
    time.sleep(0.2)
    pyautogui.click(input_x, input_y)
    time.sleep(0.5)
    
    # Check cursor
    cursor_x, cursor_y = pyautogui.position()
    print(f"   光标位置: ({cursor_x}, {cursor_y})")
    if abs(cursor_x - input_x) < 50 and abs(cursor_y - input_y) < 50:
        print("   ✓ 光标在输入框附近")
    else:
        print("   ✗ 光标不在输入框！")
    
    # Step 2: Type
    print(f"\n[2/3] 输入文字: {message}")
    pyautogui.write(message)
    time.sleep(0.3)
    
    # Step 3: Send
    print(f"\n[3/3] 点击发送按钮...")
    pyautogui.moveTo(send_x, send_y, duration=0.3)
    time.sleep(0.2)
    pyautogui.click(send_x, send_y)
    
    print("\n完成！检查微信是否收到消息")


if __name__ == "__main__":
    main()
