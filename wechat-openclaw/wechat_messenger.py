#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple WeChat Messenger for OpenClaw
A lightweight script to send/receive WeChat messages.
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wxauto import WeChat
except ImportError:
    print("Please install wxauto: pip install wxauto")
    sys.exit(1)

# Import Windows API for login assistant
try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

def ensure_wechat_ready(wait_seconds=5):
    """Ensure WeChat window is visible, active, and fully loaded"""
    if not WIN32_AVAILABLE:
        print("[WeChat] Win32 API not available")
        return True
    
    print(f"[WeChat] Ensuring WeChat is ready (waiting {wait_seconds}s)...")
    
    try:
        # Find WeChat window
        hwnd = win32gui.FindWindow(None, "微信")
        if hwnd == 0:
            print("[WeChat] WeChat window not found")
            return False
        
        # Get window position
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        
        # Restore and activate window
        for attempt in range(3):
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)
                
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                
                if win32gui.GetForegroundWindow() == hwnd:
                    break
                    
            except Exception as e:
                print(f"[WeChat] Attempt {attempt + 1}: {e}")
                time.sleep(0.5)
        
        # Wait for WeChat to fully load
        print(f"[WeChat] Waiting {wait_seconds}s for WeChat to fully load...")
        time.sleep(wait_seconds)
        
        # Verify window is still valid
        if win32gui.IsWindow(hwnd):
            print("[WeChat] ✓ WeChat is ready")
            return True
        else:
            print("[WeChat] ✗ Window handle became invalid")
            return False
        
    except Exception as e:
        print(f"[WeChat] Error: {e}")
        return False


class WeChatMessenger:
    """Simple WeChat messenger"""
    
    def __init__(self):
        self.wx = None
        self.listen_list = []
        self.processed = set()
    
    def init(self, listen_list=None):
        """Initialize"""
        print("[WeChat] Initializing...")
        
        # Ensure WeChat is ready first
        if WIN32_AVAILABLE:
            ensure_wechat_ready(wait_seconds=5)
        
        try:
            self.wx = WeChat()
            self.listen_list = listen_list or []
            
            for chat in self.listen_list:
                try:
                    if self.wx.ChatWith(chat):
                        self.wx.AddListenChat(who=chat, savepic=True, savevoice=True)
                        print(f"[WeChat] ✓ Listening to: {chat}")
                except Exception as e:
                    print(f"[WeChat] ✗ Failed to add {chat}: {e}")
            
            print("[WeChat] Initialization complete\n")
            return True
        except Exception as e:
            print(f"[WeChat] Error: {e}")
            print("\n[WeChat] Troubleshooting:")
            print("1. Make sure WeChat is fully loaded (showing chat list)")
            print("2. Try: python wechat_messenger.py --login")
            print("3. Wait a few seconds, then try again")
            return False
    
    def send(self, to, message):
        """Send a message"""
        try:
            if self.wx.ChatWith(to):
                self.wx.SendMsg(message)
                print(f"[WeChat] ✓ Sent to {to}: {message[:30]}...")
                return True
            else:
                print(f"[WeChat] ✗ Failed to open chat: {to}")
                return False
        except Exception as e:
            print(f"[WeChat] Send error: {e}")
            return False
    
    def send_image(self, to, path):
        """Send an image"""
        try:
            if self.wx.ChatWith(to):
                self.wx.SendImage(path)
                print(f"[WeChat] ✓ Sent image to {to}")
                return True
            return False
        except Exception as e:
            print(f"[WeChat] Image error: {e}")
            return False
    
    def listen_once(self, callback=None):
        """Listen for one message cycle"""
        if not self.wx:
            return []
        
        messages = []
        try:
            msgs = self.wx.GetListenMessage()
            if msgs:
                for chat in msgs:
                    chat_name = chat.who
                    chat_msgs = msgs.get(chat)
                    
                    if chat_msgs:
                        for msg in chat_msgs:
                            msg_id = f"{msg.sender}-{msg.time}"
                            if msg_id in self.processed:
                                continue
                            self.processed.add(msg_id)
                            
                            normalized = {
                                "id": msg_id,
                                "chat": chat_name,
                                "sender": msg.sender,
                                "content": msg.content or msg.text or "",
                                "is_group": msg.sender != chat_name,
                                "timestamp": msg.time or int(time.time())
                            }
                            
                            messages.append(normalized)
                            if callback:
                                callback(normalized)
        except Exception as e:
            print(f"[WeChat] Listen error: {e}")
        
        return messages
    
    def get_chats(self):
        """Get chat list"""
        if not self.wx:
            return []
        try:
            sessions = self.wx.GetSessionList() or []
            return [{"id": s.who, "name": s.nickname or s.who} for s in sessions]
        except:
            return []


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat Messenger for OpenClaw")
    parser.add_argument("--send", nargs=2, metavar=("TO", "MESSAGE"), help="Send message")
    parser.add_argument("--send-image", nargs=2, metavar=("TO", "PATH"), help="Send image")
    parser.add_argument("--listen", nargs="*", default=[], help="Chat names to listen")
    parser.add_argument("--continuous", action="store_true", help="Continuous listening")
    parser.add_argument("--chats", action="store_true", help="List chats")
    parser.add_argument("--login", action="store_true", help="Ensure WeChat window is active")
    
    args = parser.parse_args()
    
    # Handle login/activate command first
    if args.login:
        ensure_wechat_ready()
        return
    
    messenger = WeChatMessenger()
    
    if not messenger.init(args.listen):
        sys.exit(1)
    
    if args.chats:
        print("\n[WeChat] Chat list:")
        for chat in messenger.get_chats():
            print(f"  - {chat['name']} ({chat['id']})")
        print()
    
    if args.send:
        messenger.send(args.send[0], args.send[1])
    
    if args.send_image:
        messenger.send_image(args.send_image[0], args.send_image[1])
    
    if args.continuous:
        print("\n[WeChat] Listening (Ctrl+C to stop)...")
        try:
            while True:
                msgs = messenger.listen_once(lambda m: print(f"[WeChat] Message from {m['sender']}: {m['content'][:50]}"))
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[WeChat] Stopped")


if __name__ == "__main__":
    main()
