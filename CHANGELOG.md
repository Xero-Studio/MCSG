# 更新日志 / Changelog

## [2.0.0] - 2024-07-19

### 新增 / Added
- 🎉 完全重写为Python版本
- 🔧 添加Nuitka构建支持
- 🚀 GitHub Actions自动构建
- 📦 跨平台支持（Windows、Linux、macOS）
- ⚙️ 改进的配置管理（INI格式）
- 🛠️ 本地构建脚本

### 改进 / Improved
- 📊 优化GitHub Actions配置（从14个jobs减少到4个jobs）
- 🔄 更新Actions到最新版本（修复弃用警告）
- 📝 完善的文档和构建说明
- 🎯 单文件可执行文件构建
- 🔒 自动EULA处理

### 修复 / Fixed
- ✅ 修复GitHub Actions弃用警告
- 🔧 更新actions/upload-artifact到v4
- 🔧 更新actions/download-artifact到v4
- 🔧 更新actions/setup-python到v5

### 技术细节 / Technical Details
- Python 3.6+ 支持
- 使用Nuitka编译器
- 无外部依赖（仅标准库）
- 配置文件格式：INI
- 构建输出：单文件可执行程序

### 迁移说明 / Migration Notes
- 原批处理版本移至 `old/` 文件夹
- 配置文件格式从TXT改为INI
- 启动方式：`python start.py` 或平台特定脚本

---

## [1.x.x] - 历史版本

### 原始批处理版本
- Windows批处理脚本实现
- 基本的服务器管理功能
- 配置文件支持
- 多个版本迭代（Version8, VersionO, VersionOL, VersionOLD）

---

## 版本说明 / Version Notes

- **2.x.x**: Python重写版本，现代化实现
- **1.x.x**: 原始批处理版本（已归档）