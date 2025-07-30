#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSH远程工具 - Windows可执行文件构建脚本
自动化构建Windows下的可执行文件
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def check_dependencies():
    """检查构建依赖"""
    print("🔍 检查构建依赖...")

    # 检查包的映射关系
    package_imports = {
        'PyQt6': 'PyQt6.QtCore',
        'paramiko': 'paramiko',
        'cryptography': 'cryptography',
        'psutil': 'psutil',
        'pyinstaller': 'PyInstaller'
    }

    missing_packages = []

    for package, import_name in package_imports.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")

    if missing_packages:
        print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False

    print("✅ 所有依赖检查通过")
    return True

def create_spec_file():
    """创建PyInstaller spec文件"""
    print("📝 创建PyInstaller配置文件...")

    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'paramiko',
        'cryptography',
        'psutil'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SSH_Remote_Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI应用，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''

    try:
        with open('ssh_remote_tool.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
        print("✅ PyInstaller配置文件创建完成")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False

def clean_build():
    """清理之前的构建"""
    print("🧹 清理之前的构建...")

    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  🗑️ 删除 {dir_name}/")
            except Exception as e:
                print(f"  ⚠️ 无法删除 {dir_name}/: {e}")

    print("✅ 构建目录清理完成")
    return True

def build_executable():
    """构建可执行文件"""
    print("\n🔨 开始构建可执行文件...")
    
    try:
        # 运行PyInstaller
        cmd = ['pyinstaller', '--clean', 'ssh_remote_tool.spec']
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 构建成功！")
            return True
        else:
            print("❌ 构建失败！")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出现异常: {e}")
        return False

def create_release_package():
    """创建发布包"""
    print("\n📦 创建发布包...")
    
    # 创建release目录
    release_dir = Path('release')
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 复制可执行文件
    exe_path = Path('dist/SSH_Remote_Tool.exe')
    if exe_path.exists():
        shutil.copy2(exe_path, release_dir / 'SSH_Remote_Tool.exe')
        print(f"  ✅ 复制可执行文件: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("  ❌ 找不到可执行文件")
        return False
    
    # 创建安装脚本
    install_script = '''@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    SSH Remote Tool - Installer
echo ========================================
echo.

set "INSTALL_DIR=%USERPROFILE%\\SSH_Remote_Tool"
set "SHORTCUT=%USERPROFILE%\\Desktop\\SSH_Remote_Tool.lnk"

echo Installing to: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying program files...
copy "SSH_Remote_Tool.exe" "%INSTALL_DIR%\\" >nul
if errorlevel 1 (
    echo Error: Cannot copy program files
    pause
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%INSTALL_DIR%\\SSH_Remote_Tool.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'SSH Remote Tool'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo Installation completed!
    echo.
    echo Program installed to: %INSTALL_DIR%
    echo Desktop shortcut created
    echo.
    echo You can:
    echo 1. Double-click desktop shortcut to start
    echo 2. Or run directly: %INSTALL_DIR%\\SSH_Remote_Tool.exe
) else (
    echo Program installed successfully, but shortcut creation failed
    echo Please run manually: %INSTALL_DIR%\\SSH_Remote_Tool.exe
)

echo.
pause
'''

    with open(release_dir / 'install.bat', 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    # 创建用户说明
    readme_content = '''# SSH远程工具 - 用户指南

## 安装方法

### 方法1: 一键安装（推荐）
1. 双击运行 `install.bat`
2. 按提示完成安装
3. 桌面会自动创建快捷方式

### 方法2: 直接运行
直接双击 `SSH_Remote_Tool.exe` 即可运行

## 系统要求
- Windows 10 或更高版本
- 64位操作系统
- 无需安装Python或其他依赖

## 功能特性
- SSH连接管理
- 双面板文件浏览器
- 文件传输（支持拖拽）
- 远程脚本执行
- 实时日志查看

## 使用说明
1. 添加SSH连接配置
2. 连接到远程服务器
3. 使用文件浏览器管理文件
4. 执行远程脚本和命令

## 技术支持
如有问题，请检查：
- 网络连接是否正常
- SSH服务器配置是否正确
- 防火墙设置是否允许SSH连接
'''
    
    with open(release_dir / 'README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 发布包创建完成")
    return True

def cleanup_build_files():
    """清理构建文件"""
    print("🧹 清理构建文件...")

    files_to_clean = ['ssh_remote_tool.spec']
    dirs_to_clean = ['build', 'dist']

    for file_name in files_to_clean:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"  🗑️ 删除 {file_name}")
            except Exception as e:
                print(f"  ⚠️ 无法删除 {file_name}: {e}")

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"  🗑️ 删除 {dir_name}/")
            except Exception as e:
                print(f"  ⚠️ 无法删除 {dir_name}/: {e}")

    print("✅ 构建文件清理完成")
    return True

def main():
    """主函数"""
    print("🚀 SSH远程工具 - Windows可执行文件构建器")
    print("=" * 50)
    
    # 检查当前目录
    if not os.path.exists('src/main.py'):
        print("❌ 错误: 请在项目根目录运行此脚本")
        print("当前目录应包含 src/main.py 文件")
        return False
    
    # 执行构建步骤
    steps = [
        ("检查依赖", check_dependencies),
        ("创建配置文件", create_spec_file),
        ("清理构建目录", clean_build),
        ("构建可执行文件", build_executable),
        ("创建发布包", create_release_package),
        ("清理构建文件", cleanup_build_files),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 步骤: {step_name}")
        if not step_func():
            print(f"❌ 步骤失败: {step_name}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 构建完成！")
    print("\n📁 发布文件位置:")
    print("  release/SSH_Remote_Tool.exe  - 主程序")
    print("  release/install.bat         - 安装脚本")
    print("  release/README.md           - 用户说明")
    print("\n💡 使用方法:")
    print("  1. 将 release/ 文件夹打包分发给用户")
    print("  2. 用户运行 install.bat 进行安装")
    print("  3. 或直接运行 SSH_Remote_Tool.exe")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 构建被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 构建过程中出现未预期的错误: {e}")
        sys.exit(1)
