#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Automation - Combines wxautold with pyautogui fallback
Works with WeChat 4.x
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(__file__))

try:
    import pyautogui
    import pyperclip
    import pygetwindow as gw
except ImportError:
    print("pip install pyautogui pyperclip pygetwindow")

# Load positions
POSITIONS_FILE = 'positions.json'

def load_positions():
    """Load calibrated positions"""
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'r') as f:
            return json.load(f)
    return None

def save_positions(positions):
    """Save positions"""
    with open(POSITIONS_FILE, 'w') as f:
        json.dump(positions, f, indent=2)

def get_window():
    """Get WeChat window"""
    windows = gw.getWindowsWithTitle('微信')
    if not windows:
        return None
    return windows[0]

class WeChatBot:
    """WeChat automation bot"""
    
    def __init__(self):
        self.window = None
        self.positions = load_positions()
        
    def find_window(self):
        """Find and activate WeChat window"""
        self.window = get_window()
        if not self.window:
            print("✗ WeChat not found!")
            return False
        
        self.window.activate()
        time.sleep(0.5)
        print(f"✓ Found WeChat: {self.window.width}x{self.window.height}")
        return True
    
    def send_message(self, chat_name, message):
        """Send a text message"""
        if not self.find_window():
            return False
        
        if not self.positions:
            print("✗ No positions configured! Run calibration first.")
            return False
        
        left, top, right, bottom = (
            self.window.left, self.window.top,
            self.window.right, self.window.bottom
        )
        width = right - left
        height = bottom - top
        
        # Calculate positions
        input_x = int(left + width * self.positions['input_box']['x_pct'] / 100)
        input_y = int(top + height * self.positions['input_box']['y_pct'] / 100)
        send_x = int(left + width * self.positions['send_btn']['x_pct'] / 100)
        send_y = int(top + height * self.positions['send_btn']['y_pct'] / 100)
        
        try:
            # Click input box
            pyautogui.click(input_x, input_y)
            time.sleep(0.3)
            
            # Paste message using clipboard
            pyperclip.copy(message)
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # Click send button
            pyautogui.click(send_x, send_y)
            time.sleep(0.3)
            
            print(f"✓ Sent to {chat_name}: {message[:30]}...")
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def get_chat_list(self):
        """Get list of chats (simplified)"""
        if not self.find_window():
            return []
        
        # Return a placeholder - real implementation needs wxauto or uiautomation
        print("Chat list not available - requires wxauto")
        return []


def calibrate():
    """Interactive calibration"""
    print("=== Calibration ===\n")
    
    if not get_window():
        print("✗ WeChat not found!")
        return
    
    print("Click on:")
    print("1. Input box")
    print("2. Send button")
    print("\nI'll record the positions...")
    
    input("\nPress Enter to start...")
    
    clicks = []
    
    def on_click(x, y, button, pressed):
        if pressed:
            clicks.append((x, y))
            print(f"  Recorded: ({x}, {y})")
            if len(clicks) >= 2:
                return False
    
    from pynput import mouse
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()
    
    if len(clicks) >= 2:
        win = get_window()
        left, top = win.left, win.top
        width, height = win.width, win.height
        
        input_x, input_y = clicks[0]
        send_x, send_y = clicks[1]
        
        positions = {
            'input_box': {
                'x_pct': round((input_x - left) / width * 100, 1),
                'y_pct': round((input_y - top) / height * 100, 1)
            },
            'send_btn': {
                'x_pct': round((send_x - left) / width * 100, 1),
                'y_pct': round((send_y - top) / height * 100, 1)
            }
        }
        
        save_positions(positions)
        print(f"\n✓ Saved positions:")
        print(f"  Input: ({positions['input_box']['x_pct']}%, {positions['input_box']['y_pct']}%)")
        print(f"  Send: ({positions['send_btn']['x_pct']}%, {positions['send_btn']['y_pct']}%)")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python wechat_bot.py send <chat> <message>")
        print("  python wechat_bot.py calibrate")
        return
    
    command = sys.argv[1]
    
    bot = WeChatBot()
    
    if command == 'send':
        if len(sys.argv) < 4:
            print("Usage: python wechat_bot.py send <chat> <message>")
            return
        chat = sys.argv[2]
        message = sys.argv[3]
        bot.send_message(chat, message)
    
    elif command == 'calibrate':
        calibrate()
    
    elif command == 'test':
        bot.find_window()
        print(f"Positions: {bot.positions}")


if __name__ == "__main__":
    main()
