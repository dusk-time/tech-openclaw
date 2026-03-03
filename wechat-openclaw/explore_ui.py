#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep UI Explorer for WeChat
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uiautomation as auto
except ImportError:
    print("pip install uiautomation")
    sys.exit(1)


def find_wechat():
    """Find WeChat window"""
    window = auto.WindowControl(searchDepth=2, Name="微信")
    if not window.Exists(5, 1):
        print("WeChat not found")
        return None
    print(f"Found window: {window.Name}")
    return window


def deep_explore(elem, max_depth=10, max_children=50, current_depth=0):
    """Explore UI tree deeply"""
    if current_depth > max_depth:
        return
    
    try:
        name = elem.Name or "(no name)"
        ctype = elem.ControlTypeName or "(unknown)"
        
        # Print this element
        prefix = "  " * current_depth
        print(f"{prefix}[{ctype}] {name[:60]}")
        
        # Get children
        try:
            children = list(elem.GetChildren())
            print(f"{prefix}  -> {len(children)} children")
            
            # Show first few children
            for i, child in enumerate(children[:max_children]):
                try:
                    cname = child.Name or "(no name)"
                    ctype = child.ControlTypeName or "(unknown)"
                    print(f"{prefix}  [{i}] [{ctype}] {cname[:50]}")
                except:
                    pass
            
            # Recurse into interesting elements
            for child in children[:5]:  # Only first 5
                try:
                    ctype = child.ControlTypeName or ""
                    cname = child.Name or ""
                    
                    # Follow into interesting controls
                    if any(x in ctype.lower() for x in ['edit', 'button', 'list', 'pane', 'custom']):
                        deep_explore(child, max_depth, max_children, current_depth + 1)
                except:
                    pass
                    
        except Exception as e:
            print(f"{prefix}  Error getting children: {e}")
            
    except Exception as e:
        pass


def find_input_box(window):
    """Find the chat input box"""
    print("\n=== Searching for Input Box ===\n")
    
    # Method 1: Search all edits
    print("Method 1: Finding all EditControls...")
    edits = window.EditControl()
    if isinstance(edits, list):
        print(f"Found {len(edits)} EditControls")
        for i, edit in enumerate(edits):
            try:
                print(f"  [{i}] {edit.Name[:50] if edit.Name else '(no name)'}")
                print(f"      Bounding: {edit.BoundingRectangle}")
            except:
                print(f"  [{i}] Error")
    else:
        print(f"Found 1 EditControl: {edits.Name if edits.Name else '(no name)'}")
    
    # Method 2: Search all buttons
    print("\nMethod 2: Finding all ButtonControls...")
    buttons = window.ButtonControl()
    if isinstance(buttons, list):
        print(f"Found {len(buttons)} ButtonControls")
        for i, btn in enumerate(buttons[:20]):
            try:
                print(f"  [{i}] {btn.Name[:40] if btn.Name else '(no name)'}")
            except:
                print(f"  [{i}] Error")
    else:
        print(f"Found 1 ButtonControl: {buttons.Name}")
    
    # Method 3: Search all panes
    print("\nMethod 3: Finding PaneControls...")
    panes = window.PaneControl()
    if isinstance(panes, list):
        print(f"Found {len(panes)} PaneControls")
        for i, pane in enumerate(panes[:15]):
            try:
                print(f"  [{i}] {pane.Name[:40] if pane.Name else '(no name)'}")
            except:
                print(f"  [{i}] Error")
    else:
        print(f"Found 1 PaneControl: {panes.Name}")


def find_chat_list(window):
    """Find chat list"""
    print("\n=== Searching for Chat List ===\n")
    
    # Look for list controls
    lists = window.ListControl()
    if isinstance(lists, list):
        print(f"Found {len(lists)} ListControls")
        for i, lst in enumerate(lists):
            try:
                print(f"  [{i}] {lst.Name[:50] if lst.Name else '(no name)'}")
                # Show first few items
                items = list(lst.GetChildren())[:5]
                print(f"      Items: {len(items)}")
                for item in items:
                    try:
                        print(f"        - {item.Name[:40] if item.Name else '(no name)'}")
                    except:
                        pass
            except:
                print(f"  [{i}] Error")
    else:
        print(f"Found 1 ListControl: {lists.Name if lists.Name else '(no name)'}")


def main():
    print("=== WeChat UI Deep Explorer ===\n")
    
    window = find_wechat()
    if not window:
        return
    
    print("\n=== UI Tree (first 3 levels) ===\n")
    deep_explore(window, max_depth=3, max_children=20, current_depth=0)
    
    find_chat_list(window)
    find_input_box(window)
    
    print("\n\n=== Complete ===")


if __name__ == "__main__":
    main()
