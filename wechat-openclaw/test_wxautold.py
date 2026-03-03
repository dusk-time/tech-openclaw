#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test wxautold
"""

import sys
import time

try:
    from wxauto import WeChat
    
    print("=== wxautold Test ===\n")
    
    print("Creating WeChat instance...")
    wx = WeChat()
    print("OK Created!")
    
    print("\nGetting session list...")
    sessions = wx.GetSessionList()
    print(f"Found {len(sessions)} sessions")
    
    for i, session in enumerate(sessions[:5]):
        print(f"  [{i+1}] {session.who}")
    
    print("\n✓ wxautold is working!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
