"""
性能监控工具
实时监控SSH远程工具的性能指标，确保满足PRD要求
"""

import time
import threading
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: float
    memory_usage_mb: float
    cpu_usage_percent: float
    active_connections: int
    cached_sftp_connections: int
    ui_response_time_ms: float
    operation_type: str

class PerformanceMonitor(QObject):
    """性能监控器"""
    
    # 信号定义
    metrics_updated = pyqtSignal(PerformanceMetrics)
    performance_warning = pyqtSignal(str, str)  # type, message
    
    def __init__(self):
        super().__init__()
        self.is_monitoring = False
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 1000
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._collect_metrics)
        
        # 性能阈值（基于PRD要求）
        self.thresholds = {
            'ui_response_time_ms': 200,  # 0.2秒
            'memory_usage_mb': 500,      # 500MB内存限制
            'cpu_usage_percent': 80,     # 80% CPU使用率
            'max_connections': 10        # 最大连接数
        }
        
        # 组件引用
        self.ssh_manager = None
        self.file_manager = None
        
    def set_components(self, ssh_manager, file_manager):
        """设置要监控的组件"""
        self.ssh_manager = ssh_manager
        self.file_manager = file_manager
    
    def start_monitoring(self, interval_ms: int = 1000):
        """开始性能监控"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_timer.start(interval_ms)
            print(f"性能监控已启动，监控间隔: {interval_ms}ms")
    
    def stop_monitoring(self):
        """停止性能监控"""
        if self.is_monitoring:
            self.is_monitoring = False
            self.monitor_timer.stop()
            print("性能监控已停止")
    
    def _collect_metrics(self):
        """收集性能指标"""
        try:
            # 获取系统指标
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
            
            # 获取连接指标
            active_connections = 0
            cached_sftp_connections = 0
            
            if self.ssh_manager:
                active_connections = len(self.ssh_manager.active_clients)
            
            if self.file_manager:
                cached_sftp_connections = len(self.file_manager._sftp_cache)
            
            # 创建性能指标
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                memory_usage_mb=memory_mb,
                cpu_usage_percent=cpu_percent,
                active_connections=active_connections,
                cached_sftp_connections=cached_sftp_connections,
                ui_response_time_ms=0,  # 由UI操作时更新
                operation_type="monitoring"
            )
            
            # 添加到历史记录
            self._add_metrics(metrics)
            
            # 检查性能阈值
            self._check_thresholds(metrics)
            
            # 发送更新信号
            self.metrics_updated.emit(metrics)
            
        except Exception as e:
            print(f"性能监控错误: {e}")
    
    def _add_metrics(self, metrics: PerformanceMetrics):
        """添加指标到历史记录"""
        self.metrics_history.append(metrics)
        
        # 限制历史记录大小
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
    
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """检查性能阈值并发出警告"""
        # 检查UI响应时间
        if metrics.ui_response_time_ms > self.thresholds['ui_response_time_ms']:
            self.performance_warning.emit(
                "UI响应时间",
                f"UI响应时间 {metrics.ui_response_time_ms:.1f}ms 超过阈值 {self.thresholds['ui_response_time_ms']}ms"
            )
        
        # 检查内存使用
        if metrics.memory_usage_mb > self.thresholds['memory_usage_mb']:
            self.performance_warning.emit(
                "内存使用",
                f"内存使用 {metrics.memory_usage_mb:.1f}MB 超过阈值 {self.thresholds['memory_usage_mb']}MB"
            )
        
        # 检查CPU使用率
        if metrics.cpu_usage_percent > self.thresholds['cpu_usage_percent']:
            self.performance_warning.emit(
                "CPU使用率",
                f"CPU使用率 {metrics.cpu_usage_percent:.1f}% 超过阈值 {self.thresholds['cpu_usage_percent']}%"
            )
        
        # 检查连接数
        if metrics.active_connections > self.thresholds['max_connections']:
            self.performance_warning.emit(
                "连接数",
                f"活动连接数 {metrics.active_connections} 超过阈值 {self.thresholds['max_connections']}"
            )
    
    def record_ui_operation(self, operation_type: str, duration_ms: float):
        """记录UI操作的响应时间"""
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            memory_usage_mb=0,  # 不在此处测量
            cpu_usage_percent=0,  # 不在此处测量
            active_connections=0,  # 不在此处测量
            cached_sftp_connections=0,  # 不在此处测量
            ui_response_time_ms=duration_ms,
            operation_type=operation_type
        )
        
        self._add_metrics(metrics)
        
        # 检查UI响应时间阈值
        if duration_ms > self.thresholds['ui_response_time_ms']:
            self.performance_warning.emit(
                "UI响应时间",
                f"{operation_type} 操作耗时 {duration_ms:.1f}ms 超过阈值 {self.thresholds['ui_response_time_ms']}ms"
            )
    
    def get_performance_summary(self) -> Dict:
        """获取性能摘要"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.metrics_history[-10:]  # 最近10个指标
        
        # 计算平均值
        avg_memory = sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m.cpu_usage_percent for m in recent_metrics) / len(recent_metrics)
        
        # 获取UI响应时间指标
        ui_metrics = [m for m in self.metrics_history if m.ui_response_time_ms > 0]
        avg_ui_response = 0
        max_ui_response = 0
        
        if ui_metrics:
            avg_ui_response = sum(m.ui_response_time_ms for m in ui_metrics) / len(ui_metrics)
            max_ui_response = max(m.ui_response_time_ms for m in ui_metrics)
        
        # 获取当前连接状态
        current_metrics = recent_metrics[-1]
        
        return {
            'average_memory_mb': avg_memory,
            'average_cpu_percent': avg_cpu,
            'average_ui_response_ms': avg_ui_response,
            'max_ui_response_ms': max_ui_response,
            'current_active_connections': current_metrics.active_connections,
            'current_cached_sftp': current_metrics.cached_sftp_connections,
            'total_operations': len(ui_metrics),
            'monitoring_duration_minutes': (time.time() - self.metrics_history[0].timestamp) / 60 if self.metrics_history else 0
        }
    
    def export_metrics(self, filepath: str):
        """导出性能指标到文件"""
        try:
            import json
            
            data = {
                'export_time': time.time(),
                'thresholds': self.thresholds,
                'metrics': [
                    {
                        'timestamp': m.timestamp,
                        'memory_usage_mb': m.memory_usage_mb,
                        'cpu_usage_percent': m.cpu_usage_percent,
                        'active_connections': m.active_connections,
                        'cached_sftp_connections': m.cached_sftp_connections,
                        'ui_response_time_ms': m.ui_response_time_ms,
                        'operation_type': m.operation_type
                    }
                    for m in self.metrics_history
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"性能指标已导出到: {filepath}")
            
        except Exception as e:
            print(f"导出性能指标失败: {e}")

class UIPerformanceDecorator:
    """UI性能装饰器 - 自动测量UI操作响应时间"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __call__(self, operation_name: str):
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    self.monitor.record_ui_operation(operation_name, duration_ms)
            return wrapper
        return decorator

# 全局性能监控器实例
performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    return performance_monitor

def monitor_ui_operation(operation_name: str):
    """装饰器：监控UI操作性能"""
    return UIPerformanceDecorator(performance_monitor)(operation_name)
