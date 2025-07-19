#!/bin/bash
# MC服务器管理器 - Nuitka构建脚本 (Linux/macOS)

echo "MC服务器管理器 - Nuitka构建脚本"
echo "====================================="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3未安装"
    exit 1
fi

python3 --version

echo ""
echo "开始构建..."
python3 build.py

if [ $? -eq 0 ]; then
    echo ""
    echo "构建成功！"
    echo "可执行文件位于 dist/ 目录下"
else
    echo ""
    echo "构建失败！"
    exit 1
fi