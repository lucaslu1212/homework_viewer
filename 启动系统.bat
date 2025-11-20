@echo off
chcp 65001 > nul
echo ========================================
echo      作业查看器系统启动器
echo ========================================
echo.

python launcher.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查Python环境
    echo.
    pause
)