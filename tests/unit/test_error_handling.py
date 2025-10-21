#!/usr/bin/env python3
"""
Error Handling System Unit Tests

Test error classification, handling, recovery strategies and user-friendly reporting
"""

import unittest
import logging
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils.error_handler import (
    ErrorHandler, ErrorSeverity, ErrorCategory,
    Fusion360Error, PluginCommunicationError, FusionAPIError,
    ValidationError, ResourceError, error_handler_decorator
)
from utils.logging_config import LoggingConfig, PerformanceMonitor

class TestErrorSeverity(unittest.TestCase):
    """Test error severity level enum"""
    
    def test_error_severity_values(self):
        """Test error severity level values"""
        self.assertEqual(ErrorSeverity.LOW.value, "low")
        self.assertEqual(ErrorSeverity.MEDIUM.value, "medium")
        self.assertEqual(ErrorSeverity.HIGH.value, "high")
        self.assertEqual(ErrorSeverity.CRITICAL.value, "critical")

class TestErrorCategory(unittest.TestCase):
    """Test error category enum"""
    
    def test_error_category_values(self):
        """Test error category values"""
        self.assertEqual(ErrorCategory.FUSION_API.value, "fusion_api")
        self.assertEqual(ErrorCategory.PLUGIN_COMM.value, "plugin_comm")
        self.assertEqual(ErrorCategory.VALIDATION.value, "validation")
        self.assertEqual(ErrorCategory.RESOURCE.value, "resource")
        self.assertEqual(ErrorCategory.NETWORK.value, "network")
        self.assertEqual(ErrorCategory.FILESYSTEM.value, "filesystem")
        self.assertEqual(ErrorCategory.CONFIG.value, "config")
        self.assertEqual(ErrorCategory.UNKNOWN.value, "unknown")

