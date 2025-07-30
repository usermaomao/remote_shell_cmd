@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    SSH远程工具 - 构建可执行文件
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python 3.8或更高版本
    echo.
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

REM 检查是否在正确目录
if not exist "src\main.py" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    echo 当前目录应包含 src\main.py 文件
    echo.
    pause
    exit /b 1
)

echo ✅ 项目目录检查通过
echo.

REM 运行构建脚本
echo 🚀 开始构建...
python build_exe.py

if errorlevel 1 (
    echo.
    echo ❌ 构建失败！
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 构建成功完成！
echo.
echo 📁 发布文件已生成在 release/ 目录中
echo.
pause
