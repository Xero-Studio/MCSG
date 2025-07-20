#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的GUI测试程序
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

def test_basic_gui():
    """测试基本GUI功能"""
    print("开始测试基本GUI...")
    
    try:
        # 创建应用程序
        app = QApplication(sys.argv)
        print("QApplication 创建成功")
        
        # 创建简单窗口
        window = QWidget()
        window.setWindowTitle("MC Server Manager - 测试")
        window.resize(400, 300)
        window.move(100, 100)
        
        # 添加内容
        layout = QVBoxLayout()
        
        label = QLabel("Minecraft Server Manager")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        status_label = QLabel("GUI测试成功！程序可以正常显示界面。")
        status_label.setAlignment(Qt.AlignCenter)
        
        test_button = QPushButton("测试按钮")
        test_button.clicked.connect(lambda: print("按钮点击测试成功"))
        
        layout.addWidget(label)
        layout.addWidget(status_label)
        layout.addWidget(test_button)
        
        window.setLayout(layout)
        
        print("窗口创建成功")
        
        # 显示窗口
        window.show()
        window.raise_()
        window.activateWindow()
        
        print("窗口显示成功，进入事件循环")
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"GUI测试失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

def test_qfluentwidgets():
    """测试qfluentwidgets导入"""
    print("测试qfluentwidgets导入...")
    
    try:
        from qfluentwidgets import FluentWindow, PushButton, BodyLabel
        print("✓ qfluentwidgets 导入成功")
        
        app = QApplication(sys.argv)
        
        window = FluentWindow()
        window.setWindowTitle("MC Server Manager - Fluent测试")
        window.resize(500, 400)
        
        # 创建中央widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        title_label = BodyLabel("Fluent Design 测试")
        title_label.setStyleSheet("font-size: 16px;")
        
        fluent_button = PushButton("Fluent按钮")
        fluent_button.clicked.connect(lambda: print("Fluent按钮点击成功"))
        
        layout.addWidget(title_label)
        layout.addWidget(fluent_button)
        
        window.setCentralWidget(central_widget)
        window.show()
        
        print("Fluent窗口显示成功")
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"✗ qfluentwidgets 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ Fluent测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== MC Server Manager GUI 诊断工具 ===")
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "fluent":
        test_qfluentwidgets()
    else:
        test_basic_gui()