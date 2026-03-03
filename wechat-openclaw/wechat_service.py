#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Service for OpenClaw
A background service that handles WeChat messaging via wxauto.
Provides HTTP API for OpenClaw to communicate with WeChat.
"""

import os
import sys
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wxauto import WeChat
    from src.utils.console import print_status
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install wxauto: pip install wxauto")
    sys.exit(1)

# Configuration
CONFIG = {
    "host": "127.0.0.1",
    "port": 18787,
    "poll_interval": 1,
    "max_message_length": 5000
}

class WeChatService:
    """WeChat service handler"""
    
    def __init__(self):
        self.wx = None
        self.running = False
        self.listen_list = []
        self.processed_messages = set()
        self.message_callback = None
        
    def initialize(self, listen_list=None):
        """Initialize WeChat connection"""
        print_status("Initializing WeChat service...", "info", "BOT")
        
        try:
            self.wx = WeChat()
            self.listen_list = listen_list or []
            
            # Add listening chats
            for chat_name in self.listen_list:
                try:
                    if self.wx.ChatWith(chat_name):
                        self.wx.AddListenChat(who=chat_name, savepic=True, savevoice=True)
                        print_status(f"Added listener for: {chat_name}", "success", "CHECK")
                except Exception as e:
                    print_status(f"Failed to add listener for {chat_name}: {e}", "warning", "WARNING")
            
            print_status("WeChat service initialized successfully", "success", "CHECK")
            return {"status": "success", "message": "WeChat initialized"}
            
        except Exception as e:
            print_status(f"Failed to initialize WeChat: {e}", "error", "ERROR")
            return {"status": "error", "message": str(e)}
    
    def start(self, callback=None):
        """Start listening for messages"""
        self.running = True
        self.message_callback = callback
        
        print_status("Starting message listener...", "info", "ANTENNA")
        
        # Start polling thread
        self.poll_thread = threading.Thread(target=self._poll_messages, daemon=True)
        self.poll_thread.start()
        
        print_status("WeChat service started", "success", "CHECK")
        return {"status": "success"}
    
    def stop(self):
        """Stop the service"""
        self.running = False
        print_status("WeChat service stopped", "info", "STOP")
        return {"status": "success"}
    
    def _poll_messages(self):
        """Poll for new messages"""
        while self.running:
            try:
                if self.wx:
                    messages = self.wx.GetListenMessage()
                    if messages:
                        for chat in messages:
                            chat_name = chat.who
                            chat_messages = messages.get(chat)
                            
                            if chat_messages:
                                for msg in chat_messages:
                                    normalized = self._normalize_message(msg, chat_name)
                                    if normalized and self.message_callback:
                                        self.message_callback(normalized)
                                        
            except Exception as e:
                print(f"Poll error: {e}")
            
            time.sleep(CONFIG["poll_interval"])
    
    def _normalize_message(self, msg, chat_name):
        """Normalize message to standard format"""
        try:
            content = msg.content or msg.text or ""
            msg_id = f"{msg.sender}-{msg.time}-{content}"
            
            # Skip duplicates
            if msg_id in self.processed_messages:
                return None
            self.processed_messages.add(msg_id)
            
            is_group = msg.sender != chat_name
            
            return {
                "id": msg_id,
                "channel": "wechat",
                "type": "group" if is_group else "private",
                "chat": chat_name,
                "chat_name": chat_name,
                "sender": msg.sender,
                "sender_name": msg.senderName or msg.sender,
                "content": content,
                "timestamp": msg.time if hasattr(msg, 'time') and msg.time else int(time.time()),
                "is_self": getattr(msg, 'isSelf', False),
                "is_group": is_group,
                "raw": {
                    "type": getattr(msg, 'type', 'text'),
                    "sender": msg.sender,
                    "content": content
                }
            }
        except Exception as e:
            print(f"Normalize error: {e}")
            return None
    
    def send_message(self, to, message):
        """Send a text message"""
        try:
            if not self.wx:
                return {"status": "error", "message": "WeChat not initialized"}
            
            if self.wx.ChatWith(to):
                self.wx.SendMsg(message)
                print(f"[WeChat] Sent to {to}: {message[:50]}...")
                return {"status": "success", "to": to, "content": message}
            else:
                return {"status": "error", "message": f"Failed to open chat: {to}"}
                
        except Exception as e:
            print(f"Send error: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_image(self, to, image_path):
        """Send an image"""
        try:
            if not self.wx:
                return {"status": "error", "message": "WeChat not initialized"}
            
            if self.wx.ChatWith(to):
                self.wx.SendImage(image_path)
                print(f"[WeChat] Sent image to {to}")
                return {"status": "success", "to": to, "path": image_path}
            else:
                return {"status": "error", "message": f"Failed to open chat: {to}"}
                
        except Exception as e:
            print(f"Send image error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_chat_list(self):
        """Get list of active chats"""
        try:
            if not self.wx:
                return {"status": "error", "message": "WeChat not initialized"}
            
            sessions = self.wx.GetSessionList() or []
            chats = []
            for session in sessions:
                chats.append({
                    "id": session.who,
                    "name": session.nickname or session.who,
                    "type": getattr(session, 'type', 'private'),
                    "unread": getattr(session, 'unread', 0)
                })
            
            return {"status": "success", "chats": chats}
            
        except Exception as e:
            print(f"Get chat list error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_status(self):
        """Get service status"""
        return {
            "status": "success" if self.wx else "not_initialized",
            "running": self.running,
            "listen_list": self.listen_list,
            "processed_count": len(self.processed_messages)
        }


# Global service instance
service = WeChatService()


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler"""
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[WeChat-API] {self.address_string()} - {format % args}")
    
    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == "/status":
            self.send_json_response(200, service.get_status())
        elif parsed.path == "/chats":
            self.send_json_response(200, service.get_chat_list())
        elif parsed.path == "/health":
            self.send_json_response(200, {"status": "ok"})
        else:
            self.send_json_response(404, {"error": "Not found"})
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == "/send":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode()
                data = json.loads(body)
                
                result = service.send_message(
                    data.get("to", ""),
                    data.get("message", "")
                )
                self.send_json_response(200, result)
                
            except Exception as e:
                self.send_json_response(400, {"error": str(e)})
        
        elif parsed.path == "/send-image":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode()
                data = json.loads(body)
                
                result = service.send_image(
                    data.get("to", ""),
                    data.get("path", "")
                )
                self.send_json_response(200, result)
                
            except Exception as e:
                self.send_json_response(400, {"error": str(e)})
        
        elif parsed.path == "/init":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode()
                data = json.loads(body)
                
                result = service.initialize(data.get("listen_list", []))
                self.send_json_response(200, result)
                
            except Exception as e:
                self.send_json_response(400, {"error": str(e)})
        
        elif parsed.path == "/start":
            # Start listening with callback URL
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode()
                data = json.loads(body)
                
                # Store callback for messages
                callback_url = data.get("callback_url")
                
                def message_callback(msg):
                    """Forward messages to callback URL"""
                    if callback_url:
                        try:
                            import requests
                            requests.post(callback_url, json=msg, timeout=5)
                        except:
                            pass
                
                result = service.start(message_callback)
                self.send_json_response(200, result)
                
            except Exception as e:
                self.send_json_response(400, {"error": str(e)})
        
        elif parsed.path == "/stop":
            result = service.stop()
            self.send_json_response(200, result)
        
        else:
            self.send_json_response(404, {"error": "Not found"})


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat Service for OpenClaw")
    parser.add_argument("--host", default=CONFIG["host"], help="Host to bind")
    parser.add_argument("--port", type=int, default=CONFIG["port"], help="Port to bind")
    parser.add_argument("--listen", nargs="*", default=[], help="Chat names to listen to")
    
    args = parser.parse_args()
    
    CONFIG["host"] = args.host
    CONFIG["port"] = args.port
    
    # Initialize service
    service.initialize(args.listen)
    
    # Start HTTP server
    server = HTTPServer((args.host, args.port), RequestHandler)
    
    print(f"\n{'='*50}")
    print(f"WeChat Service started on http://{args.host}:{args.port}")
    print(f"Listen list: {args.listen}")
    print(f"{'='*50}\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        service.stop()
        server.shutdown()


if __name__ == "__main__":
    main()
