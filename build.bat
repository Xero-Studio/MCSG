@echo off
title MC服务器管理器 - Nuitka构建脚本 (Windows)

echo MC服务器管理器 - Nuitka构建脚本
echo =====================================

python --version
if errorlevel 1 (
    echo 错误: Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo 开始构建...
python build.py

if errorlevel 1 (
    echo.
    echo 构建失败！
    pause
    exit /b 1
) else (
    echo.
    echo 构建成功！
    echo 可执行文件位于 dist/ 目录下
    pause
)