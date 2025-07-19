#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Server Manager
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from qfluentwidgets import (FluentWindow, NavigationItemPosition, FluentIcon,
                           PushButton, LineEdit, SpinBox, CheckBox, TextEdit,
                           ComboBox, InfoBar, InfoBarPosition, MessageBox,
                           CardWidget, HeaderCardWidget, SimpleCardWidget,
                           StrongBodyLabel, BodyLabel, CaptionLabel)


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

class MainWindow(FluentWindow):
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
        self.resize(900, 700)
        
        # 创建导航界面
        self.server_interface = ServerInterface(self)
        self.config_interface = ConfigInterface(self)
        self.console_interface = ConsoleInterface(self)
        
        # 添加导航项
        self.addSubInterface(self.server_interface, FluentIcon.PLAY, "服务器控制")
        self.addSubInterface(self.config_interface, FluentIcon.SETTING, "服务器配置") 
        self.addSubInterface(self.console_interface, FluentIcon.COMMAND_PROMPT, "控制台")
        
        # 设置默认界面
        self.stackedWidget.setCurrentWidget(self.server_interface)
        
    def load_config(self):
        """加载配置到UI"""
        config = self.config_interface
        config.memory_edit.setText(self.manager.get_config_value('memory'))
        config.core_edit.setText(self.manager.get_config_value('core'))
        config.motd_edit.setText(self.manager.get_config_value('motd'))
        config.port_spin.setValue(int(self.manager.get_config_value('port')))
        config.max_players_spin.setValue(int(self.manager.get_config_value('max_players')))
        config.view_distance_spin.setValue(int(self.manager.get_config_value('view_distance')))
        config.online_mode_check.setChecked(self.manager.get_config_value('online_mode').lower() == 'true')
        config.jvm_args_edit.setText(self.manager.get_config_value('jvm_args'))
        config.server_args_edit.setText(self.manager.get_config_value('server_args'))
        config.seed_edit.setText(self.manager.get_config_value('level_seed'))
        
    def save_config(self):
        """保存配置"""
        config = self.config_interface
        self.manager.set_config_value('memory', config.memory_edit.text())
        self.manager.set_config_value('core', config.core_edit.text())
        self.manager.set_config_value('motd', config.motd_edit.text())
        self.manager.set_config_value('port', str(config.port_spin.value()))
        self.manager.set_config_value('max_players', str(config.max_players_spin.value()))
        self.manager.set_config_value('view_distance', str(config.view_distance_spin.value()))
        self.manager.set_config_value('online_mode', 'true' if config.online_mode_check.isChecked() else 'false')
        self.manager.set_config_value('jvm_args', config.jvm_args_edit.text())
        self.manager.set_config_value('server_args', config.server_args_edit.text())
        self.manager.set_config_value('level_seed', config.seed_edit.text())
        
        self.manager.save_config()
        
        InfoBar.success(
            title="保存成功",
            content="配置已保存！",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
        
    def browse_core(self):
        """浏览服务器核心文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择服务器核心文件", "", "JAR文件 (*.jar)"
        )
        if file_path:
            self.config_interface.core_edit.setText(os.path.basename(file_path))
            
    def start_server(self):
        """启动服务器"""
        core_file = self.config_interface.core_edit.text()
        if not os.path.exists(core_file):
            InfoBar.error(
                title="错误",
                content=f"服务器核心文件 '{core_file}' 不存在!",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            return
            
        # 保存当前配置
        self.save_config()
        
        # 启动服务器线程
        self.server_thread = ServerThread(self.manager)
        self.server_thread.output_signal.connect(self.append_console_output)
        self.server_thread.finished_signal.connect(self.server_finished)
        self.server_thread.start()
        
        # 更新UI状态
        self.server_interface.start_button.setEnabled(False)
        self.server_interface.stop_button.setEnabled(True)
        self.server_interface.status_label.setText("运行中")
        self.server_interface.status_label.setStyleSheet("color: green;")
        self.console_interface.send_command_button.setEnabled(True)
        
        # 切换到控制台界面
        self.stackedWidget.setCurrentWidget(self.console_interface)
        
    def stop_server(self):
        """停止服务器"""
        if self.server_thread:
            self.server_thread.stop_server()
            
    def server_finished(self):
        """服务器结束"""
        self.server_interface.start_button.setEnabled(True)
        self.server_interface.stop_button.setEnabled(False)
        self.server_interface.status_label.setText("未运行")
        self.server_interface.status_label.setStyleSheet("color: red;")
        self.console_interface.send_command_button.setEnabled(False)
        self.append_console_output("=== 服务器已停止 ===")
        
    def append_console_output(self, text):
        """添加控制台输出"""
        self.console_interface.console_output.append(text)
        # 自动滚动到底部
        scrollbar = self.console_interface.console_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class ServerInterface(QWidget):
    """服务器控制界面"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 状态卡片
        self.status_card = HeaderCardWidget(self)
        self.status_card.setTitle("服务器状态")
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(BodyLabel("当前状态:"))
        self.status_label = StrongBodyLabel("未运行")
        self.status_label.setStyleSheet("color: red;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.status_card.viewLayout.addLayout(status_layout)
        layout.addWidget(self.status_card)
        
        # 控制按钮卡片
        control_card = SimpleCardWidget(self)
        control_layout = QHBoxLayout(control_card)
        
        self.start_button = PushButton("启动服务器", self)
        self.start_button.setIcon(FluentIcon.PLAY)
        self.stop_button = PushButton("停止服务器", self)
        self.stop_button.setIcon(FluentIcon.PAUSE)
        self.stop_button.setEnabled(False)
        
        self.start_button.clicked.connect(self.parent.start_server)
        self.stop_button.clicked.connect(self.parent.stop_server)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        
        layout.addWidget(control_card)
        layout.addStretch()
        
class ConfigInterface(QWidget):
    """配置界面"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 基本配置卡片
        basic_card = HeaderCardWidget(self)
        basic_card.setTitle("基本配置")
        
        basic_layout = QGridLayout()
        
        # 内存配置
        basic_layout.addWidget(BodyLabel("内存分配:"), 0, 0)
        self.memory_edit = LineEdit(self)
        self.memory_edit.setPlaceholderText("例如: 2G, 4G")
        basic_layout.addWidget(self.memory_edit, 0, 1)
        
        # 服务器核心
        basic_layout.addWidget(BodyLabel("服务器核心:"), 1, 0)
        core_layout = QHBoxLayout()
        self.core_edit = LineEdit(self)
        self.browse_core_button = PushButton("浏览", self)
        self.browse_core_button.setIcon(FluentIcon.FOLDER)
        self.browse_core_button.clicked.connect(self.parent.browse_core)
        core_layout.addWidget(self.core_edit)
        core_layout.addWidget(self.browse_core_button)
        basic_layout.addLayout(core_layout, 1, 1)
        
        basic_card.viewLayout.addLayout(basic_layout)
        layout.addWidget(basic_card)
        
        # 服务器配置卡片
        server_card = HeaderCardWidget(self)
        server_card.setTitle("服务器配置")
        
        server_layout = QGridLayout()
        
        # MOTD
        server_layout.addWidget(BodyLabel("MOTD描述:"), 0, 0)
        self.motd_edit = LineEdit(self)
        self.motd_edit.setPlaceholderText("支持中文，如：欢迎来到我的服务器！")
        server_layout.addWidget(self.motd_edit, 0, 1)
        
        # 端口
        server_layout.addWidget(BodyLabel("服务器端口:"), 1, 0)
        self.port_spin = SpinBox(self)
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(25565)
        server_layout.addWidget(self.port_spin, 1, 1)
        
        # 最大玩家数
        server_layout.addWidget(BodyLabel("最大玩家数:"), 2, 0)
        self.max_players_spin = SpinBox(self)
        self.max_players_spin.setRange(1, 1000)
        self.max_players_spin.setValue(20)
        server_layout.addWidget(self.max_players_spin, 2, 1)
        
        # 视距
        server_layout.addWidget(BodyLabel("视距:"), 3, 0)
        self.view_distance_spin = SpinBox(self)
        self.view_distance_spin.setRange(4, 32)
        self.view_distance_spin.setValue(10)
        server_layout.addWidget(self.view_distance_spin, 3, 1)
        
        # 正版验证
        self.online_mode_check = CheckBox("启用正版验证", self)
        self.online_mode_check.setChecked(True)
        server_layout.addWidget(self.online_mode_check, 4, 0, 1, 2)
        
        server_card.viewLayout.addLayout(server_layout)
        layout.addWidget(server_card)
        
        # 高级配置卡片
        advanced_card = HeaderCardWidget(self)
        advanced_card.setTitle("高级配置")
        
        advanced_layout = QGridLayout()
        
        # JVM参数
        advanced_layout.addWidget(BodyLabel("JVM参数:"), 0, 0)
        self.jvm_args_edit = LineEdit(self)
        self.jvm_args_edit.setPlaceholderText("-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions")
        advanced_layout.addWidget(self.jvm_args_edit, 0, 1)
        
        # 服务器参数
        advanced_layout.addWidget(BodyLabel("服务器参数:"), 1, 0)
        self.server_args_edit = LineEdit(self)
        self.server_args_edit.setPlaceholderText("nogui")
        advanced_layout.addWidget(self.server_args_edit, 1, 1)
        
        # 世界种子
        advanced_layout.addWidget(BodyLabel("世界种子:"), 2, 0)
        self.seed_edit = LineEdit(self)
        advanced_layout.addWidget(self.seed_edit, 2, 1)
        
        advanced_card.viewLayout.addLayout(advanced_layout)
        layout.addWidget(advanced_card)
        
        # 保存按钮
        save_button = PushButton("保存配置", self)
        save_button.setIcon(FluentIcon.SAVE)
        save_button.clicked.connect(self.parent.save_config)
        layout.addWidget(save_button)
        
        layout.addStretch()
        
class ConsoleInterface(QWidget):
    """控制台界面"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 控制台卡片
        console_card = HeaderCardWidget(self)
        console_card.setTitle("服务器控制台")
        
        console_layout = QVBoxLayout()
        
        # 控制台输出
        self.console_output = TextEdit(self)
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 9))
        console_layout.addWidget(self.console_output)
        
        # 命令输入
        command_layout = QHBoxLayout()
        self.command_input = LineEdit(self)
        self.command_input.setPlaceholderText("输入服务器命令...")
        self.send_command_button = PushButton("发送", self)
        self.send_command_button.setIcon(FluentIcon.SEND)
        self.send_command_button.setEnabled(False)
        
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_command_button)
        console_layout.addLayout(command_layout)
        
        console_card.viewLayout.addLayout(console_layout)
        layout.addWidget(console_card)

def main():
    """主函数"""
    # 启用高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("MC Server Manager")
    
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"GUI启动失败: {e}")
        print("尝试启动命令行版本...")
        from mc_server_manager import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()