class TestCustomExceptions(unittest.TestCase):
    """Test custom exception classes"""
    
    def test_fusion360_error(self):
        """Test Fusion360Error base exception"""
        error = Fusion360Error(
            "Test error",
            ErrorCategory.FUSION_API,
            ErrorSeverity.HIGH,
            {"detail": "test"}
        )
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.category, ErrorCategory.FUSION_API)
        self.assertEqual(error.severity, ErrorSeverity.HIGH)
        self.assertEqual(error.details["detail"], "test")
        self.assertIsInstance(error.timestamp, datetime)
    
    def test_plugin_communication_error(self):
        """Test plugin communication error"""
        error = PluginCommunicationError("Connection failed", {"port": 8765})
        
        self.assertEqual(error.message, "Connection failed")
        self.assertEqual(error.category, ErrorCategory.PLUGIN_COMM)
        self.assertEqual(error.severity, ErrorSeverity.HIGH)
        self.assertEqual(error.details["port"], 8765)
    
    def test_fusion_api_error(self):
        """Test Fusion360 API error"""
        error = FusionAPIError("API call failed", {"method": "create_sketch"})
        
        self.assertEqual(error.message, "API call failed")
        self.assertEqual(error.category, ErrorCategory.FUSION_API)
        self.assertEqual(error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(error.details["method"], "create_sketch")
    
    def test_validation_error(self):
        """Test data validation error"""
        error = ValidationError("Invalid parameter", {"param": "width", "value": -1})
        
        self.assertEqual(error.message, "Invalid parameter")
        self.assertEqual(error.category, ErrorCategory.VALIDATION)
        self.assertEqual(error.severity, ErrorSeverity.LOW)
        self.assertEqual(error.details["param"], "width")
    
    def test_resource_error(self):
        """Test resource access error"""
        error = ResourceError("File not found", {"path": "/test/file.txt"})
        
        self.assertEqual(error.message, "File not found")
        self.assertEqual(error.category, ErrorCategory.RESOURCE)
        self.assertEqual(error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(error.details["path"], "/test/file.txt")

class TestErrorHandler(unittest.TestCase):
    """Test error handler"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = Mock(spec=logging.Logger)
        self.error_handler = ErrorHandler(self.logger)
    
    def test_initialization(self):
        """Test error handler initialization"""
        self.assertEqual(self.error_handler.logger, self.logger)
        self.assertEqual(len(self.error_handler.error_history), 0)
        self.assertEqual(self.error_handler.max_history_size, 100)
        self.assertIsInstance(self.error_handler.retry_strategies, dict)
    
    def test_retry_strategies_initialization(self):
        """Test retry strategy initialization"""
        strategies = self.error_handler.retry_strategies
        
        # Check plugin communication retry strategy
        plugin_strategy = strategies[ErrorCategory.PLUGIN_COMM]
        self.assertEqual(plugin_strategy["max_retries"], 3)
        self.assertEqual(plugin_strategy["backoff_factor"], 2.0)
        self.assertTrue(plugin_strategy["recoverable"])
        
        # Check validation error strategy (not recoverable)
        validation_strategy = strategies[ErrorCategory.VALIDATION]
        self.assertEqual(validation_strategy["max_retries"], 0)
        self.assertFalse(validation_strategy["recoverable"])
    
    def test_classify_fusion360_error(self):
        """Test Fusion360 error classification"""
        original_error = Fusion360Error("Test error", ErrorCategory.FUSION_API)
        classified = self.error_handler._classify_error(original_error)
        
        self.assertEqual(classified, original_error)
    
    def test_classify_plugin_communication_error(self):
        """Test plugin communication error classification"""
        error = Exception("Connection timeout")
        classified = self.error_handler._classify_error(error)
        
        self.assertIsInstance(classified, PluginCommunicationError)
        self.assertEqual(classified.category, ErrorCategory.PLUGIN_COMM)
        self.assertIn("Connection timeout", classified.message)
    
    def test_classify_fusion_api_error(self):
        """Test Fusion API error classification"""
        error = Exception("Fusion sketch creation failed")
        classified = self.error_handler._classify_error(error)
        
        self.assertIsInstance(classified, FusionAPIError)
        self.assertEqual(classified.category, ErrorCategory.FUSION_API)
        self.assertIn("sketch creation failed", classified.message)
    
    def test_classify_validation_error(self):
        """Test validation error classification"""
        error = Exception("Invalid parameter value")
        classified = self.error_handler._classify_error(error)
        
        self.assertIsInstance(classified, ValidationError)
        self.assertEqual(classified.category, ErrorCategory.VALIDATION)
        self.assertIn("Invalid parameter", classified.message)
    
    def test_classify_resource_error(self):
        """Test resource error classification"""
        error = Exception("File access denied")
        classified = self.error_handler._classify_error(error)
        
        self.assertIsInstance(classified, ResourceError)
        self.assertEqual(classified.category, ErrorCategory.RESOURCE)
        self.assertIn("File access", classified.message)
    
    def test_classify_unknown_error(self):
        """Test unknown error classification"""
        error = Exception("Some random error")
        classified = self.error_handler._classify_error(error)
        
        self.assertIsInstance(classified, Fusion360Error)
        self.assertEqual(classified.category, ErrorCategory.UNKNOWN)
        self.assertEqual(classified.severity, ErrorSeverity.MEDIUM)
    
    def test_handle_error(self):
        """Test error handling"""
        error = PluginCommunicationError("Connection failed")
        context = {"operation": "test_operation"}
        
        result = self.error_handler.handle_error(error, context)
        
        # Check return result
        self.assertIn("error_id", result)
        self.assertEqual(result["category"], "plugin_comm")
        self.assertEqual(result["severity"], "high")
        self.assertEqual(result["message"], "Connection failed")
        self.assertIn("user_message", result)
        self.assertIn("recovery_suggestions", result)
        self.assertTrue(result["recoverable"])
        
        # Check error history recording
        self.assertEqual(len(self.error_handler.error_history), 1)
        
        # Check log calls
        self.logger.log.assert_called_once()
    
    def test_error_history_limit(self):
        """Test error history record limit"""
        # Set smaller history record limit
        self.error_handler.max_history_size = 3
        
        # Add multiple errors
        for i in range(5):
            error = Fusion360Error(f"Error {i}")
            self.error_handler.handle_error(error)
        
        # Check history record size
        self.assertEqual(len(self.error_handler.error_history), 3)
        
        # Check that the latest errors are kept
        last_error = self.error_handler.error_history[-1]
        self.assertIn("Error 4", last_error["message"])
    
    def test_generate_user_report(self):
        """Test user-friendly error report generation"""
        error = PluginCommunicationError("Connection failed")
        report = self.error_handler._generate_user_report(error)
        
        self.assertIn("user_message", report)
        self.assertIn("technical_details", report)
        self.assertIn("Connection issue with Fusion360 plugin", report["user_message"])
        
        tech_details = report["technical_details"]
        self.assertEqual(tech_details["error_type"], "plugin_comm")
        self.assertEqual(tech_details["severity"], "high")
    
    def test_get_recovery_suggestions(self):
        """Test recovery suggestion retrieval"""
        error = PluginCommunicationError("Connection failed")
        suggestions = self.error_handler._get_recovery_suggestions(error)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        self.assertIn("Ensure Fusion360 is running", suggestions)
    
    def test_is_recoverable(self):
        """Test error recoverability determination"""
        # Recoverable error
        plugin_error = PluginCommunicationError("Connection failed")
        self.assertTrue(self.error_handler._is_recoverable(plugin_error))
        
        # Non-recoverable error
        validation_error = ValidationError("Invalid parameter")
        self.assertFalse(self.error_handler._is_recoverable(validation_error))
    
    @patch('time.sleep')
    def test_retry_with_backoff_success(self, mock_sleep):
        """Test retry mechanism success case"""
        # Create a function that succeeds on second call
        call_count = 0
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise PluginCommunicationError("Connection failed")
            return "success"
        
        # Set retry strategy
        self.error_handler.retry_strategies[ErrorCategory.PLUGIN_COMM] = {
            "max_retries": 2,
            "initial_delay": 0.1,
            "backoff_factor": 2.0,
            "recoverable": True
        }
        
        result = self.error_handler.retry_with_backoff(test_func)
        
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)
        mock_sleep.assert_called_once_with(0.1)
    
    @patch('time.sleep')
    def test_retry_with_backoff_failure(self, mock_sleep):
        """Test retry mechanism failure case"""
        def test_func():
            raise PluginCommunicationError("Connection failed")
        
        # Set retry strategy
        self.error_handler.retry_strategies[ErrorCategory.PLUGIN_COMM] = {
            "max_retries": 1,
            "initial_delay": 0.1,
            "backoff_factor": 2.0,
            "recoverable": True
        }
        
        with self.assertRaises(PluginCommunicationError):
            self.error_handler.retry_with_backoff(test_func)
        
        mock_sleep.assert_called_once_with(0.1)
    
    def test_get_error_summary(self):
        """Test error summary retrieval"""
        # Add some errors
        error1 = PluginCommunicationError("Error 1")
        error2 = FusionAPIError("Error 2")
        
        self.error_handler.handle_error(error1)
        self.error_handler.handle_error(error2)
        
        summary = self.error_handler.get_error_summary()
        
        self.assertEqual(summary["total_errors"], 2)
        self.assertEqual(summary["recent_errors"], 2)
        self.assertIn("plugin_comm", summary["categories"])
        self.assertIn("fusion_api", summary["categories"])
        self.assertIsNotNone(summary["last_error"])

class TestErrorHandlerDecorator(unittest.TestCase):
    """Test error handler decorator"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = Mock(spec=logging.Logger)
        self.error_handler = ErrorHandler(self.logger)
    
    def test_decorator_success(self):
        """Test decorator success case"""
        @error_handler_decorator(self.error_handler)
        def test_func(x, y):
            return x + y
        
        result = test_func(1, 2)
        self.assertEqual(result, 3)
    
    def test_decorator_error_handling(self):
        """Test decorator error handling"""
        @error_handler_decorator(self.error_handler)
        def test_func():
            raise ValidationError("Invalid input")
        
        result = test_func()
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["error"])
        self.assertEqual(result["category"], "validation")
        self.assertFalse(result["recoverable"])
    
    @patch('time.sleep')
    def test_decorator_retry_recoverable_error(self, mock_sleep):
        """Test decorator recoverable error retry"""
        call_count = 0
        
        @error_handler_decorator(self.error_handler)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise PluginCommunicationError("Connection failed")
            return "success"
        
        # Set retry strategy
        self.error_handler.retry_strategies[ErrorCategory.PLUGIN_COMM] = {
            "max_retries": 1,
            "initial_delay": 0.1,
            "backoff_factor": 2.0,
            "recoverable": True
        }
        
        result = test_func()
        
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)

