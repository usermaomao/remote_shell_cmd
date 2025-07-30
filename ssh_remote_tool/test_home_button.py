#!/usr/bin/env python3
"""
测试Home按钮功能 - 验证是否正确导航到连接配置的默认目录
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_home_button_functionality():
    """测试Home按钮功能"""
    print("=== 测试Home按钮功能 ===")

    try:
        from PyQt6.QtWidgets import QApplication
        from core.ssh_manager import SSHManager
        from core.file_manager import FileManager
        from ui.file_browser_widget import FileBrowserWidget

        # 创建QApplication（如果还没有）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建组件
        ssh_manager = SSHManager()
        file_manager = FileManager(ssh_manager)
        file_browser = FileBrowserWidget(file_manager)
        
        # 模拟连接配置数据
        test_connection_data = {
            "name": "test_server",
            "host": "192.168.1.100",
            "port": 22,
            "user": "testuser",
            "default_dir": "/home/testuser/projects",  # 自定义默认目录
            "auth_method": "password",
            "password": "testpass"
        }
        
        # 模拟ssh_manager的get_connection方法
        def mock_get_connection(name):
            if name == "test_server":
                return test_connection_data
            return None
        
        ssh_manager.get_connection = mock_get_connection
        
        # 测试设置连接
        print("✓ 设置测试连接...")
        file_browser.set_connection("test_server", ssh_manager)
        
        # 验证初始路径是否为默认目录
        initial_path = file_browser.remote_current_path
        expected_default = "/home/testuser/projects"
        
        print(f"✓ 初始路径: {initial_path}")
        print(f"✓ 期望默认目录: {expected_default}")
        
        if initial_path == expected_default:
            print("✅ 连接时正确设置为默认目录")
        else:
            print(f"❌ 连接时路径错误，期望 {expected_default}，实际 {initial_path}")
            return False
        
        # 模拟导航到其他目录
        print("✓ 模拟导航到其他目录...")
        file_browser.remote_current_path = "/tmp"
        file_browser.remote_path_edit.setText("/tmp")
        
        current_path = file_browser.remote_current_path
        print(f"✓ 当前路径: {current_path}")
        
        # 测试Home按钮功能
        print("✓ 测试Home按钮功能...")
        file_browser.go_home()
        
        # 验证是否回到默认目录
        home_path = file_browser.remote_current_path
        path_edit_text = file_browser.remote_path_edit.text()
        
        print(f"✓ Home后路径: {home_path}")
        print(f"✓ 路径编辑框文本: {path_edit_text}")
        
        if home_path == expected_default and path_edit_text == expected_default:
            print("✅ Home按钮功能正常 - 正确回到默认目录")
            return True
        else:
            print(f"❌ Home按钮功能异常")
            print(f"   期望路径: {expected_default}")
            print(f"   实际路径: {home_path}")
            print(f"   编辑框文本: {path_edit_text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_home_button_without_default():
    """测试没有设置默认目录时的Home按钮功能"""
    print("\n=== 测试无默认目录的Home按钮功能 ===")

    try:
        from PyQt6.QtWidgets import QApplication
        from core.ssh_manager import SSHManager
        from core.file_manager import FileManager
        from ui.file_browser_widget import FileBrowserWidget

        # 确保QApplication存在
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建组件
        ssh_manager = SSHManager()
        file_manager = FileManager(ssh_manager)
        file_browser = FileBrowserWidget(file_manager)
        
        # 模拟没有默认目录的连接配置
        test_connection_data = {
            "name": "test_server2",
            "host": "192.168.1.101",
            "port": 22,
            "user": "testuser2",
            # 没有default_dir字段
            "auth_method": "password",
            "password": "testpass"
        }
        
        # 模拟ssh_manager的get_connection方法
        def mock_get_connection(name):
            if name == "test_server2":
                return test_connection_data
            return None
        
        ssh_manager.get_connection = mock_get_connection
        
        # 测试设置连接
        print("✓ 设置无默认目录的测试连接...")
        file_browser.set_connection("test_server2", ssh_manager)
        
        # 验证初始路径是否为根目录
        initial_path = file_browser.remote_current_path
        expected_default = "/"
        
        print(f"✓ 初始路径: {initial_path}")
        print(f"✓ 期望默认目录: {expected_default}")
        
        # 模拟导航到其他目录
        file_browser.remote_current_path = "/home/user"
        file_browser.remote_path_edit.setText("/home/user")
        
        # 测试Home按钮功能
        print("✓ 测试Home按钮功能...")
        file_browser.go_home()
        
        # 验证是否回到根目录
        home_path = file_browser.remote_current_path
        
        print(f"✓ Home后路径: {home_path}")
        
        if home_path == expected_default:
            print("✅ 无默认目录时Home按钮功能正常 - 回到根目录")
            return True
        else:
            print(f"❌ 无默认目录时Home按钮功能异常，期望 {expected_default}，实际 {home_path}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_home_button_edge_cases():
    """测试Home按钮的边界情况"""
    print("\n=== 测试Home按钮边界情况 ===")

    try:
        from PyQt6.QtWidgets import QApplication
        from core.ssh_manager import SSHManager
        from core.file_manager import FileManager
        from ui.file_browser_widget import FileBrowserWidget

        # 确保QApplication存在
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建组件
        ssh_manager = SSHManager()
        file_manager = FileManager(ssh_manager)
        file_browser = FileBrowserWidget(file_manager)
        
        # 测试1: 没有连接时点击Home
        print("✓ 测试无连接时的Home按钮...")
        file_browser.current_connection = None
        file_browser.go_home()  # 应该安全返回，不报错
        print("✅ 无连接时Home按钮安全处理")
        
        # 测试2: 连接不存在时点击Home
        print("✓ 测试不存在连接的Home按钮...")
        file_browser.current_connection = "nonexistent"
        file_browser.ssh_manager = ssh_manager
        
        def mock_get_connection(name):
            return None  # 连接不存在
        
        ssh_manager.get_connection = mock_get_connection
        file_browser.go_home()  # 应该回到根目录
        
        if file_browser.remote_current_path == "/":
            print("✅ 不存在连接时Home按钮回到根目录")
        else:
            print(f"❌ 不存在连接时Home按钮异常: {file_browser.remote_current_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 边界情况测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("Home按钮功能测试")
    print("=" * 50)
    
    tests = [
        ("Home按钮基本功能", test_home_button_functionality),
        ("无默认目录的Home按钮", test_home_button_without_default),
        ("Home按钮边界情况", test_home_button_edge_cases)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有Home按钮功能测试通过！")
        print("\n✅ Home按钮优化总结:")
        print("• Home按钮现在会导航到连接配置中设置的默认目录")
        print("• 如果没有设置默认目录，则回到根目录 (/)")
        print("• 正确处理各种边界情况（无连接、连接不存在等）")
        print("• 路径编辑框会同步更新显示正确路径")
    else:
        print("❌ 部分测试失败，请检查Home按钮实现")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
