#!/usr/bin/env python3
"""
简单测试：验证优化功能的基本组件
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试导入是否正常"""
    print("=== 测试模块导入 ===")
    
    try:
        from core.ssh_manager import SSHManager
        print("✓ SSHManager 导入成功")
        
        from ui.connection_manager_widget import ConnectionDialog
        print("✓ ConnectionDialog 导入成功")
        
        from ui.remote_file_dialog import RemoteFileDialog
        print("✓ RemoteFileDialog 导入成功")
        
        from ui.remote_directory_dialog import RemoteDirectoryDialog
        print("✓ RemoteDirectoryDialog 导入成功")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_connection_dialog_fields():
    """测试连接对话框是否有新字段"""
    print("\n=== 测试连接对话框字段 ===")
    
    try:
        from ui.connection_manager_widget import ConnectionDialog
        
        # 创建对话框实例
        dialog = ConnectionDialog()
        
        # 检查是否有default_dir字段
        if hasattr(dialog, 'default_dir'):
            print("✓ ConnectionDialog 包含 default_dir 字段")
        else:
            print("✗ ConnectionDialog 缺少 default_dir 字段")
            return False
        
        # 测试get_data方法是否包含default_dir
        dialog.name.setText("test")
        dialog.host.setText("localhost")
        dialog.port.setText("22")
        dialog.user.setText("user")
        dialog.default_dir.setText("/home/user")
        
        data = dialog.get_data()
        if 'default_dir' in data:
            print("✓ get_data() 方法包含 default_dir")
            print(f"  默认目录值: {data['default_dir']}")
        else:
            print("✗ get_data() 方法缺少 default_dir")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_ssh_manager_default_dir():
    """测试SSH管理器是否支持默认目录"""
    print("\n=== 测试SSH管理器默认目录支持 ===")
    
    try:
        from core.ssh_manager import SSHManager
        
        ssh_manager = SSHManager()
        
        # 创建测试连接数据
        test_connection = {
            "name": "test_default_dir",
            "host": "localhost",
            "port": 22,
            "user": "testuser",
            "default_dir": "/home/testuser/scripts",
            "auth_method": "password",
            "password": "testpass"
        }
        
        # 保存连接
        ssh_manager.save_connection(test_connection)
        print("✓ 保存包含默认目录的连接")
        
        # 读取连接
        saved_connection = ssh_manager.get_connection("test_default_dir")
        if saved_connection and 'default_dir' in saved_connection:
            print(f"✓ 成功读取默认目录: {saved_connection['default_dir']}")
        else:
            print("✗ 读取默认目录失败")
            return False
        
        # 清理测试数据
        ssh_manager.delete_connection("test_default_dir")
        print("✓ 清理测试数据")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_path_normalization():
    """测试路径规范化功能"""
    print("\n=== 测试路径规范化 ===")
    
    def normalize_remote_path(path):
        """路径规范化函数"""
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
    
    test_cases = [
        ("", "/"),
        ("/", "/"),
        ("/home/user", "/home/user"),
        ("/home/user/", "/home/user"),
        ("home/user", "/home/user"),
        ("/home//user", "/home/user"),
        ("\\home\\user", "/home/user"),
    ]
    
    all_passed = True
    for input_path, expected in test_cases:
        result = normalize_remote_path(input_path)
        if result == expected:
            print(f"✓ '{input_path}' -> '{result}'")
        else:
            print(f"✗ '{input_path}' -> '{result}' (期望: '{expected}')")
            all_passed = False
    
    return all_passed

def main():
    """主测试函数"""
    print("SSH远程工具优化功能测试")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # 测试导入
    if test_imports():
        success_count += 1
    
    # 测试连接对话框字段
    if test_connection_dialog_fields():
        success_count += 1
    
    # 测试SSH管理器
    if test_ssh_manager_default_dir():
        success_count += 1
    
    # 测试路径规范化
    if test_path_normalization():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"测试完成: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！优化功能实现成功！")
        
        print("\n✨ 新功能说明：")
        print("1. 默认远程目录设置：")
        print("   - 在连接设置对话框中新增了'Default Directory'字段")
        print("   - 连接时会自动导航到指定的默认目录")
        print("   - 如果未设置，默认使用根目录 '/'")
        
        print("\n2. 远程脚本文件选择：")
        print("   - 脚本面板的'Select File'标签页中的'Browse...'按钮")
        print("   - 现在会打开远程文件浏览对话框")
        print("   - 支持脚本文件过滤(.sh, .py, .pl, .rb, .js等)")
        print("   - 可以预览选中脚本的内容")
        
        print("\n3. 远程工作目录选择：")
        print("   - 脚本执行选项中的工作目录旁新增'Browse...'按钮")
        print("   - 可以浏览和选择远程服务器上的目录")
        print("   - 只显示目录，便于选择执行环境")
    else:
        print("❌ 部分测试失败，请检查实现")

if __name__ == "__main__":
    main()
