#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-detect click positions for calibration
No need to press Enter - just click!
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pyautogui
    import pygetwindow as gw
    from pynput import mouse
    SCREEN_AVAILABLE = True
except ImportError:
    SCREEN_AVAILABLE = False
    print("pip install pynput")

# Global variables
click_count = 0
positions = []


def on_click(x, y, button, pressed):
    """Detect mouse clicks"""
    global click_count, positions
    
    if pressed:  # Only on click down
        click_count += 1
        positions.append((x, y))
        print(f"✓ 记录点击 {click_count}: ({x}, {y})")
        
        if click_count == 1:
            print("  → 请点击发送按钮...")
        elif click_count == 2:
            print("\n  完成！正在保存...")
            return False  # Stop listening


def get_window_info():
    """Get WeChat window info"""
    windows = gw.getWindowsWithTitle("微信")
    if not windows:
        print("✗ 没找到微信窗口")
        return None
    
    win = windows[0]
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


def main():
    global click_count, positions
    
    print("=== 微信坐标自动校准 ===\n")
    
    # Check dependencies
    if not SCREEN_AVAILABLE:
        print("请安装: pip install pynput")
        return
    
    # Get window info
    info = get_window_info()
    if not info:
        return
    
    print(f"微信窗口: {info['width']}x{info['height']}")
    print(f"位置: ({info['left']}, {info['top']})\n")
    
    print("操作说明：")
    print("1. 在微信窗口中，点击【输入框】")
    print("2. 在微信窗口中，点击【发送按钮】")
    print("3. 自动保存，无需按回车\n")
    
    print("=" * 40)
    print("准备好了吗？3秒后开始检测点击...")
    print("=" * 40)
    time.sleep(3)
    
    print("\n请开始点击...\n")
    
    # Setup mouse listener
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    # Wait for 2 clicks
    listener.join()
    
    # Calculate percentages
    if len(positions) >= 2:
        input_x, input_y = positions[0]
        send_x, send_y = positions[1]
        
        # Calculate percentages relative to window
        input_pct_x = round((input_x - info['left']) / info['width'] * 100, 1)
        input_pct_y = round((input_y - info['top']) / info['height'] * 100, 1)
        send_pct_x = round((send_x - info['left']) / info['width'] * 100, 1)
        send_pct_y = round((send_y - info['top']) / info['height'] * 100, 1)
        
        config = {
            "input_box": {
                "x_pct": input_pct_x,
                "y_pct": input_pct_y
            },
            "send_btn": {
                "x_pct": send_pct_x,
                "y_pct": send_pct_y
            }
        }
        
        # Save
        config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "positions.json"
        )
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\n" + "=" * 40)
        print("✓ 校准完成！")
        print("=" * 40)
        print(f"\n输入框: ({input_pct_x}%, {input_pct_y}%)")
        print(f"发送按钮: ({send_pct_x}%, {send_pct_y}%)")
        print(f"\n已保存到: {config_file}")
        print("\n现在可以测试发送消息了！")
        
    else:
        print("\n✗ 点击次数不足，需要点击2次")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n取消")
