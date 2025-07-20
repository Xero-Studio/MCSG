#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Server Manager
"""


import os
import sys
import subprocess
import configparser
import json
from pathlib import Path
import time

class MinecraftServerManager:
    def __init__(self):
        self.config_file = "Config.ini"
        self.eula_file = "eula.txt"
        self.properties_file = "server.properties"
        
        # 默认配置
        self.defaults = {
            'memory': '2G',
            'core': 'server.jar',
            'online_mode': 'true',
            'motd': '欢迎来到我的Minecraft服务器！',
            'port': '25565',
            'max_players': '20',
            'view_distance': '10',
            'level_seed': '15',
            'jvm_args': '-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions',
            'server_args': 'nogui'
        }
        
        self.config = configparser.ConfigParser()
        self.ensure_eula()
        self.load_config()
    
    def ensure_eula(self):
        """确保EULA文件存在并已同意"""
        if not os.path.exists(self.eula_file):
            with open(self.eula_file, 'w', encoding='utf-8') as f:
                f.write('eula=true\n')
            print("EULA已经默认同意，如果您不同意Mojang Studios的EULA，请关闭此程序。")
    
    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            self.create_config()
        
        self.config.read(self.config_file, encoding='utf-8')
        
        # 确保有默认section
        if not self.config.has_section('SERVER'):
            self.config.add_section('SERVER')
            
        # 设置默认值
        for key, value in self.defaults.items():
            if not self.config.has_option('SERVER', key):
                self.config.set('SERVER', key, value)
    
    def create_config(self):
        """创建配置文件"""
        self.config.add_section('SERVER')
        for key, value in self.defaults.items():
            self.config.set('SERVER', key, value)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
        print(f"已创建配置文件: {self.config_file}")
    
    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_config_value(self, key):
        """获取配置值"""
        return self.config.get('SERVER', key, fallback=self.defaults.get(key, ''))
    
    def set_config_value(self, key, value):
        """设置配置值"""
        self.config.set('SERVER', key, value)
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_main_menu(self):
        """显示主菜单"""
        self.clear_screen()
        print("=" * 30)
        print("   Minecraft Server Manager")
        print("=" * 30)
        print("1. 启动服务器")
        print("2. 配置服务器")
        print("3. 编辑配置文件")
        print("4. 退出")
        print()
        
        while True:
            try:
                choice = input("请选择操作 (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    return int(choice)
                else:
                    print("请输入有效选项 (1-4)")
            except (ValueError, KeyboardInterrupt):
                print("\n程序已退出")
                sys.exit(0)
    
    def start_server(self):
        """启动服务器"""
        memory = self.get_config_value('memory')
        core = self.get_config_value('core')
        jvm_args = self.get_config_value('jvm_args')
        server_args = self.get_config_value('server_args')
        
        # 检查核心文件是否存在
        if not os.path.exists(core):
            print(f"错误: 服务器核心文件 '{core}' 不存在!")
            print("请检查配置或将服务器核心文件放在当前目录下")
            input("按回车键继续...")
            return
        
        # 创建server.properties文件
        self.create_properties()
        
        print("正在启动服务器...")
        print(f"使用内存: {memory}")
        print(f"服务器核心: {core}")
        print()
        
        # 构建Java命令
        cmd = [
            'java',
            f'-Xms{memory}',
            f'-Xmx{memory}'
        ]
        
        # 添加JVM参数
        if jvm_args:
            cmd.extend(jvm_args.split())
        
        cmd.extend(['-jar', core])
        
        # 添加服务器参数
        if server_args:
            cmd.extend(server_args.split())
        
        try:
            # 启动服务器
            process = subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print("\n服务器启动失败，请检查:")
            print("1. 内存设置是否过大")
            print("2. 核心文件是否存在")
            print("3. Java是否安装正确")
            print()
            input("按回车键继续...")
        except FileNotFoundError:
            print("\n错误: 找不到Java!")
            print("请确保已安装Java并添加到系统PATH中")
            input("按回车键继续...")
    
    def create_properties(self):
        """创建或更新server.properties文件"""
        properties = {
            'online-mode': self.get_config_value('online_mode'),
            'motd': self.get_config_value('motd'),
            'server-port': self.get_config_value('port'),
            'max-players': self.get_config_value('max_players'),
            'view-distance': self.get_config_value('view_distance'),
            'level-seed': self.get_config_value('level_seed')
        }
        
        # 读取现有的properties文件（如果存在）
        existing_props = {}
        if os.path.exists(self.properties_file):
            # 尝试多种编码方式读取
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']
            content_read = False
            
            for encoding in encodings:
                try:
                    with open(self.properties_file, 'r', encoding=encoding) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                existing_props[key.strip()] = value.strip()
                    content_read = True
                    print(f"成功使用 {encoding} 编码读取 server.properties")
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if not content_read:
                print("警告: 无法读取现有的 server.properties 文件，将创建新文件")
        
        # 更新属性
        existing_props.update(properties)
        
        # 处理MOTD中文编码
        motd_value = existing_props.get('motd', '')
        if motd_value:
            # 确保MOTD使用正确的编码
            try:
                # 如果包含中文字符，进行特殊处理
                if any('\u4e00' <= char <= '\u9fff' for char in motd_value):
                    # 中文字符范围检测
                    print(f"检测到中文MOTD: {motd_value}")
                    # 使用Unicode转义或保持UTF-8编码
                    existing_props['motd'] = motd_value
            except Exception as e:
                print(f"MOTD编码处理警告: {e}")
        
        # 写入文件，使用UTF-8编码并添加BOM以确保兼容性
        try:
            with open(self.properties_file, 'w', encoding='utf-8-sig', newline='\n') as f:
                # 添加注释说明编码
                f.write("# Minecraft server properties\n")
                f.write("# File encoding: UTF-8\n")
                f.write("#\n")
                
                # 写入属性，按字母顺序排序以保持一致性
                for key in sorted(existing_props.keys()):
                    value = existing_props[key]
                    f.write(f"{key}={value}\n")
            
            print(f"✓ server.properties 已更新 (UTF-8编码)")
            
        except Exception as e:
            print(f"写入 server.properties 时出错: {e}")
            # 备用方案：使用标准UTF-8编码
            try:
                with open(self.properties_file, 'w', encoding='utf-8') as f:
                    for key, value in existing_props.items():
                        f.write(f"{key}={value}\n")
                print("✓ 使用备用方案写入 server.properties")
            except Exception as e2:
                print(f"备用方案也失败: {e2}")
    
    def configure_server(self):
        """配置服务器"""
        while True:
            self.clear_screen()
            print("=" * 30)
            print("       服务器配置")
            print("=" * 30)
            print("当前配置:")
            print(f"1. 内存分配: {self.get_config_value('memory')}")
            print(f"2. 服务器核心: {self.get_config_value('core')}")
            print(f"3. 正版验证: {self.get_config_value('online_mode')}")
            print(f"4. MOTD描述: {self.get_config_value('motd')}")
            print(f"5. 服务器端口: {self.get_config_value('port')}")
            print(f"6. 最大玩家数: {self.get_config_value('max_players')}")
            print(f"7. 视距: {self.get_config_value('view_distance')}")
            print(f"8. 世界种子: {self.get_config_value('level_seed')}")
            print(f"9. JVM参数: {self.get_config_value('jvm_args')}")
            print(f"10. 服务器参数: {self.get_config_value('server_args')}")
            print("0. 返回主菜单")
            print()
            
            try:
                choice = input("选择要修改的选项 (0-10): ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    new_value = input("输入新内存分配 (例如 2G, 4G): ").strip()
                    if new_value:
                        self.set_config_value('memory', new_value)
                elif choice == '2':
                    print("可用的服务器核心:")
                    jar_files = [f for f in os.listdir('.') if f.endswith('.jar')]
                    if jar_files:
                        for jar in jar_files:
                            print(f"  {jar}")
                    else:
                        print("  未找到.jar文件")
                    new_value = input("输入核心文件名: ").strip()
                    if new_value:
                        self.set_config_value('core', new_value)
                elif choice == '3':
                    new_value = input("启用正版验证? (true/false): ").strip().lower()
                    if new_value in ['true', 'false']:
                        self.set_config_value('online_mode', new_value)
                elif choice == '4':
                    print("当前MOTD:", self.get_config_value('motd'))
                    print("提示: 支持中文字符，如 '欢迎来到我的服务器！'")
                    new_value = input("输入新MOTD描述: ").strip()
                    if new_value:
                        self.set_config_value('motd', new_value)
                        print(f"✓ MOTD已更新为: {new_value}")
                elif choice == '5':
                    new_value = input("输入新端口号: ").strip()
                    if new_value.isdigit():
                        self.set_config_value('port', new_value)
                elif choice == '6':
                    new_value = input("输入最大玩家数: ").strip()
                    if new_value.isdigit():
                        self.set_config_value('max_players', new_value)
                elif choice == '7':
                    new_value = input("输入视距 (4-32): ").strip()
                    if new_value.isdigit() and 4 <= int(new_value) <= 32:
                        self.set_config_value('view_distance', new_value)
                elif choice == '8':
                    new_value = input("输入世界种子: ").strip()
                    if new_value:
                        self.set_config_value('level_seed', new_value)
                elif choice == '9':
                    new_value = input("输入JVM参数: ").strip()
                    if new_value:
                        self.set_config_value('jvm_args', new_value)
                elif choice == '10':
                    new_value = input("输入服务器参数: ").strip()
                    if new_value:
                        self.set_config_value('server_args', new_value)
                else:
                    print("请输入有效选项 (0-10)")
                    time.sleep(1)
                    continue
                
                # 保存配置
                self.save_config()
                
            except KeyboardInterrupt:
                print("\n返回主菜单...")
                break
    
    def edit_config_file(self):
        """编辑配置文件"""
        if os.name == 'nt':  # Windows
            os.system(f'notepad "{self.config_file}"')
        else:  # Linux/Mac
            editor = os.environ.get('EDITOR', 'nano')
            os.system(f'{editor} "{self.config_file}"')
        
        # 重新加载配置
        self.load_config()
    
    def run(self):
        """运行主程序"""
        print("Minecraft Server Manager")
        print()
        
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == 1:
                    self.start_server()
                elif choice == 2:
                    self.configure_server()
                elif choice == 3:
                    self.edit_config_file()
                elif choice == 4:
                    print("感谢使用!")
                    break
                    
            except KeyboardInterrupt:
                print("\n\n感谢使用!")
                break

def main():
    """主函数"""
    try:
        manager = MinecraftServerManager()
        manager.run()
    except Exception as e:
        print(f"程序运行出错: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()