@echo off
echo ========================================
echo 创建 docx Skill 符号链接
echo ========================================

echo.
echo 正在创建符号链接...
echo.

mklink /D "C:\Users\28054\AppData\Roaming\npm\node_modules\openclaw\skills\docx" "F:\skills-main\skills-main\skills\docx"

echo.
echo ========================================
echo 完成！
echo.
echo docx Skill 已链接到 OpenClaw
echo.
echo 现在可以用 Skill 了！
echo.
echo 按任意键退出...
pause >nul
