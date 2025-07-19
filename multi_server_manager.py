#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多服务器管理模块
"""

import json
import os
import uuid
from typing import Dict, List, Optional
from mc_server_manager import MinecraftServerManager
from server_template import ServerTemplate, ServerTemplateManager


class ServerInstance:
    """服务器实例类"""
    
    def __init__(self, server_id: str, name: str, directory: str, config: Dict[str, str]):
        self.server_id = server_id
        self.name = name
        self.directory = directory
        self.config = config
        self.manager: Optional[MinecraftServerManager] = None
        self._initialize_manager()
    
    def _initialize_manager(self):
        """初始化服务器管理器"""
        config_file = os.path.join(self.directory, "server_config.json")
        self.manager = MinecraftServerManager(config_file)
        
        # 应用配置
        for key, value in self.config.items():
            self.manager.set_config_value(key, value)
        self.manager.save_config()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "server_id": self.server_id,
            "name": self.name,
            "directory": self.directory,
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ServerInstance':
        """从字典创建实例"""
        return cls(
            server_id=data["server_id"],
            name=data["name"],
            directory=data["directory"],
            config=data["config"]
        )
    
    def is_running(self) -> bool:
        """检查服务器是否运行"""
        return self.manager.is_server_running() if self.manager else False
    
    def start(self) -> bool:
        """启动服务器"""
        if not self.manager:
            return False
        
        # 切换到服务器目录
        original_dir = os.getcwd()
        try:
            os.chdir(self.directory)
            return self.manager.start_server()
        finally:
            os.chdir(original_dir)
    
    def stop(self) -> bool:
        """停止服务器"""
        return self.manager.stop_server() if self.manager else False
    
    def send_command(self, command: str) -> bool:
        """发送命令"""
        return self.manager.send_command(command) if self.manager else False
    
    def read_output(self) -> Optional[str]:
        """读取输出"""
        return self.manager.read_server_output() if self.manager else None


class MultiServerManager:
    """多服务器管理器"""
    
    def __init__(self, servers_file: str = "servers.json"):
        self.servers_file = servers_file
        self.servers: Dict[str, ServerInstance] = {}
        self.template_manager = ServerTemplateManager()
        self.load_servers()
    
    def load_servers(self):
        """加载服务器列表"""
        if os.path.exists(self.servers_file):
            try:
                with open(self.servers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for server_data in data:
                        server = ServerInstance.from_dict(server_data)
                        self.servers[server.server_id] = server
            except Exception as e:
                print(f"加载服务器列表失败: {e}")
    
    def save_servers(self):
        """保存服务器列表"""
        try:
            with open(self.servers_file, 'w', encoding='utf-8') as f:
                data = [server.to_dict() for server in self.servers.values()]
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存服务器列表失败: {e}")
    
    def create_server(self, name: str, template_name: str = None, custom_config: Dict[str, str] = None) -> str:
        """创建新服务器"""
        server_id = str(uuid.uuid4())
        directory = os.path.join("servers", server_id)
        
        # 创建服务器目录
        os.makedirs(directory, exist_ok=True)
        
        # 获取配置
        config = {}
        if template_name:
            template = self.template_manager.get_template_by_name(template_name)
            if template:
                config = template.config.copy()
        
        if custom_config:
            config.update(custom_config)
        
        # 创建服务器实例
        server = ServerInstance(server_id, name, directory, config)
        self.servers[server_id] = server
        self.save_servers()
        
        return server_id
    
    def delete_server(self, server_id: str) -> bool:
        """删除服务器"""
        if server_id not in self.servers:
            return False
        
        server = self.servers[server_id]
        
        # 停止服务器
        if server.is_running():
            server.stop()
        
        # 删除服务器
        del self.servers[server_id]
        self.save_servers()
        
        return True
    
    def get_server(self, server_id: str) -> Optional[ServerInstance]:
        """获取服务器实例"""
        return self.servers.get(server_id)
    
    def get_all_servers(self) -> List[ServerInstance]:
        """获取所有服务器"""
        return list(self.servers.values())
    
    def get_running_servers(self) -> List[ServerInstance]:
        """获取运行中的服务器"""
        return [server for server in self.servers.values() if server.is_running()]
    
    def stop_all_servers(self):
        """停止所有服务器"""
        for server in self.servers.values():
            if server.is_running():
                server.stop()
    
    def get_server_status(self) -> Dict[str, Dict]:
        """获取所有服务器状态"""
        status = {}
        for server_id, server in self.servers.items():
            status[server_id] = {
                "name": server.name,
                "running": server.is_running(),
                "port": server.config.get("port", "未知"),
                "players": server.config.get("max_players", "未知")
            }
        return status
    
    def update_server_config(self, server_id: str, config: Dict[str, str]):
        """更新服务器配置"""
        if server_id in self.servers:
            server = self.servers[server_id]
            server.config.update(config)
            
            # 更新管理器配置
            for key, value in config.items():
                server.manager.set_config_value(key, value)
            server.manager.save_config()
            
            self.save_servers()
    
    def clone_server(self, source_id: str, new_name: str) -> str:
        """克隆服务器"""
        if source_id not in self.servers:
            return None
        
        source_server = self.servers[source_id]
        return self.create_server(new_name, custom_config=source_server.config.copy())
    
    def import_from_template(self, name: str, template_name: str) -> str:
        """从模板导入服务器"""
        return self.create_server(name, template_name)
    
    def export_as_template(self, server_id: str, template_name: str, description: str):
        """将服务器导出为模板"""
        if server_id in self.servers:
            server = self.servers[server_id]
            template = ServerTemplate(template_name, description, server.config.copy())
            self.template_manager.add_template(template)