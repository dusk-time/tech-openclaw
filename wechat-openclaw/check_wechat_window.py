#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check WeChat window info
"""

import win32gui
import win32process

def list_all_windows():
    """List all windows"""
    windows = []
    
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            if title and '微信' in title:
                pid = win32process.GetWindowThreadProcessId(hwnd)[0]
                windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    'class': class_name,
                    'pid': pid
                })
        return True
    
    win32gui.EnumWindows(enum_callback, windows)
    return windows

def main():
    print("=== WeChat Window Check ===\n")
    
    windows = list_all_windows()
    
    if not windows:
        print("No WeChat windows found!")
        print("Make sure WeChat is running and visible.")
        return
    
    print(f"Found {len(windows)} WeChat window(s):\n")
    
    for i, win in enumerate(windows, 1):
        print(f"[{i}] Window:")
        print(f"    Title: {win['title']}")
        print(f"    Class: {win['class']}")
        print(f"    HWND: {win['hwnd']}")
        print(f"    PID: {win['pid']}")
        print()
    
    # Test FindWindow with different class names
    print("Testing FindWindow...")
    
    test_classes = [
        'WeChatMainWndForPC',
        'WeChat',
        '微信',
        'ChatWnd',
    ]
    
    for class_name in test_classes:
        hwnd = win32gui.FindWindow(class_name, None)
        if hwnd:
            print(f"✓ FindWindow('{class_name}') = {hwnd}")
        else:
            print(f"✗ FindWindow('{class_name}') = None")

if __name__ == "__main__":
    main()
