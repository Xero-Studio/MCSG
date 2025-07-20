#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件管理模块
"""

import os
import json
import requests
import zipfile
import shutil
from typing import List, Dict, Optional
from dataclasses import dataclass
import threading
from urllib.parse import urlparse


@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    description: str
    author: str
    file_name: str
    file_size: int
    download_url: str = ""
    installed: bool = False
    enabled: bool = True
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "download_url": self.download_url,
            "installed": self.installed,
            "enabled": self.enabled,
            "dependencies": self.dependencies
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PluginInfo':
        return cls(**data)


class PluginManager:
    """插件管理器"""
    
    def __init__(self, server_directory: str):
        self.server_directory = server_directory
        self.plugins_directory = os.path.join(server_directory, "plugins")
        self.plugin_cache_file = os.path.join(server_directory, "plugin_cache.json")
        self.installed_plugins: List[PluginInfo] = []
        self.available_plugins: List[PluginInfo] = []
        
        # 创建插件目录
        os.makedirs(self.plugins_directory, exist_ok=True)
        
        # 加载已安装插件
        self.load_installed_plugins()
        
        # 加载可用插件列表
        self.load_available_plugins()
    
    def load_installed_plugins(self):
        """加载已安装的插件"""
        self.installed_plugins = []
        
        if not os.path.exists(self.plugins_directory):
            return
        
        for file_name in os.listdir(self.plugins_directory):
            if file_name.endswith('.jar'):
                plugin_info = self.get_plugin_info_from_jar(file_name)
                if plugin_info:
                    plugin_info.installed = True
                    self.installed_plugins.append(plugin_info)
    
    def get_plugin_info_from_jar(self, file_name: str) -> Optional[PluginInfo]:
        """从JAR文件获取插件信息"""
        jar_path = os.path.join(self.plugins_directory, file_name)
        
        try:
            # 尝试从文件名解析基本信息
            name = file_name.replace('.jar', '')
            version = "未知"
            
            # 尝试从plugin.yml获取详细信息
            try:
                with zipfile.ZipFile(jar_path, 'r') as jar:
                    if 'plugin.yml' in jar.namelist():
                        with jar.open('plugin.yml') as yml_file:
                            import yaml
                            plugin_data = yaml.safe_load(yml_file.read().decode('utf-8'))
                            name = plugin_data.get('name', name)
                            version = plugin_data.get('version', version)
                            description = plugin_data.get('description', '无描述')
                            author = plugin_data.get('author', '未知作者')
                            dependencies = plugin_data.get('depend', [])
                    else:
                        description = '无描述'
                        author = '未知作者'
                        dependencies = []
            except:
                description = '无描述'
                author = '未知作者'
                dependencies = []
            
            file_size = os.path.getsize(jar_path)
            
            return PluginInfo(
                name=name,
                version=version,
                description=description,
                author=author,
                file_name=file_name,
                file_size=file_size,
                installed=True,
                dependencies=dependencies
            )
        except Exception as e:
            print(f"解析插件文件失败 {file_name}: {e}")
            return None
    
    def load_available_plugins(self):
        """加载可用插件列表"""
        # 从缓存加载
        if os.path.exists(self.plugin_cache_file):
            try:
                with open(self.plugin_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.available_plugins = [PluginInfo.from_dict(p) for p in data]
                return
            except Exception as e:
                print(f"加载插件缓存失败: {e}")
        
        # 默认插件列表
        self.available_plugins = [
            PluginInfo(
                name="EssentialsX",
                version="2.20.1",
                description="基础服务器管理插件，提供传送、家园、经济等功能",
                author="EssentialsX Team",
                file_name="EssentialsX-2.20.1.jar",
                file_size=1024000,
                download_url="https://github.com/EssentialsX/Essentials/releases/download/2.20.1/EssentialsX-2.20.1.jar"
            ),
            PluginInfo(
                name="WorldEdit",
                version="7.2.15",
                description="强大的世界编辑工具",
                author="sk89q",
                file_name="worldedit-bukkit-7.2.15.jar",
                file_size=2048000,
                download_url="https://dev.bukkit.org/projects/worldedit/files/latest"
            ),
            PluginInfo(
                name="WorldGuard",
                version="7.0.9",
                description="区域保护插件",
                author="sk89q",
                file_name="worldguard-bukkit-7.0.9.jar",
                file_size=1536000,
                download_url="https://dev.bukkit.org/projects/worldguard/files/latest",
                dependencies=["WorldEdit"]
            ),
            PluginInfo(
                name="LuckPerms",
                version="5.4.102",
                description="权限管理插件",
                author="Luck",
                file_name="LuckPerms-Bukkit-5.4.102.jar",
                file_size=3072000,
                download_url="https://download.luckperms.net/1515/bukkit/loader/LuckPerms-Bukkit-5.4.102.jar"
            ),
            PluginInfo(
                name="Vault",
                version="1.7.3",
                description="经济系统API",
                author="MilkBowl",
                file_name="Vault.jar",
                file_size=512000,
                download_url="https://dev.bukkit.org/projects/vault/files/latest"
            )
        ]
        
        self.save_plugin_cache()
    
    def save_plugin_cache(self):
        """保存插件缓存"""
        try:
            with open(self.plugin_cache_file, 'w', encoding='utf-8') as f:
                data = [p.to_dict() for p in self.available_plugins]
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存插件缓存失败: {e}")
    
    def get_installed_plugins(self) -> List[PluginInfo]:
        """获取已安装插件列表"""
        return self.installed_plugins
    
    def get_available_plugins(self) -> List[PluginInfo]:
        """获取可用插件列表"""
        return self.available_plugins
    
    def is_plugin_installed(self, plugin_name: str) -> bool:
        """检查插件是否已安装"""
        return any(p.name == plugin_name for p in self.installed_plugins)
    
    def install_plugin(self, plugin: PluginInfo, progress_callback=None) -> bool:
        """安装插件"""
        if self.is_plugin_installed(plugin.name):
            return False
        
        try:
            # 检查依赖
            for dep in plugin.dependencies:
                if not self.is_plugin_installed(dep):
                    print(f"缺少依赖插件: {dep}")
                    return False
            
            # 下载插件
            if plugin.download_url:
                plugin_path = os.path.join(self.plugins_directory, plugin.file_name)
                
                if self.download_file(plugin.download_url, plugin_path, progress_callback):
                    # 更新插件信息
                    plugin.installed = True
                    self.installed_plugins.append(plugin)
                    return True
            
            return False
        except Exception as e:
            print(f"安装插件失败: {e}")
            return False
    
    def download_file(self, url: str, file_path: str, progress_callback=None) -> bool:
        """下载文件"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return True
        except Exception as e:
            print(f"下载文件失败: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        plugin = None
        for p in self.installed_plugins:
            if p.name == plugin_name:
                plugin = p
                break
        
        if not plugin:
            return False
        
        try:
            plugin_path = os.path.join(self.plugins_directory, plugin.file_name)
            if os.path.exists(plugin_path):
                os.remove(plugin_path)
            
            self.installed_plugins.remove(plugin)
            return True
        except Exception as e:
            print(f"卸载插件失败: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        for plugin in self.installed_plugins:
            if plugin.name == plugin_name:
                plugin.enabled = True
                return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        for plugin in self.installed_plugins:
            if plugin.name == plugin_name:
                plugin.enabled = False
                # 可以通过重命名文件来禁用插件
                plugin_path = os.path.join(self.plugins_directory, plugin.file_name)
                disabled_path = plugin_path + ".disabled"
                
                try:
                    if os.path.exists(plugin_path):
                        os.rename(plugin_path, disabled_path)
                    return True
                except Exception as e:
                    print(f"禁用插件失败: {e}")
                    return False
        return False
    
    def update_plugin_list(self, callback=None):
        """更新插件列表（异步）"""
        def update_async():
            try:
                # 这里可以从在线源更新插件列表
                # 目前使用静态列表
                if callback:
                    callback(True)
            except Exception as e:
                print(f"更新插件列表失败: {e}")
                if callback:
                    callback(False)
        
        threading.Thread(target=update_async, daemon=True).start()
    
    def search_plugins(self, keyword: str) -> List[PluginInfo]:
        """搜索插件"""
        results = []
        keyword_lower = keyword.lower()
        
        for plugin in self.available_plugins:
            if (keyword_lower in plugin.name.lower() or 
                keyword_lower in plugin.description.lower() or
                keyword_lower in plugin.author.lower()):
                results.append(plugin)
        
        return results
    
    def get_plugin_statistics(self) -> Dict:
        """获取插件统计信息"""
        total_installed = len(self.installed_plugins)
        enabled_count = sum(1 for p in self.installed_plugins if p.enabled)
        total_size = sum(p.file_size for p in self.installed_plugins)
        
        return {
            "total_installed": total_installed,
            "enabled_count": enabled_count,
            "disabled_count": total_installed - enabled_count,
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }