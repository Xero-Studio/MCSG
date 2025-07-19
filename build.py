#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地构建脚本 - 使用Nuitka打包MC服务器管理器
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_nuitka():
    """检查Nuitka是否安装"""
    try:
        subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                      check=True, capture_output=True)
        print("✓ Nuitka已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Nuitka未安装")
        return False

def install_nuitka():
    """安装Nuitka"""
    print("正在安装Nuitka...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "nuitka", "ordered-set"], 
                      check=True)
        print("✓ Nuitka安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ Nuitka安装失败")
        return False

def build_onefile():
    """尝试单文件构建"""
    print("尝试单文件构建...")
    
    system = platform.system()
    if system == "Windows":
        output_name = "mc-server-manager.exe"
    else:
        output_name = "mc-server-manager"
    
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        f"--output-filename={output_name}",
        "--enable-plugin=no-qt",
        "--assume-yes-for-downloads",
        "--output-dir=dist",
        "start.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✓ 单文件构建成功")
        return True, "dist"
    except subprocess.CalledProcessError:
        print("✗ 单文件构建失败")
        return False, None

def build_standalone():
    """多文件构建"""
    print("尝试多文件构建...")
    
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--output-filename=mc-server-manager",
        "--enable-plugin=no-qt",
        "--assume-yes-for-downloads",
        "--output-dir=dist-standalone",
        "start.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✓ 多文件构建成功")
        return True, "dist-standalone"
    except subprocess.CalledProcessError:
        print("✗ 多文件构建失败")
        return False, None

def test_executable(dist_dir):
    """测试可执行文件"""
    system = platform.system()
    
    if "standalone" in dist_dir:
        # 多文件模式
        if system == "Windows":
            exe_path = Path(dist_dir) / "start.dist" / "mc-server-manager.exe"
        else:
            exe_path = Path(dist_dir) / "start.dist" / "mc-server-manager"
    else:
        # 单文件模式
        if system == "Windows":
            exe_path = Path(dist_dir) / "mc-server-manager.exe"
        else:
            exe_path = Path(dist_dir) / "mc-server-manager"
    
    if exe_path.exists():
        print(f"✓ 可执行文件已创建: {exe_path}")
        print(f"文件大小: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        if system != "Windows":
            os.chmod(exe_path, 0o755)
        
        return True
    else:
        print(f"✗ 可执行文件未找到: {exe_path}")
        return False

def package_standalone(dist_dir):
    """打包多文件构建结果"""
    if "standalone" not in dist_dir:
        return
    
    system = platform.system()
    source_dir = Path(dist_dir) / "start.dist"
    
    if not source_dir.exists():
        print("✗ 多文件构建目录不存在")
        return
    
    if system == "Windows":
        # 创建ZIP文件
        archive_name = "mc-server-manager-standalone-windows.zip"
        shutil.make_archive("mc-server-manager-standalone-windows", "zip", source_dir)
        print(f"✓ 已创建压缩包: {archive_name}")
    else:
        # 创建tar.gz文件
        archive_name = f"mc-server-manager-standalone-{system.lower()}.tar.gz"
        shutil.make_archive(f"mc-server-manager-standalone-{system.lower()}", "gztar", source_dir)
        print(f"✓ 已创建压缩包: {archive_name}")

def main():
    """主函数"""
    print("MC服务器管理器 - Nuitka构建脚本")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print(f"✗ Python版本过低: {sys.version}")
        print("需要Python 3.6或更高版本")
        return False
    
    print(f"✓ Python版本: {sys.version}")
    print(f"✓ 操作系统: {platform.system()} {platform.release()}")
    
    # 检查并安装Nuitka
    if not check_nuitka():
        if not install_nuitka():
            return False
    
    # 清理旧的构建文件
    for dir_name in ["dist", "dist-standalone"]:
        if os.path.exists(dir_name):
            print(f"清理旧构建目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 尝试构建
    success = False
    
    # 首先尝试单文件构建
    success, dist_dir = build_onefile()
    if success and test_executable(dist_dir):
        print("\n🎉 单文件构建完成！")
        return True
    
    # 如果单文件失败，尝试多文件构建
    print("\n单文件构建失败，尝试多文件构建...")
    success, dist_dir = build_standalone()
    if success and test_executable(dist_dir):
        package_standalone(dist_dir)
        print("\n🎉 多文件构建完成！")
        return True
    
    print("\n❌ 所有构建方式都失败了")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)