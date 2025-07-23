import os
import sys
import platform
import json
import shutil
import traceback
import time
import subprocess

# 清屏函数（跨平台）
def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def init():
    global config_path, server_dir
    # 获取当前脚本所在目录的绝对路径
    server_dir = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(server_dir, "config.txt")
    
    # 确保工作目录正确
    os.chdir(server_dir)
    print(f"服务器目录: {server_dir}")

def load_config():
    """加载配置文件，如果不存在则创建默认配置"""
    default_config = {
        # ============== 重要配置项 ==============
        "java_path": "",       # Java可执行文件路径 (必须配置)
        "memory": "4",         # 服务器内存 (单位GB, 必须配置)
        "online_mode": "true",  # 正版验证开关 (重要)
        # ============== 其他配置项 ==============
        "server_port": "25565",
        "max_players": "20",
        "spawn_protection": "16",
        "view_distance": "10",
        "motd": "A Minecraft Server",
        "pvp": "true",
        "difficulty": "easy",
        "gamemode": "survival",
        "enable_command_block": "false"
    }
    
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    # 加载现有配置
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            
            # 确保新版本添加的配置项存在
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
            
            return config
    except json.JSONDecodeError:
        print("错误: 配置文件格式不正确，使用默认配置")
        shutil.copy(config_path, config_path + ".bak")
        print(f"原始配置文件已备份为: {config_path}.bak")
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config

def save_config(config):
    """保存配置到文件"""
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

def get_user_input(prompt, default_value, validation_func=None, required=False):
    """获取用户输入，提供默认值"""
    while True:
        user_input = input(f"{prompt} [默认: {default_value}]: ").strip()
        if not user_input:
            if required and not default_value:
                print("此项为必填项，请输入值")
                continue
            return default_value
        
        if validation_func and not validation_func(user_input):
            print("输入无效，请重新输入")
            continue
        
        return user_input

def validate_memory(input_val):
    """验证内存输入是否为有效数字"""
    try:
        value = int(input_val)
        return value > 0 and value <= 64  # 限制在1-64GB之间
    except ValueError:
        return False

def validate_java_path(input_val):
    """验证Java路径是否存在"""
    return os.path.exists(input_val)

