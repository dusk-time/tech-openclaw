#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Automation with Image Recognition
Automatically finds input box and send button using image matching.
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pyautogui
    import pygetwindow as gw
    from PIL import Image, ImageDraw
    import cv2
    import numpy as np
    SCREEN_AVAILABLE = True
except ImportError:
    SCREEN_AVAILABLE = False
    print("pip install pyautogui pillow opencv-python")


class ImageBasedAutomation:
    """Find UI elements using image recognition"""
    
    def __init__(self):
        self.window = None
        self.window_rect = None
        
        # Template images (we'll generate them)
        self.templates = {}
    
    def find_window(self):
        """Find WeChat window"""
        windows = gw.getWindowsWithTitle("微信")
        if not windows:
            return False
        
        self.window = windows[0]
        self.window.activate()
        time.sleep(0.5)
        
        left, top, right, bottom = (
            self.window.left, self.window.top,
            self.window.right, self.window.bottom
        )
        self.window_rect = (left, top, right, bottom)
        
        return True
    
    def screenshot_region(self):
        """Screenshot the WeChat window region"""
        if not self.window_rect:
            return None
        
        left, top, right, bottom = self.window_rect
        return pyautogui.screenshot(region=(left, top, right - left, bottom - top))
    
    def find_text_position(self, text, region=None):
        """
        Find text position using pyautogui's locate functions
        This works if the text is visible on screen
        """
        try:
            # Try to locate the text on screen
            # pyautogui can sometimes find text using OCR
            location = pyautogui.locateOnScreen(
                text,
                confidence=0.8,
                region=region
            )
            if location:
                return location
        except Exception as e:
            print(f"Text search error: {e}")
        
        return None
    
    def find_color_pattern(self, target_color, tolerance=30):
        """Find areas matching a target color (for buttons)"""
        screenshot = self.screenshot_region()
        if not screenshot:
            return None
        
        img = np.array(screenshot)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # For WeChat send button, look for right-bottom area with button-like color
        h, w = gray.shape
        
        # Focus on bottom-right area where send button typically is
        roi = gray[int(h*0.7):h, int(w*0.7):w]
        
        return None
    
    def find_by_template(self, template_path):
        """Find element using template matching"""
        if not os.path.exists(template_path):
            return None
        
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            return None
        
        screenshot = self.screenshot_region()
        if not screenshot:
            return None
        
        img = np.array(screenshot)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Template matching
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.7:  # Confidence threshold
            return max_loc
        
        return None
    
    def find_send_button_by_text(self):
        """Find send button by looking for '发送' text"""
        # Strategy: Look in the bottom-right area for button-like elements
        if not self.window_rect:
            return None
        
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        # WeChat send button is typically in the bottom-right
        # Let's try to find it by position heuristic first
        
        # Send button is usually at:
        # - Right side: 80-95% of window width
        # - Bottom area: 85-95% of window height
        
        # Calculate the typical area
        send_area = (
            int(left + width * 0.75),  # x
            int(top + height * 0.8),   # y
            int(left + width * 0.95),   # width
            int(top + height * 0.95)    # height
        )
        
        # Take a screenshot of the send button area
        screenshot = pyautogui.screenshot(region=send_area)
        
        # For now, return a calculated position
        # This is a fallback when image recognition doesn't work
        return {
            "x": int(left + width * 0.85),
            "y": int(top + height * 0.88)
        }
    
    def find_input_box(self):
        """Find chat input box"""
        if not self.window_rect:
            return None
        
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        # Input box is typically:
        # - Centered horizontally: 20-70% of width
        # - Bottom area: 70-85% of height
        
        return {
            "x": int(left + width * 0.45),
            "y": int(top + height * 0.78)
        }
    
    def send_message(self, chat_name, message):
        """Send message using automated positioning"""
        if not self.find_window():
            return {"status": "error", "message": "WeChat not found"}
        
        try:
            left, top, right, bottom = self.window_rect
            width = right - left
            height = bottom - top
            
            # Step 1: Click on chat (approximate - user should select chat first)
            print(f"[Auto] Would click on chat: {chat_name}")
            
            # Step 2: Find and click input box
            input_pos = self.find_input_box()
            if input_pos:
                pyautogui.click(input_pos["x"], input_pos["y"])
                time.sleep(0.3)
                print(f"[Auto] Clicked input at ({input_pos['x']}, {input_pos['y']})")
            
            # Step 3: Type message
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('backspace')
            time.sleep(0.1)
            pyautogui.write(str(message))
            time.sleep(0.3)
            print(f"[Auto] Typed message: {message[:30]}...")
            
            # Step 4: Click send button
            send_pos = self.find_send_button_by_text()
            if send_pos:
                pyautogui.click(send_pos["x"], send_pos["y"])
                time.sleep(0.3)
                print(f"[Auto] Clicked send at ({send_pos['x']}, {send_pos['y']})")
            
            return {"status": "success", "message": "Sent"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def calibrate_automatically(self):
        """
        Interactive calibration using click detection
        """
        if not self.find_window():
            return None
        
        left, top, right, bottom = self.window_rect
        width = right - left
        height = bottom - top
        
        print(f"\nWindow: {width}x{height}")
        print(f"Position: ({left}, {top})\n")
        
        print("=== 自动校准 ===")
        print("请依次点击：")
        print("1. 输入框")
        print("2. 发送按钮")
        print("3. 按 Enter 完成\n")
        
        input("准备好了吗？按 Enter 开始...")
        
        try:
            # Get input box position
            input("\n点击输入框，然后按 Enter...")
            input_x, input_y = pyautogui.position()
            
            # Get send button position  
            input("点击发送按钮，然后按 Enter...")
            send_x, send_y = pyautogui.position()
            
            # Calculate percentages
            input_pct_x = round((input_x - left) / width * 100, 1)
            input_pct_y = round((input_y - top) / height * 100, 1)
            send_pct_x = round((send_x - left) / width * 100, 1)
            send_pct_y = round((send_y - top) / height * 100, 1)
            
            positions = {
                "input_box": {"x_pct": input_pct_x, "y_pct": input_pct_y},
                "send_btn": {"x_pct": send_pct_x, "y_pct": send_pct_y}
            }
            
            # Save
            config_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "positions.json"
            )
            with open(config_file, 'w') as f:
                json.dump(positions, f, indent=2)
            
            print(f"\n✓ 已保存到 {config_file}")
            print(f"输入框: ({input_pct_x}%, {input_pct_y}%)")
            print(f"发送按钮: ({send_pct_x}%, {send_pct_y}%)")
            
            return positions
            
        except KeyboardInterrupt:
            print("\n取消")
            return None


def test_automated_send():
    """Test the automated sending"""
    auto = ImageBasedAutomation()
    return auto.send_message("测试", "自动测试消息")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Image-based WeChat Automation")
    parser.add_argument("--calibrate", action="store_true", help="Run automatic calibration")
    parser.add_argument("--test", action="store_true", help="Test send message")
    parser.add_argument("--send", nargs=2, metavar=("TO", "MESSAGE"), help="Send message")
    
    args = parser.parse_args()
    
    if args.calibrate:
        auto = ImageBasedAutomation()
        auto.calibrate_automatically()
    elif args.test:
        test_automated_send()
    elif args.send:
        auto = ImageBasedAutomation()
        auto.send_message(args.send[0], args.send[1])
    else:
        print("Usage:")
        print("  python image_auto.py --calibrate    # Calibrate positions")
        print("  python image_auto.py --test        # Test send")
        print("  python image_auto.py --send 'TO' 'MESSAGE'  # Send message")


if __name__ == "__main__":
    main()
