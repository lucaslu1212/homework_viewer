@echo off
chcp 65001 > nul
title 作业查看器系统 - EXE打包工具

echo ========================================
echo     作业查看器系统 - EXE打包工具
echo ========================================
echo.
echo 正在安装依赖包...
echo.

pip install pyinstaller

echo.
echo 正在开始打包...
echo.

python build_exe.py

echo.
echo 打包完成！
echo.
echo 按任意键退出...
pause > nul