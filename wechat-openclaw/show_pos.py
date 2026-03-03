import pyautogui
import json
import time

print("=== 快速校准 ===\n")

# 获取微信窗口位置
import pygetwindow as gw

windows = gw.getWindowsWithTitle("微信")
if not windows:
    print("✗ 没找到微信窗口")
    exit()

win = windows[0]
win.activate()
left, top, right, bottom = win.left, win.top, win.right, win.bottom
width = right - left
height = bottom - top

print(f"微信窗口: {width}x{height}")
print(f"左上角: ({left}, {top})\n")

print("请手动操作：")
print("1. 把鼠标移到输入框中间")
print("2. 读取鼠标坐标（看屏幕或任务管理器）")
print("\n然后把坐标发给我，我来帮你算！\n")

# 实时显示鼠标位置
try:
    print("实时鼠标位置（Ctrl+C 退出）:\n")
    while True:
        x, y = pyautogui.position()
        rel_x = x - left
        rel_y = y - top
        
        # 检查是否在窗口内
        if left < x < right and top < y < bottom:
            pct_x = rel_x / width * 100
            pct_y = rel_y / height * 100
            print(f"\r绝对: ({x:4d}, {y:4d}) | 相对: ({rel_x:4d}, {rel_y:4d}) | 百分比: ({pct_x:5.1f}%, {pct_y:5.1f}%)     ", end="", flush=True)
        else:
            print(f"\r绝对: ({x:4d}, {y:4d}) | 鼠标在窗口外                                             ", end="", flush=True)
        
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n退出")
