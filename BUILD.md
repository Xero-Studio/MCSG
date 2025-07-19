# 构建说明 / Build Instructions

## 概述 / Overview

本项目使用Nuitka将Python代码编译为独立的可执行文件，支持Windows、Linux和macOS平台。

This project uses Nuitka to compile Python code into standalone executables for Windows, Linux, and macOS.

## 自动构建 / Automated Builds

### GitHub Actions

项目配置了GitHub Actions自动构建流程：
- 每次推送到main/master分支时触发构建
- 创建标签时自动发布
- 使用Python 3.10（稳定版本）
- 支持三大操作系统平台
- **优化后仅需3-4个jobs**（原来需要10+个jobs）

The project is configured with GitHub Actions automated build pipeline:
- Triggered on push to main/master branch
- Automatic release on tag creation
- Uses Python 3.10 (stable version)
- Supports three major OS platforms
- **Optimized to only 3-4 jobs** (originally required 10+ jobs)

### 构建矩阵 / Build Matrix

| OS | Python Version | Output | Jobs |
|---|---|---|---|
| Windows | 3.10 | `.exe` | 1 |
| Linux | 3.10 | binary | 1 |
| macOS | 3.10 | binary | 1 |
| **总计** | | | **3-4个jobs** |

*优化说明：使用单一稳定的Python版本（3.10）减少构建复杂度*

## 本地构建 / Local Build

### 快速开始 / Quick Start

**Windows:**
```cmd
build.bat
```

**Linux/macOS:**
```bash
./build.sh
```

### 手动构建 / Manual Build

1. **安装依赖 / Install Dependencies:**
   ```bash
   pip install nuitka ordered-set
   ```

2. **单文件构建 / Single File Build:**
   ```bash
   python -m nuitka \
     --standalone \
     --onefile \
     --output-filename=mc-server-manager \
     --enable-plugin=no-qt \
     --assume-yes-for-downloads \
     --output-dir=dist \
     start.py
   ```

3. **多文件构建 / Multi-file Build (fallback):**
   ```bash
   python -m nuitka \
     --standalone \
     --output-filename=mc-server-manager \
     --enable-plugin=no-qt \
     --assume-yes-for-downloads \
     --output-dir=dist-standalone \
     start.py
   ```

### 使用构建脚本 / Using Build Script

```bash
python build.py
```

构建脚本会自动：
- 检查Python版本
- 安装Nuitka（如果需要）
- 尝试单文件构建
- 如果失败，回退到多文件构建
- 测试生成的可执行文件

The build script automatically:
- Checks Python version
- Installs Nuitka (if needed)
- Attempts single-file build
- Falls back to multi-file build if failed
- Tests the generated executable

## 构建选项说明 / Build Options Explained

| 选项 / Option | 说明 / Description |
|---|---|
| `--standalone` | 创建独立的可执行文件，包含所有依赖 |
| `--onefile` | 将所有文件打包成单个可执行文件 |
| `--enable-plugin=no-qt` | 禁用Qt插件以减小文件大小 |
| `--assume-yes-for-downloads` | 自动下载所需的编译器 |
| `--output-dir` | 指定输出目录 |

## 故障排除 / Troubleshooting

### 常见问题 / Common Issues

1. **单文件构建失败 / Single-file build fails:**
   - 自动回退到多文件构建
   - 检查可用磁盘空间
   - 确保有足够的内存

2. **缺少编译器 / Missing compiler:**
   - Windows: 自动下载MinGW64
   - Linux: 安装build-essential
   - macOS: 安装Xcode命令行工具

3. **权限问题 / Permission issues:**
   - Linux/macOS: 使用`chmod +x`给予执行权限
   - Windows: 以管理员身份运行

### 平台特定注意事项 / Platform-specific Notes

**Windows:**
- 可能需要Visual Studio Build Tools
- 防病毒软件可能误报

**Linux:**
- 需要安装`patchelf`和`ccache`
- 某些发行版可能需要额外的开发包

**macOS:**
- 需要Xcode命令行工具
- 可能需要处理代码签名问题

## 性能优化 / Performance Optimization

- 使用`ccache`加速重复构建
- 启用编译器优化选项
- 考虑使用`--lto=yes`进行链接时优化

## 发布流程 / Release Process

1. 更新版本号
2. 创建Git标签：`git tag v1.0.0`
3. 推送标签：`git push origin v1.0.0`
4. GitHub Actions自动构建并创建发布

## 文件大小参考 / File Size Reference

| 平台 / Platform | 单文件 / Single File | 多文件 / Multi-file |
|---|---|---|
| Windows | ~15-25 MB | ~30-50 MB |
| Linux | ~20-30 MB | ~40-60 MB |
| macOS | ~20-30 MB | ~40-60 MB |

*实际大小可能因Python版本和系统配置而异*