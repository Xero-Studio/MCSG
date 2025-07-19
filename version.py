#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本信息
"""

__version__ = "2.0.0"
__author__ = "PowerCMD"
__description__ = "Minecraft Server Manager - Python版本"
__license__ = "GPL-3.0"

# 版本历史
VERSION_HISTORY = {
    "2.0.0": "Python重写版本，支持跨平台，添加Nuitka构建支持",
    "1.x.x": "原始批处理版本（已移至old/文件夹）"
}

def get_version_info():
    """获取版本信息"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "license": __license__
    }

if __name__ == "__main__":
    info = get_version_info()
    print(f"{info['description']} v{info['version']}")
    print(f"作者: {info['author']}")
    print(f"许可证: {info['license']}")