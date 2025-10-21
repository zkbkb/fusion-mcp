#!/usr/bin/env python3
"""
Error Handling Module

Provides comprehensive error handling mechanisms, classification, recovery strategies and user-friendly error reporting
"""

import traceback
import functools
import time
from typing import Any, Dict, Optional, Callable, Union, List, Tuple
from enum import Enum
import logging
from datetime import datetime

# Error severity levels
class ErrorSeverity(Enum):
    LOW = "low"           # Minor error, doesn't affect main functionality
    MEDIUM = "medium"     # Medium error, affects some functionality
    HIGH = "high"         # Severe error, affects main functionality
    CRITICAL = "critical" # Fatal error, system cannot continue

# Error categories
class ErrorCategory(Enum):
    FUSION_API = "fusion_api"         # Fusion360 API related errors
    PLUGIN_COMM = "plugin_comm"       # Plugin communication errors
    VALIDATION = "validation"         # Data validation errors
    RESOURCE = "resource"             # Resource access errors
    NETWORK = "network"               # Network related errors
    FILESYSTEM = "filesystem"         # File system errors
    CONFIG = "config"                 # Configuration errors
    UNKNOWN = "unknown"               # Unknown errors

# Custom exception classes
class Fusion360Error(Exception):
    """Base exception class for Fusion360 related errors"""
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.now()

class PluginCommunicationError(Fusion360Error):
    """Plugin communication error"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.PLUGIN_COMM, ErrorSeverity.HIGH, details)

class FusionAPIError(Fusion360Error):
    """Fusion360 API error"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.FUSION_API, ErrorSeverity.MEDIUM, details)

class ValidationError(Fusion360Error):
    """Data validation error"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.VALIDATION, ErrorSeverity.LOW, details)

class ResourceError(Fusion360Error):
    """Resource access error"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, ErrorCategory.RESOURCE, ErrorSeverity.MEDIUM, details)

