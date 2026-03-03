#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试 wxautold 和 WeChat 初始化
"""

import sys
import time
import win32gui
import win32process

def get_wechat_info():
    """获取微信详细信息"""
    print("=== WeChat Info ===\n")
    
    # 方法1: FindWindow
    print("Method 1: FindWindow")
    class_names = [
        'WeChatMainWndForPC',
        'WeChat',
        None,  # Will try by title
    ]
    
    for class_name in class_names:
        try:
            if class_name:
                hwnd = win32gui.FindWindow(class_name, None)
            else:
                hwnd = win32gui.FindWindow(None, '微信')
            
            if hwnd:
                print(f"  ✓ FindWindow('{class_name or '微信'}') = {hwnd}")
                
                # Get window text
                title = win32gui.GetWindowText(hwnd)
                print(f"    Title: {title}")
                
                # Get class name
                cls = win32gui.GetClassName(hwnd)
                print(f"    Class: {cls}")
                
                # Get PID
                try:
                    pid = win32process.GetWindowThreadProcessId(hwnd)[0]
                    print(f"    PID: {pid}")
                except:
                    pass
            else:
                print(f"  ✗ FindWindow('{class_name or '微信'}') = None")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Method 2: EnumWindows
    print("\nMethod 2: EnumWindows")
    wechat_windows = []
    
    def enum_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if '微信' in title:
                windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    'class': win32gui.GetClassName(hwnd)
                })
        return True
    
    win32gui.EnumWindows(enum_callback, wechat_windows)
    
    if wechat_windows:
        print(f"  ✓ Found {len(wechat_windows)} window(s)")
        for win in wechat_windows:
            print(f"    HWND: {win['hwnd']}, Title: {win['title']}, Class: {win['class']}")
    else:
        print("  ✗ No WeChat windows found")
    
    return wechat_windows

def test_wxautold():
    """测试 wxautold"""
    print("\n=== Testing wxautold ===\n")
    
    try:
        from wxauto import WeChat
        print("Imported WeChat successfully")
        
        print("\nCreating WeChat instance...")
        wx = WeChat()
        print("WeChat instance created!")
        
        print("\nGetting session list...")
        sessions = wx.GetSessionList()
        print(f"Session list: {sessions}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("Detailed WeChat + wxautold Test")
    print("=" * 50)
    
    # Step 1: Get WeChat info
    wechat_windows = get_wechat_info()
    
    # Step 2: Test wxautold
    success = test_wxautold()
    
    print("\n" + "=" * 50)
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    print("=" * 50)

if __name__ == "__main__":
    main()
