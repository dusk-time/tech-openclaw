@echo off
echo ========================================
echo OpenClaw Skill 符号链接创建脚本
echo ========================================

echo.
echo 正在创建符号链接...
echo.

mklink /D "C:\Users\28054\AppData\Roaming\npm\node_modules\openclaw\skills\我的技能" "F:\OpenClaw-Skills"

echo.
echo ========================================
echo 完成！
echo.
echo 你的Skill应放在: F:\OpenClaw-Skills
echo 链接到: OpenClaw skills目录
echo.
echo 按任意键退出...
pause >nul
