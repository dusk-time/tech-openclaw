#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple uiautomation test
"""

import sys
import uiautomation as auto

print("=== uiautomation Test ===")
print(f"Python: {sys.version}")

# Find WeChat
print("\nSearching for WeChat...")
window = auto.WindowControl(searchDepth=2, Name="微信")

if window.Exists(3, 1):
    print("OK Found WeChat!")
    print(f"Window: {window.Name}")
    print(f"ControlType: {window.ControlTypeName}")
    
    # Try to explore children
    print("\nExploring UI structure...")
    children = list(window.GetChildren())[:5]
    print(f"Found {len(list(window.GetChildren()))} children")
    
    for i, child in enumerate(children):
        try:
            print(f"  [{i}] {child.ControlTypeName}: {child.Name[:30] if child.Name else '(no name)'}")
        except:
            print(f"  [{i}] Error getting child info")
else:
    print("WeChat not found! Make sure WeChat is open.")
