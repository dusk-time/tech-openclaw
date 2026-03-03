# WeChat Personal Channel Plugin for OpenClaw (已封存)

<div align="center">

[![OpenClaw](https://img.shields.io/badge/OpenClaw-WeChat-blue?style=for-the-badge)](https://openclaw.ai)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)]()

</div>

> ⚠️ **项目状态**: 已封存 - 微信 4.x 使用自定义渲染引擎，无法实现监听功能

## 📱 简介

这是一个 ~~OpenClaw~~ ~~工具~~ ~~使 OpenClaw 能够通过 **微信 PC 版** (Windows) 进行消息收发~~ **未完成的项目**。

**问题根源**: 微信 4.x 使用自定义渲染引擎 `MMUIRenderSubWindowHW`，不实现标准 UIAutomation 接口，导致所有 UI 自动化工具（wxauto、pywinauto、uiautomation）都无法访问内部控件。

## 🔴 封存原因

```
微信 4.x 窗口结构:
WeChat Window (Qt51514QWindowIcon)
  └── MMUIRenderSubWindowHW  ← 自定义渲染引擎，隐藏所有UI控件
       ├── 聊天列表 (不可访问)
       ├── 输入框 (不可访问)
       ├── 发送按钮 (不可访问)
       └── ... (所有控件都不可访问)
```

### 受影响的功能
- ❌ 监听/接收消息
- ❌ 自动回复
- ❌ 获取聊天列表
- ❌ 读取历史消息

### 可用的功能
- ✅ 发送消息（通过 pyautogui 模拟点击）
- ✅ 发送图片（通过 pyautogui 模拟点击）

## 📁 项目结构

```
wechat-openclaw/
├── README.md              # 本文档
├── send.py                # 发送消息脚本 (可用)
├── simple_send.py         # 简单发送脚本 (可用)
├── positions.json         # 校准后的点击坐标
├── wxautold_backup_20260220.tar.gz  # wxautold 备份
├── debug_ui.py            # UI 调试脚本
├── detailed_test.py       # 详细测试脚本
└── ...
```

## 🚀 使用方法 (仅发送功能)

```bash
# 确保微信已打开并登录
cd C:\Users\28054\.openclaw\workspace\wechat-openclaw

# 发送消息 (确保已校准位置)
python send.py "文件传输助手" "测试消息"

# 或使用简单版本
python simple_send.py "文件传输助手" "消息内容"
```

## 🔧 恢复方案 (如需完整功能)

### 方案 1: 降级微信 (推荐)
1. 卸载微信 4.x
2. 安装微信 3.9.10.x (百度搜索"微信历史版本")
3. 恢复原始 wxauto:
   ```bash
   copy F:\python\3.11.8\Lib\site-packages\wxauto\wxauto.py.bak F:\python\3.11.8\Lib\site-packages\wxauto\wxauto.py
   ```
4. 使用 KouriChat 项目 (F:\KouriChat-112) 获取完整功能

### 方案 2: 使用 KouriChat (完整替代方案)
```bash
cd F:\KouriChat-112
pip install -r requirements.txt
python run.py
```

## 📅 封存日期

**2026-02-20**

## 📝 更新日志

### v1.0.0 (2026-02-20) - 初始版本
- ✨ 初始版本
- ✅ 支持发送文本消息 (pyautogui 方案)
- ✅ 支持发送图片
- ❌ 监听功能 (因微信 4.x 限制无法实现)

### v1.0.1 (2026-02-20) - 已封存
- 🔴 发现微信 4.x 自定义渲染引擎限制
- 🔴 无法实现监听/接收功能
- 📦 项目封存

---

**许可证**: MIT
