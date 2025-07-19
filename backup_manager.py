#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份管理模块
"""

import os
import json
import shutil
import zipfile
import datetime
import threading
import time
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class BackupInfo:
    """备份信息"""
    backup_id: str
    server_id: str
    server_name: str
    backup_time: str
    backup_size: int
    backup_path: str
    backup_type: str  # "manual", "auto", "scheduled"
    description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "backup_id": self.backup_id,
            "server_id": self.server_id,
            "server_name": self.server_name,
            "backup_time": self.backup_time,
            "backup_size": self.backup_size,
            "backup_path": self.backup_path,
            "backup_type": self.backup_type,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BackupInfo':
        return cls(**data)


class BackupManager:
    """备份管理器"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        self.backups_file = os.path.join(backup_dir, "backups.json")
        self.backups: List[BackupInfo] = []
        self.auto_backup_enabled = False
        self.auto_backup_interval = 3600  # 1小时
        self.auto_backup_thread = None
        self.max_backups_per_server = 10
        
        # 创建备份目录
        os.makedirs(backup_dir, exist_ok=True)
        self.load_backups()
    
    def load_backups(self):
        """加载备份列表"""
        if os.path.exists(self.backups_file):
            try:
                with open(self.backups_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.backups = [BackupInfo.from_dict(b) for b in data]
            except Exception as e:
                print(f"加载备份列表失败: {e}")
                self.backups = []
    
    def save_backups(self):
        """保存备份列表"""
        try:
            with open(self.backups_file, 'w', encoding='utf-8') as f:
                data = [b.to_dict() for b in self.backups]
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存备份列表失败: {e}")
    
    def create_backup(self, server_id: str, server_name: str, server_directory: str, 
                     backup_type: str = "manual", description: str = "") -> Optional[BackupInfo]:
        """创建备份"""
        try:
            # 生成备份ID和文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"{server_id}_{timestamp}"
            backup_filename = f"{server_name}_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # 创建ZIP备份
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(server_directory):
                    # 跳过日志文件和缓存文件
                    dirs[:] = [d for d in dirs if d not in ['logs', 'cache', '.git']]
                    
                    for file in files:
                        if file.endswith(('.log', '.log.gz', '.tmp')):
                            continue
                        
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, server_directory)
                        zipf.write(file_path, arc_path)
            
            # 获取备份大小
            backup_size = os.path.getsize(backup_path)
            
            # 创建备份信息
            backup_info = BackupInfo(
                backup_id=backup_id,
                server_id=server_id,
                server_name=server_name,
                backup_time=datetime.datetime.now().isoformat(),
                backup_size=backup_size,
                backup_path=backup_path,
                backup_type=backup_type,
                description=description
            )
            
            # 添加到备份列表
            self.backups.append(backup_info)
            self.save_backups()
            
            # 清理旧备份
            self.cleanup_old_backups(server_id)
            
            return backup_info
            
        except Exception as e:
            print(f"创建备份失败: {e}")
            return None
    
    def restore_backup(self, backup_id: str, target_directory: str) -> bool:
        """恢复备份"""
        backup_info = self.get_backup_by_id(backup_id)
        if not backup_info or not os.path.exists(backup_info.backup_path):
            return False
        
        try:
            # 清空目标目录
            if os.path.exists(target_directory):
                shutil.rmtree(target_directory)
            os.makedirs(target_directory, exist_ok=True)
            
            # 解压备份
            with zipfile.ZipFile(backup_info.backup_path, 'r') as zipf:
                zipf.extractall(target_directory)
            
            return True
            
        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        backup_info = self.get_backup_by_id(backup_id)
        if not backup_info:
            return False
        
        try:
            # 删除备份文件
            if os.path.exists(backup_info.backup_path):
                os.remove(backup_info.backup_path)
            
            # 从列表中移除
            self.backups = [b for b in self.backups if b.backup_id != backup_id]
            self.save_backups()
            
            return True
            
        except Exception as e:
            print(f"删除备份失败: {e}")
            return False
    
    def get_backup_by_id(self, backup_id: str) -> Optional[BackupInfo]:
        """根据ID获取备份信息"""
        for backup in self.backups:
            if backup.backup_id == backup_id:
                return backup
        return None
    
    def get_backups_by_server(self, server_id: str) -> List[BackupInfo]:
        """获取指定服务器的所有备份"""
        return [b for b in self.backups if b.server_id == server_id]
    
    def get_all_backups(self) -> List[BackupInfo]:
        """获取所有备份"""
        return sorted(self.backups, key=lambda x: x.backup_time, reverse=True)
    
    def cleanup_old_backups(self, server_id: str):
        """清理旧备份"""
        server_backups = self.get_backups_by_server(server_id)
        server_backups.sort(key=lambda x: x.backup_time, reverse=True)
        
        # 保留最新的N个备份
        if len(server_backups) > self.max_backups_per_server:
            old_backups = server_backups[self.max_backups_per_server:]
            for backup in old_backups:
                self.delete_backup(backup.backup_id)
    
    def get_backup_statistics(self) -> Dict:
        """获取备份统计信息"""
        total_backups = len(self.backups)
        total_size = sum(b.backup_size for b in self.backups)
        
        # 按服务器统计
        server_stats = {}
        for backup in self.backups:
            if backup.server_id not in server_stats:
                server_stats[backup.server_id] = {
                    "count": 0,
                    "size": 0,
                    "latest": None
                }
            
            server_stats[backup.server_id]["count"] += 1
            server_stats[backup.server_id]["size"] += backup.backup_size
            
            if (server_stats[backup.server_id]["latest"] is None or 
                backup.backup_time > server_stats[backup.server_id]["latest"]):
                server_stats[backup.server_id]["latest"] = backup.backup_time
        
        return {
            "total_backups": total_backups,
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "server_stats": server_stats
        }
    
    def start_auto_backup(self, multi_server_manager):
        """启动自动备份"""
        if self.auto_backup_enabled:
            return
        
        self.auto_backup_enabled = True
        self.auto_backup_thread = threading.Thread(
            target=self._auto_backup_worker,
            args=(multi_server_manager,),
            daemon=True
        )
        self.auto_backup_thread.start()
    
    def stop_auto_backup(self):
        """停止自动备份"""
        self.auto_backup_enabled = False
        if self.auto_backup_thread:
            self.auto_backup_thread.join(timeout=5)
    
    def _auto_backup_worker(self, multi_server_manager):
        """自动备份工作线程"""
        while self.auto_backup_enabled:
            try:
                # 为所有服务器创建备份
                for server in multi_server_manager.get_all_servers():
                    if not server.is_running():  # 只备份未运行的服务器
                        self.create_backup(
                            server.server_id,
                            server.name,
                            server.directory,
                            backup_type="auto",
                            description="自动备份"
                        )
                
                # 等待下次备份
                time.sleep(self.auto_backup_interval)
                
            except Exception as e:
                print(f"自动备份出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再试
    
    def set_auto_backup_interval(self, interval_hours: float):
        """设置自动备份间隔（小时）"""
        self.auto_backup_interval = int(interval_hours * 3600)
    
    def set_max_backups_per_server(self, max_backups: int):
        """设置每个服务器最大备份数量"""
        self.max_backups_per_server = max_backups
    
    def export_backup_list(self, file_path: str):
        """导出备份列表"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                data = {
                    "export_time": datetime.datetime.now().isoformat(),
                    "backups": [b.to_dict() for b in self.backups],
                    "statistics": self.get_backup_statistics()
                }
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"导出备份列表失败: {e}")
    
    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"