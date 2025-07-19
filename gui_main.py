#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Server Manager - GUI界面
"""

import sys
import os
import threading
import time
from typing import Optional

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon,
    PushButton, LineEdit, SpinBox, CheckBox, TextEdit,
    ComboBox, InfoBar, InfoBarPosition,
    HeaderCardWidget, SimpleCardWidget,
    StrongBodyLabel, BodyLabel, setTheme, Theme
)

from mc_server_manager import MinecraftServerManager


class ServerOutputThread(QThread):
    """服务器输出监控线程"""
    output_received = pyqtSignal(str)
    
    def __init__(self, manager: MinecraftServerManager):
        super().__init__()
        self.manager = manager
        self.running = False
    
    def run(self):
        """监控服务器输出"""
        self.running = True
        while self.running and self.manager.is_server_running():
            output = self.manager.read_server_output()
            if output:
                self.output_received.emit(output.strip())
            else:
                time.sleep(0.1)
    
    def stop(self):
        """停止监控"""
        self.running = False


class MainWindow(FluentWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.manager = MinecraftServerManager()
        self.output_thread: Optional[ServerOutputThread] = None
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_server_status)
        self.status_timer.start(1000)  # 每秒更新一次状态
        
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Minecraft Server Manager")
        self.resize(1000, 700)
        
        # 创建界面
        self.server_interface = ServerInterface(self)
        self.config_interface = ConfigInterface(self)
        self.console_interface = ConsoleInterface(self)
        
        # 添加到导航
        self.addSubInterface(
            self.server_interface, 
            FluentIcon.PLAY, 
            "服务器控制",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.config_interface, 
            FluentIcon.SETTING, 
            "服务器配置",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.console_interface, 
            FluentIcon.COMMAND_PROMPT, 
            "控制台",
            NavigationItemPosition.TOP
        )
        
        # 设置默认界面
        self.stackedWidget.setCurrentWidget(self.server_interface)
    
    def load_config(self):
        """加载配置到界面"""
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
        
        # 设置下拉框
        difficulty = self.manager.get_config_value('difficulty')
        config.difficulty_combo.setCurrentText(difficulty.title())
        
        gamemode = self.manager.get_config_value('gamemode')
        config.gamemode_combo.setCurrentText(gamemode.title())
        
        config.pvp_check.setChecked(self.manager.get_config_value('pvp').lower() == 'true')
    
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
        self.manager.set_config_value('difficulty', config.difficulty_combo.currentText().lower())
        self.manager.set_config_value('gamemode', config.gamemode_combo.currentText().lower())
        self.manager.set_config_value('pvp', 'true' if config.pvp_check.isChecked() else 'false')
        
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
    
    def browse_core_file(self):
        """浏览服务器核心文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择服务器核心文件", 
            "", 
            "JAR文件 (*.jar);;所有文件 (*)"
        )
        if file_path:
            self.config_interface.core_edit.setText(os.path.basename(file_path))
    
    def start_server(self):
        """启动服务器"""
        # 检查核心文件
        core_file = self.config_interface.core_edit.text()
        if not os.path.exists(core_file):
            InfoBar.error(
                title="错误",
                content=f"服务器核心文件 '{core_file}' 不存在！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            return
        
        # 保存配置
        self.save_config()
        
        try:
            if self.manager.start_server():
                # 启动输出监控线程
                self.output_thread = ServerOutputThread(self.manager)
                self.output_thread.output_received.connect(self.console_interface.append_output)
                self.output_thread.start()
                
                InfoBar.success(
                    title="启动成功",
                    content="服务器正在启动...",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                
                # 切换到控制台界面
                self.stackedWidget.setCurrentWidget(self.console_interface)
            else:
                InfoBar.error(
                    title="启动失败",
                    content="服务器启动失败！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
        except Exception as e:
            InfoBar.error(
                title="启动失败",
                content=f"启动失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
    
    def stop_server(self):
        """停止服务器"""
        if self.output_thread:
            self.output_thread.stop()
            self.output_thread.wait()
            self.output_thread = None
        
        if self.manager.stop_server():
            InfoBar.success(
                title="停止成功",
                content="服务器已停止",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.warning(
                title="停止失败",
                content="服务器停止失败或未在运行",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def send_command(self, command: str):
        """发送命令到服务器"""
        if self.manager.send_command(command):
            self.console_interface.append_output(f"> {command}")
        else:
            InfoBar.warning(
                title="发送失败",
                content="命令发送失败，服务器可能未运行",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def update_server_status(self):
        """更新服务器状态"""
        is_running = self.manager.is_server_running()
        self.server_interface.update_status(is_running)
        self.console_interface.update_status(is_running)


class ServerInterface(QWidget):
    """服务器控制界面"""
    
    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 状态卡片
        status_card = HeaderCardWidget(self)
        status_card.setTitle("服务器状态")
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(BodyLabel("当前状态:"))
        self.status_label = StrongBodyLabel("未运行")
        self.status_label.setStyleSheet("color: #d13438;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        status_card.viewLayout.addLayout(status_layout)
        layout.addWidget(status_card)
        
        # 控制按钮卡片
        control_card = SimpleCardWidget(self)
        control_layout = QHBoxLayout(control_card)
        
        self.start_button = PushButton("启动服务器", self)
        self.start_button.setIcon(FluentIcon.PLAY)
        self.start_button.clicked.connect(self.parent.start_server)
        
        self.stop_button = PushButton("停止服务器", self)
        self.stop_button.setIcon(FluentIcon.PAUSE)
        self.stop_button.clicked.connect(self.parent.stop_server)
        self.stop_button.setEnabled(False)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        
        layout.addWidget(control_card)
        layout.addStretch()
    
    def update_status(self, is_running: bool):
        """更新状态显示"""
        if is_running:
            self.status_label.setText("运行中")
            self.status_label.setStyleSheet("color: #107c10;")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.status_label.setText("未运行")
            self.status_label.setStyleSheet("color: #d13438;")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)


class ConfigInterface(QWidget):
    """配置界面"""
    
    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 基本配置卡片
        basic_card = HeaderCardWidget(self)
        basic_card.setTitle("基本配置")
        
        basic_layout = QGridLayout()
        
        # 内存分配
        basic_layout.addWidget(BodyLabel("内存分配:"), 0, 0)
        self.memory_edit = LineEdit(self)
        self.memory_edit.setPlaceholderText("例如: 2G, 4G, 8G")
        basic_layout.addWidget(self.memory_edit, 0, 1)
        
        # 服务器核心
        basic_layout.addWidget(BodyLabel("服务器核心:"), 1, 0)
        core_layout = QHBoxLayout()
        self.core_edit = LineEdit(self)
        self.core_edit.setPlaceholderText("server.jar")
        self.browse_button = PushButton("浏览", self)
        self.browse_button.setIcon(FluentIcon.FOLDER)
        self.browse_button.clicked.connect(self.parent.browse_core_file)
        core_layout.addWidget(self.core_edit)
        core_layout.addWidget(self.browse_button)
        basic_layout.addLayout(core_layout, 1, 1)
        
        basic_card.viewLayout.addLayout(basic_layout)
        layout.addWidget(basic_card)
        
        # 服务器配置卡片
        server_card = HeaderCardWidget(self)
        server_card.setTitle("服务器配置")
        
        server_layout = QGridLayout()
        
        # MOTD
        server_layout.addWidget(BodyLabel("服务器描述(MOTD):"), 0, 0)
        self.motd_edit = LineEdit(self)
        self.motd_edit.setPlaceholderText("A Minecraft Server")
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
        
        # 难度
        server_layout.addWidget(BodyLabel("游戏难度:"), 4, 0)
        self.difficulty_combo = ComboBox(self)
        self.difficulty_combo.addItems(["Peaceful", "Easy", "Normal", "Hard"])
        self.difficulty_combo.setCurrentText("Easy")
        server_layout.addWidget(self.difficulty_combo, 4, 1)
        
        # 游戏模式
        server_layout.addWidget(BodyLabel("游戏模式:"), 5, 0)
        self.gamemode_combo = ComboBox(self)
        self.gamemode_combo.addItems(["Survival", "Creative", "Adventure", "Spectator"])
        self.gamemode_combo.setCurrentText("Survival")
        server_layout.addWidget(self.gamemode_combo, 5, 1)
        
        # 正版验证
        self.online_mode_check = CheckBox("启用正版验证", self)
        self.online_mode_check.setChecked(True)
        server_layout.addWidget(self.online_mode_check, 6, 0, 1, 2)
        
        # PVP
        self.pvp_check = CheckBox("启用PVP", self)
        self.pvp_check.setChecked(True)
        server_layout.addWidget(self.pvp_check, 7, 0, 1, 2)
        
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
        self.seed_edit.setPlaceholderText("留空为随机种子")
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
    
    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
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
        self.console_output.setFont(QFont("Consolas", 10))
        self.console_output.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        console_layout.addWidget(self.console_output)
        
        # 命令输入
        command_layout = QHBoxLayout()
        self.command_input = LineEdit(self)
        self.command_input.setPlaceholderText("输入服务器命令...")
        self.command_input.returnPressed.connect(self.send_command)
        
        self.send_button = PushButton("发送", self)
        self.send_button.setIcon(FluentIcon.SEND)
        self.send_button.clicked.connect(self.send_command)
        self.send_button.setEnabled(False)
        
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_button)
        console_layout.addLayout(command_layout)
        
        console_card.viewLayout.addLayout(console_layout)
        layout.addWidget(console_card)
    
    def send_command(self):
        """发送命令"""
        command = self.command_input.text().strip()
        if command:
            self.parent.send_command(command)
            self.command_input.clear()
    
    def append_output(self, text: str):
        """添加输出文本"""
        self.console_output.append(text)
        # 自动滚动到底部
        scrollbar = self.console_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_status(self, is_running: bool):
        """更新状态"""
        self.send_button.setEnabled(is_running)
        self.command_input.setEnabled(is_running)


def main():
    """主函数"""
    # 启用高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Minecraft Server Manager")
    
    # 设置主题
    setTheme(Theme.AUTO)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()