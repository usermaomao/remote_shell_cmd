# SSH远程工具 - 构建指南

## 🚀 快速构建

### Windows用户
1. 双击运行 `build.bat`
2. 等待构建完成
3. 在 `release/` 目录获取可执行文件

### 手动构建
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行构建脚本
python build_exe.py
```

## 📦 构建输出

构建成功后，`release/` 目录将包含：
- `SSH_Remote_Tool.exe` - 主程序（约31MB）
- `install.bat` - 一键安装脚本
- `README.md` - 用户使用说明

## 🔧 构建要求

### 系统要求
- Windows 10 或更高版本
- Python 3.8+
- 64位操作系统

### 依赖包
- PyQt6 - GUI框架
- paramiko - SSH连接
- cryptography - 加密支持
- psutil - 系统监控
- pyinstaller - 打包工具

## 📋 构建过程

构建脚本会自动执行以下步骤：
1. ✅ 检查Python环境和依赖包
2. ✅ 创建PyInstaller配置文件
3. ✅ 清理之前的构建文件
4. ✅ 使用PyInstaller构建可执行文件
5. ✅ 创建发布包和安装脚本
6. ✅ 清理临时构建文件

## 🎯 分发说明

### 给最终用户
1. 将整个 `release/` 文件夹打包为ZIP
2. 用户解压后运行 `install.bat` 安装
3. 或直接运行 `SSH_Remote_Tool.exe`

### 特性
- ✅ 单文件可执行程序
- ✅ 无需安装Python环境
- ✅ 包含所有依赖库
- ✅ 一键安装脚本
- ✅ Windows 10/11兼容

## 🔍 故障排除

### 构建失败
- 确保Python版本 ≥ 3.8
- 运行 `pip install -r requirements.txt` 安装依赖
- 检查是否在项目根目录运行脚本

### 可执行文件问题
- 确保Windows版本 ≥ 10
- 检查防病毒软件是否误报
- 确保有足够的磁盘空间（至少100MB）

### 性能优化
- 可选安装UPX压缩工具减小文件大小
- 构建时会自动启用UPX压缩（如果可用）

## 📊 构建统计

- **源代码**: ~3000行
- **模块数量**: 15个
- **依赖包**: 4个主要依赖
- **构建时间**: 约2-3分钟
- **最终大小**: ~31MB
- **兼容性**: Windows 10/11 (64位)

---

**注意**: 首次构建可能需要下载依赖包，请确保网络连接正常。
