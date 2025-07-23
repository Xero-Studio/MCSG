[English](README.md) | 简体中文


# 重要！
现在我建了一个新PMSS服务器启动器，在这个[仓库](https://github.com/Xero-Studio/PythonMineCraftServerStart),由[TedZyzsdy](https://github.com/TedZyzsdy) 编写
因为PyQt太难了，此项目已停用，现由[TedZyzsdy](https://github.com/TedZyzsdt)维护


# MC Server Manager

基于 Python 和现代 GUI 的 Minecraft 服务器管理器！(原批处理版本已移至 `old/` 文件夹)

## ✨ 功能特性

- 🎨 **现代化界面** - 基于 PyQt5 + Fluent Design 的美观界面
- 🏗️ **多服务器管理** - 同时管理多个服务器实例
- 🔌 **插件管理** - 浏览、安装和管理服务器插件
- 📊 **性能监控** - 实时 CPU、内存、TPS 监控
- 👥 **玩家管理** - 轻松踢人、封禁、给予OP权限
- 💾 **备份系统** - 自动化备份和恢复功能
- ⚙️ **服务器模板** - 预设不同类型服务器的配置模板
- 🖥️ **实时控制台** - 查看服务器输出，发送命令
- 🔧 **智能控制** - 双击强制停止，EULA 自动处理
- 📁 **配置持久化** - 自动保存和加载配置
- 🚫 **隐藏终端** - 启动服务器时不显示 Java 控制台窗口
- 🎯 **Windows 优化** - 专为 Windows 系统优化

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

# 🌟 核心功能概览

## 🏗️ 多服务器管理
- 创建和管理多个服务器实例
- 一键切换不同服务器
- 每个服务器独立配置
- 服务器模板快速设置

## 🔌 插件管理
- 浏览和安装热门插件（EssentialsX、WorldEdit、WorldGuard等）
- 自动依赖检查
- 无需重启启用/禁用插件
- 插件搜索和筛选

## 📊 性能监控
- 实时 CPU、内存、TPS 监控
- 性能状态指示器（优秀/良好/一般/较差）
- 智能优化建议
- 历史性能数据记录

## 👥 玩家管理
- 查看在线/离线玩家状态
- 踢人、封禁/解封玩家
- 给予/移除 OP 权限
- 玩家统计和管理

## 💾 备份系统
- 自动化世界和配置备份
- 一键备份创建和恢复
- 备份调度和清理
- 备份大小和统计追踪

## 🔧 智能控制
- 双击强制停止（200ms检测）
- 自动 EULA 协议处理
- 隐藏 Java 控制台窗口
- 内存滑块配置

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
- [ ] **高级日志** - 智能分析服务器日志，提供问题诊断
- [ ] **远程管理** - 通过网页界面远程管理服务器
- [ ] **自动化任务** - 定时服务器维护和优化

### 🌟 中优先级
- [ ] **世界管理** - 世界备份、恢复和生成工具
- [ ] **经济系统** - 内置经济管理功能
- [ ] **事件调度** - 自动化服务器事件和公告
- [ ] **API集成** - REST API 支持外部集成

### 💡 低优先级
- [ ] **主题切换** - 支持多种界面主题
- [ ] **多语言支持** - 英文、中文等多语言界面
- [ ] **自动更新** - 自动检查和更新服务器核心
- [ ] **云同步** - 配置文件云端同步

### ✅ 已完成
- [x] **Windows GUI 界面** - 现代化的 PyQt5 + Fluent Design 界面
- [x] **隐藏终端** - 启动服务器时不显示 Java 控制台窗口
- [x] **控制台控制** - 控制台界面中的停止服务器按钮
- [x] **多服务器管理** - 同时管理多个 Minecraft 服务器实例
- [x] **服务器模板** - 预设不同类型服务器的配置模板
- [x] **备份系统** - 定时备份世界文件和配置
- [x] **插件管理** - 自动下载和管理服务器插件
- [x] **性能监控** - 实时显示 CPU、内存、TPS 等性能指标
- [x] **玩家管理** - 在线玩家列表，踢人/封禁功能
- [x] **智能控制** - 双击强制停止，EULA 自动处理
- [x] **高级配置** - 内存滑块，路径选择，核心文件浏览

## 👨‍💻 作者 B站

[点击这里!](https://space.bilibili.com/3546703915387263)

## 星标数量

[![Star History Chart](https://api.star-history.com/svg?repos=CatEazy/MC-Server-MGR&type=Date)](https://www.star-history.com/#CatEazy/MC-Server-MGR&Date)
