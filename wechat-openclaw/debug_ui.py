#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug WeChat 4.x UI structure with uiautomation
"""

import sys
sys.path.insert(0, r'F:\python\3.11.8\Lib\site-packages\wxauto')

import uiautomation as uia
import time

def print_control_tree(control, depth=0, max_depth=5):
    """Print control tree"""
    if depth > max_depth:
        return
    
    indent = "  " * depth
    try:
        name = control.Name if hasattr(control, 'Name') else 'NoName'
        class_name = control.ClassName if hasattr(control, 'ClassName') else 'NoClass'
        control_type = control.ControlType if hasattr(control, 'ControlType') else 'NoType'
        
        print("{}[{}] {} (Class: {}, Type: {})".format(
            indent, depth, name[:30], class_name[:20], str(control_type)
        ))
        
        # Get children
        try:
            children = control.GetChildren()
            for child in children[:10]:  # Limit children
                print_control_tree(child, depth + 1, max_depth)
            if len(children) > 10:
                print("{}  ... and {} more".format(indent, len(children) - 10))
        except:
            pass
    except Exception as e:
        print("{}Error: {}".format(indent, e))

def main():
    print("=== WeChat 4.x UI Structure Debug ===\n")
    
    # Find WeChat window
    print("Step 1: Finding WeChat window...")
    window = uia.WindowControl(Name='微信', searchDepth=2)
    
    if not window.Exists(3, 1):
        print("✗ Window '微信' not found!")
        
        # Try with ClassName
        print("\nTrying with ClassName...")
        window = uia.WindowControl(ClassName='Qt51514QWindowIcon', searchDepth=2)
        
        if not window.Exists(3, 1):
            print("✗ Window not found with ClassName either!")
            return
        else:
            print("✓ Found window with ClassName")
    else:
        print("✓ Found window with Name")
    
    print("\nWindow Info:")
    print("  Name: {}".format(window.Name))
    print("  ClassName: {}".format(window.ClassName))
    print("  ControlType: {}".format(window.ControlType))
    print("  BoundingRectangle: {}".format(window.BoundingRectangle))
    
    print("\n" + "=" * 50)
    print("UI Control Tree (depth 0-3):")
    print("=" * 50)
    
    print_control_tree(window, 0, 3)
    
    print("\n" + "=" * 50)
    print("Trying to find specific controls:")
    print("=" * 50)
    
    # Try to find chat list
    try:
        chat_list = window.ListControl(Name='消息')
        if chat_list.Exists(1, 0.5):
            print("✓ Found ListControl '消息'")
        else:
            print("✗ ListControl '消息' not found")
    except Exception as e:
        print("✗ Error finding list: {}".format(e))
    
    # Try to find edit control
    try:
        edit = window.EditControl()
        if edit.Exists(1, 0.5):
            print("✓ Found EditControl")
        else:
            print("✗ EditControl not found")
    except Exception as e:
        print("✗ Error finding edit: {}".format(e))
    
    # Try button controls
    try:
        buttons = window.GetChildren()
        button_controls = [c for c in buttons if 'Button' in str(c.ControlType)]
        print("\nFound {} Button-like controls".format(len(button_controls)))
        for btn in button_controls[:5]:
            print("  - {}".format(btn.Name))
    except Exception as e:
        print("✗ Error finding buttons: {}".format(e))

if __name__ == "__main__":
    main()
