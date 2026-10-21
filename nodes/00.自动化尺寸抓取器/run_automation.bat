@echo off
chcp 65001 > nul
echo 正在启动 OpenClaw ChatGPT 自动化脚本...
echo 请确保：
echo 1. OpenClaw 浏览器中的 ChatGPT 已经登录
echo 2. 不要移动鼠标或操作键盘直到脚本完成
echo.
pause

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_from_config.ps1" %*

echo.
echo 脚本执行完成！
pause
