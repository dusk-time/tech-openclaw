#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Monitor - Screenshot + OCR to detect new messages
"""

import sys
import os
import time
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pyautogui
    import pygetwindow as gw
    from PIL import Image
except ImportError:
    print("pip install pyautogui pillow pygetwindow")
    sys.exit(1)

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    print("Warning: pytesseract not installed, OCR disabled")
    print("pip install pytesseract")
    OCR_AVAILABLE = False


class WeChatMonitor:
    """Monitor WeChat for new messages using screenshot comparison"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.last_screenshot_hash = None
        self.last_message_time = None
        self.window = None
        self.message_regions = []
        
    def find_window(self):
        """Find WeChat window"""
        windows = gw.getWindowsWithTitle("微信")
        if not windows:
            print("✗ WeChat not found")
            return False
        
        self.window = windows[0]
        print(f"✓ Found WeChat: {self.window.width}x{self.window.height}")
        return True
    
    def capture_chat_area(self):
        """Capture the chat message area"""
        if not self.window:
            return None
        
        try:
            # Screenshot the window area
            screenshot = pyautogui.screenshot(region=(
                self.window.left,
                self.window.top,
                self.window.width,
                self.window.height
            ))
            return screenshot
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    
    def get_screenshot_hash(self, screenshot):
        """Get a simple hash of the screenshot"""
        if not screenshot:
            return None
        return hashlib.md5(screenshot.tobytes()).hexdigest()
    
    def extract_text(self, screenshot):
        """Extract text from screenshot using OCR"""
        if not OCR_AVAILABLE or not screenshot:
            return None
        try:
            text = pytesseract.image_to_string(screenshot, lang='chi_sim+eng')
            return text
        except Exception as e:
            print(f"OCR error: {e}")
            return None
    
    def monitor(self, callback=None, interval=3):
        """Monitor for new messages"""
        if not self.find_window():
            return
        
        self.callback = callback
        self.running = True
        
        print(f"\n=== Monitoring WeChat ===")
        print(f"Check interval: {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        while self.running:
            try:
                # Bring window to front
                self.window.activate()
                time.sleep(0.5)
                
                # Capture screenshot
                screenshot = self.capture_chat_area()
                if not screenshot:
                    time.sleep(interval)
                    continue
                
                # Check if changed
                current_hash = self.get_screenshot_hash(screenshot)
                if current_hash != self.last_screenshot_hash:
                    self.last_screenshot_hash = current_hash
                    
                    # Notify callback
                    if self.callback:
                        self.callback({
                            "time": datetime.now().isoformat(),
                            "type": "change_detected"
                        })
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Change detected in chat area")
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(interval)
        
        print("Monitor stopped")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False


def on_new_message(msg):
    """Callback when new message detected"""
    print(f"🔔 New message detected: {msg}")


def main():
    print("=== WeChat Chat Monitor ===\n")
    
    if not OCR_AVAILABLE:
        print("⚠️  OCR not available - install for text extraction:")
        print("   pip install pytesseract")
        print("   Also need Tesseract OCR installed on system\n")
    
    monitor = WeChatMonitor(callback=on_new_message)
    
    try:
        monitor.monitor(interval=3)
    except KeyboardInterrupt:
        print("\nStopping...")
        monitor.stop()


if __name__ == "__main__":
    main()
