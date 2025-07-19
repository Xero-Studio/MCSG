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

# 🔧 Building from Source

If you want to build the executable yourself:

**Prerequisites:**
- Python 3.6 or higher
- Nuitka (will be installed automatically)

**Build Instructions:**

1. **Automatic build (recommended):**
   - **Windows**: Run `build.bat`
   - **Linux/macOS**: Run `./build.sh`

2. **Manual build:**
   ```bash
   # Install Nuitka
   pip install nuitka ordered-set
   
   # Build (single file)
   python -m nuitka --standalone --onefile --output-filename=mc-server-manager --enable-plugin=no-qt --assume-yes-for-downloads --output-dir=dist start.py
   ```

3. **Using the build script:**
   ```bash
   python build.py
   ```

**GitHub Actions:**
This project includes automated builds via GitHub Actions. Executables are automatically built for Windows, Linux, and macOS on every release.

# Wish List


- [ ] Multilingual support
- [x] Windows GUI interface (PyQt)
- [ ] Plugin management
- [ ] Backup functionality
- [ ] Server performance monitoring
- [ ] More...


# Author on Bilibili


[Click here!](https://space.bilibili.com/3546703915387263)
