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
from multi_server_manager import MultiServerManager, ServerInstance
from server_template import ServerTemplateManager
from backup_manager import BackupManager
from plugin_manager import PluginManager
from performance_monitor import PerformanceMonitor
from player_manager import PlayerManager


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
        # 初始化管理器
        self.multi_server_manager = MultiServerManager()
        self.template_manager = ServerTemplateManager()
        self.backup_manager = BackupManager()
        self.performance_monitor = PerformanceMonitor()
        
        # 当前服务器相关管理器
        self.plugin_manager: Optional[PluginManager] = None
        self.player_manager: Optional[PlayerManager] = None
        
        # 当前选中的服务器
        self.current_server: Optional[ServerInstance] = None
        self.manager: Optional[MinecraftServerManager] = None
        
        self.output_thread: Optional[ServerOutputThread] = None
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_server_status)
        self.status_timer.start(1000)  # 每秒更新一次状态
        
        self.init_ui()
        self.load_default_server()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Minecraft Server Manager")
        self.resize(1000, 700)
        
        # 创建界面
        self.server_list_interface = ServerListInterface(self)
        self.server_list_interface.setObjectName("ServerListInterface")
        
        self.server_interface = ServerInterface(self)
        self.server_interface.setObjectName("ServerInterface")
        
        self.config_interface = ConfigInterface(self)
        self.config_interface.setObjectName("ConfigInterface")
        
        self.console_interface = ConsoleInterface(self)
        self.console_interface.setObjectName("ConsoleInterface")
        
        self.backup_interface = BackupInterface(self)
        self.backup_interface.setObjectName("BackupInterface")
        
        self.plugin_interface = PluginInterface(self)
        self.plugin_interface.setObjectName("PluginInterface")
        
        self.performance_interface = PerformanceInterface(self)
        self.performance_interface.setObjectName("PerformanceInterface")
        
        self.player_interface = PlayerInterface(self)
        self.player_interface.setObjectName("PlayerInterface")
        
        # 添加到导航
        self.addSubInterface(
            self.server_list_interface, 
            FluentIcon.MENU, 
            "服务器列表",
            NavigationItemPosition.TOP
        )
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
        self.addSubInterface(
            self.backup_interface, 
            FluentIcon.SAVE, 
            "备份管理",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.plugin_interface, 
            FluentIcon.APPLICATION, 
            "插件管理",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.performance_interface, 
            FluentIcon.SPEED_HIGH, 
            "性能监控",
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.player_interface, 
            FluentIcon.PEOPLE, 
            "玩家管理",
            NavigationItemPosition.TOP
        )
        
        # 设置默认界面
        self.stackedWidget.setCurrentWidget(self.server_list_interface)
    
    def load_default_server(self):
        """加载默认服务器或创建新服务器"""
        servers = self.multi_server_manager.get_all_servers()
        if servers:
            self.select_server(servers[0].server_id)
        else:
            # 创建默认服务器
            server_id = self.multi_server_manager.create_server("默认服务器", "原版生存服务器")
            self.select_server(server_id)
    
    def select_server(self, server_id: str):
        """选择服务器"""
        self.current_server = self.multi_server_manager.get_server(server_id)
        if self.current_server:
            self.manager = self.current_server.manager
            
            # 初始化当前服务器的管理器
            self.plugin_manager = PluginManager(self.current_server.directory)
            self.player_manager = PlayerManager(self.current_server.directory, self.manager)
            self.performance_monitor.server_manager = self.manager
            
            self.load_config()
            self.server_list_interface.refresh_server_list()
            
            # 刷新相关界面
            self.plugin_interface.refresh_plugin_list()
            self.player_interface.refresh_player_list()
            
            # 启动性能监控
            if self.manager and self.manager.is_server_running():
                self.performance_monitor.start_monitoring()
            else:
                self.performance_monitor.stop_monitoring()
    
    def load_config(self):
        """加载配置到界面"""
        if not self.manager:
            return
            
        config = self.config_interface
        config.set_memory_value(self.manager.get_config_value('memory'))
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
        if not self.manager or not self.current_server:
            return
            
        config = self.config_interface
        config_dict = {
            'memory': config.get_memory_value(),
            'core': config.core_edit.text(),
            'motd': config.motd_edit.text(),
            'port': str(config.port_spin.value()),
            'max_players': str(config.max_players_spin.value()),
            'view_distance': str(config.view_distance_spin.value()),
            'online_mode': 'true' if config.online_mode_check.isChecked() else 'false',
            'jvm_args': config.jvm_args_edit.text(),
            'server_args': config.server_args_edit.text(),
            'level_seed': config.seed_edit.text(),
            'difficulty': config.difficulty_combo.currentText().lower(),
            'gamemode': config.gamemode_combo.currentText().lower(),
            'pvp': 'true' if config.pvp_check.isChecked() else 'false'
        }
        
        # 更新多服务器管理器中的配置
        self.multi_server_manager.update_server_config(self.current_server.server_id, config_dict)
        
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
        if not self.current_server:
            InfoBar.error(
                title="错误",
                content="请先选择一个服务器！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        # 检查核心文件
        core_file = os.path.join(self.current_server.directory, self.current_server.config.get('core', 'server.jar'))
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
        
        # 检查并处理EULA
        if not self.check_and_handle_eula():
            return
        
        try:
            if self.current_server.start():
                # 启动输出监控线程
                self.output_thread = ServerOutputThread(self.current_server.manager)
                self.output_thread.output_received.connect(self.console_interface.append_output)
                self.output_thread.start()
                
                InfoBar.success(
                    title="启动成功",
                    content=f"服务器 '{self.current_server.name}' 正在启动...",
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
        
        if self.manager and self.manager.stop_server():
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
    
    def force_stop_server(self):
        """强制停止服务器"""
        if self.output_thread:
            self.output_thread.stop()
            self.output_thread.wait()
            self.output_thread = None
        
        # 立即显示强制停止提示
        InfoBar.warning(
            title="强制停止中",
            content="正在强制关闭服务器...",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
        
        # 使用线程异步处理强制停止，避免界面卡顿
        def force_stop_async():
            try:
                if self.current_server:
                    self.current_server.force_stop()
                # 强制停止后立即更新状态
                QTimer.singleShot(100, self.update_server_status)
            except Exception as e:
                print(f"异步强制停止失败: {e}")
        
        import threading
        threading.Thread(target=force_stop_async, daemon=True).start()
    
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
        is_running = self.manager.is_server_running() if self.manager else False
        self.server_interface.update_status(is_running)
        self.console_interface.update_status(is_running)
    
    def check_and_handle_eula(self) -> bool:
        """检查并处理EULA"""
        if not self.current_server:
            return False
        
        eula_path = os.path.join(self.current_server.directory, "eula.txt")
        
        # 检查EULA文件是否存在且已同意
        if os.path.exists(eula_path):
            try:
                with open(eula_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "eula=true" in content:
                        return True
            except Exception:
                pass
        
        # 需要用户同意EULA
        from qfluentwidgets import MessageBox
        
        dialog = MessageBox(
            "Minecraft EULA 协议",
            "启动服务器需要同意 Minecraft 最终用户许可协议 (EULA)。\n\n"
            "通过点击'同意'，您确认已阅读并同意 Minecraft EULA:\n"
            "https://account.mojang.com/documents/minecraft_eula\n\n"
            "您是否同意该协议？",
            self
        )
        
        if dialog.exec():
            # 用户同意，创建EULA文件
            try:
                os.makedirs(self.current_server.directory, exist_ok=True)
                with open(eula_path, 'w', encoding='utf-8') as f:
                    f.write("#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).\n")
                    f.write("#Generated by MC Server Manager\n")
                    f.write("eula=true\n")
                
                InfoBar.success(
                    title="EULA已同意",
                    content="已创建EULA文件，服务器可以启动",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return True
            except Exception as e:
                InfoBar.error(
                    title="EULA创建失败",
                    content=f"无法创建EULA文件: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                return False
        else:
            # 用户不同意，强制结束
            InfoBar.warning(
                title="EULA未同意",
                content="用户未同意EULA协议，无法启动服务器",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            
            # 强制结束当前进程（如果有的话）
            if self.current_server and self.current_server.is_running():
                self.force_stop_server()
            
            return False


class ServerListInterface(QWidget):
    """服务器列表界面"""
    
    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题和操作按钮
        header_layout = QHBoxLayout()
        title_label = StrongBodyLabel("服务器管理")
        title_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.create_server_button = PushButton("创建服务器", self)
        self.create_server_button.setIcon(FluentIcon.ADD)
        self.create_server_button.clicked.connect(self.create_server)
        header_layout.addWidget(self.create_server_button)
        
        layout.addLayout(header_layout)
        
        # 服务器列表
        self.server_list_card = HeaderCardWidget(self)
        self.server_list_card.setTitle("服务器列表")
        
        self.server_list_layout = QVBoxLayout()
        self.refresh_server_list()
        
        self.server_list_card.viewLayout.addLayout(self.server_list_layout)
        layout.addWidget(self.server_list_card)
        
        layout.addStretch()
    
    def refresh_server_list(self):
        """刷新服务器列表"""
        # 清空现有列表
        for i in reversed(range(self.server_list_layout.count())):
            child = self.server_list_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加服务器项
        servers = self.parent.multi_server_manager.get_all_servers()
        for server in servers:
            server_widget = self.create_server_widget(server)
            self.server_list_layout.addWidget(server_widget)
        
        if not servers:
            no_servers_label = BodyLabel("暂无服务器，点击上方按钮创建新服务器")
            no_servers_label.setAlignment(Qt.AlignCenter)
            self.server_list_layout.addWidget(no_servers_label)
    
    def create_server_widget(self, server: ServerInstance):
        """创建服务器项组件"""
        server_card = SimpleCardWidget(self)
        server_layout = QHBoxLayout(server_card)
        
        # 服务器信息
        info_layout = QVBoxLayout()
        name_label = StrongBodyLabel(server.name)
        status_text = "运行中" if server.is_running() else "未运行"
        status_color = "#107c10" if server.is_running() else "#d13438"
        status_label = BodyLabel(f"状态: {status_text}")
        status_label.setStyleSheet(f"color: {status_color};")
        
        port_label = BodyLabel(f"端口: {server.config.get('port', '未知')}")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(status_label)
        info_layout.addWidget(port_label)
        
        server_layout.addLayout(info_layout)
        server_layout.addStretch()
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        select_button = PushButton("选择", self)
        select_button.setIcon(FluentIcon.ACCEPT)
        select_button.clicked.connect(lambda: self.select_server(server.server_id))
        
        backup_button = PushButton("备份", self)
        backup_button.setIcon(FluentIcon.SAVE)
        backup_button.clicked.connect(lambda: self.backup_server(server.server_id))
        
        delete_button = PushButton("删除", self)
        delete_button.setIcon(FluentIcon.DELETE)
        delete_button.clicked.connect(lambda: self.delete_server(server.server_id))
        
        button_layout.addWidget(select_button)
        button_layout.addWidget(backup_button)
        button_layout.addWidget(delete_button)
        
        server_layout.addLayout(button_layout)
        
        return server_card
    
    def create_server(self):
        """创建新服务器"""
        dialog = CreateServerDialog(self.parent)
        if dialog.exec():
            server_info = dialog.get_server_info()
            if server_info:
                try:
                    server_id = self.parent.multi_server_manager.create_server_advanced(
                        server_info['name'],
                        server_info['template'],
                        server_info['directory'],
                        server_info['core_file']
                    )
                    self.refresh_server_list()
                    
                    InfoBar.success(
                        title="创建成功",
                        content=f"服务器 '{server_info['name']}' 创建成功！",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self.parent
                    )
                except Exception as e:
                    InfoBar.error(
                        title="创建失败",
                        content=f"创建服务器失败: {str(e)}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self.parent
                    )
    
    def select_server(self, server_id: str):
        """选择服务器"""
        self.parent.select_server(server_id)
        InfoBar.success(
            title="选择成功",
            content="服务器已选择",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self.parent
        )
    
    def backup_server(self, server_id: str):
        """备份服务器"""
        server = self.parent.multi_server_manager.get_server(server_id)
        if server:
            backup_info = self.parent.backup_manager.create_backup(
                server_id, server.name, server.directory, "manual", "手动备份"
            )
            if backup_info:
                InfoBar.success(
                    title="备份成功",
                    content=f"服务器 '{server.name}' 备份完成",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
            else:
                InfoBar.error(
                    title="备份失败",
                    content="备份创建失败",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
    
    def delete_server(self, server_id: str):
        """删除服务器"""
        from qfluentwidgets import MessageBox
        
        server = self.parent.multi_server_manager.get_server(server_id)
        if not server:
            return
        
        dialog = MessageBox(
            "确认删除",
            f"确定要删除服务器 '{server.name}' 吗？\n此操作不可撤销！",
            self
        )
        
        if dialog.exec():
            if self.parent.multi_server_manager.delete_server(server_id):
                self.refresh_server_list()
                InfoBar.success(
                    title="删除成功",
                    content=f"服务器 '{server.name}' 已删除",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )


class BackupInterface(QWidget):
    """备份管理界面"""
    
    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题和统计信息
        header_layout = QHBoxLayout()
        title_label = StrongBodyLabel("备份管理")
        title_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # 统计信息
        stats = self.parent.backup_manager.get_backup_statistics()
        stats_label = BodyLabel(f"总备份数: {stats['total_backups']} | 总大小: {stats['total_size_mb']} MB")
        header_layout.addWidget(stats_label)
        
        layout.addLayout(header_layout)
        
        # 备份列表
        backup_card = HeaderCardWidget(self)
        backup_card.setTitle("备份列表")
        
        self.backup_list_layout = QVBoxLayout()
        self.refresh_backup_list()
        
        backup_card.viewLayout.addLayout(self.backup_list_layout)
        layout.addWidget(backup_card)
        
        layout.addStretch()
    
    def refresh_backup_list(self):
        """刷新备份列表"""
        # 清空现有列表
        for i in reversed(range(self.backup_list_layout.count())):
            child = self.backup_list_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加备份项
        backups = self.parent.backup_manager.get_all_backups()
        for backup in backups[:20]:  # 只显示最新的20个备份
            backup_widget = self.create_backup_widget(backup)
            self.backup_list_layout.addWidget(backup_widget)
        
        if not backups:
            no_backups_label = BodyLabel("暂无备份")
            no_backups_label.setAlignment(Qt.AlignCenter)
            self.backup_list_layout.addWidget(no_backups_label)
    
    def create_backup_widget(self, backup):
        """创建备份项组件"""
        backup_card = SimpleCardWidget(self)
        backup_layout = QHBoxLayout(backup_card)
        
        # 备份信息
        info_layout = QVBoxLayout()
        name_label = StrongBodyLabel(f"{backup.server_name}")
        time_label = BodyLabel(f"时间: {backup.backup_time[:19]}")
        size_label = BodyLabel(f"大小: {self.parent.backup_manager.format_size(backup.backup_size)}")
        type_label = BodyLabel(f"类型: {backup.backup_type}")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(time_label)
        info_layout.addWidget(size_label)
        info_layout.addWidget(type_label)
        
        backup_layout.addLayout(info_layout)
        backup_layout.addStretch()
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        restore_button = PushButton("恢复", self)
        restore_button.setIcon(FluentIcon.SYNC)
        restore_button.clicked.connect(lambda: self.restore_backup(backup.backup_id))
        
        delete_button = PushButton("删除", self)
        delete_button.setIcon(FluentIcon.DELETE)
        delete_button.clicked.connect(lambda: self.delete_backup(backup.backup_id))
        
        button_layout.addWidget(restore_button)
        button_layout.addWidget(delete_button)
        
        backup_layout.addLayout(button_layout)
        
        return backup_card
    
    def restore_backup(self, backup_id: str):
        """恢复备份"""
        from qfluentwidgets import MessageBox
        
        backup = self.parent.backup_manager.get_backup_by_id(backup_id)
        if not backup:
            return
        
        dialog = MessageBox(
            "确认恢复",
            f"确定要恢复备份 '{backup.server_name}' 吗？\n当前服务器数据将被覆盖！",
            self
        )
        
        if dialog.exec():
            server = self.parent.multi_server_manager.get_server(backup.server_id)
            if server and self.parent.backup_manager.restore_backup(backup_id, server.directory):
                InfoBar.success(
                    title="恢复成功",
                    content=f"备份已恢复到服务器 '{backup.server_name}'",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
            else:
                InfoBar.error(
                    title="恢复失败",
                    content="备份恢复失败",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
    
    def delete_backup(self, backup_id: str):
        """删除备份"""
        from qfluentwidgets import MessageBox
        
        backup = self.parent.backup_manager.get_backup_by_id(backup_id)
        if not backup:
            return
        
        dialog = MessageBox(
            "确认删除",
            f"确定要删除备份 '{backup.server_name}' 吗？\n此操作不可撤销！",
            self
        )
        
        if dialog.exec():
            if self.parent.backup_manager.delete_backup(backup_id):
                self.refresh_backup_list()
                InfoBar.success(
                    title="删除成功",
                    content="备份已删除",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )


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
        memory_layout = QVBoxLayout()
        
        from qfluentwidgets import Slider
        self.memory_slider = Slider(Qt.Horizontal, self)
        self.memory_slider.setRange(512, 16384)  # 512MB to 16GB
        self.memory_slider.setValue(2048)  # 默认2GB
        self.memory_slider.valueChanged.connect(self.update_memory_label)
        
        self.memory_label = BodyLabel("2048 MB (2 GB)")
        
        memory_layout.addWidget(self.memory_slider)
        memory_layout.addWidget(self.memory_label)
        basic_layout.addLayout(memory_layout, 0, 1)
        
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
    
    def update_memory_label(self, value):
        """更新内存标签"""
        gb_value = value / 1024
        if gb_value >= 1:
            self.memory_label.setText(f"{value} MB ({gb_value:.1f} GB)")
        else:
            self.memory_label.setText(f"{value} MB")
    
    def get_memory_value(self):
        """获取内存值（字符串格式）"""
        value = self.memory_slider.value()
        if value >= 1024:
            return f"{int(value/1024)}G"
        else:
            return f"{value}M"
    
    def set_memory_value(self, memory_str):
        """设置内存值"""
        try:
            if memory_str.upper().endswith('G'):
                value = int(float(memory_str[:-1]) * 1024)
            elif memory_str.upper().endswith('M'):
                value = int(memory_str[:-1])
            else:
                value = int(memory_str)
            
            self.memory_slider.setValue(value)
        except:
            self.memory_slider.setValue(2048)  # 默认值


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
        
        self.start_server_button = PushButton("启动服务器", self)
        self.start_server_button.setIcon(FluentIcon.PLAY)
        self.start_server_button.clicked.connect(self.parent.start_server)
        
        self.stop_server_button = PushButton("停止服务器", self)
        self.stop_server_button.setIcon(FluentIcon.POWER_BUTTON)
        self.stop_server_button.clicked.connect(self.stop_server_with_double_click)
        self.stop_server_button.setEnabled(False)
        
        # 双击检测
        self.last_stop_click_time = 0
        self.stop_command_sent = False
        
        command_layout.addWidget(self.command_input)
        command_layout.addWidget(self.send_button)
        command_layout.addWidget(self.start_server_button)
        command_layout.addWidget(self.stop_server_button)
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
        self.start_server_button.setEnabled(not is_running)
        self.stop_server_button.setEnabled(is_running)
        
        # 重置停止状态
        if not is_running:
            self.stop_command_sent = False
    
    def stop_server_with_double_click(self):
        """带双击检测的停止服务器"""
        import time
        current_time = time.time() * 1000  # 转换为毫秒
        
        if not self.stop_command_sent:
            # 第一次点击，发送stop命令
            self.parent.send_command("stop")
            self.stop_command_sent = True
            self.last_stop_click_time = current_time
            
            InfoBar.info(
                title="正在停止服务器",
                content="双击可以强制关闭服务器（不推荐）",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self.parent
            )
        else:
            # 检查是否在200ms内双击
            if current_time - self.last_stop_click_time <= 200:
                # 双击，强制停止
                InfoBar.warning(
                    title="强制停止",
                    content="正在强制关闭服务器...",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
                self.parent.force_stop_server()
            else:
                # 超过200ms，重新开始
                self.parent.send_command("stop")
                self.last_stop_click_time = current_time


class CreateServerDialog(QWidget):
    """创建服务器对话框"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.result = False
        self.setWindowTitle("创建新服务器")
        self.setFixedSize(500, 400)
        self.setWindowModality(Qt.ApplicationModal)
        
        self.init_ui()
        
        # 居中显示
        if parent:
            self.move(parent.geometry().center() - self.rect().center())
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = StrongBodyLabel("创建新服务器")
        title_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(title_label)
        
        # 表单
        form_layout = QGridLayout()
        
        # 服务器名称
        form_layout.addWidget(BodyLabel("服务器名称:"), 0, 0)
        self.name_edit = LineEdit(self)
        self.name_edit.setPlaceholderText("输入服务器名称")
        form_layout.addWidget(self.name_edit, 0, 1)
        
        # 服务器模板
        form_layout.addWidget(BodyLabel("服务器模板:"), 1, 0)
        self.template_combo = ComboBox(self)
        template_names = self.parent.template_manager.get_template_names()
        self.template_combo.addItems(template_names)
        form_layout.addWidget(self.template_combo, 1, 1)
        
        # 服务器路径
        form_layout.addWidget(BodyLabel("服务器路径:"), 2, 0)
        path_layout = QHBoxLayout()
        self.path_edit = LineEdit(self)
        self.path_edit.setPlaceholderText("服务器路径(基于当前根目录): /Servers")
        self.path_edit.setText("Servers")
        
        self.browse_path_button = PushButton("浏览", self)
        self.browse_path_button.setIcon(FluentIcon.FOLDER)
        self.browse_path_button.clicked.connect(self.browse_path)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_path_button)
        form_layout.addLayout(path_layout, 2, 1)
        
        # 服务器核心文件
        form_layout.addWidget(BodyLabel("服务器核心:"), 3, 0)
        core_layout = QHBoxLayout()
        self.core_edit = LineEdit(self)
        self.core_edit.setPlaceholderText("选择服务器核心文件 (server.jar)")
        
        self.browse_core_button = PushButton("浏览", self)
        self.browse_core_button.setIcon(FluentIcon.DOCUMENT)
        self.browse_core_button.clicked.connect(self.browse_core)
        
        core_layout.addWidget(self.core_edit)
        core_layout.addWidget(self.browse_core_button)
        form_layout.addLayout(core_layout, 3, 1)
        
        layout.addLayout(form_layout)
        
        # 提示信息
        tip_label = BodyLabel("提示: 如果没有服务器核心文件，请先下载对应版本的 server.jar 文件")
        tip_label.setStyleSheet("color: #888888;")
        layout.addWidget(tip_label)
        
        layout.addStretch()
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = PushButton("取消", self)
        self.cancel_button.clicked.connect(self.reject)
        
        self.create_button = PushButton("创建", self)
        self.create_button.setIcon(FluentIcon.ADD)
        self.create_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
    
    def browse_path(self):
        """浏览服务器路径"""
        path = QFileDialog.getExistingDirectory(self, "选择服务器目录", ".")
        if path:
            # 转换为相对路径
            rel_path = os.path.relpath(path, ".")
            self.path_edit.setText(rel_path)
    
    def browse_core(self):
        """浏览服务器核心文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择服务器核心文件", 
            "", 
            "JAR文件 (*.jar);;所有文件 (*)"
        )
        if file_path:
            self.core_edit.setText(file_path)
    
    def get_server_info(self):
        """获取服务器信息"""
        name = self.name_edit.text().strip()
        if not name:
            InfoBar.warning(
                title="警告",
                content="请输入服务器名称",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            return None
        
        core_file = self.core_edit.text().strip()
        if not core_file:
            InfoBar.warning(
                title="警告", 
                content="请选择服务器核心文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            return None
        
        if not os.path.exists(core_file):
            InfoBar.error(
                title="错误",
                content="服务器核心文件不存在",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            return None
        
        return {
            'name': name,
            'template': self.template_combo.currentText(),
            'directory': self.path_edit.text().strip() or "Servers",
            'core_file': core_file
        }
    
    def exec(self):
        """显示对话框"""
        self.show()
        # 简单的事件循环
        from PyQt5.QtCore import QEventLoop
        loop = QEventLoop()
        self.finished = loop.quit
        loop.exec_()
        return self.result
    
    def accept(self):
        """接受"""
        self.result = True
        self.close()
        if hasattr(self, 'finished'):
            self.finished()
    
    def reject(self):
        """拒绝"""
        self.result = False
        self.close()
        if hasattr(self, 'finished'):
            self.finished()


class PluginInterface(QWidget):
    """插件管理界面"""
    
    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题和操作按钮
        header_layout = QHBoxLayout()
        title_label = StrongBodyLabel("插件管理")
        title_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.refresh_button = PushButton("刷新", self)
        self.refresh_button.setIcon(FluentIcon.SYNC)
        self.refresh_button.clicked.connect(self.refresh_plugin_list)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # 选项卡
        from qfluentwidgets import TabWidget
        self.tab_widget = TabWidget(self)
        
        # 已安装插件选项卡
        self.installed_tab = QWidget()
        self.init_installed_tab()
        self.tab_widget.addTab(self.installed_tab, "已安装插件")
        
        # 可用插件选项卡
        self.available_tab = QWidget()
        self.init_available_tab()
        self.tab_widget.addTab(self.available_tab, "可用插件")
        
        layout.addWidget(self.tab_widget)
    
    def init_installed_tab(self):
        """初始化已安装插件选项卡"""
        layout = QVBoxLayout(self.installed_tab)
        layout.setSpacing(15)
        
        self.installed_list_layout = QVBoxLayout()
        layout.addLayout(self.installed_list_layout)
        layout.addStretch()
    
    def init_available_tab(self):
        """初始化可用插件选项卡"""
        layout = QVBoxLayout(self.available_tab)
        layout.setSpacing(15)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_edit = LineEdit(self)
        self.search_edit.setPlaceholderText("搜索插件...")
        self.search_button = PushButton("搜索", self)
        self.search_button.setIcon(FluentIcon.SEARCH)
        self.search_button.clicked.connect(self.search_plugins)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        self.available_list_layout = QVBoxLayout()
        layout.addLayout(self.available_list_layout)
        layout.addStretch()
    
    def refresh_plugin_list(self):
        """刷新插件列表"""
        if not self.parent.plugin_manager:
            return
        
        # 刷新已安装插件
        self.refresh_installed_plugins()
        
        # 刷新可用插件
        self.refresh_available_plugins()
    
    def refresh_installed_plugins(self):
        """刷新已安装插件列表"""
        # 清空现有列表
        for i in reversed(range(self.installed_list_layout.count())):
            child = self.installed_list_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not self.parent.plugin_manager:
            return
        
        plugins = self.parent.plugin_manager.get_installed_plugins()
        for plugin in plugins:
            plugin_widget = self.create_installed_plugin_widget(plugin)
            self.installed_list_layout.addWidget(plugin_widget)
        
        if not plugins:
            no_plugins_label = BodyLabel("暂无已安装插件")
            no_plugins_label.setAlignment(Qt.AlignCenter)
            self.installed_list_layout.addWidget(no_plugins_label)
    
    def refresh_available_plugins(self):
        """刷新可用插件列表"""
        # 清空现有列表
        for i in reversed(range(self.available_list_layout.count())):
            child = self.available_list_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not self.parent.plugin_manager:
            return
        
        plugins = self.parent.plugin_manager.get_available_plugins()
        for plugin in plugins:
            if not self.parent.plugin_manager.is_plugin_installed(plugin.name):
                plugin_widget = self.create_available_plugin_widget(plugin)
                self.available_list_layout.addWidget(plugin_widget)
    
    def create_installed_plugin_widget(self, plugin):
        """创建已安装插件组件"""
        plugin_card = SimpleCardWidget(self)
        plugin_layout = QHBoxLayout(plugin_card)
        
        # 插件信息
        info_layout = QVBoxLayout()
        name_label = StrongBodyLabel(plugin.name)
        version_label = BodyLabel(f"版本: {plugin.version}")
        author_label = BodyLabel(f"作者: {plugin.author}")
        desc_label = BodyLabel(plugin.description)
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(version_label)
        info_layout.addWidget(author_label)
        info_layout.addWidget(desc_label)
        
        plugin_layout.addLayout(info_layout)
        plugin_layout.addStretch()
        
        # 操作按钮
        button_layout = QVBoxLayout()
        
        if plugin.enabled:
            disable_button = PushButton("禁用", self)
            disable_button.clicked.connect(lambda: self.disable_plugin(plugin.name))
            button_layout.addWidget(disable_button)
        else:
            enable_button = PushButton("启用", self)
            enable_button.clicked.connect(lambda: self.enable_plugin(plugin.name))
            button_layout.addWidget(enable_button)
        
        uninstall_button = PushButton("卸载", self)
        uninstall_button.setIcon(FluentIcon.DELETE)
        uninstall_button.clicked.connect(lambda: self.uninstall_plugin(plugin.name))
        button_layout.addWidget(uninstall_button)
        
        plugin_layout.addLayout(button_layout)
        
        return plugin_card
    
    def create_available_plugin_widget(self, plugin):
        """创建可用插件组件"""
        plugin_card = SimpleCardWidget(self)
        plugin_layout = QHBoxLayout(plugin_card)
        
        # 插件信息
        info_layout = QVBoxLayout()
        name_label = StrongBodyLabel(plugin.name)
        version_label = BodyLabel(f"版本: {plugin.version}")
        author_label = BodyLabel(f"作者: {plugin.author}")
        desc_label = BodyLabel(plugin.description)
        desc_label.setWordWrap(True)
        
        if plugin.dependencies:
            deps_label = BodyLabel(f"依赖: {', '.join(plugin.dependencies)}")
            deps_label.setStyleSheet("color: #888888;")
            info_layout.addWidget(deps_label)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(version_label)
        info_layout.addWidget(author_label)
        info_layout.addWidget(desc_label)
        
        plugin_layout.addLayout(info_layout)
        plugin_layout.addStretch()
        
        # 安装按钮
        install_button = PushButton("安装", self)
        install_button.setIcon(FluentIcon.DOWNLOAD)
        install_button.clicked.connect(lambda: self.install_plugin(plugin))
        plugin_layout.addWidget(install_button)
        
        return plugin_card
    
    def install_plugin(self, plugin):
        """安装插件"""
        if not self.parent.plugin_manager:
            return
        
        InfoBar.info(
            title="开始安装",
            content=f"正在安装插件 {plugin.name}...",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self.parent
        )
        
        # 异步安装
        def install_async():
            success = self.parent.plugin_manager.install_plugin(plugin)
            QTimer.singleShot(100, lambda: self.install_finished(plugin.name, success))
        
        import threading
        threading.Thread(target=install_async, daemon=True).start()
    
    def install_finished(self, plugin_name: str, success: bool):
        """安装完成"""
        if success:
            InfoBar.success(
                title="安装成功",
                content=f"插件 {plugin_name} 安装成功！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            self.refresh_plugin_list()
        else:
            InfoBar.error(
                title="安装失败",
                content=f"插件 {plugin_name} 安装失败！",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
    
    def uninstall_plugin(self, plugin_name: str):
        """卸载插件"""
        from qfluentwidgets import MessageBox
        
        dialog = MessageBox(
            "确认卸载",
            f"确定要卸载插件 '{plugin_name}' 吗？",
            self
        )
        
        if dialog.exec():
            if self.parent.plugin_manager.uninstall_plugin(plugin_name):
                InfoBar.success(
                    title="卸载成功",
                    content=f"插件 {plugin_name} 已卸载",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
                self.refresh_plugin_list()
    
    def enable_plugin(self, plugin_name: str):
        """启用插件"""
        if self.parent.plugin_manager.enable_plugin(plugin_name):
            InfoBar.success(
                title="启用成功",
                content=f"插件 {plugin_name} 已启用",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
            self.refresh_plugin_list()
    
    def disable_plugin(self, plugin_name: str):
        """禁用插件"""
        if self.parent.plugin_manager.disable_plugin(plugin_name):
            InfoBar.success(
                title="禁用成功",
                content=f"插件 {plugin_name} 已禁用",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
            self.refresh_plugin_list()
    
    def search_plugins(self):
        """搜索插件"""
        keyword = self.search_edit.text().strip()
        if not keyword or not self.parent.plugin_manager:
            self.refresh_available_plugins()
            return
        
        # 清空现有列表
        for i in reversed(range(self.available_list_layout.count())):
            child = self.available_list_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 搜索结果
        results = self.parent.plugin_manager.search_plugins(keyword)
        for plugin in results:
            if not self.parent.plugin_manager.is_plugin_installed(plugin.name):
                plugin_widget = self.create_available_plugin_widget(plugin)
                self.available_list_layout.addWidget(plugin_widget)
        
        if not results:
            no_results_label = BodyLabel(f"未找到包含 '{keyword}' 的插件")
            no_results_label.setAlignment(Qt.AlignCenter)
            self.available_list_layout.addWidget(no_results_label)


class PerformanceInterface(QWidget):
    """性能监控界面"""
    
    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent
        self.init_ui()
        
        # 添加性能监控回调
        if parent.performance_monitor:
            parent.performance_monitor.add_callback(self.update_performance_data)
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = StrongBodyLabel("性能监控")
        title_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(title_label)
        
        # 实时数据卡片
        realtime_card = HeaderCardWidget(self)
        realtime_card.setTitle("实时性能数据")
        
        realtime_layout = QGridLayout()
        
        # CPU使用率
        realtime_layout.addWidget(BodyLabel("CPU使用率:"), 0, 0)
        self.cpu_label = StrongBodyLabel("0%")
        realtime_layout.addWidget(self.cpu_label, 0, 1)
        
        # 内存使用
        realtime_layout.addWidget(BodyLabel("内存使用:"), 0, 2)
        self.memory_label = StrongBodyLabel("0 MB")
        realtime_layout.addWidget(self.memory_label, 0, 3)
        
        # TPS
        realtime_layout.addWidget(BodyLabel("服务器TPS:"), 1, 0)
        self.tps_label = StrongBodyLabel("0.0")
        realtime_layout.addWidget(self.tps_label, 1, 1)
        
        # 在线玩家
        realtime_layout.addWidget(BodyLabel("在线玩家:"), 1, 2)
        self.players_label = StrongBodyLabel("0")
        realtime_layout.addWidget(self.players_label, 1, 3)
        
        realtime_card.viewLayout.addLayout(realtime_layout)
        layout.addWidget(realtime_card)
        
        # 性能状态卡片
        status_card = HeaderCardWidget(self)
        status_card.setTitle("性能状态")
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(BodyLabel("当前状态:"))
        self.status_label = StrongBodyLabel("未知")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        status_card.viewLayout.addLayout(status_layout)
        layout.addWidget(status_card)
        
        # 优化建议卡片
        suggestions_card = HeaderCardWidget(self)
        suggestions_card.setTitle("优化建议")
        
        self.suggestions_layout = QVBoxLayout()
        suggestions_card.viewLayout.addLayout(self.suggestions_layout)
        layout.addWidget(suggestions_card)
        
        layout.addStretch()
    
    def update_performance_data(self, data):
        """更新性能数据"""
        # 更新实时数据
        self.cpu_label.setText(f"{data.cpu_percent:.1f}%")
        self.memory_label.setText(f"{data.memory_used} MB")
        self.tps_label.setText(f"{data.tps:.1f}")
        self.players_label.setText(str(data.online_players))
        
        # 更新状态
        status = self.parent.performance_monitor.get_performance_status()
        self.status_label.setText(status)
        
        # 设置状态颜色
        if status == "优秀":
            self.status_label.setStyleSheet("color: #107c10;")
        elif status == "良好":
            self.status_label.setStyleSheet("color: #0078d4;")
        elif status == "一般":
            self.status_label.setStyleSheet("color: #ff8c00;")
        else:
            self.status_label.setStyleSheet("color: #d13438;")
        
        # 更新建议
        self.update_suggestions()
    
    def update_suggestions(self):
        """更新优化建议"""
        # 清空现有建议
        for i in reversed(range(self.suggestions_layout.count())):
            child = self.suggestions_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        suggestions = self.parent.performance_monitor.get_performance_suggestions()
        for suggestion in suggestions:
            suggestion_label = BodyLabel(f"• {suggestion}")
            suggestion_label.setWordWrap(True)
            self.suggestions_layout.addWidget(suggestion_label)


class PlayerInterface(QWidget):
    """玩家管理界面"""
    
    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题和操作按钮
        header_layout = QHBoxLayout()
        title_label = StrongBodyLabel("玩家管理")
        title_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.refresh_button = PushButton("刷新", self)
        self.refresh_button.setIcon(FluentIcon.SYNC)
        self.refresh_button.clicked.connect(self.refresh_player_list)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # 统计信息卡片
        stats_card = HeaderCardWidget(self)
        stats_card.setTitle("玩家统计")
        
        self.stats_layout = QGridLayout()
        stats_card.viewLayout.addLayout(self.stats_layout)
        layout.addWidget(stats_card)
        
        # 玩家列表
        players_card = HeaderCardWidget(self)
        players_card.setTitle("玩家列表")
        
        self.player_list_layout = QVBoxLayout()
        players_card.viewLayout.addLayout(self.player_list_layout)
        layout.addWidget(players_card)
        
        layout.addStretch()
    
    def refresh_player_list(self):
        """刷新玩家列表"""
        if not self.parent.player_manager:
            return
        
        # 更新统计信息
        self.update_statistics()
        
        # 清空现有列表
        for i in reversed(range(self.player_list_layout.count())):
            child = self.player_list_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加玩家项
        players = self.parent.player_manager.get_all_players()
        for player in players:
            player_widget = self.create_player_widget(player)
            self.player_list_layout.addWidget(player_widget)
        
        if not players:
            no_players_label = BodyLabel("暂无玩家数据")
            no_players_label.setAlignment(Qt.AlignCenter)
            self.player_list_layout.addWidget(no_players_label)
    
    def update_statistics(self):
        """更新统计信息"""
        # 清空现有统计
        for i in reversed(range(self.stats_layout.count())):
            child = self.stats_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        if not self.parent.player_manager:
            return
        
        stats = self.parent.player_manager.get_player_statistics()
        
        # 总玩家数
        self.stats_layout.addWidget(BodyLabel("总玩家数:"), 0, 0)
        self.stats_layout.addWidget(StrongBodyLabel(str(stats["total_players"])), 0, 1)
        
        # 在线玩家
        self.stats_layout.addWidget(BodyLabel("在线玩家:"), 0, 2)
        online_label = StrongBodyLabel(str(stats["online_players"]))
        online_label.setStyleSheet("color: #107c10;")
        self.stats_layout.addWidget(online_label, 0, 3)
        
        # 封禁玩家
        self.stats_layout.addWidget(BodyLabel("封禁玩家:"), 1, 0)
        banned_label = StrongBodyLabel(str(stats["banned_players"]))
        banned_label.setStyleSheet("color: #d13438;")
        self.stats_layout.addWidget(banned_label, 1, 1)
        
        # OP玩家
        self.stats_layout.addWidget(BodyLabel("OP玩家:"), 1, 2)
        self.stats_layout.addWidget(StrongBodyLabel(str(stats["op_players"])), 1, 3)
    
    def create_player_widget(self, player):
        """创建玩家组件"""
        player_card = SimpleCardWidget(self)
        player_layout = QHBoxLayout(player_card)
        
        # 玩家信息
        info_layout = QVBoxLayout()
        name_label = StrongBodyLabel(player.username)
        
        status_text = "在线" if player.is_online else "离线"
        status_color = "#107c10" if player.is_online else "#888888"
        status_label = BodyLabel(f"状态: {status_text}")
        status_label.setStyleSheet(f"color: {status_color};")
        
        # 标签
        tags = []
        if player.is_op:
            tags.append("OP")
        if player.is_banned:
            tags.append("封禁")
        if player.is_whitelisted:
            tags.append("白名单")
        
        if tags:
            tags_label = BodyLabel(f"标签: {', '.join(tags)}")
            info_layout.addWidget(tags_label)
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(status_label)
        
        player_layout.addLayout(info_layout)
        player_layout.addStretch()
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        if player.is_online:
            kick_button = PushButton("踢出", self)
            kick_button.clicked.connect(lambda: self.kick_player(player.username))
            button_layout.addWidget(kick_button)
        
        if not player.is_banned:
            ban_button = PushButton("封禁", self)
            ban_button.clicked.connect(lambda: self.ban_player(player.username))
            button_layout.addWidget(ban_button)
        else:
            unban_button = PushButton("解封", self)
            unban_button.clicked.connect(lambda: self.unban_player(player.username))
            button_layout.addWidget(unban_button)
        
        if not player.is_op:
            op_button = PushButton("给予OP", self)
            op_button.clicked.connect(lambda: self.op_player(player.username))
            button_layout.addWidget(op_button)
        else:
            deop_button = PushButton("移除OP", self)
            deop_button.clicked.connect(lambda: self.deop_player(player.username))
            button_layout.addWidget(deop_button)
        
        player_layout.addLayout(button_layout)
        
        return player_card
    
    def kick_player(self, username: str):
        """踢出玩家"""
        if self.parent.player_manager.kick_player(username):
            InfoBar.success(
                title="踢出成功",
                content=f"玩家 {username} 已被踢出",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
    
    def ban_player(self, username: str):
        """封禁玩家"""
        if self.parent.player_manager.ban_player(username):
            InfoBar.success(
                title="封禁成功",
                content=f"玩家 {username} 已被封禁",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            self.refresh_player_list()
    
    def unban_player(self, username: str):
        """解封玩家"""
        if self.parent.player_manager.unban_player(username):
            InfoBar.success(
                title="解封成功",
                content=f"玩家 {username} 已被解封",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            self.refresh_player_list()
    
    def op_player(self, username: str):
        """给予OP权限"""
        if self.parent.player_manager.op_player(username):
            InfoBar.success(
                title="OP成功",
                content=f"已给予玩家 {username} OP权限",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            self.refresh_player_list()
    
    def deop_player(self, username: str):
        """移除OP权限"""
        if self.parent.player_manager.deop_player(username):
            InfoBar.success(
                title="移除OP成功",
                content=f"已移除玩家 {username} 的OP权限",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            self.refresh_player_list()


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