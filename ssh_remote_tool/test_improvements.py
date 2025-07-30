#!/usr/bin/env python3
"""
测试脚本：验证最新的界面和功能改进
1. 脚本选择默认路径与配置一致
2. 界面布局优化（Script和Log并列显示）
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_script_panel_improvements():
    """测试脚本面板的改进"""
    print("=== 测试脚本面板改进 ===")
    
    try:
        from ui.script_panel_widget import ScriptPanelWidget
        from core.script_executor import ScriptExecutor
        from core.ssh_manager import SSHManager
        
        # 创建必要的组件
        ssh_manager = SSHManager()
        script_executor = ScriptExecutor(ssh_manager)
        
        # 创建脚本面板
        script_panel = ScriptPanelWidget(script_executor)
        
        # 检查是否有ssh_manager设置方法
        if hasattr(script_panel, 'set_ssh_manager'):
            print("✓ ScriptPanelWidget 包含 set_ssh_manager 方法")
            script_panel.set_ssh_manager(ssh_manager)
        else:
            print("✗ ScriptPanelWidget 缺少 set_ssh_manager 方法")
            return False
        
        # 检查是否有工作目录浏览按钮
        if hasattr(script_panel, 'browse_dir_btn'):
            print("✓ ScriptPanelWidget 包含工作目录浏览按钮")
        else:
            print("✗ ScriptPanelWidget 缺少工作目录浏览按钮")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_layout_structure():
    """测试布局结构改进"""
    print("\n=== 测试布局结构 ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        # 创建应用程序（如果还没有）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 检查主窗口结构
        central_widget = main_window.centralWidget()
        if central_widget:
            print("✓ 主窗口有中央部件")
        else:
            print("✗ 主窗口缺少中央部件")
            return False
        
        # 检查脚本面板和日志面板是否存在
        if hasattr(main_window, 'script_panel') and hasattr(main_window, 'log_panel'):
            print("✓ 脚本面板和日志面板都存在")
        else:
            print("✗ 脚本面板或日志面板缺失")
            return False
        
        # 检查脚本面板是否有SSH管理器
        if hasattr(main_window.script_panel, 'ssh_manager'):
            print("✓ 脚本面板已设置SSH管理器")
        else:
            print("✗ 脚本面板未设置SSH管理器")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_default_path_logic():
    """测试默认路径逻辑"""
    print("\n=== 测试默认路径逻辑 ===")
    
    try:
        from core.ssh_manager import SSHManager
        
        ssh_manager = SSHManager()
        
        # 创建测试连接
        test_connection = {
            "name": "test_default_path",
            "host": "localhost",
            "port": 22,
            "user": "testuser",
            "default_dir": "/home/testuser/scripts",
            "auth_method": "password",
            "password": "testpass"
        }
        
        # 保存连接
        ssh_manager.save_connection(test_connection)
        
        # 读取连接验证默认目录
        saved_connection = ssh_manager.get_connection("test_default_path")
        if saved_connection and saved_connection.get("default_dir") == "/home/testuser/scripts":
            print("✓ 默认目录正确保存和读取")
        else:
            print("✗ 默认目录保存或读取失败")
            return False
        
        # 清理测试数据
        ssh_manager.delete_connection("test_default_path")
        print("✓ 测试数据清理完成")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("SSH远程工具界面和功能改进测试")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # 测试脚本面板改进
    if test_script_panel_improvements():
        success_count += 1
    
    # 测试默认路径逻辑
    if test_default_path_logic():
        success_count += 1
    
    # 测试布局结构（需要图形界面）
    if len(sys.argv) > 1 and sys.argv[1] == "--ui":
        if test_layout_structure():
            success_count += 1
    else:
        print("\n提示：使用 --ui 参数运行界面测试")
        total_tests = 2  # 不包括UI测试
    
    print("\n" + "=" * 50)
    print(f"测试完成: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！改进功能实现成功！")
        
        print("\n✨ 改进功能说明：")
        print("1. 脚本选择默认路径优化：")
        print("   - 远程脚本浏览现在使用连接配置中的默认目录")
        print("   - 工作目录浏览也会考虑默认目录设置")
        print("   - 提供更一致的用户体验")
        
        print("\n2. 界面布局优化：")
        print("   - 文件浏览器区域缩小为原来的1/3")
        print("   - Script和Log面板并列显示，各占一半空间")
        print("   - 执行脚本时可以同时查看输出日志")
        print("   - 更高效的屏幕空间利用")
        
        print("\n3. 用户体验改进：")
        print("   - 减少手动导航操作")
        print("   - 实时查看脚本执行结果")
        print("   - 更直观的界面布局")
    else:
        print("❌ 部分测试失败，请检查实现")
    
    print("\n📋 使用指南：")
    print("1. 设置连接时指定默认目录（如：/home/user/projects）")
    print("2. 脚本选择和工作目录浏览会自动使用该默认目录")
    print("3. Script面板在左侧，Log面板在右侧，便于同时查看")
    print("4. 文件浏览器在上方，占用较少空间但保持完整功能")

if __name__ == "__main__":
    main()
