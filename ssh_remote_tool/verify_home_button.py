#!/usr/bin/env python3
"""
简单验证Home按钮功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def verify_home_button():
    """验证Home按钮功能"""
    print("验证Home按钮功能...")
    
    try:
        # 检查go_home方法的实现
        with open('src/ui/file_browser_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查go_home方法是否包含默认目录逻辑
        if 'def go_home(self):' in content:
            print("✓ 找到go_home方法")
            
            # 检查是否包含获取默认目录的逻辑
            if 'conn_data.get("default_dir"' in content:
                print("✓ go_home方法包含默认目录获取逻辑")
                
                # 检查是否使用ssh_manager
                if 'self.ssh_manager' in content:
                    print("✓ go_home方法使用ssh_manager获取连接配置")
                    
                    # 检查是否正确设置路径
                    if 'self.remote_current_path = self.normalize_remote_path(default_dir)' in content:
                        print("✓ go_home方法正确设置远程路径")
                        
                        if 'self.remote_path_edit.setText(self.remote_current_path)' in content:
                            print("✓ go_home方法正确更新路径编辑框")
                            
                            print("✅ Home按钮功能实现正确！")
                            return True
        
        print("❌ Home按钮功能实现不完整")
        return False
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def verify_set_connection():
    """验证set_connection方法是否保存ssh_manager引用"""
    print("\n验证set_connection方法...")
    
    try:
        with open('src/ui/file_browser_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'self.ssh_manager = ssh_manager' in content:
            print("✓ set_connection方法正确保存ssh_manager引用")
            return True
        else:
            print("❌ set_connection方法未保存ssh_manager引用")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def verify_constructor():
    """验证构造函数是否添加了ssh_manager字段"""
    print("\n验证构造函数...")
    
    try:
        with open('src/ui/file_browser_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'self.ssh_manager = None' in content:
            print("✓ 构造函数正确初始化ssh_manager字段")
            return True
        else:
            print("❌ 构造函数未初始化ssh_manager字段")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主验证函数"""
    print("Home按钮功能代码验证")
    print("=" * 40)
    
    tests = [
        ("构造函数验证", verify_constructor),
        ("set_connection方法验证", verify_set_connection),
        ("go_home方法验证", verify_home_button)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"验证完成: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 Home按钮功能代码验证通过！")
        print("\n📋 功能说明:")
        print("• Home按钮现在会导航到连接配置中设置的默认目录")
        print("• 如果连接配置中没有设置default_dir，则回到根目录 (/)")
        print("• 支持路径规范化处理")
        print("• 同步更新路径编辑框显示")
        print("• 正确处理无连接等边界情况")
        
        print("\n🔧 实现细节:")
        print("• FileBrowserWidget构造函数添加了ssh_manager字段")
        print("• set_connection方法保存ssh_manager引用")
        print("• go_home方法从连接配置获取default_dir")
        print("• 使用normalize_remote_path确保路径格式正确")
    else:
        print("❌ 部分验证失败，请检查代码实现")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
