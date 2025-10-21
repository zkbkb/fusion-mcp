#!/usr/bin/env python3
"""
Enhanced Logging Configuration System

Provides multi-level logging, file rotation, structured logging and performance monitoring
"""

import logging
import logging.handlers
import os
import sys
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'error_id'):
            log_entry['error_id'] = record.error_id
        if hasattr(record, 'category'):
            log_entry['category'] = record.category
        if hasattr(record, 'severity'):
            log_entry['severity'] = record.severity
        if hasattr(record, 'details'):
            log_entry['details'] = record.details
        if hasattr(record, 'context'):
            log_entry['context'] = record.context
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration
        if hasattr(record, 'performance'):
            log_entry['performance'] = record.performance
        
        # Add exception info
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Add color
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format time
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Build message
        message = f"{color}[{timestamp}] {record.levelname:8} {record.name:20} | {record.getMessage()}{reset}"
        
        # Add exception info
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message

class PerformanceFilter(logging.Filter):
    """Performance monitoring filter"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Only allow performance-related logs through
        return hasattr(record, 'performance') or hasattr(record, 'duration')

class LoggingConfig:
    """Logging configuration manager"""
    
    def __init__(self, base_dir: str = "logs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Log file paths
        self.main_log_file = self.base_dir / "fusion360_mcp.log"
        self.error_log_file = self.base_dir / "error.log"
        self.performance_log_file = self.base_dir / "performance.log"
        self.debug_log_file = self.base_dir / "debug.log"
        
        # Configuration parameters
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        self.console_level = logging.INFO
        self.file_level = logging.DEBUG
        
    def setup_logging(self, enable_console: bool = True, 
                     enable_file: bool = True,
                     enable_json: bool = True,
                     console_level: Optional[str] = None,
                     file_level: Optional[str] = None) -> logging.Logger:
        """Setup logging system
        
        Args:
            enable_console: Enable console output
            enable_file: Enable file output
            enable_json: Enable JSON format
            console_level: Console log level
            file_level: File log level
            
        Returns:
            Configured main logger
        """
        # Create main logger
        logger = logging.getLogger("fusion360-mcp")
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Set log levels
        if console_level:
            self.console_level = getattr(logging, console_level.upper())
        if file_level:
            self.file_level = getattr(logging, file_level.upper())
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.console_level)
            
            # Use colored formatter
            console_formatter = ColoredFormatter()
            console_handler.setFormatter(console_formatter)
            
            logger.addHandler(console_handler)
        
        # File handlers
        if enable_file:
            # Main log file (rotating)
            main_handler = logging.handlers.RotatingFileHandler(
                self.main_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            main_handler.setLevel(self.file_level)
            
            if enable_json:
                main_formatter = JSONFormatter()
            else:
                main_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            main_handler.setFormatter(main_formatter)
            logger.addHandler(main_handler)
            
            # Error log file
            error_handler = logging.handlers.RotatingFileHandler(
                self.error_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(JSONFormatter() if enable_json else main_formatter)
            logger.addHandler(error_handler)
            
            # Performance log file
            performance_handler = logging.handlers.RotatingFileHandler(
                self.performance_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            performance_handler.setLevel(logging.INFO)
            performance_handler.addFilter(PerformanceFilter())
            performance_handler.setFormatter(JSONFormatter() if enable_json else main_formatter)
            logger.addHandler(performance_handler)
            
            # Debug log file (detailed info)
            debug_handler = logging.handlers.RotatingFileHandler(
                self.debug_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(JSONFormatter() if enable_json else main_formatter)
            logger.addHandler(debug_handler)
        
        return logger
    
    def create_child_logger(self, name: str) -> logging.Logger:
        """Create child logger"""
        return logging.getLogger(f"fusion360-mcp.{name}")
    
    def log_performance(self, logger: logging.Logger, operation: str, 
                       duration: float, details: Dict[str, Any] = None):
        """Log performance information
        
        Args:
            logger: Logger
            operation: Operation name
            duration: Duration (milliseconds)
            details: Detail information
        """
        logger.info(
            f"Performance: {operation} completed in {duration:.2f}ms",
            extra={
                "performance": {
                    "operation": operation,
                    "duration_ms": duration,
                    "details": details or {}
                },
                "duration": duration
            }
        )
    
    def log_api_call(self, logger: logging.Logger, endpoint: str, 
                    method: str, duration: float, status: str,
                    request_data: Dict[str, Any] = None,
                    response_data: Dict[str, Any] = None):
        """Log API call
        
        Args:
            logger: Logger
            endpoint: API endpoint
            method: HTTP method
            duration: Response time (milliseconds)
            status: Status
            request_data: Request data
            response_data: Response data
        """
        logger.info(
            f"API Call: {method} {endpoint} - {status} ({duration:.2f}ms)",
            extra={
                "performance": {
                    "type": "api_call",
                    "endpoint": endpoint,
                    "method": method,
                    "duration_ms": duration,
                    "status": status,
                    "request_size": len(str(request_data)) if request_data else 0,
                    "response_size": len(str(response_data)) if response_data else 0
                },
                "duration": duration
            }
        )
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get log statistics"""
        stats = {
            "log_directory": str(self.base_dir),
            "files": {}
        }
        
        for log_file in [self.main_log_file, self.error_log_file, 
                        self.performance_log_file, self.debug_log_file]:
            if log_file.exists():
                stat = log_file.stat()
                stats["files"][log_file.name] = {
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / 1024 / 1024, 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
        
        return stats

class PerformanceMonitor:
    """Performance monitor"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str):
        """Start timer"""
        self._start_times[operation] = time.time() * 1000  # Milliseconds
    
    def end_timer(self, operation: str, details: Dict[str, Any] = None) -> float:
        """End timer and log"""
        if operation not in self._start_times:
            self.logger.warning(f"Timer for operation '{operation}' was not started")
            return 0.0
        
        duration = time.time() * 1000 - self._start_times[operation]
        del self._start_times[operation]
        
        # Log performance info
        logging_config.log_performance(self.logger, operation, duration, details)
        
        return duration
    
    def __call__(self, operation: str):
        """Use as decorator"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self.start_timer(operation)
                try:
                    result = func(*args, **kwargs)
                    self.end_timer(operation, {"success": True})
                    return result
                except Exception as e:
                    self.end_timer(operation, {"success": False, "error": str(e)})
                    raise
            return wrapper
        return decorator

# Global logging configuration instance
logging_config = LoggingConfig()

def get_logger(name: str = None) -> logging.Logger:
    """Convenient function to get logger"""
    if name:
        return logging_config.create_child_logger(name)
    return logging.getLogger("fusion360-mcp")

def setup_logging(**kwargs) -> logging.Logger:
    """Convenient function to setup logging system"""
    return logging_config.setup_logging(**kwargs)

# Auto setup basic logging on import
import functools
try:
    # If no handlers exist, setup default logging
    root_logger = logging.getLogger("fusion360-mcp")
    if not root_logger.handlers:
        setup_logging(enable_console=True, enable_file=True, console_level='INFO')
except Exception as e:
    # If setup fails, use basic configuration
    logging.basicConfig(level=logging.INFO)
    print(f"Warning: Failed to setup enhanced logging: {e}")
