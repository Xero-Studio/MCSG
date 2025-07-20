#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Server Manager
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
        print(f"GUI启动失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n正在启动命令行版本...")
        # 回退到命令行版本
        from mc_server_manager import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()