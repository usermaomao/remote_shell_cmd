# SSH Remote Operations Tool

一个基于PyQt6的SSH远程操作工具，提供简洁直观的图形用户界面，用于执行常见的SSH远程操作。

## 功能特性

### ✅ 已实现功能

#### 1. SSH连接管理
- ✅ 创建、保存、编辑、删除SSH连接配置
- ✅ 支持密码和SSH密钥认证
- ✅ 密码AES-256加密存储
- ✅ 连接状态显示和错误处理
- ✅ 批量导入/导出连接配置（JSON格式）
- ✅ SSH密钥文件权限验证（Unix系统）

#### 2. 远程脚本执行
- ✅ 输入脚本模式：在UI中输入/粘贴脚本并执行
- ✅ 文件选择模式：选择远程服务器上的脚本文件执行
- ✅ 支持执行目录和参数设置
- ✅ 实时捕获stdout和stderr输出
- ✅ 脚本终止功能
- ✅ 脚本保存功能

#### 3. 文件管理
- ✅ 双栏文件浏览器（本地/远程）
- ✅ 显示文件属性（名称、大小、修改日期、类型）
- ✅ 右键菜单操作（下载、上传、编辑、删除、重命名）
- ✅ 工具栏快捷操作
- ✅ 新建文件夹功能
- ✅ 文件上传下载功能

#### 4. 日志输出
- ✅ 实时日志显示
- ✅ 时间戳记录
- ✅ 按类型过滤日志（全部、信息、成功、错误、输出）
- ✅ 自动滚动控制
- ✅ 日志清空和导出功能
- ✅ 错误信息高亮显示

#### 5. 用户界面
- ✅ 现代化三栏式布局
- ✅ 状态栏显示连接状态
- ✅ 响应式界面设计
- ✅ 标签页式脚本和日志面板

## 安装和运行

### 系统要求
- Python 3.9+
- Windows 10/11, macOS 12+, 或 Linux

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用程序
```bash
# 方法1：使用启动脚本
python ssh_remote_tool/run.py

# 方法2：直接运行主程序
cd ssh_remote_tool/src
python main.py
```

### 功能测试
```bash
# 运行功能测试
python ssh_remote_tool/test_functionality.py
```

## 使用指南

### 1. 连接管理
1. 点击左侧边栏的"Add"按钮添加新连接
2. 填写连接信息（名称、主机、端口、用户名、认证方式）
3. 双击连接项或右键选择"Connect"建立连接
4. 使用"Import..."和"Export..."进行批量管理

### 2. 文件操作
1. 连接成功后，文件浏览器会显示本地和远程文件系统
2. 使用工具栏按钮或右键菜单进行文件操作
3. 支持文件上传、下载、删除、重命名等操作

### 3. 脚本执行
1. 在"Script"标签页中选择执行模式：
   - "Input Script"：直接输入脚本内容
   - "Select File"：选择远程服务器上的脚本文件
2. 设置工作目录和参数
3. 点击"Execute"执行脚本
4. 在"Log"标签页查看执行结果

### 4. 日志查看
1. 在"Log"标签页查看所有操作日志
2. 使用过滤器筛选特定类型的日志
3. 可以导出日志到文件或清空日志

## 技术架构

### 核心模块
- `core/ssh_manager.py` - SSH连接管理
- `core/file_manager.py` - 文件操作管理
- `core/script_executor.py` - 脚本执行管理
- `core/credentials_manager.py` - 凭据加密管理

### UI组件
- `ui/main_window.py` - 主窗口
- `ui/connection_manager_widget.py` - 连接管理器
- `ui/file_browser_widget.py` - 文件浏览器
- `ui/script_panel_widget.py` - 脚本执行面板
- `ui/log_panel_widget.py` - 日志显示面板

### 依赖库
- PyQt6 - GUI框架
- paramiko - SSH/SFTP协议
- cryptography - 密码加密

## 安全特性

1. **密码加密存储**：使用AES-256加密算法存储密码
2. **SSH密钥权限验证**：自动检查和修复SSH密钥文件权限
3. **安全连接**：使用SSH v2协议进行安全通信
4. **凭据保护**：导出配置时不包含敏感密码信息

## 开发和测试

### 运行测试
```bash
# 导入测试
python ssh_remote_tool/test_import.py

# 功能测试
python ssh_remote_tool/test_functionality.py
```

### 项目结构
```
ssh_remote_tool/
├── src/
│   ├── core/           # 核心业务逻辑
│   ├── ui/             # 用户界面组件
│   ├── utils/          # 工具函数
│   └── main.py         # 主程序入口
├── run.py              # 启动脚本
├── test_import.py      # 导入测试
├── test_functionality.py  # 功能测试
├── requirements.txt    # 依赖列表
└── README.md          # 说明文档
```

## 版本信息

- **版本**: 1.0
- **开发状态**: 基本功能完成
- **兼容性**: 跨平台支持

## 许可证

本项目遵循MIT许可证。