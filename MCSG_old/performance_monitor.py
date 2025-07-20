#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控模块
"""

import psutil
import time
import threading
import re
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from collections import deque


@dataclass
class PerformanceData:
    """性能数据"""
    timestamp: float
    cpu_percent: float
    memory_used: int  # MB
    memory_percent: float
    tps: float = 0.0
    online_players: int = 0
    chunks_loaded: int = 0
    entities_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "cpu_percent": self.cpu_percent,
            "memory_used": self.memory_used,
            "memory_percent": self.memory_percent,
            "tps": self.tps,
            "online_players": self.online_players,
            "chunks_loaded": self.chunks_loaded,
            "entities_count": self.entities_count
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, server_manager=None):
        self.server_manager = server_manager
        self.monitoring = False
        self.monitor_thread = None
        self.data_history = deque(maxlen=300)  # 保存5分钟数据（每秒一次）
        self.callbacks: List[Callable] = []
        
        # TPS相关
        self.last_tps_check = 0
        self.tps_samples = deque(maxlen=20)  # 保存20个TPS样本
        
        # 服务器进程
        self.server_process = None
        
    def add_callback(self, callback: Callable):
        """添加数据更新回调"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """移除数据更新回调"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_monitoring(self):
        """开始监控"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 获取性能数据
                data = self._collect_performance_data()
                
                # 添加到历史记录
                self.data_history.append(data)
                
                # 通知回调
                for callback in self.callbacks:
                    try:
                        callback(data)
                    except Exception as e:
                        print(f"性能监控回调错误: {e}")
                
                time.sleep(1)  # 每秒更新一次
                
            except Exception as e:
                print(f"性能监控错误: {e}")
                time.sleep(1)
    
    def _collect_performance_data(self) -> PerformanceData:
        """收集性能数据"""
        timestamp = time.time()
        
        # 系统性能
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_used = round((memory.total - memory.available) / 1024 / 1024)  # MB
        memory_percent = memory.percent
        
        # 服务器特定数据
        tps = self._get_server_tps()
        online_players = self._get_online_players()
        chunks_loaded = self._get_chunks_loaded()
        entities_count = self._get_entities_count()
        
        return PerformanceData(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_used=memory_used,
            memory_percent=memory_percent,
            tps=tps,
            online_players=online_players,
            chunks_loaded=chunks_loaded,
            entities_count=entities_count
        )
    
    def _get_server_process(self):
        """获取服务器进程"""
        if not self.server_manager or not self.server_manager.is_server_running():
            return None
        
        try:
            if hasattr(self.server_manager, 'server_process') and self.server_manager.server_process:
                return psutil.Process(self.server_manager.server_process.pid)
        except (psutil.NoSuchProcess, AttributeError):
            pass
        
        return None
    
    def _get_server_tps(self) -> float:
        """获取服务器TPS"""
        try:
            # 尝试从服务器日志或命令获取TPS
            if self.server_manager and self.server_manager.is_server_running():
                # 这里可以发送/tps命令或解析日志
                # 目前返回模拟数据
                current_time = time.time()
                if current_time - self.last_tps_check > 5:  # 每5秒检查一次
                    self.last_tps_check = current_time
                    # 模拟TPS计算
                    import random
                    tps = random.uniform(18.0, 20.0)
                    self.tps_samples.append(tps)
                
                if self.tps_samples:
                    return sum(self.tps_samples) / len(self.tps_samples)
        except Exception:
            pass
        
        return 0.0
    
    def _get_online_players(self) -> int:
        """获取在线玩家数"""
        try:
            # 可以通过解析服务器日志或发送命令获取
            # 目前返回模拟数据
            if self.server_manager and self.server_manager.is_server_running():
                import random
                return random.randint(0, 5)
        except Exception:
            pass
        
        return 0
    
    def _get_chunks_loaded(self) -> int:
        """获取已加载区块数"""
        try:
            # 可以通过服务器API或日志获取
            # 目前返回模拟数据
            if self.server_manager and self.server_manager.is_server_running():
                import random
                return random.randint(100, 500)
        except Exception:
            pass
        
        return 0
    
    def _get_entities_count(self) -> int:
        """获取实体数量"""
        try:
            # 可以通过服务器API或日志获取
            # 目前返回模拟数据
            if self.server_manager and self.server_manager.is_server_running():
                import random
                return random.randint(50, 200)
        except Exception:
            pass
        
        return 0
    
    def get_current_data(self) -> Optional[PerformanceData]:
        """获取当前性能数据"""
        if self.data_history:
            return self.data_history[-1]
        return None
    
    def get_history_data(self, minutes: int = 5) -> List[PerformanceData]:
        """获取历史数据"""
        if not self.data_history:
            return []
        
        # 计算需要的数据点数量
        points_needed = minutes * 60  # 每分钟60个数据点
        
        if len(self.data_history) <= points_needed:
            return list(self.data_history)
        else:
            return list(self.data_history)[-points_needed:]
    
    def get_average_data(self, minutes: int = 5) -> Dict:
        """获取平均性能数据"""
        history = self.get_history_data(minutes)
        
        if not history:
            return {
                "cpu_percent": 0.0,
                "memory_used": 0,
                "memory_percent": 0.0,
                "tps": 0.0,
                "online_players": 0,
                "chunks_loaded": 0,
                "entities_count": 0
            }
        
        return {
            "cpu_percent": sum(d.cpu_percent for d in history) / len(history),
            "memory_used": sum(d.memory_used for d in history) / len(history),
            "memory_percent": sum(d.memory_percent for d in history) / len(history),
            "tps": sum(d.tps for d in history) / len(history),
            "online_players": sum(d.online_players for d in history) / len(history),
            "chunks_loaded": sum(d.chunks_loaded for d in history) / len(history),
            "entities_count": sum(d.entities_count for d in history) / len(history)
        }
    
    def get_peak_data(self, minutes: int = 5) -> Dict:
        """获取峰值数据"""
        history = self.get_history_data(minutes)
        
        if not history:
            return {
                "max_cpu": 0.0,
                "max_memory": 0,
                "min_tps": 0.0,
                "max_players": 0
            }
        
        return {
            "max_cpu": max(d.cpu_percent for d in history),
            "max_memory": max(d.memory_used for d in history),
            "min_tps": min(d.tps for d in history) if any(d.tps > 0 for d in history) else 0.0,
            "max_players": max(d.online_players for d in history)
        }
    
    def get_performance_status(self) -> str:
        """获取性能状态"""
        current = self.get_current_data()
        if not current:
            return "未知"
        
        # 根据TPS和CPU使用率判断性能状态
        if current.tps >= 19.5 and current.cpu_percent < 50:
            return "优秀"
        elif current.tps >= 18.0 and current.cpu_percent < 70:
            return "良好"
        elif current.tps >= 15.0 and current.cpu_percent < 85:
            return "一般"
        else:
            return "较差"
    
    def get_performance_suggestions(self) -> List[str]:
        """获取性能优化建议"""
        suggestions = []
        current = self.get_current_data()
        
        if not current:
            return ["无法获取性能数据"]
        
        # CPU使用率建议
        if current.cpu_percent > 80:
            suggestions.append("CPU使用率过高，建议减少插件或优化服务器配置")
        
        # 内存使用建议
        if current.memory_percent > 85:
            suggestions.append("内存使用率过高，建议增加内存分配或清理无用数据")
        
        # TPS建议
        if current.tps < 18.0:
            suggestions.append("TPS过低，建议检查插件性能或减少实体数量")
        
        # 实体数量建议
        if current.entities_count > 1000:
            suggestions.append("实体数量过多，建议清理不必要的实体")
        
        if not suggestions:
            suggestions.append("服务器性能良好，无需特别优化")
        
        return suggestions
    
    def export_performance_report(self, file_path: str, hours: int = 1):
        """导出性能报告"""
        try:
            history = self.get_history_data(hours * 60)
            average = self.get_average_data(hours * 60)
            peak = self.get_peak_data(hours * 60)
            
            report = {
                "report_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_hours": hours,
                "data_points": len(history),
                "average_performance": average,
                "peak_performance": peak,
                "current_status": self.get_performance_status(),
                "suggestions": self.get_performance_suggestions(),
                "detailed_data": [d.to_dict() for d in history]
            }
            
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"导出性能报告失败: {e}")
            return False