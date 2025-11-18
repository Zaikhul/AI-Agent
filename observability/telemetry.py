"""
Comprehensive observability system with logging, metrics, and tracing
"""
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from collections import defaultdict
import threading

class MetricsCollector:
    """Thread-safe metrics collection"""
    
    def __init__(self):
        self._metrics = defaultdict(list)
        self._lock = threading.Lock()
    
    def record(self, metric_name: str, value: float, tags: Optional[Dict] = None):
        """Record a metric value"""
        with self._lock:
            self._metrics[metric_name].append({
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "tags": tags or {}
            })
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        with self._lock:
            values = [m["value"] for m in self._metrics.get(metric_name, [])]
            
            if not values:
                return {}
            
            return {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics"""
        with self._lock:
            return {
                name: {
                    "stats": self.get_stats(name),
                    "raw_data": metrics
                }
                for name, metrics in self._metrics.items()
            }

class StructuredLogger:
    """Structured logging with JSON output"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # JSON file handler
        json_handler = logging.FileHandler(
            self.log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        json_handler.setFormatter(logging.Formatter('%(message)s'))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        self.logger.addHandler(json_handler)
        self.logger.addHandler(console_handler)
    
    def log(self, level: str, event: str, **kwargs):
        """Log structured event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "level": level,
            **kwargs
        }
        
        log_func = getattr(self.logger, level.lower(), self.logger.info)
        log_func(json.dumps(log_entry))

class ObservabilityManager:
    """Central observability management"""
    
    def __init__(self):
        self.logger = StructuredLogger("agent_system")
        self.metrics = MetricsCollector()
        self._active_traces = {}
    
    def start_trace(self, trace_id: str, operation: str, **metadata):
        """Start a trace"""
        self._active_traces[trace_id] = {
            "operation": operation,
            "start_time": time.time(),
            "metadata": metadata
        }
        
        self.logger.log("info", "trace_start", trace_id=trace_id, operation=operation, **metadata)
    
    def end_trace(self, trace_id: str, success: bool = True, **result):
        """End a trace"""
        if trace_id not in self._active_traces:
            return
        
        trace = self._active_traces.pop(trace_id)
        duration = time.time() - trace["start_time"]
        
        self.metrics.record(
            f"{trace['operation']}_duration",
            duration,
            tags={"success": success}
        )
        
        self.logger.log(
            "info" if success else "error",
            "trace_end",
            trace_id=trace_id,
            operation=trace["operation"],
            duration=duration,
            success=success,
            **result
        )
    
    def log_error(self, error_type: str, error_msg: str, **context):
        """Log error with context"""
        self.logger.log("error", "error_occurred", error_type=error_type, error=error_msg, **context)
        self.metrics.record("errors", 1, tags={"type": error_type})

# Global observability instance
observability = ObservabilityManager()

def trace_operation(operation_name: str):
    """Decorator to trace function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            trace_id = f"{operation_name}_{id(args)}"
            observability.start_trace(trace_id, operation_name)
            
            try:
                result = func(*args, **kwargs)
                observability.end_trace(trace_id, success=True)
                return result
            except Exception as e:
                observability.end_trace(trace_id, success=False, error=str(e))
                raise
        return wrapper
    return decorator
