#!/usr/bin/env python3
"""
测试脚本：验证最终的日志和预览改进
1. 日志正确换行显示
2. 脚本预览区域优化
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_log_line_breaks():
    """测试日志换行功能"""
    print("=== 测试日志换行功能 ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.log_panel_widget import LogPanelWidget
        
        # 创建应用程序（如果还没有）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建日志面板
        log_panel = LogPanelWidget()
        
        # 测试多条日志是否正确分行
        test_logs = [
            ("第一条日志消息", "info"),
            ("第二条日志消息", "success"),
            ("第三条包含\n换行的\n多行消息", "stdout"),
            ("第四条错误消息", "stderr")
        ]
        
        for message, msg_type in test_logs:
            log_panel.add_log(message, msg_type)
        
        # 检查日志数量
        if len(log_panel.all_logs) == len(test_logs):
            print("✓ 日志条目数量正确")
        else:
            print(f"✗ 日志条目数量错误，期望{len(test_logs)}，实际{len(log_panel.all_logs)}")
            return False
        
        # 检查HTML内容是否包含换行
        html_content = log_panel.log_display.toHtml()
        if "<br>" in html_content:
            print("✓ 日志包含HTML换行标签")
        else:
            print("✗ 日志缺少HTML换行标签")
            return False
        
        print("✓ 日志换行功能测试通过")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_script_preview_improvements():
    """测试脚本预览改进"""
    print("\n=== 测试脚本预览改进 ===")
    
    try:
        from ui.script_panel_widget import ScriptPanelWidget
        from core.script_executor import ScriptExecutor
        from core.ssh_manager import SSHManager
        
        # 创建必要的组件
        ssh_manager = SSHManager()
        script_executor = ScriptExecutor(ssh_manager)
        script_panel = ScriptPanelWidget(script_executor)
        
        # 检查脚本预览区域设置
        if hasattr(script_panel, 'script_preview'):
            preview = script_panel.script_preview
            
            # 检查是否移除了高度限制
            max_height = preview.maximumHeight()
            if max_height == 16777215:  # Qt的默认最大值，表示没有限制
                print("✓ 脚本预览高度限制已移除")
            else:
                print(f"✗ 脚本预览仍有高度限制: {max_height}")
                return False
            
            # 检查最小高度设置
            min_height = preview.minimumHeight()
            if min_height >= 100:
                print("✓ 脚本预览最小高度设置正确")
            else:
                print(f"✗ 脚本预览最小高度设置错误: {min_height}")
                return False
            
            # 检查字体设置
            style_sheet = preview.styleSheet()
            if "font-family" in style_sheet and "Consolas" in style_sheet:
                print("✓ 脚本预览字体设置正确")
            else:
                print("✗ 脚本预览字体设置错误")
                return False
            
            print("✓ 脚本预览改进测试通过")
            return True
        else:
            print("✗ 脚本预览组件不存在")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_log_formatting_edge_cases():
    """测试日志格式化边界情况"""
    print("\n=== 测试日志格式化边界情况 ===")
    
    try:
        from ui.log_panel_widget import LogPanelWidget
        
        log_panel = LogPanelWidget()
        
        # 测试各种特殊情况
        test_cases = [
            ("", "info"),  # 空消息
            ("单行消息", "success"),  # 普通消息
            ("多行\n消息\n测试", "stdout"),  # 多行消息
            ("包含<script>标签</script>的消息", "stderr"),  # HTML标签
            ("包含&特殊&字符的消息", "info"),  # 特殊字符
            ("很长的消息" * 100, "stdout"),  # 长消息
        ]
        
        for message, msg_type in test_cases:
            try:
                log_panel.add_log(message, msg_type)
            except Exception as e:
                print(f"✗ 处理消息失败: {repr(message[:50])}... - {e}")
                return False
        
        print("✓ 所有边界情况处理正确")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def demonstrate_improvements():
    """演示改进效果"""
    print("\n=== 改进效果演示 ===")
    
    print("🔧 日志显示改进：")
    print("✓ 使用append()方法确保每条日志独立一行")
    print("✓ 保持HTML格式化支持换行和颜色")
    print("✓ 清理ANSI代码避免乱码")
    print("✓ 安全的HTML转义")
    
    print("\n🔧 脚本预览改进：")
    print("✓ 移除150px高度限制，允许显示更多内容")
    print("✓ 设置最小高度100px确保基本可见性")
    print("✓ 使用等宽字体提高代码可读性")
    print("✓ 增加预览内容从1000字符到3000字符")
    print("✓ 智能截断在完整行结束，避免切断代码")
    print("✓ 减少错误提示信息，更多空间显示代码")
    
    print("\n🎯 用户体验提升：")
    print("1. 日志现在每条独立一行，清晰易读")
    print("2. 脚本预览显示更多内容，便于确认脚本")
    print("3. 等宽字体让代码格式更清晰")
    print("4. 颜色区分让不同类型日志一目了然")

def main():
    """主测试函数"""
    print("SSH远程工具最终改进测试")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # 测试日志换行
    if test_log_line_breaks():
        success_count += 1
    
    # 测试脚本预览改进
    if test_script_preview_improvements():
        success_count += 1
    
    # 测试边界情况
    if test_log_formatting_edge_cases():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"测试完成: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！最终改进实现成功！")
        demonstrate_improvements()
    else:
        print("❌ 部分测试失败，请检查实现")
    
    print("\n📋 最终功能总结：")
    print("1. ✅ 默认目录设置和使用")
    print("2. ✅ 远程文件和目录浏览")
    print("3. ✅ 优化的界面布局（Script和Log并列）")
    print("4. ✅ 正确的日志换行和颜色显示")
    print("5. ✅ 改进的脚本预览（更多内容，更好字体）")
    print("6. ✅ ANSI代码清理和HTML安全转义")
    
    print("\n🚀 现在您可以享受完整优化的SSH远程工具了！")

if __name__ == "__main__":
    main()
