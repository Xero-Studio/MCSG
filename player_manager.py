#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
玩家管理模块
"""

import json
import os
import time
import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class PlayerInfo:
    """玩家信息"""
    username: str
    uuid: str = ""
    display_name: str = ""
    first_join: str = ""
    last_seen: str = ""
    play_time: int = 0  # 游戏时间（分钟）
    is_online: bool = False
    is_op: bool = False
    is_banned: bool = False
    is_whitelisted: bool = False
    ban_reason: str = ""
    ban_expires: str = ""
    ip_address: str = ""
    location: Dict = None
    
    def __post_init__(self):
        if self.location is None:
            self.location = {"world": "", "x": 0, "y": 0, "z": 0}
        if not self.display_name:
            self.display_name = self.username
    
    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "uuid": self.uuid,
            "display_name": self.display_name,
            "first_join": self.first_join,
            "last_seen": self.last_seen,
            "play_time": self.play_time,
            "is_online": self.is_online,
            "is_op": self.is_op,
            "is_banned": self.is_banned,
            "is_whitelisted": self.is_whitelisted,
            "ban_reason": self.ban_reason,
            "ban_expires": self.ban_expires,
            "ip_address": self.ip_address,
            "location": self.location
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlayerInfo':
        return cls(**data)


class PlayerManager:
    """玩家管理器"""
    
    def __init__(self, server_directory: str, server_manager=None):
        self.server_directory = server_directory
        self.server_manager = server_manager
        self.players_file = os.path.join(server_directory, "player_data.json")
        self.whitelist_file = os.path.join(server_directory, "whitelist.json")
        self.banned_players_file = os.path.join(server_directory, "banned-players.json")
        self.banned_ips_file = os.path.join(server_directory, "banned-ips.json")
        self.ops_file = os.path.join(server_directory, "ops.json")
        
        self.players: Dict[str, PlayerInfo] = {}
        self.online_players: Set[str] = set()
        
        self.load_player_data()
    
    def load_player_data(self):
        """加载玩家数据"""
        # 加载自定义玩家数据
        if os.path.exists(self.players_file):
            try:
                with open(self.players_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.players = {name: PlayerInfo.from_dict(info) for name, info in data.items()}
            except Exception as e:
                print(f"加载玩家数据失败: {e}")
        
        # 加载服务器文件
        self._load_server_files()
    
    def _load_server_files(self):
        """加载服务器文件"""
        # 加载白名单
        self._load_whitelist()
        
        # 加载封禁列表
        self._load_banned_players()
        
        # 加载OP列表
        self._load_ops()
    
    def _load_whitelist(self):
        """加载白名单"""
        if os.path.exists(self.whitelist_file):
            try:
                with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                    whitelist = json.load(f)
                    for entry in whitelist:
                        username = entry.get('name', '')
                        if username:
                            if username not in self.players:
                                self.players[username] = PlayerInfo(username=username)
                            self.players[username].is_whitelisted = True
                            self.players[username].uuid = entry.get('uuid', '')
            except Exception as e:
                print(f"加载白名单失败: {e}")
    
    def _load_banned_players(self):
        """加载封禁玩家列表"""
        if os.path.exists(self.banned_players_file):
            try:
                with open(self.banned_players_file, 'r', encoding='utf-8') as f:
                    banned = json.load(f)
                    for entry in banned:
                        username = entry.get('name', '')
                        if username:
                            if username not in self.players:
                                self.players[username] = PlayerInfo(username=username)
                            self.players[username].is_banned = True
                            self.players[username].ban_reason = entry.get('reason', '')
                            self.players[username].ban_expires = entry.get('expires', '')
                            self.players[username].uuid = entry.get('uuid', '')
            except Exception as e:
                print(f"加载封禁列表失败: {e}")
    
    def _load_ops(self):
        """加载OP列表"""
        if os.path.exists(self.ops_file):
            try:
                with open(self.ops_file, 'r', encoding='utf-8') as f:
                    ops = json.load(f)
                    for entry in ops:
                        username = entry.get('name', '')
                        if username:
                            if username not in self.players:
                                self.players[username] = PlayerInfo(username=username)
                            self.players[username].is_op = True
                            self.players[username].uuid = entry.get('uuid', '')
            except Exception as e:
                print(f"加载OP列表失败: {e}")
    
    def save_player_data(self):
        """保存玩家数据"""
        try:
            data = {name: player.to_dict() for name, player in self.players.items()}
            with open(self.players_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存玩家数据失败: {e}")
    
    def get_all_players(self) -> List[PlayerInfo]:
        """获取所有玩家"""
        return list(self.players.values())
    
    def get_online_players(self) -> List[PlayerInfo]:
        """获取在线玩家"""
        return [player for player in self.players.values() if player.is_online]
    
    def get_player(self, username: str) -> Optional[PlayerInfo]:
        """获取指定玩家"""
        return self.players.get(username)
    
    def add_player(self, username: str, uuid: str = "") -> PlayerInfo:
        """添加玩家"""
        if username not in self.players:
            self.players[username] = PlayerInfo(
                username=username,
                uuid=uuid,
                first_join=datetime.now().isoformat()
            )
        return self.players[username]
    
    def update_player_online_status(self, username: str, is_online: bool):
        """更新玩家在线状态"""
        if username not in self.players:
            self.add_player(username)
        
        self.players[username].is_online = is_online
        if is_online:
            self.online_players.add(username)
        else:
            self.online_players.discard(username)
            self.players[username].last_seen = datetime.now().isoformat()
    
    def kick_player(self, username: str, reason: str = "被管理员踢出") -> bool:
        """踢出玩家"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"kick {username} {reason}"
            return self.server_manager.send_command(command)
        except Exception as e:
            print(f"踢出玩家失败: {e}")
            return False
    
    def ban_player(self, username: str, reason: str = "违反服务器规则", duration: str = "") -> bool:
        """封禁玩家"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            if duration:
                # 临时封禁
                command = f"tempban {username} {duration} {reason}"
            else:
                # 永久封禁
                command = f"ban {username} {reason}"
            
            if self.server_manager.send_command(command):
                # 更新本地数据
                if username not in self.players:
                    self.add_player(username)
                
                self.players[username].is_banned = True
                self.players[username].ban_reason = reason
                if duration:
                    # 计算过期时间
                    expire_time = self._calculate_ban_expire_time(duration)
                    self.players[username].ban_expires = expire_time
                
                self.save_player_data()
                return True
        except Exception as e:
            print(f"封禁玩家失败: {e}")
        
        return False
    
    def unban_player(self, username: str) -> bool:
        """解封玩家"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"pardon {username}"
            if self.server_manager.send_command(command):
                # 更新本地数据
                if username in self.players:
                    self.players[username].is_banned = False
                    self.players[username].ban_reason = ""
                    self.players[username].ban_expires = ""
                    self.save_player_data()
                return True
        except Exception as e:
            print(f"解封玩家失败: {e}")
        
        return False
    
    def op_player(self, username: str) -> bool:
        """给予玩家OP权限"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"op {username}"
            if self.server_manager.send_command(command):
                # 更新本地数据
                if username not in self.players:
                    self.add_player(username)
                
                self.players[username].is_op = True
                self.save_player_data()
                return True
        except Exception as e:
            print(f"给予OP权限失败: {e}")
        
        return False
    
    def deop_player(self, username: str) -> bool:
        """移除玩家OP权限"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"deop {username}"
            if self.server_manager.send_command(command):
                # 更新本地数据
                if username in self.players:
                    self.players[username].is_op = False
                    self.save_player_data()
                return True
        except Exception as e:
            print(f"移除OP权限失败: {e}")
        
        return False
    
    def whitelist_add(self, username: str) -> bool:
        """添加到白名单"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"whitelist add {username}"
            if self.server_manager.send_command(command):
                # 更新本地数据
                if username not in self.players:
                    self.add_player(username)
                
                self.players[username].is_whitelisted = True
                self.save_player_data()
                return True
        except Exception as e:
            print(f"添加白名单失败: {e}")
        
        return False
    
    def whitelist_remove(self, username: str) -> bool:
        """从白名单移除"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"whitelist remove {username}"
            if self.server_manager.send_command(command):
                # 更新本地数据
                if username in self.players:
                    self.players[username].is_whitelisted = False
                    self.save_player_data()
                return True
        except Exception as e:
            print(f"移除白名单失败: {e}")
        
        return False
    
    def teleport_player(self, username: str, target: str) -> bool:
        """传送玩家"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"tp {username} {target}"
            return self.server_manager.send_command(command)
        except Exception as e:
            print(f"传送玩家失败: {e}")
            return False
    
    def send_message_to_player(self, username: str, message: str) -> bool:
        """向玩家发送消息"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"tell {username} {message}"
            return self.server_manager.send_command(command)
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def broadcast_message(self, message: str) -> bool:
        """广播消息"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return False
        
        try:
            command = f"say {message}"
            return self.server_manager.send_command(command)
        except Exception as e:
            print(f"广播消息失败: {e}")
            return False
    
    def _calculate_ban_expire_time(self, duration: str) -> str:
        """计算封禁过期时间"""
        try:
            # 解析时间格式 (例如: 1d, 2h, 30m)
            match = re.match(r'(\d+)([dhm])', duration.lower())
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                
                now = datetime.now()
                if unit == 'd':
                    expire_time = now + timedelta(days=amount)
                elif unit == 'h':
                    expire_time = now + timedelta(hours=amount)
                elif unit == 'm':
                    expire_time = now + timedelta(minutes=amount)
                else:
                    return ""
                
                return expire_time.isoformat()
        except Exception:
            pass
        
        return ""
    
    def get_player_statistics(self) -> Dict:
        """获取玩家统计信息"""
        total_players = len(self.players)
        online_players = len(self.get_online_players())
        banned_players = len([p for p in self.players.values() if p.is_banned])
        op_players = len([p for p in self.players.values() if p.is_op])
        whitelisted_players = len([p for p in self.players.values() if p.is_whitelisted])
        
        return {
            "total_players": total_players,
            "online_players": online_players,
            "banned_players": banned_players,
            "op_players": op_players,
            "whitelisted_players": whitelisted_players
        }
    
    def search_players(self, keyword: str) -> List[PlayerInfo]:
        """搜索玩家"""
        results = []
        keyword_lower = keyword.lower()
        
        for player in self.players.values():
            if (keyword_lower in player.username.lower() or
                keyword_lower in player.display_name.lower()):
                results.append(player)
        
        return results
    
    def export_player_list(self, file_path: str) -> bool:
        """导出玩家列表"""
        try:
            data = {
                "export_time": datetime.now().isoformat(),
                "statistics": self.get_player_statistics(),
                "players": [player.to_dict() for player in self.players.values()]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"导出玩家列表失败: {e}")
            return False