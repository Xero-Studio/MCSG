#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试启动脚本
"""

import sys
import os

def check_dependencies():
    """检查依赖"""
    print("=== 依赖检查 ===")
    
    missing = []
    
    try:
        import PyQt5
        print(f"✓ PyQt5: {PyQt5.QtCore.PYQT_VERSION_STR}")
    except ImportError as e:
        print(f"✗ PyQt5: {e}")
        missing.append("PyQt5")
    
    try:
        import qfluentwidgets
        print(f"✓ qfluentwidgets")
    except ImportError as e:
        print(f"✗ qfluentwidgets: {e}")
        missing.append("qfluentwidgets")
    
    try:
        import psutil
        print(f"✓ psutil")
    except ImportError as e:
        print(f"✗ psutil: {e}")
        missing.append("psutil")
    
    return missing

def test_basic_imports():
    """测试基本导入"""
    print("\n=== 基本导入测试 ===")
    
    try:
        from PyQt5.QtWidgets import QApplication, QWidget
        from PyQt5.QtCore import Qt
        print("✓ PyQt5 基础组件导入成功")
    except Exception as e:
        print(f"✗ PyQt5 基础组件导入失败: {e}")
        return False
    
    try:
        from qfluentwidgets import FluentWindow, PushButton
        print("✓ qfluentwidgets 基础组件导入成功")
    except Exception as e:
        print(f"✗ qfluentwidgets 基础组件导入失败: {e}")
        return False
    
    return True

def test_gui_creation():
    """测试GUI创建"""
    print("\n=== GUI创建测试 ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication([])
        print("✓ QApplication 创建成功")
        
        from qfluentwidgets import FluentWindow
        window = FluentWindow()
        print("✓ FluentWindow 创建成功")
        
        window.setWindowTitle("测试窗口")
        window.resize(400, 300)
        print("✓ 窗口配置成功")
        
        return True
        
    except Exception as e:
        print(f"✗ GUI创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("MC Server Manager 启动诊断工具")
    print("=" * 50)
    
    # 检查依赖
    missing = check_dependencies()
    if missing:
        print(f"\n❌ 缺少依赖: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        input("按回车键退出...")
        return
    
    # 测试导入
    if not test_basic_imports():
        print("\n❌ 基本导入测试失败")
        input("按回车键退出...")
        return
    
    # 测试GUI创建
    if not test_gui_creation():
        print("\n❌ GUI创建测试失败")
        input("按回车键退出...")
        return
    
    print("\n✅ 所有测试通过！")
    print("\n现在尝试启动完整程序...")
    
    try:
        # 尝试启动完整程序
        print("导入主程序模块...")
        
        # 逐步导入检查
        from mc_server_manager import MinecraftServerManager
        print("✓ mc_server_manager 导入成功")
        
        from multi_server_manager import MultiServerManager
        print("✓ multi_server_manager 导入成功")
        
        from server_template import ServerTemplateManager
        print("✓ server_template 导入成功")
        
        from backup_manager import BackupManager
        print("✓ backup_manager 导入成功")
        
        from plugin_manager import PluginManager
        print("✓ plugin_manager 导入成功")
        
        from performance_monitor import PerformanceMonitor
        print("✓ performance_monitor 导入成功")
        
        from player_manager import PlayerManager
        print("✓ player_manager 导入成功")
        
        print("\n所有模块导入成功！启动GUI...")
        
        # 启动简化版GUI
        from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
        from qfluentwidgets import FluentWindow, BodyLabel, PushButton as FluentButton
        
        app = QApplication(sys.argv)
        
        window = FluentWindow()
        window.setWindowTitle("MC Server Manager - 启动成功")
        window.resize(500, 400)
        window.move(100, 100)
        
        # 创建内容
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        title = BodyLabel("🎉 MC Server Manager")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        
        status = BodyLabel("程序启动成功！所有模块加载正常。")
        status.setStyleSheet("font-size: 14px; color: #107c10;")
        
        info = BodyLabel("如果您看到这个窗口，说明程序可以正常运行。\n原始程序可能在初始化时遇到了问题。")
        info.setStyleSheet("font-size: 12px; color: #666666;")
        
        start_button = FluentButton("启动完整程序")
        start_button.clicked.connect(lambda: start_full_program())
        
        layout.addWidget(title)
        layout.addWidget(status)
        layout.addWidget(info)
        layout.addWidget(start_button)
        layout.addStretch()
        
        window.setCentralWidget(central_widget)
        window.show()
        window.raise_()
        window.activateWindow()
        
        print("✅ 简化版GUI启动成功！")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"\n❌ 程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

def start_full_program():
    """启动完整程序"""
    print("尝试启动完整程序...")
    try:
        from gui_main import main as gui_main
        gui_main()
    except Exception as e:
        print(f"完整程序启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()