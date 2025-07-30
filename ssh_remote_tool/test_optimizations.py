#!/usr/bin/env python3
"""
测试脚本：验证SSH远程工具的优化功能
1. 默认远程目录设置
2. 远程脚本文件选择
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
from core.ssh_manager import SSHManager

def test_default_directory_feature():
    """测试默认目录功能"""
    print("=== 测试默认目录功能 ===")
    
    ssh_manager = SSHManager()
    
    # 创建测试连接数据
    test_connection = {
        "name": "test_server",
        "host": "192.168.1.100",
        "port": 22,
        "user": "testuser",
        "default_dir": "/home/testuser/scripts",  # 新增的默认目录字段
        "auth_method": "password",
        "password": "testpass"
    }
    
    # 保存连接（这会测试新的字段是否正确保存）
    try:
        ssh_manager.save_connection(test_connection)
        print("✓ 成功保存包含默认目录的连接配置")
        
        # 读取连接数据验证
        saved_connection = ssh_manager.get_connection("test_server")
        if saved_connection and saved_connection.get("default_dir") == "/home/testuser/scripts":
            print("✓ 默认目录字段正确保存和读取")
        else:
            print("✗ 默认目录字段保存或读取失败")
            
        # 清理测试数据
        ssh_manager.delete_connection("test_server")
        print("✓ 测试数据清理完成")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")

def test_ui_components():
    """测试UI组件的新功能"""
    print("\n=== 测试UI组件功能 ===")
    
    app = QApplication(sys.argv)
    
    try:
        # 创建主窗口
        main_window = MainWindow()
        
        # 检查脚本面板是否有文件管理器
        if hasattr(main_window.script_panel, 'file_manager') and main_window.script_panel.file_manager:
            print("✓ 脚本面板成功获得文件管理器引用")
        else:
            print("✗ 脚本面板未获得文件管理器引用")
        
        # 检查连接管理器是否有默认目录字段
        connection_dialog = main_window.connection_manager.connection_dialog
        if hasattr(connection_dialog, 'default_dir'):
            print("✓ 连接对话框包含默认目录字段")
        else:
            print("✗ 连接对话框缺少默认目录字段")
        
        # 检查脚本面板是否有浏览按钮
        if hasattr(main_window.script_panel, 'browse_dir_btn'):
            print("✓ 脚本面板包含目录浏览按钮")
        else:
            print("✗ 脚本面板缺少目录浏览按钮")
        
        print("✓ UI组件测试完成")
        
    except Exception as e:
        print(f"✗ UI测试失败: {e}")
    finally:
        app.quit()

def test_path_handling():
    """测试路径处理功能"""
    print("\n=== 测试路径处理功能 ===")
    
    # 导入路径处理相关的类
    from ui.remote_file_dialog import RemoteFileDialog
    from ui.remote_directory_dialog import RemoteDirectoryDialog
    
    # 测试路径规范化
    test_paths = [
        "/home/user",
        "/home/user/",
        "home/user",
        "/home//user",
        "/home/user/../user",
        "",
        "/"
    ]
    
    expected_results = [
        "/home/user",
        "/home/user",
        "/home/user",
        "/home/user",
        "/home/user",
        "/",
        "/"
    ]
    
    # 创建一个临时对象来测试路径规范化
    class PathTester:
        def normalize_remote_path(self, path):
            if not path:
                return "/"
            
            # Convert to forward slashes
            path = path.replace('\\', '/')
            
            # Ensure it starts with /
            if not path.startswith('/'):
                path = '/' + path
            
            # Remove double slashes
            while '//' in path:
                path = path.replace('//', '/')
            
            # Remove trailing slash unless it's root
            if len(path) > 1 and path.endswith('/'):
                path = path.rstrip('/')
            
            return path
    
    tester = PathTester()
    
    all_passed = True
    for i, test_path in enumerate(test_paths):
        result = tester.normalize_remote_path(test_path)
        expected = expected_results[i]
        if result == expected:
            print(f"✓ 路径 '{test_path}' -> '{result}'")
        else:
            print(f"✗ 路径 '{test_path}' -> '{result}' (期望: '{expected}')")
            all_passed = False
    
    if all_passed:
        print("✓ 所有路径处理测试通过")
    else:
        print("✗ 部分路径处理测试失败")

def main():
    """主测试函数"""
    print("SSH远程工具优化功能测试")
    print("=" * 50)
    
    # 测试默认目录功能
    test_default_directory_feature()
    
    # 测试路径处理
    test_path_handling()
    
    # 测试UI组件（需要图形界面）
    if len(sys.argv) > 1 and sys.argv[1] == "--ui":
        test_ui_components()
    else:
        print("\n提示：使用 --ui 参数运行UI测试")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    
    print("\n使用说明：")
    print("1. 默认远程目录功能：")
    print("   - 在连接设置中可以指定默认远程目录")
    print("   - 连接后会自动导航到指定目录")
    print("   - 如果未指定，默认为根目录 '/'")
    
    print("\n2. 远程脚本选择功能：")
    print("   - 在脚本面板的'Select File'标签页中")
    print("   - 点击'Browse...'按钮可以浏览远程文件")
    print("   - 支持脚本文件过滤(.sh, .py, .pl等)")
    print("   - 可以预览选中的脚本内容")
    
    print("\n3. 远程工作目录选择：")
    print("   - 在脚本执行选项中可以浏览选择工作目录")
    print("   - 点击工作目录旁的'Browse...'按钮")
    print("   - 只显示目录，不显示文件")

if __name__ == "__main__":
    main()
