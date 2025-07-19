[English](README.md) | 简体中文

# MC Server Manager

基于 Python 和现代 GUI 的 Minecraft 服务器管理器！(原批处理版本已移至 `old/` 文件夹)

## ✨ 功能特性

- 🎨 **现代化界面** - 基于 PyQt5 + Fluent Design 的美观界面
- ⚙️ **完整配置管理** - 支持所有常用服务器配置项
- 🖥️ **实时控制台** - 查看服务器输出，发送命令
- 🔧 **一键启停** - 简单的服务器启动和停止操作
- 📁 **配置持久化** - 自动保存和加载配置
- 🚫 **隐藏终端** - 启动服务器时不显示 Java 控制台窗口
- 🎯 **Windows 优化** - 专为 Windows 系统优化
- 📜 **自动 EULA** - 自动处理 EULA 协议

## 🚀 快速开始

**系统要求:**
- Windows 10/11
- Python 3.9 或更高版本
- Java 8+ (用于运行 Minecraft 服务器)

**安装步骤:**
1. 下载或克隆此仓库
2. 安装依赖: `pip install -r requirements.txt`
3. 确保在同一目录下有 Minecraft 服务器核心文件 (例如 `server.jar`)
4. 运行程序: 双击 `start.bat` 或运行 `python start.py`

程序会自动创建配置文件并处理 EULA 协议。您只需要有一个服务器核心文件即可开始使用。

## 🔧 从源码构建

如果您想自己构建可执行文件:

**前置要求:**
- Python 3.9 或更高版本
- PyInstaller (会自动安装)

**构建说明:**

1. **自动构建 (推荐):**
   - **Windows**: 运行 `build.bat`

2. **手动构建:**
   ```bash
   # 安装 PyInstaller
   pip install pyinstaller
   pip install -r requirements.txt
   
   # 构建 (单文件)
   pyinstaller MinecraftServerManager.spec
   ```

**GitHub Actions (推荐):**
本项目包含 GitHub Actions 自动构建。**预构建的可执行文件可在 [Releases](../../releases) 部分获取** - 无需手动构建！每次发布时都会自动为 Windows 构建可执行文件。

## 🎯 愿望单

### 🔥 高优先级
- [ ] **多服务器管理** - 同时管理多个 Minecraft 服务器实例
- [ ] **服务器模板** - 预设不同类型服务器的配置模板
- [ ] **插件管理** - 自动下载和管理服务器插件
- [ ] **备份系统** - 定时备份世界文件和配置

### 🌟 中优先级
- [ ] **性能监控** - 实时显示 CPU、内存、TPS 等性能指标
- [ ] **玩家管理** - 在线玩家列表，踢人/封禁功能
- [ ] **日志分析** - 智能分析服务器日志，提供问题诊断
- [ ] **远程管理** - 通过网页界面远程管理服务器

### 💡 低优先级
- [ ] **主题切换** - 支持多种界面主题
- [ ] **多语言支持** - 英文、中文等多语言界面
- [ ] **自动更新** - 自动检查和更新服务器核心
- [ ] **云同步** - 配置文件云端同步

### ✅ 已完成
- [x] **Windows GUI 界面** - 现代化的 PyQt5 + Fluent Design 界面
- [x] **隐藏终端** - 启动服务器时不显示 Java 控制台窗口
- [x] **控制台控制** - 控制台界面中的停止服务器按钮

## 👨‍💻 作者 B站

[点击这里!](https://space.bilibili.com/3546703915387263)