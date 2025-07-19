#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Server Manager
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QComboBox, QSpinBox,
                             QCheckBox, QGroupBox, QTabWidget, QMessageBox,
                             QFileDialog, QProgressBar, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap


from mc_server_manager import MinecraftServerManager
import subprocess
import threading

class ServerThread(QThread):
    """服务器运行线程"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.process = None
        
    def run(self):
        """运行服务器"""
        memory = self.manager.get_config_value('memory')
        core = self.manager.get_config_value('core')
        jvm_args = self.manager.get_config_value('jvm_args')
        server_args = self.manager.get_config_value('server_args')
        
        # 检查核心文件
        if not os.path.exists(core):
            self.output_signal.emit(f"错误: 服务器核心文件 '{core}' 不存在!")
            self.finished_signal.emit()
            return
        
        # 创建server.properties
        self.manager.create_properties()
        
        # 构建命令
        cmd = ['java', f'-Xms{memory}', f'-Xmx{memory}']
        if jvm_args:
            cmd.extend(jvm_args.split())
        cmd.extend(['-jar', core])
        if server_args:
            cmd.extend(server_args.split())
        
        try:
            self.output_signal.emit(f"启动命令: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 读取输出
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.output_signal.emit(line.strip())
                    
        except Exception as e:
            self.output_signal.emit(f"启动失败: {e}")
        finally:
            self.finished_signal.emit()
    
    def stop_server(self):
        """停止服务器"""
        if self.process:
            self.process.terminate()

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.manager = MinecraftServerManager()
        self.server_thread = None
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Minecraft Server Manager")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置图标（如果有的话）
        # self.setWindowIcon(QIcon('icon.ico'))
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_server_tab()
        self.create_config_tab()
        self.create_console_tab()
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def create_server_tab(self):
        """创建服务器控制标签页"""
        server_widget = QWidget()
        layout = QVBoxLayout(server_widget)
        
        # 服务器状态组
        status_group = QGroupBox("服务器状态")
        status_layout = QGridLayout(status_group)
        
        self.status_label = QLabel("未运行")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(QLabel("状态:"), 0, 0)
        status_layout.addWidget(self.status_label, 0, 1)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("启动服务器")
        self.stop_button = QPushButton("停止服务器")
        self.stop_button.setEnabled(False)
        
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        
        layout.addWidget(status_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(server_widget, "服务器控制")
        
    def create_config_tab(self):
        """创建配置标签页"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # 创建滚动区域
        scroll_layout = QGridLayout()
        
        # 基本配置
        basic_group = QGroupBox("基本配置")
        basic_layout = QGridLayout(basic_group)
        
        # 内存配置
        basic_layout.addWidget(QLabel("内存分配:"), 0, 0)
        self.memory_edit = QLineEdit()
        basic_layout.addWidget(self.memory_edit, 0, 1)
        
        # 服务器核心
        basic_layout.addWidget(QLabel("服务器核心:"), 1, 0)
        core_layout = QHBoxLayout()
        self.core_edit = QLineEdit()
        self.browse_core_button = QPushButton("浏览...")
        self.browse_core_button.clicked.connect(self.browse_core)
        core_layout.addWidget(self.core_edit)
        core_layout.addWidget(self.browse_core_button)
        basic_layout.addLayout(core_layout, 1, 1)
        
        # 服务器配置
        server_group = QGroupBox("服务器配置")
        server_layout = QGridLayout(server_group)
        
        # MOTD
        server_layout.addWidget(QLabel("MOTD描述:"), 0, 0)
        self.motd_edit = QLineEdit()
        self.motd_edit.setPlaceholderText("支持中文，如：欢迎来到我的服务器！")
        server_layout.addWidget(self.motd_edit, 0, 1)
        
        # 端口
        server_layout.addWidget(QLabel("服务器端口:"), 1, 0)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(25565)
        server_layout.addWidget(self.port_spin, 1, 1)
        
        # 最大玩家数
        server_layout.addWidget(QLabel("最大玩家数:"), 2, 0)
        self.max_players_spin = QSpinBox()
        self.max_players_spin.setRange(1, 1000)
        self.max_players_spin.setValue(20)
        server_layout.addWidget(self.max_players_spin, 2, 1)
        
        # 视距
        server_layout.addWidget(QLabel("视距:"), 3, 0)
        self.view_distance_spin = QSpinBox()
        self.view_distance_spin.setRange(4, 32)
        self.view_distance_spin.setValue(10)
        server_layout.addWidget(self.view_distance_spin, 3, 1)
        
        # 正版验证
        self.online_mode_check = QCheckBox("启用正版验证")
        self.online_mode_check.setChecked(True)
        server_layout.addWidget(self.online_mode_check, 4, 0, 1, 2)
        
        # 高级配置
        advanced_group = QGroupBox("高级配置")
        advanced_layout = QGridLayout(advanced_group)
        
        # JVM参数
        advanced_layout.addWidget(QLabel("JVM参数:"), 0, 0)
        self.jvm_args_edit = QLineEdit()
        self.jvm_args_edit.setPlaceholderText("-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions")
        advanced_layout.addWidget(self.jvm_args_edit, 0, 1)
        
        # 服务器参数
        advanced_layout.addWidget(QLabel("服务器参数:"), 1, 0)
        self.server_args_edit = QLineEdit()
        self.server_args_edit.setPlaceholderText("nogui")
        advanced_layout.addWidget(self.server_args_edit, 1, 1)
        
        # 世界种子
        advanced_layout.addWidget(QLabel("世界种子:"), 2, 0)
        self.seed_edit = QLineEdit()
        advanced_layout.addWidget(self.seed_edit, 2, 1)
        
        # 保存按钮
        save_button = QPushButton("保存配置")
        save_button.clicked.connect(self.save_config)
        
        layout.addWidget(basic_group)
        layout.addWidget(server_group)
        layout.addWidget(advanced_group)
        layout.addWidget(save_button)
        layout.addStretch()
        
        self.tab_widget.addTab(config_widget, "服务器配置")
        
    def create_console_tab(self):
        """创建控制台标签页"""
        console_widget = QWidget()
        layout = QVBoxLayout(console_widget)
        
        # 控制台输出
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 9))
        layout.addWidget(self.console_output)
        
        # 命令输入
        command_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("输入服务器命令...")
        self.send_command_button = QPushButton("发送")
        self.send_command_button.setEnabled(False)
        
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_command_button)
        
        layout.addLayout(command_layout)
        
        self.tab_widget.addTab(console_widget, "控制台")
        
    def load_config(self):
        """加载配置到UI"""
        self.memory_edit.setText(self.manager.get_config_value('memory'))
        self.core_edit.setText(self.manager.get_config_value('core'))
        self.motd_edit.setText(self.manager.get_config_value('motd'))
        self.port_spin.setValue(int(self.manager.get_config_value('port')))
        self.max_players_spin.setValue(int(self.manager.get_config_value('max_players')))
        self.view_distance_spin.setValue(int(self.manager.get_config_value('view_distance')))
        self.online_mode_check.setChecked(self.manager.get_config_value('online_mode').lower() == 'true')
        self.jvm_args_edit.setText(self.manager.get_config_value('jvm_args'))
        self.server_args_edit.setText(self.manager.get_config_value('server_args'))
        self.seed_edit.setText(self.manager.get_config_value('level_seed'))
        
    def save_config(self):
        """保存配置"""
        self.manager.set_config_value('memory', self.memory_edit.text())
        self.manager.set_config_value('core', self.core_edit.text())
        self.manager.set_config_value('motd', self.motd_edit.text())
        self.manager.set_config_value('port', str(self.port_spin.value()))
        self.manager.set_config_value('max_players', str(self.max_players_spin.value()))
        self.manager.set_config_value('view_distance', str(self.view_distance_spin.value()))
        self.manager.set_config_value('online_mode', 'true' if self.online_mode_check.isChecked() else 'false')
        self.manager.set_config_value('jvm_args', self.jvm_args_edit.text())
        self.manager.set_config_value('server_args', self.server_args_edit.text())
        self.manager.set_config_value('level_seed', self.seed_edit.text())
        
        self.manager.save_config()
        
        QMessageBox.information(self, "保存成功", "配置已保存！")
        self.statusBar().showMessage("配置已保存", 3000)
        
    def browse_core(self):
        """浏览服务器核心文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择服务器核心文件", "", "JAR文件 (*.jar)"
        )
        if file_path:
            self.core_edit.setText(os.path.basename(file_path))
            
    def start_server(self):
        """启动服务器"""
        if not os.path.exists(self.core_edit.text()):
            QMessageBox.warning(self, "错误", f"服务器核心文件 '{self.core_edit.text()}' 不存在!")
            return
            
        # 保存当前配置
        self.save_config()
        
        # 启动服务器线程
        self.server_thread = ServerThread(self.manager)
        self.server_thread.output_signal.connect(self.append_console_output)
        self.server_thread.finished_signal.connect(self.server_finished)
        self.server_thread.start()
        
        # 更新UI状态
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("运行中")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.send_command_button.setEnabled(True)
        self.statusBar().showMessage("服务器正在运行...")
        
        # 切换到控制台标签
        self.tab_widget.setCurrentIndex(2)
        
    def stop_server(self):
        """停止服务器"""
        if self.server_thread:
            self.server_thread.stop_server()
            
    def server_finished(self):
        """服务器结束"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("未运行")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.send_command_button.setEnabled(False)
        self.statusBar().showMessage("服务器已停止")
        self.append_console_output("=== 服务器已停止 ===")
        
    def append_console_output(self, text):
        """添加控制台输出"""
        self.console_output.append(text)
        # 自动滚动到底部
        scrollbar = self.console_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("MC Server Manager")
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()