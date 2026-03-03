#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to send WeChat message directly
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


def send_wechat_message(chat_name, message):
    """Send a WeChat message directly"""
    
    # Load positions
    config_file = os.path.join(os.path.dirname(__file__), "positions.json")
    if not os.path.exists(config_file):
        print(f"✗ 没找到 {config_file}")
        print("请先运行: python auto_calibrate.py")
        return False
    
    with open(config_file, 'r') as f:
        pos = json.load(f)
    
    # Find WeChat window
    windows = gw.getWindowsWithTitle("微信")
    if not windows:
        print("✗ 没找到微信窗口")
        return False
    
    win = windows[0]
    win.activate()
    time.sleep(0.5)
    
    left, top, right, bottom = win.left, win.top, win.right, win.bottom
    width = right - left
    height = bottom - top
    
    print(f"窗口: {width}x{height}")
    
    # Calculate positions
    input_x = int(left + width * pos['input_box']['x_pct'] / 100)
    input_y = int(top + height * pos['input_box']['y_pct'] / 100)
    send_x = int(left + width * pos['send_btn']['x_pct'] / 100)
    send_y = int(top + height * pos['send_btn']['y_pct'] / 100)
    
    print(f"输入框: ({input_x}, {input_y})")
    print(f"发送按钮: ({send_x}, {send_y})")
    
    try:
        # Step 1: Click input
        print("\n点击输入框...")
        pyautogui.click(input_x, input_y)
        time.sleep(0.5)
        
        # Step 2: Type message
        print(f"输入文字: {message}")
        pyautogui.write(message)
        time.sleep(0.3)
        
        # Step 3: Click send
        print("点击发送...")
        pyautogui.click(send_x, send_y)
        time.sleep(0.3)
        
        print("\n✓ 发送完成！")
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python simple_send.py <chat_name> <message>")
        print("Example: python simple_send.py 文件传输助手 Hello!")
        return
    
    chat_name = sys.argv[1]
    message = sys.argv[2]
    
    send_wechat_message(chat_name, message)


if __name__ == "__main__":
    main()
