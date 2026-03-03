#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Automation using uiautomation
Works with WeChat 4.x versions.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uiautomation as auto
except ImportError:
    print("Please install uiautomation: pip install uiautomation")
    sys.exit(1)


class WeChatUIA:
    """WeChat automation using uiautomation"""
    
    def __init__(self):
        self.window = None
        self.chat_list_control = None
        self.chat_input_control = None
        self.send_button_control = None
    
    def connect(self, timeout=10):
        """Connect to WeChat window"""
        print(f"[WeChat] Connecting to WeChat (timeout: {timeout}s)...")
        
        # Try to find WeChat window
        self.window = auto.WindowControl(searchDepth=2, Name="微信")
        
        if not self.window.Exists(timeout, 1):
            print("[WeChat] ✗ WeChat window not found")
            return False
        
        print(f"[WeChat] ✓ Connected to: {self.window.Name}")
        return True
    
    def explore_ui(self):
        """Explore WeChat UI structure"""
        if not self.window:
            print("Not connected")
            return
        
        print("\n=== UI Structure ===\n")
        
        # Get all children recursively
        def print_tree(elem, indent=0):
            try:
                name = elem.Name or "(no name)"
                ctype = elem.ControlTypeName or "(unknown)"
                print("  " * indent + f"[{ctype}] {name[:50]}")
                
                # Only go 2 levels deep
                if indent < 2:
                    for child in elem.GetChildren()[:20]:  # Limit children
                        print_tree(child, indent + 1)
            except:
                pass
        
        print_tree(self.window)
    
    def find_controls(self):
        """Find key controls"""
        if not self.window:
            return False
        
        print("\n=== Finding Controls ===\n")
        
        # Find all ListControls (chat list)
        lists = self.window.ListControl()
        print(f"Found ListControl(s): {len(lists) if isinstance(lists, list) else 1}")
        
        # Find Input (chat input)
        edits = self.window.EditControl()
        print(f"Found EditControl(s): {len(edits) if isinstance(edits, list) else 1}")
        
        # Find Buttons
        buttons = self.window.ButtonControl()
        print(f"Found ButtonControl(s): {len(buttons) if isinstance(buttons, list) else 1}")
        
        return True
    
    def send_message(self, chat_name, message):
        """Send a message"""
        if not self.window:
            print("Not connected")
            return False
        
        try:
            print(f"\n[WeChat] Attempting to send message...")
            print(f"  To: {chat_name}")
            print(f"  Message: {message[:50]}...")
            
            # Step 1: Find and click on the chat in the list
            print("\n[Step 1] Finding chat...")
            
            # Search in the contact list
            contact_list = self.window.ListControl(Name="会话")
            if not contact_list.Exists(2, 0.5):
                # Try alternative
                contact_list = self.window.ListControl()
            
            if contact_list.Exists(2, 0.5):
                print("  ✓ Found contact list")
                
                # Try to find the contact
                contact = contact_list.TextControl(Name=chat_name)
                if contact.Exists(2, 0.5):
                    print(f"  ✓ Found contact: {chat_name}")
                    contact.Click()
                    time.sleep(0.5)
                else:
                    print(f"  ✗ Contact not found: {chat_name}")
                    # Try clicking first item for testing
                    items = contact_list.GetChildren()
                    if items:
                        print(f"  Clicking first available contact")
                        items[0].Click()
                        time.sleep(0.5)
            
            # Step 2: Find input box
            print("\n[Step 2] Finding input box...")
            edit = self.window.EditControl()
            if edit.Exists(2, 0.5):
                print("  ✓ Found input box")
                edit.Click()
                time.sleep(0.2)
            else:
                print("  ✗ Input box not found")
                return False
            
            # Step 3: Type message
            print("\n[Step 3] Typing message...")
            edit.SendKeys(message)
            time.sleep(0.3)
            print("  ✓ Message typed")
            
            # Step 4: Click send button
            print("\n[Step 4] Clicking send...")
            
            # Try different send button locations
            send_btn = self.window.ButtonControl(Name="发送")
            if not send_btn.Exists(1, 0.2):
                send_btn = self.window.ButtonControl(Name="Send")
            if not send_btn.Exists(1, 0.2):
                # Look for button near input
                send_btns = self.window.ButtonControl()
                if send_btns:
                    for btn in send_btns[:5]:
                        if btn.Name and "发送" in btn.Name:
                            send_btn = btn
                            break
            
            if send_btn.Exists(1, 0.2):
                send_btn.Click()
                print("  ✓ Message sent!")
                return True
            else:
                print("  ✗ Send button not found")
                # Try Enter key
                print("  Trying Enter key...")
                auto.SendKeys("{Enter}")
                return True
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_send():
    """Test sending a message"""
    wechat = WeChatUIA()
    
    if not wechat.connect(5):
        return
    
    wechat.explore_ui()
    
    print("\n=== Test Send ===\n")
    
    # Try to send to "文件传输助手"
    success = wechat.send_message("文件传输助手", "Hello from uiautomation! 🚀")
    
    print(f"\n{'='*50}")
    print(f"Send result: {'✓ SUCCESS' if success else '✗ FAILED'}")
    print(f"{'='*50}\n")


def explore():
    """Explore UI structure"""
    wechat = WeChatUIA()
    
    if not wechat.connect(5):
        return
    
    wechat.explore_ui()
    wechat.find_controls()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat uiautomation Tool")
    parser.add_argument("--explore", action="store_true", help="Explore UI structure")
    parser.add_argument("--test", action="store_true", help="Test send message")
    
    args = parser.parse_args()
    
    if args.explore:
        explore()
    elif args.test:
        test_send()
    else:
        print("Usage:")
        print("  python wechat_uia.py --explore   # Explore UI structure")
        print("  python wechat_uia.py --test     # Test send message")
        print()
        print("This uses uiautomation for newer WeChat versions")


if __name__ == "__main__":
    main()
