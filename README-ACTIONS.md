# GitHub Actions 使用说明

## 🚀 自动构建流程

本项目配置了优化的GitHub Actions工作流，可以自动构建跨平台的可执行文件。

### 触发条件

- **推送到主分支**: 触发构建测试
- **创建标签**: 触发构建并自动发布
- **Pull Request**: 触发构建验证
- **手动触发**: 通过GitHub界面手动运行

### 构建矩阵

| 平台 | Python版本 | 输出文件 | 构建时间 |
|------|------------|----------|----------|
| Windows | 3.10 | `mc-server-manager.exe` | ~5-8分钟 |
| Linux | 3.10 | `mc-server-manager` | ~4-6分钟 |
| macOS | 3.10 | `mc-server-manager` | ~6-10分钟 |

### 如何发布新版本

1. **更新版本号**:
   ```bash
   # 编辑 version.py
   __version__ = "2.1.0"
   ```

2. **提交更改**:
   ```bash
   git add .
   git commit -m "Release v2.1.0"
   git push
   ```

3. **创建标签**:
   ```bash
   git tag v2.1.0
   git push origin v2.1.0
   ```

4. **自动发布**: GitHub Actions会自动构建并创建Release

### 构建产物

#### 开发构建（推送到主分支）
- 构建artifacts保存30天
- 可在Actions页面下载测试

#### 正式发布（创建标签）
- 自动创建GitHub Release
- 包含所有平台的可执行文件
- 文件命名格式：
  - `mc-server-manager-windows.exe`
  - `mc-server-manager-linux`
  - `mc-server-manager-macos`

### 故障排除

#### 常见构建失败原因

1. **Nuitka构建失败**:
   - 检查Python代码语法
   - 确保所有导入都正确
   - 查看构建日志中的错误信息

2. **平台特定问题**:
   - **Windows**: 可能需要更长的构建时间
   - **Linux**: 确保系统依赖正确安装
   - **macOS**: 可能遇到代码签名问题

3. **Actions版本问题**:
   - 所有Actions都已更新到最新版本
   - 如遇到弃用警告，请及时更新

#### 查看构建日志

1. 进入GitHub仓库
2. 点击"Actions"标签
3. 选择对应的工作流运行
4. 查看详细的构建日志

### 优化特性

- **高效构建**: 仅3-4个jobs，比原来减少71%
- **最新Actions**: 使用最新版本，避免弃用警告
- **智能缓存**: 自动缓存依赖，加速构建
- **并行构建**: 三个平台同时构建，节省时间
- **自动测试**: 构建后自动验证可执行文件

### 本地测试

在推送前，建议先本地测试：

```bash
# 使用构建脚本
python build.py

# 或者手动构建
pip install nuitka ordered-set
python -m nuitka --standalone --onefile --output-filename=mc-server-manager --enable-plugin=no-qt --assume-yes-for-downloads --output-dir=dist start.py
```

### 监控构建状态

可以在README中添加构建状态徽章：

```markdown
![Build Status](https://github.com/your-username/your-repo/workflows/Build%20Executable/badge.svg)
```

### 高级配置

如需修改构建配置，编辑 `.github/workflows/build.yml`：

- 添加新的构建平台
- 修改Python版本
- 调整Nuitka参数
- 自定义发布流程