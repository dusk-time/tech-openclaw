#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send WeChat message using clipboard for Chinese text
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pyautogui
    import pyperclip  # 剪贴板
    import pygetwindow as gw
except ImportError:
    print("pip install pyautogui pyperclip pygetwindow")
    sys.exit(1)


def send_message(chat_name, message):
    """Send message using clipboard for Chinese"""
    
    # Load positions
    config_file = os.path.join(os.path.dirname(__file__), "positions.json")
    if not os.path.exists(config_file):
        print("✗ 没找到 positions.json")
        return False
    
    with open(config_file, 'r') as f:
        pos = json.load(f)
    
    # Find window
    windows = gw.getWindowsWithTitle("微信")
    if not windows:
        print("✗ 没找到微信")
        return False
    
    win = windows[0]
    win.activate()
    time.sleep(0.5)
    
    left, top, right, bottom = win.left, win.top, win.right, win.bottom
    width = right - left
    height = bottom - top
    
    # Calculate positions
    input_x = int(left + width * pos['input_box']['x_pct'] / 100)
    input_y = int(top + height * pos['input_box']['y_pct'] / 100)
    send_x = int(left + width * pos['send_btn']['x_pct'] / 100)
    send_y = int(top + height * pos['send_btn']['y_pct'] / 100)
    
    try:
        # Step 1: Click input
        print("点击输入框...")
        pyautogui.click(input_x, input_y)
        time.sleep(0.3)
        
        # Step 2: Copy message to clipboard and paste
        print("粘贴文字...")
        pyperclip.copy(message)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        
        # Step 3: Click send
        print("点击发送...")
        pyautogui.click(send_x, send_y)
        time.sleep(0.3)
        
        print("✓ 发送完成！")
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python send.py <chat> <message>")
        print("Example: python send.py 文件传输助手 你好！")
        return
    
    chat = sys.argv[1]
    message = sys.argv[2]
    
    send_message(chat, message)


if __name__ == "__main__":
    main()
