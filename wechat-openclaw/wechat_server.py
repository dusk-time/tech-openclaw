#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat HTTP Service for OpenClaw
Provides REST API for WeChat automation.
"""

import sys
import os
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our automation module
try:
    import pyautogui
    import pygetwindow as gw
    SCREEN_AVAILABLE = True
except ImportError:
    SCREEN_AVAILABLE = False
    print("Warning: Screen automation not available")


class WeChatServer:
    """WeChat HTTP Server"""
    
    def __init__(self, host="127.0.0.1", port=18788):
        self.host = host
        self.port = port
        self.window = None
        self.window_rect = None
        self.running = False
        
        # Load positions from config or use defaults
        self.positions = self.load_positions()
    
    def load_positions(self):
        """Load calibrated positions"""
        config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "positions.json"
        )
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default positions (percentages of window)
        return {
            "chat_list": {"x": 80, "y": 150},  # Offset from left/top
            "input_box": {"x_pct": 50, "y_pct": 85},  # Percentage of window
            "send_btn": {"x_pct": 90, "y_pct": 90}   # Percentage of window
        }
    
    def save_positions(self):
        """Save calibrated positions"""
        config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "positions.json"
        )
        
        with open(config_file, 'w') as f:
            json.dump(self.positions, f, indent=2)
    
    def find_window(self):
        """Find WeChat window"""
        if not SCREEN_AVAILABLE:
            return False
        
        try:
            windows = gw.getWindowsWithTitle("微信")
            if not windows:
                return {"status": "error", "message": "WeChat not found"}
            
            self.window = windows[0]
            self.window.activate()
            time.sleep(0.5)
            
            left, top, right, bottom = (
                self.window.left,
                self.window.top,
                self.window.right,
                self.window.bottom
            )
            self.window_rect = (left, top, right, bottom)
            
            return {
                "status": "success",
                "window": {
                    "width": right - left,
                    "height": bottom - top,
                    "left": left,
                    "top": top
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_window(self):
        """Get or find window"""
        if not self.window:
            result = self.find_window()
            if result.get("status") != "success":
                return None
        return self.window
    
    def get_coords(self, x_pct=None, y_pct=None, x=None, y=None):
        """Calculate absolute coordinates"""
        if not self.window_rect:
            self.find_window()
        
        if not self.window_rect:
            return None
        
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        if x_pct is not None:
            x = left + int(width * x_pct / 100)
        if y_pct is not None:
            y = top + int(height * y_pct / 100)
        
        return (x, y)
    
    def send_message(self, chat_name, message):
        """Send a message"""
        if not self.get_window():
            return {"status": "error", "message": "WeChat not found"}
        
        try:
            left, top, right, bottom = self.window_rect
            width = right - left
            height = bottom - top
            
            # Calculate positions
            chat_x = left + self.positions["chat_list"]["x"]
            chat_y = top + self.positions["chat_list"]["y"]
            
            input_pos = self.get_coords(
                self.positions["input_box"]["x_pct"],
                self.positions["input_box"]["y_pct"]
            )
            
            send_pos = self.get_coords(
                self.positions["send_btn"]["x_pct"],
                self.positions["send_btn"]["y_pct"]
            )
            
            # Step 1: Click chat list area (approximate)
            pyautogui.click(chat_x, chat_y)
            time.sleep(0.5)
            
            # Step 2: Click input box
            if input_pos:
                pyautogui.click(input_pos[0], input_pos[1])
                time.sleep(0.3)
            
            # Step 3: Paste message using clipboard (for Chinese text support)
            import pyperclip
            pyperclip.copy(str(message))
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # Step 4: Click send
            if send_pos:
                pyautogui.click(send_pos[0], send_pos[1])
            
            return {
                "status": "success",
                "to": chat_name,
                "message": message[:50]
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def calibrate_click(self, x, y):
        """Record a calibration click"""
        # Store as absolute position
        self.positions["calibrated_click"] = {"x": x, "y": y}
        self.save_positions()
        return {"status": "success", "position": {"x": x, "y": y}}
    
    def calibrate_chat_list(self, x, y):
        """Calibrate chat list click position"""
        self.positions["chat_list"] = {
            "x": x - self.window_rect[0],
            "y": y - self.window_rect[1]
        }
        self.save_positions()
        return {"status": "success"}
    
    def calibrate_input(self, x, y):
        """Calibrate input box position"""
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        self.positions["input_box"] = {
            "x_pct": round((x - left) / width * 100, 1),
            "y_pct": round((y - top) / height * 100, 1)
        }
        self.save_positions()
        return {"status": "success"}
    
    def calibrate_send(self, x, y):
        """Calibrate send button position"""
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        self.positions["send_btn"] = {
            "x_pct": round((x - left) / width * 100, 1),
            "y_pct": round((y - top) / height * 100, 1)
        }
        self.save_positions()
        return {"status": "success"}
    
    def get_status(self):
        """Get server status"""
        return {
            "status": "running" if self.running else "stopped",
            "window_found": self.window is not None,
            "positions": self.positions,
            "screen_available": SCREEN_AVAILABLE
        }


# Global server instance
server = None


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler"""
    
    def log_message(self, format, *args):
        print(f"[WeChat-API] {args[0]}")
    
    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/status":
            self.send_json(200, server.get_status())
        elif parsed.path == "/health":
            self.send_json(200, {"status": "ok"})
        elif parsed.path == "/window":
            self.send_json(200, server.find_window())
        else:
            self.send_json(404, {"error": "Not found"})
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            data = json.loads(body) if body else {}
            
            if parsed.path == "/send":
                result = server.send_message(
                    data.get("to", ""),
                    data.get("message", "")
                )
                self.send_json(200, result)
            
            elif parsed.path == "/calibrate/chat":
                result = server.calibrate_chat_list(
                    data.get("x", 0),
                    data.get("y", 0)
                )
                self.send_json(200, result)
            
            elif parsed.path == "/calibrate/input":
                result = server.calibrate_input(
                    data.get("x", 0),
                    data.get("y", 0)
                )
                self.send_json(200, result)
            
            elif parsed.path == "/calibrate/send":
                result = server.calibrate_send(
                    data.get("x", 0),
                    data.get("y", 0)
                )
                self.send_json(200, result)
            
            else:
                self.send_json(404, {"error": "Not found"})
                
        except Exception as e:
            self.send_json(400, {"error": str(e)})


def main():
    global server
    
    import argparse
    parser = argparse.ArgumentParser(description="WeChat HTTP Service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18788)
    
    args = parser.parse_args()
    
    # Create server
    server = WeChatServer(args.host, args.port)
    
    # Find window on startup
    server.find_window()
    
    # Start HTTP server
    httpd = HTTPServer((args.host, args.port), RequestHandler)
    
    print(f"\n{'='*60}")
    print(f"WeChat HTTP Service")
    print(f"{'='*60}")
    print(f"Server: http://{args.host}:{args.port}")
    print(f"Endpoints:")
    print(f"  GET  /status       - Server status")
    print(f"  GET  /window       - Find WeChat window")
    print(f"  POST /send         - Send message")
    print(f"  POST /calibrate/*  - Calibrate positions")
    print(f"{'='*60}\n")
    
    try:
        server.running = True
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.running = False
        httpd.shutdown()


if __name__ == "__main__":
    main()
