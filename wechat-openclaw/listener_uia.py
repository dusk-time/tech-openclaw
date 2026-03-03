#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat listener using uiautomation
"""

import sys
import os
import time
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uiautomation as auto
except ImportError:
    print("pip install uiautomation")
    sys.exit(1)


class WeChatListener:
    """Listen for WeChat messages using uiautomation"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.last_messages = {}
        self.window = None
        
    def find_window(self):
        """Find WeChat window"""
        print("[Listener] Finding WeChat window...")
        self.window = auto.WindowControl(searchDepth=2, Name="微信")
        if not self.window.Exists(5, 1):
            print("[Listener] X WeChat not found")
            return False
        print("[Listener] OK Found WeChat")
        return True
    
    def get_message_area_screenshot(self):
        """Screenshot the message area"""
        if not self.window:
            return None
        
        try:
            # Try to find the chat area
            # This is a placeholder - actual implementation depends on WeChat version
            
            # Screenshot the main window
            rect = self.window.BoundingRectangle
            screenshot = auto.CaptureToImage(rect.left, rect.top, rect.right, rect.bottom)
            return screenshot
        except Exception as e:
            print(f"[Listener] Screenshot error: {e}")
            return None
    
    def listen(self, callback=None):
        """Start listening for messages"""
        if not self.find_window():
            return
        
        self.running = True
        self.callback = callback
        
        print("[Listener] Starting listener...")
        print("[Listener] This will check for new messages periodically")
        
        # Check every 3 seconds
        while self.running:
            try:
                # Get current time
                current_time = time.strftime("%H:%M:%S")
                
                # Try to detect new messages
                # This is a simplified version - real implementation would use OCR
                
                print(f"[{current_time}] Checking for messages...")
                
                # For now, just show the window is active
                if self.window.Exists(1, 0.5):
                    pass  # Window is active
                
                time.sleep(3)
                
            except Exception as e:
                print(f"[Listener] Error: {e}")
                time.sleep(5)
        
        print("[Listener] Listener stopped")
    
    def stop(self):
        """Stop listening"""
        self.running = False


def test_listener():
    """Test the listener"""
    def on_message(msg):
        print(f"[Callback] New message: {msg}")
    
    listener = WeChatListener(callback=on_message)
    listener.listen()


def main():
    print("=== WeChat Message Listener (uiautomation) ===\n")
    
    listener = WeChatListener()
    
    if not listener.find_window():
        return
    
    print("\nStarting listener...")
    print("Press Ctrl+C to stop\n")
    
    try:
        listener.listen()
    except KeyboardInterrupt:
        print("\nStopping...")
        listener.stop()


if __name__ == "__main__":
    main()
