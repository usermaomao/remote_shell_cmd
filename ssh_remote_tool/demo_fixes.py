#!/usr/bin/env python3
"""
演示修复后的路径处理功能
"""
import sys
import os
import posixpath

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

def normalize_remote_path(path):
    """Normalize remote path to use forward slashes and handle edge cases"""
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

def join_remote_path(base_path, *parts):
    """Join remote path parts using posixpath for consistent forward slashes"""
    # Use posixpath.join for Unix-style paths
    result = posixpath.join(base_path, *parts)
    # Normalize and resolve any ".." components
    result = posixpath.normpath(result)
    return normalize_remote_path(result)

def demo_navigation_scenarios():
    """演示各种导航场景"""
    print("=== SSH远程工具路径处理修复演示 ===\n")
    
    print("1. 基本目录导航:")
    current_path = "/"
    print(f"   当前路径: {current_path}")
    
    # 进入 home 目录
    current_path = join_remote_path(current_path, "home")
    print(f"   进入 'home': {current_path}")
    
    # 进入 user 目录
    current_path = join_remote_path(current_path, "user")
    print(f"   进入 'user': {current_path}")
    
    # 进入 documents 目录
    current_path = join_remote_path(current_path, "documents")
    print(f"   进入 'documents': {current_path}")
    
    print("\n2. 返回上级目录:")
    # 返回上级目录
    current_path = join_remote_path(current_path, "..")
    print(f"   返回上级: {current_path}")
    
    current_path = join_remote_path(current_path, "..")
    print(f"   再次返回上级: {current_path}")
    
    print("\n3. 处理Windows风格路径:")
    windows_style_paths = [
        "home\\user\\documents",
        "\\var\\log\\",
        "tmp\\\\temp\\\\file.txt"
    ]
    
    for win_path in windows_style_paths:
        normalized = normalize_remote_path(win_path)
        print(f"   '{win_path}' -> '{normalized}'")
    
    print("\n4. 复杂路径处理:")
    complex_scenarios = [
        ("/home/user", "../.."),  # 从 /home/user 返回到根目录
        ("/var/log", "../../tmp"),  # 从 /var/log 到 /tmp
        ("/", "home/user/../admin"),  # 从根目录到 /home/admin
    ]
    
    for base, relative in complex_scenarios:
        result = join_remote_path(base, relative)
        print(f"   从 '{base}' 导航 '{relative}' -> '{result}'")
    
    print("\n5. 错误输入处理:")
    error_inputs = [
        "",
        "//multiple//slashes//",
        "no_leading_slash",
        "/trailing/slash/",
    ]
    
    for error_input in error_inputs:
        normalized = normalize_remote_path(error_input)
        print(f"   '{error_input}' -> '{normalized}'")
    
    print("\n=== 修复总结 ===")
    print("✓ 跨平台路径兼容性 (Windows ↔ Linux)")
    print("✓ 正确处理 '..' 父目录导航")
    print("✓ 统一的路径格式化")
    print("✓ 错误输入的容错处理")
    print("✓ 多级目录导航支持")
    print("\n现在您可以安全地在远程服务器上进行多级目录导航了！")

if __name__ == "__main__":
    demo_navigation_scenarios()
