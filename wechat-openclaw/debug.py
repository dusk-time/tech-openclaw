#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to see what's happening with clicking
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
    """Get WeChat window"""
    windows = gw.getWindowsWithTitle("微信")
    if not windows:
        print("✗ 没找到微信窗口")
        return None
    
    win = windows[0]
    win.activate()
    time.sleep(0.5)
    
    left, top, right, bottom = win.left, win.top, win.right, win.bottom
    width = right - left
    height = bottom - top
    
    return {
        "left": left,
        "top": top,
        "right": right,
        "bottom": bottom,
        "width": width,
        "height": height
    }


def load_positions():
    """Load positions from config"""
    config_file = os.path.join(os.path.dirname(__file__), "positions.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return None


def test_click(x, y, label, delay=0.5):
    """Test a click at position"""
    print(f"\n[Step] {label}")
    print(f"  位置: ({x}, {y})")
    
    # Move mouse there
    pyautogui.moveTo(x, y, duration=0.2)
    time.sleep(0.2)
    
    # Click
    pyautogui.click(x, y)
    print(f"  ✓ 已点击")
    
    time.sleep(delay)
    
    # Check if this area is clickable
    try:
        # Get color at position to verify click worked
        screenshot = pyautogui.screenshot(region=(x-5, y-5, 10, 10))
        screenshot.save(f"click_{label}.png")
        print(f"  ✓ 已保存点击截图: click_{label}.png")
    except:
        pass


def interactive_test():
    """Interactive test - let user control each step"""
    print("=== 手动调试模式 ===\n")
    
    # Load config or use manual positions
    pos = load_positions()
    
    if not pos:
        print("✗ 没找到 positions.json")
        print("请先运行 auto_calibrate.py 校准")
        return
    
    print("配置:")
    print(json.dumps(pos, indent=2))
    
    # Get window
    win = get_window()
    if not win:
        return
    
    left, top, right, bottom = win['left'], win['top'], win['right'], win['bottom']
    width, height = win['width'], win['height']
    
    # Calculate absolute positions
    input_x = int(left + width * pos['input_box']['x_pct'] / 100)
    input_y = int(top + height * pos['input_box']['y_pct'] / 100)
    send_x = int(left + width * pos['send_btn']['x_pct'] / 100)
    send_y = int(top + height * pos['send_btn']['y_pct'] / 100)
    
    print(f"\n计算出的位置:")
    print(f"  输入框: ({input_x}, {input_y})")
    print(f"  发送按钮: ({send_x}, {send_y})")
    
    print("\n" + "="*50)
    print("现在请看着微信窗口，我会依次点击")
    print("="*50)
    
    input("\n准备好了吗？按 Enter 开始...")
    
    # Step 1: Click input box
    test_click(input_x, input_y, "输入框", delay=1)
    
    # Step 2: Type test
    print("\n[Step] 输入文字测试")
    print("  即将输入: 'test123'")
    pyautogui.write('test123')
    print("  ✓ 已输入")
    
    time.sleep(1)
    
    # Step 3: Click send
    test_click(send_x, send_y, "发送按钮", delay=1)
    
    # Check result
    print("\n" + "="*50)
    print("请检查微信窗口：")
    print("1. 是否点击到了正确的位置？")
    print("2. 是否输入了文字？")
    print("3. 是否发送成功？")
    print("="*50)


def fix_positions():
    """Interactive position fixer"""
    print("\n=== 位置修复 ===\n")
    
    win = get_window()
    if not win:
        return
    
    print("请依次点击正确的位置：")
    print("1. 点击【输入框】")
    print("2. 点击【发送按钮】")
    print("\n我会实时显示坐标...\n")
    
    input("准备好了吗？按 Enter 开始...")
    
    clicks = []
    
    def on_click(x, y, button, pressed):
        if pressed:
            clicks.append((x, y))
            print(f"  记录: ({x}, {y})")
            if len(clicks) >= 2:
                return False
    
    from pynput import mouse
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()
    
    if len(clicks) >= 2:
        # Calculate and save
        input_x, input_y = clicks[0]
        send_x, send_y = clicks[1]
        
        # Percentages
        left, top = win['left'], win['top']
        width, height = win['width'], win['height']
        
        input_pct_x = round((input_x - left) / width * 100, 1)
        input_pct_y = round((input_y - top) / height * 100, 1)
        send_pct_x = round((send_x - left) / width * 100, 1)
        send_pct_y = round((send_y - top) / height * 100, 1)
        
        pos = {
            "input_box": {"x_pct": input_pct_x, "y_pct": input_pct_y},
            "send_btn": {"x_pct": send_pct_x, "y_pct": send_pct_y}
        }
        
        config_file = os.path.join(os.path.dirname(__file__), "positions.json")
        with open(config_file, 'w') as f:
            json.dump(pos, f, indent=2)
        
        print(f"\n✓ 已保存:")
        print(f"  输入框: ({input_pct_x}%, {input_pct_y}%)")
        print(f"  发送按钮: ({send_pct_x}%, {send_pct_y}%)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat Debug Tool")
    parser.add_argument("--test", action="store_true", help="Test with current positions")
    parser.add_argument("--fix", action="store_true", help="Fix positions manually")
    
    args = parser.parse_args()
    
    if args.test:
        interactive_test()
    elif args.fix:
        fix_positions()
    else:
        print("Usage:")
        print("  python debug.py --test    # Test current positions")
        print("  python debug.py --fix     # Manually fix positions")


if __name__ == "__main__":
    main()