def validate_java_executable(input_val):
    """验证Java路径是否可执行"""
    if not os.path.exists(input_val):
        return False
    try:
        # 尝试运行Java -version命令来验证
        result = subprocess.run([input_val, "-version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               timeout=5)
        return result.returncode == 0
    except:
        return False

def validate_boolean(input_val):
    """验证布尔值输入"""
    return input_val.lower() in ["true", "false", "t", "f", "yes", "no", "y", "n"]

def validate_port(input_val):
    """验证端口号输入"""
    try:
        port = int(input_val)
        return 1 <= port <= 65535
    except ValueError:
        return False

def validate_difficulty(input_val):
    """验证难度设置"""
    return input_val.lower() in ["peaceful", "easy", "normal", "hard"]

def validate_gamemode(input_val):
    """验证游戏模式"""
    return input_val.lower() in ["survival", "creative", "adventure", "spectator"]

def accept_eula():
    """同意EULA协议"""
    eula_file = os.path.join(server_dir, "eula.txt")
    if os.path.exists(eula_file):
        with open(eula_file, "r") as f:
            content = f.read()
        
        # 确保EULA已同意
        if "eula=true" not in content.lower():
            with open(eula_file, "w") as f:
                f.write("eula=true")
    else:
        # 创建新的eula文件
        with open(eula_file, "w") as f:
            f.write("eula=true")

def create_server_properties(config):
    """创建或更新server.properties文件"""
    properties_file = os.path.join(server_dir, "server.properties")
    properties = {}
    
    # 如果文件已存在，加载现有属性
    if os.path.exists(properties_file):
        with open(properties_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key_value = line.split("=", 1)
                    if len(key_value) == 2:
                        properties[key_value[0]] = key_value[1]
    
    # 更新关键属性
    properties.update({
        "online-mode": config["online_mode"],
        "server-port": config["server_port"],
        "max-players": config["max_players"],
        "spawn-protection": config["spawn_protection"],
        "view-distance": config["view_distance"],
        "motd": config["motd"],
        "pvp": config["pvp"],
        "difficulty": config["difficulty"],
        "gamemode": config["gamemode"],
        "enable-command-block": config["enable_command_block"]
    })
    
    # 写入文件
    with open(properties_file, "w") as f:
        f.write("# Minecraft server properties\n")
        f.write("# Generated by PMSS Server Tool\n\n")
        for key, value in properties.items():
            f.write(f"{key}={value}\n")

def configure_server():
    """配置服务器设置"""
    config = load_config()
    
    print("\n" + "="*50)
    print(" Minecraft 服务器配置")
    print("="*50)
    
    # ============== 重要配置项 ==============
    print("\n[重要] Java路径配置 (必须)")
    java_path = get_user_input("输入Java可执行文件完整路径", config["java_path"], validate_java_executable, required=True)
    config["java_path"] = java_path
    
    # ============== 重要配置项 ==============
    print("\n[重要] 服务器内存配置")
    memory = get_user_input("输入服务器内存分配(单位GB)", config["memory"], validate_memory, required=True)
    config["memory"] = memory
    
    # ============== 重要配置项 ==============
    print("\n[重要] 正版验证设置")
    online_mode = get_user_input("启用正版验证? (true/false)", config["online_mode"], validate_boolean)
    if online_mode.lower() in ["true", "t", "yes", "y"]:
        config["online_mode"] = "true"
    else:
        config["online_mode"] = "false"
    
    # ============== 其他配置项 ==============
    print("\n[可选] 服务器端口配置")
    server_port = get_user_input("服务器端口号 (1-65535)", config["server_port"], validate_port)
    config["server_port"] = server_port
    
    print("\n[可选] 最大玩家数量")
    max_players = get_user_input("最大玩家数量", config["max_players"])
    config["max_players"] = max_players
    
    print("\n[可选] 高级配置 (按Enter使用默认值):")
    spawn_protection = get_user_input("出生点保护半径", config["spawn_protection"])
    config["spawn_protection"] = spawn_protection
    
    view_distance = get_user_input("视距", config["view_distance"])
    config["view_distance"] = view_distance
    
    motd = get_user_input("服务器描述 (MOTD)", config["motd"])
    config["motd"] = motd
    
    pvp = get_user_input("允许PVP? (true/false)", config["pvp"], validate_boolean)
    if pvp.lower() in ["true", "t", "yes", "y"]:
        config["pvp"] = "true"
    else:
        config["pvp"] = "false"
    
    difficulty = get_user_input("难度 (peaceful/easy/normal/hard)", config["difficulty"], validate_difficulty)
    config["difficulty"] = difficulty
    
    gamemode = get_user_input("游戏模式 (survival/creative/adventure/spectator)", config["gamemode"], validate_gamemode)
    config["gamemode"] = gamemode
    
    command_block = get_user_input("启用命令方块? (true/false)", config["enable_command_block"], validate_boolean)
    if command_block.lower() in ["true", "t", "yes", "y"]:
        config["enable_command_block"] = "true"
    else:
        config["enable_command_block"] = "false"
    
    # 保存配置
    save_config(config)
    create_server_properties(config)
    
    print("\n配置已保存!")
    print("重要提示: 请确保server.jar文件已放置在服务器目录下")
    print(f"当前目录: {server_dir}")
    return config

def start_server(config):
    """启动服务器的核心函数"""
    java_path = config["java_path"]
    server_jar = os.path.join(server_dir, "server.jar")
    
    # 构建启动命令
    memory = config["memory"]
    command = f'"{java_path}" -Xms{memory}G -Xmx{memory}G -jar "{server_jar}" --nogui'
    
    print(f"执行命令: {command}")
    
    # 启动服务器
    try:
        # 使用Popen保持进程运行
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # 实时输出日志
        for line in process.stdout:
            print(line, end='')
            
            # 检测到特定错误信息时处理
            if "Unsupported Java detected" in line:
                print("\n错误: Java版本不受支持!")
                print("Minecraft服务器需要Java 17或更高版本")
                print("请安装正确的Java版本后重试")
                process.terminate()
                return False
            
            if "Could not create the Java Virtual Machine" in line:
                print("\n错误: 无法创建Java虚拟机!")
                print("可能是内存分配过大或Java路径错误")
                process.terminate()
                return False
            
            if "Unable to access jarfile" in line:
                print("\n错误: 无法访问server.jar文件!")
                print("请确保server.jar存在且文件名正确")
                process.terminate()
                return False
            
            if "Address already in use" in line:
                print("\n错误: 端口已被占用!")
                print(f"请检查端口 {config['server_port']} 是否被其他程序使用")
                process.terminate()
                return False
            
            if "Failed to bind to port" in line:
                print("\n错误: 无法绑定到端口!")
                print(f"请检查端口 {config['server_port']} 是否被其他程序使用")
                process.terminate()
                return False
        
        # 等待进程结束
        process.wait()
        return process.returncode == 0
        
    except Exception as e:
        print(f"启动服务器时发生错误: {str(e)}")
        return False

def main():
    try:
        # 加载或创建配置
        config = load_config()
        
        # 验证Java路径 (重要)
        if not config["java_path"] or not validate_java_executable(config["java_path"]):
            print("Java路径未配置或无效，请重新配置")
            config = configure_server()
        
        java_path = config["java_path"]
        
        # 验证服务器jar文件 (重要)
        server_jar = os.path.join(server_dir, "server.jar")
        if not os.path.exists(server_jar):
            print("\n" + "="*50)
            print("错误: 未找到server.jar文件")
            print("="*50)
            print("请将Minecraft服务器jar文件重命名为'server.jar'并放在以下目录:")
            print(server_dir)
            print("\n1. 下载官方服务器文件: https://www.minecraft.net/download/server")
            print("2. 将下载的jar文件重命名为'server.jar'")
            print("3. 放置在此目录中")
            print("="*50)
            
            print("\n程序将在15秒后退出...")
            time.sleep(15)
            return
        
        # 首次运行设置
        eula_file = os.path.join(server_dir, "eula.txt")
        if not os.path.exists(eula_file):
            print("首次运行设置...")
            
            # 手动创建必要的文件
            accept_eula()
            print("已同意EULA协议")
            
            # 生成server.properties
            create_server_properties(config)
            
            print("已创建必要的配置文件")
            print("首次启动可能需要较长时间，请耐心等待...")
        
        # 启动服务器
        clear_screen()
        print("="*50)
        print(f"服务器配置:")
        print(f"Java路径: {java_path}")
        print(f"分配内存: {config['memory']}GB")
        print(f"正版验证: {'启用' if config['online_mode'] == 'true' else '禁用'}")
        print(f"服务器端口: {config['server_port']}")
        print(f"最大玩家: {config['max_players']}")
        print("="*50 + "\n")
        
        print("正在启动Minecraft服务器...")
        print("(Ctrl+C 或关闭窗口可停止服务器)")
        print("="*50 + "\n")
        
        # 启动服务器并捕获输出
        success = start_server(config)
        
        if not success:
            print("\n" + "="*50)
            print("服务器启动失败!")
            print("可能的原因:")
            print("1. Java路径不正确 - 请使用配置菜单重新设置")
            print("2. Java版本不兼容 - Minecraft需要Java 17或更高版本")
            print("3. 内存分配过大 - 减少配置中的内存大小")
            print("4. server.jar文件损坏 - 重新下载服务器文件")
            print("5. 端口冲突 - 检查是否有其他程序占用了相同端口")
            print("="*50)
            
            choice = input("\n是否要重新配置服务器? (y/n): ").lower()
            if choice == 'y':
                config = configure_server()
                save_config(config)
                main()  # 重新启动
        
        print("服务器已停止")
    
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"发生错误: {str(e)}")
        traceback.print_exc()
        input("按Enter键返回主菜单...")

def show_menu():
    """显示主菜单"""
    clear_screen()
    while True:
        print("="*50)
        print(f" Minecraft 服务器管理工具")
        print(f" 当前目录: {server_dir}")
        print("="*50)
        print("1. 启动服务器")
        print("2. 配置服务器")
        print("3. 编辑配置文件")
        print("4. 打开服务器目录")
        print("5. 查看重要提示")
        print("6. 安装Java指南")
        print("7. 退出")
        print("="*50)
        
        choice = input("请选择操作: ").strip()
        
        if choice == "1":
            main()
            input("\n按Enter返回主菜单...")
            clear_screen()
        elif choice == "2":
            config = configure_server()
            save_config(config)
            input("\n配置完成，按Enter返回主菜单...")
            clear_screen()
        elif choice == "3":
            if platform.system() == "Windows":
                os.system(f'notepad.exe "{config_path}"')
            else:
                # 尝试使用gedit（如果有图形界面）或nano
                if shutil.which('gedit'):
                    os.system(f'gedit "{config_path}"')
                else:
                    os.system(f'nano "{config_path}"')
            print("\n配置文件已编辑")
            input("按Enter返回主菜单...")
            clear_screen()
        elif choice == "4":
            if platform.system() == "Windows":
                os.system(f'explorer "{server_dir}"')
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{server_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{server_dir}"')
            print("\n已打开服务器目录")
            input("按Enter返回主菜单...")
            clear_screen()
        elif choice == "5":
            print("\n" + "="*50)
            print(" 重要提示")
            print("="*50)
            print("1. 请确保以下文件在同一目录:")
            print("   - 本程序")
            print("   - server.jar (Minecraft服务器文件)")
            print("   - config.txt (配置文件)")
            print("\n2. 必须配置项:")
            print("   - java_path: Java可执行文件路径 (需要Java 17+)")
            print("   - memory: 服务器内存分配 (单位GB)")
            print("\n3. 下载官方服务器文件:")
            print("   https://www.minecraft.net/download/server")
            print("\n4. 首次运行需要同意EULA协议")
            print("\n5. 常见问题:")
            print("   - Java路径错误: 使用配置菜单重新设置")
            print("   - 内存不足: 减少内存分配")
            print("   - 端口冲突: 更改server_port配置")
            print("="*50)
            input("\n按Enter返回主菜单...")
            clear_screen()
        elif choice == "6":
            print("\n" + "="*50)
            print(" Java安装指南")
            print("="*50)
            print("Minecraft服务器需要Java 17或更高版本")
            print("\n下载链接:")
            print("Windows: https://adoptium.net/temurin/releases/?version=17")
            print("macOS: https://adoptium.net/temurin/releases/?version=17")
            print("Linux: 使用包管理器安装 (如: sudo apt install openjdk-17-jdk)")
            print("\n安装后查找java.exe路径:")
            print("Windows: 通常在 C:\\Program Files\\Java\\jdk-17\\bin\\java.exe")
            print("macOS/Linux: 通常在 /usr/bin/java")
            print("\n验证安装:")
            print("打开终端/命令提示符，输入: java -version")
            print("应显示类似: openjdk version \"17.0.1\" ...")
            print("="*50)
            input("\n按Enter返回主菜单...")
            clear_screen()
        elif choice == "7":
            print("感谢使用，再见!")
            sys.exit(0)
        else:
            print("无效选择，请重新输入")
            input("按Enter继续...")
            clear_screen()

# 初始化并显示菜单
if __name__ == "__main__":
    try:
        init()
        show_menu()
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        traceback.print_exc()
        input("按Enter键退出...")