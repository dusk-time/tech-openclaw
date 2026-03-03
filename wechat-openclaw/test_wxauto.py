#!/usr/bin/env python3
"""
Simple wxauto Test
Minimal test to diagnose wxauto issues.
"""

import sys
import time

print("=== wxauto Diagnostic Test ===\n")

# Test 1: Import wxauto
print("1. Importing wxauto...")
try:
    from wxauto import WeChat
    print("   ✓ wxauto imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create WeChat instance (minimal)
print("\n2. Creating WeChat instance...")
try:
    wx = WeChat()
    print("   ✓ WeChat() created")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    print("\n   This is the core issue!")
    print("   Possible causes:")
    print("   - WeChat not fully loaded")
    print("   - Windows version incompatibility")
    print("   - wxauto version issue")
    sys.exit(1)

# Test 3: Check session list
print("\n3. Checking session list...")
try:
    sessions = wx.GetSessionList()
    print(f"   ✓ Sessions: {sessions}")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 4: Try to add listen chat
print("\n4. Testing AddListenChat...")
try:
    # This might fail if WeChat isn't ready
    wx.AddListenChat(who="文件传输助手", savepic=True, savevoice=True)
    print("   ✓ AddListenChat succeeded")
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\n=== Test Complete ===\n")
