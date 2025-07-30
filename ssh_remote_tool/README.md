# SSH远程操作工具

基于PyQt6和paramiko构建的强大SSH远程操作工具，提供直观的GUI界面用于管理SSH连接、文件传输和远程脚本执行。

## 功能特性

- **SSH连接管理**: 支持密码和密钥认证的安全连接
- **双面板文件浏览器**: 本地和远程文件管理
- **文件传输**: 拖拽式文件上传和下载，支持断点续传
- **脚本执行**: 远程脚本执行和实时日志查看
- **连接配置**: 保存和管理多个SSH连接
- **性能优化**: 连接缓存、异步加载、智能重试
- **智能导航**: Home按钮支持默认目录配置

## 系统要求

- Python 3.8+
- Windows 10+ / Linux / macOS

## 快速开始

### 开发环境运行

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行程序:
```bash
python src/main.py
```

### Windows可执行文件

直接下载并运行 `SSH_Remote_Tool.exe`，无需安装Python环境。

## 使用说明

1. **添加连接**: 在左侧连接管理器中添加SSH服务器信息
2. **连接服务器**: 选择连接并点击连接按钮
3. **浏览文件**: 使用文件浏览器管理本地和远程文件
4. **传输文件**: 在本地和远程面板间拖拽文件
5. **执行脚本**: 使用脚本面板在远程服务器运行命令

## 项目结构

```
ssh_remote_tool/
├── src/                    # 源代码
│   ├── main.py            # 程序入口
│   ├── core/              # 核心功能模块
│   ├── ui/                # 用户界面模块
│   └── utils/             # 工具模块
├── release/               # 发布文件
│   ├── SSH_Remote_Tool.exe    # Windows可执行文件
│   ├── install.bat           # 安装脚本
│   └── RELEASE_README.md     # 用户使用说明
├── requirements.txt       # Python依赖
└── README.md             # 本文件
```

## 许可证

本项目采用MIT许可证。