class ErrorHandler:
    """Error Handler
    
    Provides unified error handling, logging, recovery strategies and user-friendly error reporting
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_history: List[Dict[str, Any]] = []
        self.retry_strategies: Dict[ErrorCategory, Dict[str, Any]] = self._init_retry_strategies()
        self.max_history_size = 100
    
    def _init_retry_strategies(self) -> Dict[ErrorCategory, Dict[str, Any]]:
        """Initialize retry strategies"""
        return {
            ErrorCategory.PLUGIN_COMM: {
                "max_retries": 3,
                "backoff_factor": 2.0,
                "initial_delay": 1.0,
                "recoverable": True
            },
            ErrorCategory.FUSION_API: {
                "max_retries": 2,
                "backoff_factor": 1.5,
                "initial_delay": 0.5,
                "recoverable": True
            },
            ErrorCategory.NETWORK: {
                "max_retries": 5,
                "backoff_factor": 2.0,
                "initial_delay": 1.0,
                "recoverable": True
            },
            ErrorCategory.RESOURCE: {
                "max_retries": 2,
                "backoff_factor": 1.0,
                "initial_delay": 0.5,
                "recoverable": True
            },
            ErrorCategory.VALIDATION: {
                "max_retries": 0,
                "recoverable": False
            },
            ErrorCategory.CONFIG: {
                "max_retries": 1,
                "backoff_factor": 1.0,
                "initial_delay": 0.1,
                "recoverable": True
            }
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle error
        
        Args:
            error: Exception object
            context: Error context information
            
        Returns:
            Dict[str, Any]: Error handling result
        """
        # Classify error
        fusion_error = self._classify_error(error, context)
        
        # Log error
        error_record = self._log_error(fusion_error, context)
        
        # Add to history
        self._add_to_history(error_record)
        
        # Generate user-friendly error report
        user_report = self._generate_user_report(fusion_error)
        
        # Get recovery suggestions
        recovery_suggestions = self._get_recovery_suggestions(fusion_error)
        
        return {
            "error_id": error_record["error_id"],
            "category": fusion_error.category.value,
            "severity": fusion_error.severity.value,
            "message": fusion_error.message,
            "user_message": user_report["user_message"],
            "technical_details": user_report["technical_details"],
            "recovery_suggestions": recovery_suggestions,
            "recoverable": self._is_recoverable(fusion_error),
            "timestamp": fusion_error.timestamp.isoformat()
        }
    
    def _classify_error(self, error: Exception, context: Dict[str, Any] = None) -> Fusion360Error:
        """Classify error"""
        if isinstance(error, Fusion360Error):
            return error
        
        # Classify based on exception type and context
        error_message = str(error)
        error_type = type(error).__name__
        
        # Plugin communication related errors
        if any(keyword in error_message.lower() for keyword in 
               ["connection", "socket", "timeout", "network", "communication"]):
            return PluginCommunicationError(
                f"Plugin communication error: {error_message}",
                {"original_error": error_type, "context": context}
            )
        
        # Fusion360 API related errors
        if any(keyword in error_message.lower() for keyword in 
               ["fusion", "adsk", "sketch", "feature", "component"]):
            return FusionAPIError(
                f"Fusion360 API error: {error_message}",
                {"original_error": error_type, "context": context}
            )
        
        # Validation errors
        if any(keyword in error_message.lower() for keyword in 
               ["invalid", "validation", "parameter", "argument"]):
            return ValidationError(
                f"Data validation error: {error_message}",
                {"original_error": error_type, "context": context}
            )
        
        # Resource errors
        if any(keyword in error_message.lower() for keyword in 
               ["file", "directory", "path", "resource", "access"]):
            return ResourceError(
                f"Resource access error: {error_message}",
                {"original_error": error_type, "context": context}
            )
        
        # Default to unknown error
        return Fusion360Error(
            f"Unknown error: {error_message}",
            ErrorCategory.UNKNOWN,
            ErrorSeverity.MEDIUM,
            {"original_error": error_type, "context": context}
        )
    
    def _log_error(self, error: Fusion360Error, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Log error"""
        error_id = f"ERR_{int(time.time() * 1000)}"
        
        error_record = {
            "error_id": error_id,
            "timestamp": error.timestamp,
            "category": error.category.value,
            "severity": error.severity.value,
            "message": error.message,
            "details": error.details,
            "context": context or {},
            "traceback": traceback.format_exc()
        }
        
        # Select log level based on severity
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error.severity, logging.ERROR)
        
        self.logger.log(
            log_level,
            f"[{error_id}] {error.category.value.upper()}: {error.message}",
            extra={
                "error_id": error_id,
                "category": error.category.value,
                "severity": error.severity.value,
                "details": error.details,
                "context": context
            }
        )
        
        return error_record
    
    def _add_to_history(self, error_record: Dict[str, Any]):
        """Add to error history"""
        self.error_history.append(error_record)
        
        # Limit history size
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _generate_user_report(self, error: Fusion360Error) -> Dict[str, Any]:
        """Generate user-friendly error report"""
        user_messages = {
            ErrorCategory.PLUGIN_COMM: {
                ErrorSeverity.HIGH: "There's a problem connecting to the Fusion360 plugin, please ensure Fusion360 is running and the plugin is started.",
                ErrorSeverity.MEDIUM: "Plugin communication temporarily interrupted, system is attempting to reconnect.",
                ErrorSeverity.LOW: "Minor plugin communication issue, but doesn't affect main functionality."
            },
            ErrorCategory.FUSION_API: {
                ErrorSeverity.HIGH: "Fusion360 operation failed, please check design document status.",
                ErrorSeverity.MEDIUM: "Some Fusion360 features are temporarily unavailable, please try again later.",
                ErrorSeverity.LOW: "Fusion360 operation encountered a minor issue, automatically handled."
            },
            ErrorCategory.VALIDATION: {
                ErrorSeverity.MEDIUM: "Input parameters are incorrect, please check and correct parameter values.",
                ErrorSeverity.LOW: "Data format needs adjustment, please refer to suggestions for corrections."
            },
            ErrorCategory.RESOURCE: {
                ErrorSeverity.HIGH: "Unable to access necessary resources, please check file permissions and paths.",
                ErrorSeverity.MEDIUM: "Resource access restricted, some features may be unavailable.",
                ErrorSeverity.LOW: "Resource access encountered a minor issue, automatically handled."
            }
        }
        
        category_messages = user_messages.get(error.category, {})
        user_message = category_messages.get(
            error.severity, 
            "An issue was encountered, please check technical details or contact support."
        )
        
        return {
            "user_message": user_message,
            "technical_details": {
                "error_type": error.category.value,
                "severity": error.severity.value,
                "message": error.message,
                "timestamp": error.timestamp.isoformat()
            }
        }
    
    def _get_recovery_suggestions(self, error: Fusion360Error) -> List[str]:
        """Get recovery suggestions"""
        suggestions = {
            ErrorCategory.PLUGIN_COMM: [
                "Ensure Fusion360 is running",
                "Check if plugin is started",
                "Restart Fusion360 plugin",
                "Check firewall settings"
            ],
            ErrorCategory.FUSION_API: [
                "Check if active design document exists",
                "Save current work",
                "Reload design",
                "Check Fusion360 license status"
            ],
            ErrorCategory.VALIDATION: [
                "Check input parameter format and range",
                "Refer to API documentation for parameter requirements",
                "Test with default values"
            ],
            ErrorCategory.RESOURCE: [
                "Check file and directory permissions",
                "Verify path is correct",
                "Clean up temporary files",
                "Check disk space"
            ],
            ErrorCategory.NETWORK: [
                "Check network connection",
                "Retry operation",
                "Check proxy settings"
            ]
        }
        
        return suggestions.get(error.category, ["Contact technical support"])
    
    def _is_recoverable(self, error: Fusion360Error) -> bool:
        """Determine if error is recoverable"""
        strategy = self.retry_strategies.get(error.category, {})
        return strategy.get("recoverable", False)
    
    def retry_with_backoff(self, func: Callable, *args, error_context: Dict[str, Any] = None, **kwargs) -> Any:
        """Retry mechanism with backoff strategy"""
        last_error = None
        
        for category, strategy in self.retry_strategies.items():
            max_retries = strategy.get("max_retries", 0)
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    if attempt < max_retries:
                        delay = strategy.get("initial_delay", 1.0) * (
                            strategy.get("backoff_factor", 2.0) ** attempt
                        )
                        
                        self.logger.warning(
                            f"Operation failed, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries + 1}): {str(e)}"
                        )
                        time.sleep(delay)
                    else:
                        # Last attempt failed, handle error
                        error_result = self.handle_error(e, error_context)
                        self.logger.error(f"Retry failed, abandoning operation: {error_result}")
                        break
        
        if last_error:
            raise last_error
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        if not self.error_history:
            return {"total_errors": 0}
        
        recent_errors = [e for e in self.error_history 
                        if (datetime.now() - e["timestamp"]).total_seconds() < 3600]  # Last 1 hour
        
        categories = {}
        severities = {}
        
        for error in recent_errors:
            cat = error["category"]
            sev = error["severity"]
            categories[cat] = categories.get(cat, 0) + 1
            severities[sev] = severities.get(sev, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "categories": categories,
            "severities": severities,
            "last_error": self.error_history[-1] if self.error_history else None
        }

def error_handler_decorator(error_handler: ErrorHandler, context: Dict[str, Any] = None):
    """Error handler decorator"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_result = error_handler.handle_error(e, context)
                
                # If recoverable error, try retry
                if error_result["recoverable"]:
                    try:
                        return error_handler.retry_with_backoff(func, *args, **kwargs)
                    except Exception:
                        pass  # Retry failed, return error result
                
                # Return error info instead of raising exception
                return {"error": True, **error_result}
        
        return wrapper
    return decorator