class TestLoggingConfig(unittest.TestCase):
    """Test logging configuration"""
    
    def setUp(self):
        """Set up test environment"""
        self.log_config = LoggingConfig("test_logs")
    
    def test_initialization(self):
        """Test logging configuration initialization"""
        self.assertTrue(self.log_config.base_dir.exists())
        self.assertEqual(self.log_config.max_file_size, 10 * 1024 * 1024)
        self.assertEqual(self.log_config.backup_count, 5)
    
    def test_setup_logging(self):
        """Test logging system setup"""
        logger = self.log_config.setup_logging(
            enable_console=True,
            enable_file=False,  # Avoid creating files
            console_level="DEBUG"
        )
        
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "fusion360-mcp")
        self.assertGreater(len(logger.handlers), 0)
    
    def test_create_child_logger(self):
        """Test child logger creation"""
        child_logger = self.log_config.create_child_logger("test")
        
        self.assertEqual(child_logger.name, "fusion360-mcp.test")
    
    def test_log_performance(self):
        """Test performance log recording"""
        logger = Mock(spec=logging.Logger)
        
        self.log_config.log_performance(
            logger, "test_operation", 150.5, {"param": "value"}
        )
        
        logger.info.assert_called_once()
        call_args = logger.info.call_args
        self.assertIn("Performance", call_args[0][0])
        self.assertIn("extra", call_args[1])
    
    def test_log_api_call(self):
        """Test API call log recording"""
        logger = Mock(spec=logging.Logger)
        
        self.log_config.log_api_call(
            logger, "/api/test", "POST", 250.0, "success",
            {"input": "data"}, {"output": "result"}
        )
        
        logger.info.assert_called_once()
        call_args = logger.info.call_args
        self.assertIn("API Call", call_args[0][0])
        self.assertIn("extra", call_args[1])

class TestPerformanceMonitor(unittest.TestCase):
    """Test performance monitor"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = Mock(spec=logging.Logger)
        self.monitor = PerformanceMonitor(self.logger)
    
    def test_timer_operations(self):
        """Test timer operations"""
        operation = "test_operation"
        
        # Start timer
        self.monitor.start_timer(operation)
        self.assertIn(operation, self.monitor._start_times)
        
        # Simulate some processing time
        time.sleep(0.01)
        
        # End timer
        duration = self.monitor.end_timer(operation)
        
        self.assertGreater(duration, 0)
        self.assertNotIn(operation, self.monitor._start_times)
    
    def test_timer_not_started_warning(self):
        """Test warning for timer not started"""
        duration = self.monitor.end_timer("non_existent_operation")
        
        self.assertEqual(duration, 0.0)
        self.logger.warning.assert_called_once()
    
    @patch('time.sleep')
    def test_decorator_usage(self, mock_sleep):
        """Test usage as decorator"""
        @self.monitor("test_operation")
        def test_func():
            return "result"
        
        result = test_func()
        
        self.assertEqual(result, "result")
        # Verify performance log is recorded (by checking if related methods were called)

if __name__ == '__main__':
    unittest.main()
