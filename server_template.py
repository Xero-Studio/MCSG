#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器模板管理模块
"""

import json
import os
from typing import Dict, List, Any


class ServerTemplate:
    """服务器模板类"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any]):
        self.name = name
        self.description = description
        self.config = config
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "config": self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServerTemplate':
        """从字典创建模板"""
        return cls(
            name=data["name"],
            description=data["description"],
            config=data["config"]
        )


class ServerTemplateManager:
    """服务器模板管理器"""
    
    def __init__(self, templates_file: str = "server_templates.json"):
        self.templates_file = templates_file
        self.templates: List[ServerTemplate] = []
        self.load_templates()
        self.create_default_templates()
    
    def create_default_templates(self):
        """创建默认模板"""
        if not self.templates:
            default_templates = [
                ServerTemplate(
                    name="原版生存服务器",
                    description="标准的原版 Minecraft 生存服务器",
                    config={
                        "memory": "4G",
                        "core": "server.jar",
                        "motd": "原版生存服务器 - 欢迎来玩！",
                        "port": "25565",
                        "max_players": "20",
                        "view_distance": "10",
                        "online_mode": "true",
                        "difficulty": "normal",
                        "gamemode": "survival",
                        "pvp": "true",
                        "spawn_protection": "16",
                        "jvm_args": "-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions",
                        "server_args": "nogui",
                        "level_seed": ""
                    }
                ),
                ServerTemplate(
                    name="创造服务器",
                    description="创造模式服务器，适合建筑和创作",
                    config={
                        "memory": "2G",
                        "core": "server.jar",
                        "motd": "创造服务器 - 自由建造！",
                        "port": "25566",
                        "max_players": "10",
                        "view_distance": "12",
                        "online_mode": "true",
                        "difficulty": "peaceful",
                        "gamemode": "creative",
                        "pvp": "false",
                        "spawn_protection": "0",
                        "jvm_args": "-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions",
                        "server_args": "nogui",
                        "level_seed": ""
                    }
                ),
                ServerTemplate(
                    name="模组服务器",
                    description="高性能模组服务器配置",
                    config={
                        "memory": "8G",
                        "core": "forge-server.jar",
                        "motd": "模组服务器 - 更多内容等你探索！",
                        "port": "25567",
                        "max_players": "15",
                        "view_distance": "8",
                        "online_mode": "true",
                        "difficulty": "normal",
                        "gamemode": "survival",
                        "pvp": "true",
                        "spawn_protection": "16",
                        "jvm_args": "-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:G1HeapRegionSize=32m",
                        "server_args": "nogui",
                        "level_seed": ""
                    }
                ),
                ServerTemplate(
                    name="小型私人服务器",
                    description="适合朋友间游玩的小型服务器",
                    config={
                        "memory": "1G",
                        "core": "server.jar",
                        "motd": "私人小服 - 仅限好友",
                        "port": "25568",
                        "max_players": "5",
                        "view_distance": "6",
                        "online_mode": "false",
                        "difficulty": "easy",
                        "gamemode": "survival",
                        "pvp": "false",
                        "spawn_protection": "10",
                        "jvm_args": "-XX:+UseG1GC",
                        "server_args": "nogui",
                        "level_seed": ""
                    }
                )
            ]
            
            self.templates.extend(default_templates)
            self.save_templates()
    
    def load_templates(self):
        """加载模板"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.templates = [ServerTemplate.from_dict(t) for t in data]
            except Exception as e:
                print(f"加载模板失败: {e}")
                self.templates = []
    
    def save_templates(self):
        """保存模板"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                data = [t.to_dict() for t in self.templates]
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存模板失败: {e}")
    
    def get_templates(self) -> List[ServerTemplate]:
        """获取所有模板"""
        return self.templates
    
    def get_template_by_name(self, name: str) -> ServerTemplate:
        """根据名称获取模板"""
        for template in self.templates:
            if template.name == name:
                return template
        return None
    
    def add_template(self, template: ServerTemplate):
        """添加模板"""
        self.templates.append(template)
        self.save_templates()
    
    def remove_template(self, name: str):
        """删除模板"""
        self.templates = [t for t in self.templates if t.name != name]
        self.save_templates()
    
    def get_template_names(self) -> List[str]:
        """获取所有模板名称"""
        return [t.name for t in self.templates]