#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Server Manager 启动脚本
Windows GUI版本
"""

import sys
import os

def main():
    """主启动函数"""
    try:
        # 尝试启动GUI版本
        from gui_main import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"GUI依赖缺失: {e}")
        print("正在启动命令行版本...")
        # 回退到命令行版本
        from mc_server_manager import main as cli_main
        cli_main()
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()