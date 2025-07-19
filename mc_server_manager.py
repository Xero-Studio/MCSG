#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Server Manager - 核心管理模块
"""

import os
import json
import subprocess
import configparser
from typing import Dict, Any, Optional


class MinecraftServerManager:
    """Minecraft服务器管理器"""
    
    def __init__(self, config_file: str = "server_config.json"):
        self.config_file = config_file
        self.server_process: Optional[subprocess.Popen] = None
        self.default_config = {
            "memory": "2G",
            "core": "server.jar",
            "motd": "A Minecraft Server",
            "port": "25565",
            "max_players": "20",
            "view_distance": "10",
            "online_mode": "true",
            "jvm_args": "-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions",
            "server_args": "nogui",
            "level_seed": "",
            "difficulty": "easy",
            "gamemode": "survival",
            "pvp": "true",
            "spawn_protection": "16"
        }
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # 确保所有默认配置项都存在
                for key, value in self.default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except Exception as e:
                print(f"加载配置失败: {e}")
                self.config = self.default_config.copy()
        else:
            self.config = self.default_config.copy()
            self.save_config()
    
    def save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get_config_value(self, key: str) -> str:
        """获取配置值"""
        return self.config.get(key, self.default_config.get(key, ""))
    
    def set_config_value(self, key: str, value: str) -> None:
        """设置配置值"""
        self.config[key] = value
    
    def create_server_properties(self) -> None:
        """创建server.properties文件"""
        properties = {
            "motd": self.get_config_value("motd"),
            "server-port": self.get_config_value("port"),
            "max-players": self.get_config_value("max_players"),
            "view-distance": self.get_config_value("view_distance"),
            "online-mode": self.get_config_value("online_mode"),
            "level-seed": self.get_config_value("level_seed"),
            "difficulty": self.get_config_value("difficulty"),
            "gamemode": self.get_config_value("gamemode"),
            "pvp": self.get_config_value("pvp"),
            "spawn-protection": self.get_config_value("spawn_protection")
        }
        
        try:
            with open("server.properties", 'w', encoding='utf-8') as f:
                for key, value in properties.items():
                    f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"创建server.properties失败: {e}")
    
    def get_java_command(self) -> list:
        """构建Java启动命令"""
        memory = self.get_config_value("memory")
        core = self.get_config_value("core")
        jvm_args = self.get_config_value("jvm_args")
        server_args = self.get_config_value("server_args")
        
        cmd = ["java", f"-Xms{memory}", f"-Xmx{memory}"]
        
        if jvm_args:
            cmd.extend(jvm_args.split())
        
        cmd.extend(["-jar", core])
        
        if server_args:
            cmd.extend(server_args.split())
        
        return cmd
    
    def is_server_running(self) -> bool:
        """检查服务器是否在运行"""
        return self.server_process is not None and self.server_process.poll() is None
    
    def start_server(self) -> bool:
        """启动服务器"""
        if self.is_server_running():
            return False
        
        core_file = self.get_config_value("core")
        if not os.path.exists(core_file):
            raise FileNotFoundError(f"服务器核心文件 '{core_file}' 不存在")
        
        # 创建server.properties
        self.create_server_properties()
        
        # 构建启动命令
        cmd = self.get_java_command()
        
        try:
            # Windows下隐藏控制台窗口
            startupinfo = None
            if os.name == 'nt':  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            return True
        except Exception as e:
            print(f"启动服务器失败: {e}")
            return False
    
    def stop_server(self) -> bool:
        """停止服务器"""
        if not self.is_server_running():
            return False
        
        try:
            # 发送stop命令
            self.server_process.stdin.write("stop\n")
            self.server_process.stdin.flush()
            
            # 等待进程结束
            self.server_process.wait(timeout=30)
            self.server_process = None
            return True
        except subprocess.TimeoutExpired:
            # 强制终止
            self.server_process.terminate()
            self.server_process = None
            return True
        except Exception as e:
            print(f"停止服务器失败: {e}")
            return False
    
    def send_command(self, command: str) -> bool:
        """发送命令到服务器"""
        if not self.is_server_running():
            return False
        
        try:
            self.server_process.stdin.write(f"{command}\n")
            self.server_process.stdin.flush()
            return True
        except Exception as e:
            print(f"发送命令失败: {e}")
            return False
    
    def read_server_output(self) -> Optional[str]:
        """读取服务器输出"""
        if not self.is_server_running():
            return None
        
        try:
            return self.server_process.stdout.readline()
        except Exception:
            return None


def main():
    """命令行版本主函数"""
    manager = MinecraftServerManager()
    
    print("=== Minecraft Server Manager ===")
    print("1. 启动服务器")
    print("2. 停止服务器")
    print("3. 查看配置")
    print("4. 修改配置")
    print("5. 退出")
    
    while True:
        try:
            choice = input("\n请选择操作: ").strip()
            
            if choice == "1":
                if manager.start_server():
                    print("服务器启动成功!")
                else:
                    print("服务器启动失败!")
            
            elif choice == "2":
                if manager.stop_server():
                    print("服务器停止成功!")
                else:
                    print("服务器停止失败!")
            
            elif choice == "3":
                print("\n当前配置:")
                for key, value in manager.config.items():
                    print(f"  {key}: {value}")
            
            elif choice == "4":
                key = input("请输入配置项名称: ").strip()
                if key in manager.config:
                    value = input(f"请输入新值 (当前: {manager.config[key]}): ").strip()
                    if value:
                        manager.set_config_value(key, value)
                        manager.save_config()
                        print("配置已更新!")
                else:
                    print("配置项不存在!")
            
            elif choice == "5":
                if manager.is_server_running():
                    manager.stop_server()
                break
            
            else:
                print("无效选择!")
                
        except KeyboardInterrupt:
            print("\n正在退出...")
            if manager.is_server_running():
                manager.stop_server()
            break
        except Exception as e:
            print(f"操作失败: {e}")


if __name__ == "__main__":
    main()