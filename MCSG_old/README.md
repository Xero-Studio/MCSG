English | [简体中文](README_ZH.md)


# MC Server Manager


Now powered by Python with modern GUI! (Original batch version moved to `old/` folder)


# 🌟 Features


- Modern PyQt GUI interface
- Windows optimized
- Compact and lightweight
- Convenient for common configuration changes
- User-friendly graphical interface
- Automatic EULA handling
- And more...


# 📦 Quick Start


**Requirements:**
- Windows 10/11
- Python 3.8 or higher
- PyQt5/PyQt6
- Java (for running Minecraft server)

**Installation:**
1. Download or clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Make sure you have a Minecraft server jar file (e.g., `server.jar`) in the same directory
4. Run the program: Double-click `start.bat` or run `python start.py`

The program will automatically create configuration files and handle EULA agreement. You just need to have a server core file to get started.

# 🌟 Key Features Overview

## 🏗️ Multi-Server Management
- Create and manage multiple server instances
- Switch between servers with one click
- Independent configuration for each server
- Server templates for quick setup

## 🔌 Plugin Management
- Browse and install popular plugins (EssentialsX, WorldEdit, WorldGuard, etc.)
- Automatic dependency checking
- Enable/disable plugins without restart
- Plugin search and filtering

## 📊 Performance Monitoring
- Real-time CPU, memory, and TPS monitoring
- Performance status indicators (Excellent/Good/Fair/Poor)
- Smart optimization suggestions
- Historical performance data

## 👥 Player Management
- View online/offline player status
- Kick, ban/unban players
- Grant/revoke OP permissions
- Player statistics and management

## 💾 Backup System
- Automated world and configuration backups
- One-click backup creation and restoration
- Backup scheduling and cleanup
- Backup size and statistics tracking

## 🔧 Smart Controls
- Double-click force stop with 200ms detection
- Automatic EULA agreement handling
- Hidden Java console windows
- Memory slider configuration

# 🔧 Building from Source

If you want to build the executable yourself:

**Prerequisites:**
- Python 3.9 or higher
- PyInstaller (will be installed automatically)

**Build Instructions:**

1. **Automatic build (recommended):**
   - **Windows**: Run `build.bat`

2. **Manual build:**
   ```bash
   # Install PyInstaller
   pip install pyinstaller
   pip install -r requirements.txt
   
   # Build (single file)
   pyinstaller MinecraftServerManager.spec
   ```

**GitHub Actions (Recommended):**
This project includes automated builds via GitHub Actions. **Pre-built executables are available in the [Releases](../../releases) section** - no need to build manually! Executables are automatically built for Windows on every release.

# 🎯 Wish List

## 🔥 High Priority
- [ ] **Advanced logging** - Smart server log analysis and problem diagnosis
- [ ] **Remote management** - Web-based remote server management
- [ ] **Automated tasks** - Scheduled server maintenance and optimization

## 🌟 Medium Priority
- [ ] **World management** - World backup, restore, and generation tools
- [ ] **Economy system** - Built-in economy management
- [ ] **Event scheduling** - Automated server events and announcements
- [ ] **API integration** - REST API for external integrations

## 💡 Low Priority
- [ ] **Theme switching** - Multiple interface themes
- [ ] **Multilingual support** - English, Chinese and other languages
- [ ] **Auto-update** - Automatic server core updates
- [ ] **Cloud sync** - Configuration file cloud synchronization

## ✅ Completed
- [x] **Windows GUI interface** - Modern PyQt5 + Fluent Design interface
- [x] **Hidden terminal** - No Java console window when starting server
- [x] **Console controls** - Stop server button in console interface
- [x] **Multi-server management** - Manage multiple Minecraft server instances simultaneously
- [x] **Server templates** - Pre-configured templates for different server types
- [x] **Backup system** - Scheduled world and configuration backups
- [x] **Plugin management** - Automatic plugin download and management
- [x] **Performance monitoring** - Real-time CPU, memory, TPS monitoring
- [x] **Player management** - Online player list, kick/ban functionality
- [x] **Smart server controls** - Double-click force stop, EULA auto-handling
- [x] **Advanced configuration** - Memory slider, path selection, core file browser


# Author on Bilibili


[Click here!](https://space.bilibili.com/3546703915387263)


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CatEazy/MC-Server-MGR&type=Date)](https://www.star-history.com/#CatEazy/MC-Server-MGR&Date)