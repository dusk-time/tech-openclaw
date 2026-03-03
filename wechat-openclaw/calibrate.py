#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibration helper for WeChat positions
"""

import sys
import os
import time
import json
import pyautogui
import pygetwindow as gw

CONFIG_FILE = "positions.json"

def load_positions():
    """Load current positions"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "chat_list": {"x": 80, "y": 150},
        "input_box": {"x_pct": 50, "y_pct": 85},
        "send_btn": {"x_pct": 90, "y_pct": 90}
    }

def save_positions(pos):
    """Save positions"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(pos, f, indent=2)
    print(f"✓ Saved to {CONFIG_FILE}")

def get_window():
    """Get WeChat window"""
    windows = gw.getWindowsWithTitle("微信")
    if not windows:
        print("✗ WeChat window not found")
        return None
    
    win = windows[0]
    win.activate()
    time.sleep(0.5)
    
    left, top, right, bottom = win.left, win.top, win.right, win.bottom
    width = right - left
    height = bottom - top
    
    print(f"✓ Window: {width}x{height} at ({left}, {top})")
    return (left, top, right, bottom, width, height)

def print_current_positions(pos, rect):
    """Print current positions"""
    left, top, right, bottom, width, height = rect
    
    print("\n当前坐标配置：")
    print(f"  聊天列表: ({pos['chat_list']['x']}, {pos['chat_list']['y']})")
    
    input_x = int(left + width * pos['input_box']['x_pct'] / 100)
    input_y = int(top + height * pos['input_box']['y_pct'] / 100)
    print(f"  输入框: ({pos['input_box']['x_pct']}%, {pos['input_box']['y_pct']}%) = ({input_x}, {input_y})")
    
    send_x = int(left + width * pos['send_btn']['x_pct'] / 100)
    send_y = int(top + height * pos['send_btn']['y_pct'] / 100)
    print(f"  发送按钮: ({pos['send_btn']['x_pct']}%, {pos['send_btn']['y_pct']}%) = ({send_x}, {send_y})")

def test_click(x, y, label):
    """Test a click at position"""
    print(f"\n点击 {label}: ({x}, {y})")
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click(x, y)
    time.sleep(0.3)

def interactive_calibrate():
    """Interactive calibration"""
    print("=== 微信坐标校准工具 ===\n")
    
    # Load current positions
    pos = load_positions()
    
    # Get window
    rect = get_window()
    if not rect:
        return
    
    left, top, right, bottom, width, height = rect
    
    # Show current positions
    print_current_positions(pos, rect)
    
    print("\n" + "="*50)
    print("校准步骤：")
    print("1. 打开微信，确保能看到聊天列表和输入框")
    print("2. 我会依次点击几个位置")
    print("3. 你告诉我哪个是：")
    print("   - 输入框的位置")
    print("   - 发送按钮的位置")
    print("="*50)
    
    input("\n按 Enter 开始测试点击位置...")
    
    # Test chat list area (approximate)
    print("\n--- 测试聊天列表点击区域 ---")
    test_click(left + 80, top + 150, "聊天列表区域")
    
    # Calculate and test input box position
    input_x = int(left + width * pos['input_box']['x_pct'] / 100)
    input_y = int(top + height * pos['input_box']['y_pct'] / 100)
    print("\n--- 测试输入框位置 ---")
    test_click(input_x, input_y, "输入框")
    
    # Calculate and test send button position
    send_x = int(left + width * pos['send_btn']['x_pct'] / 100)
    send_y = int(top + height * pos['send_btn']['y_pct'] / 100)
    print("\n--- 测试发送按钮位置 ---")
    test_click(send_x, send_y, "发送按钮")
    
    print("\n" + "="*50)
    print("找到正确的位置了吗？")
    print("输入正确的坐标来更新配置：")
    print("="*50)
    
    try:
        # Get new input box position
        input("\n按 Enter，然后点击输入框位置...")
        x1, y1 = pyautogui.position()
        print(f"输入框: ({x1}, {y1})")
        
        input("\n按 Enter，然后点击发送按钮位置...")
        x2, y2 = pyautogui.position()
        print(f"发送按钮: ({x2}, {y2})")
        
        # Calculate percentages
        input_pct_x = round((x1 - left) / width * 100, 1)
        input_pct_y = round((y1 - top) / height * 100, 1)
        send_pct_x = round((x2 - left) / width * 100, 1)
        send_pct_y = round((y2 - top) / height * 100, 1)
        
        # Update positions
        pos['input_box'] = {"x_pct": input_pct_x, "y_pct": input_pct_y}
        pos['send_btn'] = {"x_pct": send_pct_x, "y_pct": send_pct_y}
        
        # Save
        save_positions(pos)
        
        print("\n✓ 新配置已保存！")
        print_current_positions(pos, rect)
        
        # Test with new positions
        print("\n--- 用新配置测试 ---")
        test_click(input_x, input_y, "输入框")
        test_click(send_x, send_y, "发送按钮")
        
        print("\n完成！请测试发送消息。")
        
    except KeyboardInterrupt:
        print("\n取消")

def simple_test():
    """Simple click test"""
    print("=== 位置测试 ===\n")
    
    rect = get_window()
    if not rect:
        return
    
    left, top, right, bottom, width, height = rect
    
    # Get user to click
    print("请依次点击以下位置（按 Enter 确认）：")
    
    input("\n1. 聊天列表中的任意一个聊天...")
    x1, y1 = pyautogui.position()
    print(f"   记录: ({x1}, {y1})")
    
    input("\n2. 输入框...")
    x2, y2 = pyautogui.position()
    print(f"   记录: ({x2}, {y2})")
    
    input("\n3. 发送按钮...")
    x3, y3 = pyautogui.position()
    print(f"   记录: ({x3}, {y3})")
    
    # Calculate relative positions
    pos = {
        "chat_list": {
            "x": x1 - left,
            "y": y1 - top
        },
        "input_box": {
            "x_pct": round((x2 - left) / width * 100, 1),
            "y_pct": round((y2 - top) / height * 100, 1)
        },
        "send_btn": {
            "x_pct": round((x3 - left) / width * 100, 1),
            "y_pct": round((y3 - top) / height * 100, 1)
        }
    }
    
    # Save
    save_positions(pos)
    
    print("\n✓ 位置已保存！")
    print(f"\n配置文件内容：")
    print(json.dumps(pos, indent=2))

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--simple':
        simple_test()
    else:
        interactive_calibrate()

if __name__ == "__main__":
    main()
