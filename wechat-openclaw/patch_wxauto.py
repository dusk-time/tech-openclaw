#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wxauto Patch for WeChat 4.x
Fixes FindWindow to work with Qt-based WeChat 4.x
"""

import sys
import os
import shutil

# Backup original
original = r'F:\python\3.11.8\Lib\site-packages\wxauto\wxauto.py'
backup = original + '.bak'

if not os.path.exists(backup):
    shutil.copy(original, backup)
    print("[OK] Backup created: {}".format(backup))

# Read original content
with open(original, 'r', encoding='utf-8') as f:
    content = f.read()

# Create patched content
# Fix 1: FindWindow('WeChatMainWndForPC') -> FindWindow(None, '微信')
content = content.replace(
    "FindWindow(classname='WeChatMainWndForPC')",
    "FindWindow(None, '微信')"
)

# Fix 2: ClassName='WeChatMainWndForPC' -> Name='微信'
content = content.replace(
    "uia.WindowControl(ClassName='WeChatMainWndForPC', searchDepth=1)",
    "uia.WindowControl(Name='微信', searchDepth=2)"
)

# Write patched content
with open(original, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Patched wxauto for WeChat 4.x")
print("\nChanges made:")
print("  1. FindWindow('WeChatMainWndForPC') -> FindWindow(None, '微信')")
print("  2. ClassName='WeChatMainWndForPC' -> Name='微信'")
print("\nOriginal backed up to: {}".format(backup))
print("To restore: copy {} back to {}".format(backup, original))
