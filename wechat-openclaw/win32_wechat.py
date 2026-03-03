#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pure Win32 WeChat Sender
Bypasses wxauto issues by using direct Windows API calls.
"""

import sys
import os
import time

try:
    import win32gui
    import win32con
    import win32api
    import pywin32_setup
except ImportError:
    print("Please install pywin32: pip install pywin32")
    sys.exit(1)

class Win32WeChat:
    """Pure Win32 WeChat implementation"""
    
    def __init__(self):
        self.hwnd = None
        self.chat_hwnds = {}
    
    def find_wechat(self):
        """Find WeChat window"""
        print("[Win32] Finding WeChat window...")
        
        # Try different window titles
        titles = ["微信", "WeChat"]
        
        for title in titles:
            hwnd = win32gui.FindWindow(None, title)
            if hwnd:
                self.hwnd = hwnd
                print(f"[Win32] Found WeChat window: {hwnd}")
                return True
        
        print("[Win32] WeChat window not found")
        return False
    
    def activate_window(self):
        """Ensure window is active"""
        if not self.hwnd:
            return False
        
        try:
            # Restore if minimized
            if win32gui.IsIconic(self.hwnd):
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)
            
            # Set foreground
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.3)
            
            print("[Win32] Window activated")
            return True
        except Exception as e:
            print(f"[Win32] Activation error: {e}")
            return False
    
    def find_chat_window(self, chat_name):
        """Find a chat window by name"""
        if not self.hwnd:
            return None
        
        try:
            # Click on search/chat input area
            # This is a workaround - wxauto's actual implementation
            
            # First, let's try to find the chat list
            # WeChat uses various controls
            
            # Try to get the main window coordinates
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            width = right - left
            height = bottom - top
            
            print(f"[Win32] Window: {width}x{height} at ({left}, {top})")
            
            # Find child windows
            def find_children(hwnd, list_):
                if win32gui.IsWindowVisible(hwnd):
                    text = win32gui.GetWindowText(hwnd)
                    cls = win32gui.GetClassName(hwnd)
                    list_.append((hwnd, text, cls))
                win32gui.EnumChildWindows(hwnd, lambda h, l: find_children(h, l), None)
                return list_
            
            children = find_children(self.hwnd, [])
            print(f"[Win32] Found {len(children)} child windows")
            
            return {
                'hwnd': self.hwnd,
                'left': left,
                'top': top,
                'width': width,
                'height': height,
                'children': children[:10]  # First 10 for debugging
            }
            
        except Exception as e:
            print(f"[Win32] Find chat error: {e}")
            return None
    
    def send_text(self, chat_name, message):
        """Send text message using clipboard method"""
        print(f"[Win32] Attempting to send to: {chat_name}")
        
        if not self.hwnd:
            if not self.find_wechat():
                return False
            self.activate_window()
        
        # Method: Use clipboard to paste message
        try:
            # Open WeChat
            win32api.ShellExecute(0, 'open', 'wechat:', None, None, 1)
            time.sleep(2)
            
            # Try to find and focus chat input
            # This is limited without wxauto
            
            print("[Win32] Direct text sending requires wxauto or UI automation")
            print("[Win32] Please use wxauto for full functionality")
            print("[Win32] Workaround: Use WeChat's phone integration or file transfer")
            
            return False
            
        except Exception as e:
            print(f"[Win32] Send error: {e}")
            return False


def check_wechat_status():
    """Check WeChat status"""
    print("\n=== WeChat Status Check ===\n")
    
    wechat = Win32WeChat()
    
    # Find window
    if not wechat.find_wechat():
        print("❌ WeChat not running")
        return
    
    # Get window info
    info = wechat.find_chat_window("")
    
    if info:
        print(f"✅ WeChat found")
        print(f"   Window: {info['hwnd']}")
        print(f"   Size: {info['width']}x{info['height']}")
        print(f"   Child windows: {len(info['children'])}")
        
        print("\n--- First 5 child windows ---")
        for hwnd, text, cls in info['children'][:5]:
            print(f"   [{hwnd}] {text[:30] if text else '(no text)'} - {cls}")
    
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Pure Win32 WeChat Tool")
    parser.add_argument("--status", action="store_true", help="Check WeChat status")
    parser.add_argument("--info", action="store_true", help="Get detailed window info")
    
    args = parser.parse_args()
    
    if args.status:
        check_wechat_status()
    elif args.info:
        wechat = Win32WeChat()
        if wechat.find_wechat():
            wechat.activate_window()
            info = wechat.find_chat_window("")
            if info:
                print(f"\nWindow Info:")
                for k, v in info.items():
                    if k != 'children':
                        print(f"  {k}: {v}")
    else:
        print("Usage:")
        print("  python win32_wechat.py --status    # Check WeChat status")
        print("  python win32_wechat.py --info     # Get detailed info")
        print()
        print("For full functionality, please resolve wxauto issues:")
        print("  1. Ensure WeChat is fully loaded")
        print("  2. Restart WeChat")
        print("  3. Check Windows version compatibility")


if __name__ == "__main__":
    main()
