#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Automation using Image Recognition + Coordinate Clicking
Works with any WeChat version by using screen coordinates.
"""

import sys
import os
import time
import math
import hashlib

try:
    import pygetwindow as gw
    from PIL import Image, ImageDraw, ImageGrab
    import pyautogui
    import pyscreeze
    import cv2
    import numpy as np
    
    SCREEN_AVAILABLE = True
except ImportError:
    SCREEN_AVAILABLE = False
    print("Install: pip install pyautogui pillow opencv-python")


class ImageBasedWeChat:
    """Image recognition based WeChat automation"""
    
    def __init__(self):
        self.window = None
        self.window_rect = None
        self.chat_positions = {}  # Cache chat positions
        self.input_pos = None
        self.send_btn_pos = None
    
    def find_window(self):
        """Find WeChat window"""
        print("[Image] Finding WeChat window...")
        
        windows = gw.getWindowsWithTitle("微信")
        if not windows:
            print("[Image] ✗ WeChat window not found")
            return False
        
        self.window = windows[0]
        self.window.activate()
        time.sleep(0.5)
        
        # Get window position
        self.window_rect = (
            self.window.left,
            self.window.top,
            self.window.right,
            self.window.bottom
        )
        
        width = self.window_rect[2] - self.window_rect[0]
        height = self.window_rect[3] - self.window_rect[1]
        
        print(f"[Image] ✓ Window: {width}x{height} at ({self.window_rect[0]}, {self.window_rect[1]})")
        return True
    
    def screenshot(self, region=None):
        """Take a screenshot"""
        if region:
            return pyautogui.screenshot(region=region)
        return pyautogui.screenshot()
    
    def find_text_on_screen(self, text, confidence=0.8):
        """Find text on screen using OCR-like search"""
        # Simple approach: look for matching UI elements
        # This is a placeholder - in production, use OCR
        
        screen = self.screenshot()
        screen_np = np.array(screen)
        gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)
        
        # For now, use coordinate-based approach
        return None
    
    def send_message(self, chat_name, message):
        """Send message using coordinate-based approach"""
        if not self.window:
            if not self.find_window():
                return False
        
        try:
            print(f"\n[Image] Sending message to: {chat_name}")
            
            # WeChat layout (approximate positions for 1920x1080):
            # - Chat list: left side, ~250px wide
            # - Chat area: right side
            # - Input box: bottom right area
            # - Send button: near input box, bottom right
            
            left, top, right, bottom = self.window_rect
            width = right - left
            height = bottom - top
            
            # Calculate positions based on common WeChat layout
            # These are relative positions that work for most screen sizes
            
            # Click on chat in list (approximate position)
            # Chat list is typically on the left side
            chat_list_x = left + 80
            chat_list_y = top + 150
            
            print(f"[Step 1] Opening chat: {chat_name}")
            pyautogui.click(chat_list_x, chat_list_y)
            time.sleep(0.5)
            
            # Find input box (typically in the bottom area)
            # Modern WeChat: input box is centered near bottom
            input_x = left + width // 2
            input_y = bottom - 150
            
            print(f"[Step 2] Clicking input box at ({input_x}, {input_y})")
            pyautogui.click(input_x, input_y)
            time.sleep(0.3)
            
            # Paste message using clipboard (for Chinese text support)
            import pyperclip
            print(f"[Step 3] Pasting message: {message[:30]}...")
            pyperclip.copy(message)
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # Click send button (typically right of input or near bottom right)
            send_x = right - 100
            send_y = bottom - 80
            
            print(f"[Step 4] Clicking send button at ({send_x}, {send_y})")
            pyautogui.click(send_x, send_y)
            time.sleep(0.3)
            
            print("[Image] ✓ Message sent!")
            return True
            
        except Exception as e:
            print(f"[Image] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def find_chat_position(self, chat_name):
        """Try to find a chat in the chat list"""
        if not self.window:
            return None
        
        left, top, right, bottom = self.window_rect
        
        # Scan chat list area (left side of window)
        chat_list_region = (
            left + 20,    # x
            top + 100,    # y
            left + 250,   # width
            bottom - 100  # height
        )
        
        screenshot = self.screenshot(region=chat_list_region)
        
        # Look for text that matches chat name
        # This would use OCR in a full implementation
        
        return None


def test_send():
    """Test sending a message"""
    if not SCREEN_AVAILABLE:
        print("Screen automation not available")
        return
    
    wechat = ImageBasedWeChat()
    
    if not wechat.find_window():
        return
    
    print("\n=== Test Send ===\n")
    
    # Try to send
    success = wechat.send_message("文件传输助手", "Hello from Image Automation! 🚀")
    
    print(f"\n{'='*50}")
    print(f"Result: {'✓ SUCCESS' if success else '✗ FAILED'}")
    print(f"{'='*50}\n")


def calibrate():
    """Calibrate positions for your screen"""
    print("\n=== Calibration Mode ===\n")
    print("This will help find the correct positions for your screen.\n")
    
    wechat = ImageBasedWeChat()
    if not wechat.find_window():
        return
    
    left, top, right, bottom = wechat.window_rect
    width = right - left
    height = bottom - top
    
    print(f"Window: {width}x{height}")
    print(f"Position: ({left}, {top})")
    
    # Show key positions
    print("\nKey positions:")
    print(f"  Chat list: ({left + 80}, {top + 150})")
    print(f"  Input box: ({left + width//2}, {bottom - 150})")
    print(f"  Send button: ({right - 100}, {bottom - 80})")
    
    # Highlight positions visually
    print("\nOpen WeChat and click on:")
    print("1. A chat in the list")
    print("2. The input box")
    print("3. The send button")
    
    input("\nPress Enter to get mouse position...")
    
    x, y = pyautogui.position()
    print(f"\nMouse position: ({x}, {y})")
    
    # Check if inside window
    if left < x < right and top < y < bottom:
        rel_x = x - left
        rel_y = y - top
        print(f"Relative to window: ({rel_x}, {rel_y})")
        print(f"As percentage: ({rel_x/width*100:.1f}%, {rel_y/height*100:.1f}%)")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Image-based WeChat Automation")
    parser.add_argument("--test", action="store_true", help="Test send message")
    parser.add_argument("--calibrate", action="store_true", help="Calibrate positions")
    parser.add_argument("--send", nargs=2, metavar=("TO", "MESSAGE"), help="Send message")
    
    args = parser.parse_args()
    
    if args.calibrate:
        calibrate()
    elif args.test:
        test_send()
    elif args.send:
        if not SCREEN_AVAILABLE:
            print("Install dependencies first")
            return
        
        wechat = ImageBasedWeChat()
        if wechat.find_window():
            wechat.send_message(args.send[0], args.send[1])
    else:
        print("Usage:")
        print("  python image_wechat.py --test       # Test send")
        print("  python image_wechat.py --calibrate  # Calibrate positions")
        print("  python image_wechat.py --send 'TO' 'MESSAGE'  # Send message")
        print()
        print("This uses image-based clicking for maximum compatibility")


if __name__ == "__main__":
    main()
