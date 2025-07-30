#!/usr/bin/env python3
"""
测试脚本：验证日志显示的改进
测试换行、颜色和ANSI代码清理功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_log_formatting():
    """测试日志格式化功能"""
    print("=== 测试日志格式化功能 ===")
    
    try:
        from ui.log_panel_widget import LogPanelWidget
        
        # 创建日志面板
        log_panel = LogPanelWidget()
        
        # 测试ANSI代码清理
        test_message_with_ansi = "\x1b[36m[09:36:01] [INFO]\x1b[0m 这是一条包含ANSI颜色代码的消息"
        cleaned = log_panel.clean_ansi_codes(test_message_with_ansi)
        expected = "[09:36:01] [INFO] 这是一条包含ANSI颜色代码的消息"
        
        if cleaned == expected:
            print("✓ ANSI代码清理功能正常")
        else:
            print(f"✗ ANSI代码清理失败")
            print(f"  输入: {repr(test_message_with_ansi)}")
            print(f"  输出: {repr(cleaned)}")
            print(f"  期望: {repr(expected)}")
            return False
        
        # 测试HTML格式化
        test_message_with_newlines = "第一行\n第二行\n第三行"
        formatted = log_panel.format_message_for_html(test_message_with_newlines)
        expected_html = "第一行<br>第二行<br>第三行"
        
        if formatted == expected_html:
            print("✓ HTML格式化功能正常")
        else:
            print(f"✗ HTML格式化失败")
            print(f"  输入: {repr(test_message_with_newlines)}")
            print(f"  输出: {repr(formatted)}")
            print(f"  期望: {repr(expected_html)}")
            return False
        
        # 测试HTML转义
        test_message_with_html = "这是<script>alert('test')</script>消息"
        formatted = log_panel.format_message_for_html(test_message_with_html)
        if "&lt;script&gt;" in formatted and "&lt;/script&gt;" in formatted:
            print("✓ HTML转义功能正常")
        else:
            print("✗ HTML转义功能失败")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_log_panel_ui():
    """测试日志面板UI改进"""
    print("\n=== 测试日志面板UI ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.log_panel_widget import LogPanelWidget
        
        # 创建应用程序（如果还没有）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建日志面板
        log_panel = LogPanelWidget()
        
        # 检查样式设置
        style_sheet = log_panel.log_display.styleSheet()
        if "font-family" in style_sheet and "Consolas" in style_sheet:
            print("✓ 日志面板字体设置正确")
        else:
            print("✗ 日志面板字体设置失败")
            return False
        
        # 测试添加不同类型的日志
        test_logs = [
            ("这是一条信息日志", "info"),
            ("这是一条成功日志", "success"),
            ("这是一条错误日志", "stderr"),
            ("这是一条\n多行\n输出日志", "stdout"),
            ("这是包含\x1b[32m颜色代码\x1b[0m的日志", "stdout")
        ]
        
        for message, msg_type in test_logs:
            log_panel.add_log(message, msg_type)
        
        print("✓ 成功添加测试日志")
        
        # 检查日志数量
        if len(log_panel.all_logs) == len(test_logs):
            print("✓ 日志存储正确")
        else:
            print(f"✗ 日志存储错误，期望{len(test_logs)}条，实际{len(log_panel.all_logs)}条")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def demonstrate_log_improvements():
    """演示日志改进效果"""
    print("\n=== 日志改进效果演示 ===")
    
    print("改进前的问题：")
    print("- 日志没有换行，所有内容挤在一行")
    print("- ANSI颜色代码显示为乱码")
    print("- 没有颜色区分不同类型的日志")
    print("- 字体不适合查看代码输出")
    
    print("\n改进后的效果：")
    print("✓ 正确处理换行符，多行输出清晰显示")
    print("✓ 自动清理ANSI颜色代码，避免乱码")
    print("✓ 不同类型日志使用不同颜色：")
    print("  - INFO: 蓝色")
    print("  - SUCCESS: 绿色") 
    print("  - ERROR/STDERR: 红色")
    print("  - STDOUT: 深绿色")
    print("✓ 使用等宽字体，便于查看代码和命令输出")
    print("✓ 改进的HTML格式化，保持原始格式")
    print("✓ 安全的HTML转义，防止XSS攻击")

def main():
    """主测试函数"""
    print("SSH远程工具日志显示改进测试")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # 测试日志格式化
    if test_log_formatting():
        success_count += 1
    
    # 测试UI改进（需要图形界面）
    if len(sys.argv) > 1 and sys.argv[1] == "--ui":
        if test_log_panel_ui():
            success_count += 1
    else:
        print("\n提示：使用 --ui 参数运行UI测试")
        total_tests = 1  # 不包括UI测试
    
    print("\n" + "=" * 50)
    print(f"测试完成: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！日志显示改进成功！")
        demonstrate_log_improvements()
    else:
        print("❌ 部分测试失败，请检查实现")
    
    print("\n📋 使用说明：")
    print("1. 日志现在会正确显示换行和格式")
    print("2. ANSI颜色代码会被自动清理")
    print("3. 不同类型的日志有不同的颜色")
    print("4. 使用等宽字体便于查看代码输出")
    print("5. 支持HTML安全转义")

if __name__ == "__main__":
    main()
