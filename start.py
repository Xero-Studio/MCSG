#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Server Manager - 启动程序
"""

import sys
import os


def check_dependencies():
    """检查依赖"""
    missing_deps = []
    
    try:
        import PyQt5
    except ImportError:
        missing_deps.append("PyQt5")
    
    try:
        import qfluentwidgets
    except ImportError:
        missing_deps.append("qfluentwidgets")
    
    return missing_deps


def main():
    """主启动函数"""
    print("Minecraft Server Manager 启动中...")
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"缺少依赖: {', '.join(missing)}")
        print("请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        input("按回车键退出...")
        return
    
    try:
        # 启动GUI版本
        print("启动GUI界面...")
        from gui_main import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"GUI依赖导入失败: {e}")
        print("启动命令行版本...")
        from mc_server_manager import main as cli_main
        cli_main()
        
    except Exception as e:
        print(f"GUI启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键查看详细错误信息...")


if __name__ == "__main__":
    main()