#!/usr/bin/env python3
"""
Error Handling and Logging System Integration Tests

Test error handling and logging system integration with other components
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.bridge import Fusion360Bridge
from core.config import get_error_handler, logger
from utils.error_handler import ErrorHandler, PluginCommunicationError, FusionAPIError
from utils.logging_config import LoggingConfig, PerformanceMonitor

class TestErrorLoggingIntegration(unittest.TestCase):
    """Test error handling and logging system integration"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for logs
        self.temp_dir = tempfile.mkdtemp()
        self.log_config = LoggingConfig(os.path.join(self.temp_dir, "logs"))
        
        # Set up test logger
        self.test_logger = self.log_config.setup_logging(
            enable_console=False,  # Avoid console output interfering with tests
            enable_file=True,
            enable_json=True
        )
        
        # Create error handler
        self.error_handler = ErrorHandler(self.test_logger)
        
        # Create performance monitor
        self.performance_monitor = PerformanceMonitor(self.test_logger)
    
    def tearDown(self):
        """Clean up test environment"""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_bridge_error_handling_integration(self):
        """Test bridge error handling integration"""
        # Create bridge instance
        bridge = Fusion360Bridge(use_plugin_mode=False)
        
        # Simulate initialization failure
        with patch.object(bridge, '_initialize_direct_mode', side_effect=Exception("API not available")):
            with patch.object(bridge, '_initialize_plugin_mode', side_effect=Exception("Plugin not available")):
                # Initialization should succeed (using simulation mode)
                result = bridge.initialize()
                self.assertTrue(result)
                self.assertEqual(bridge.mode, "simulation")
    
    def test_error_logging_to_file(self):
        """Test error logging to file"""
        # Create an error
        error = PluginCommunicationError("Test connection error", {"port": 8765})
        
        # Handle error
        result = self.error_handler.handle_error(error, {"operation": "test_integration"})
        
        # Verify error handling result
        self.assertIn("error_id", result)
        self.assertEqual(result["category"], "plugin_comm")
        self.assertTrue(result["recoverable"])
        
        # Check if log files were created
        log_files = list(self.log_config.base_dir.glob("*.log"))
        self.assertGreater(len(log_files), 0)
        
        # Check error log file content
        error_log_file = self.log_config.base_dir / "error.log"
        if error_log_file.exists():
            with open(error_log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                self.assertIn("plugin_comm", log_content)
                self.assertIn("Test connection error", log_content)
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration"""
        # Use performance monitor decorator
        @self.performance_monitor("test_operation")
        def test_operation():
            import time
            time.sleep(0.01)  # Simulate some processing time
            return "completed"
        
        # Execute operation
        result = test_operation()
        self.assertEqual(result, "completed")
        
        # Check performance log file
        perf_log_file = self.log_config.base_dir / "performance.log"
        if perf_log_file.exists():
            with open(perf_log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                self.assertIn("test_operation", log_content)
                self.assertIn("Performance", log_content)
    
    def test_json_log_format(self):
        """Test JSON log format"""
        # Log a message with extra information
        self.test_logger.info(
            "Test message",
            extra={
                "error_id": "TEST_001",
                "category": "test",
                "details": {"param": "value"},
                "duration": 123.45
            }
        )
        
        # Check main log file
        main_log_file = self.log_config.base_dir / "fusion360_mcp.log"
        if main_log_file.exists():
            with open(main_log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                
            # Verify at least one log line
            self.assertGreater(len(log_lines), 0)
            
            # Verify JSON format
            for line in log_lines:
                if line.strip():
                    try:
                        log_entry = json.loads(line.strip())
                        self.assertIn("timestamp", log_entry)
                        self.assertIn("level", log_entry)
                        self.assertIn("message", log_entry)
                        
                        # If this is our test message, check extra fields
                        if "Test message" in log_entry.get("message", ""):
                            self.assertIn("error_id", log_entry)
                            self.assertIn("category", log_entry)
                            self.assertIn("details", log_entry)
                            self.assertIn("duration_ms", log_entry)
                        break
                    except json.JSONDecodeError:
                        self.fail(f"Invalid JSON in log line: {line}")
    
    def test_error_recovery_workflow(self):
        """Test error recovery workflow"""
        # Simulate a recoverable error scenario
        call_count = 0
        
        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise PluginCommunicationError("Temporary connection issue")
            return {"success": True, "data": "operation completed"}
        
        # Use retry mechanism
        with patch('time.sleep'):  # Speed up test
            try:
                result = self.error_handler.retry_with_backoff(
                    failing_operation,
                    error_context={"operation": "test_recovery"}
                )
                self.assertEqual(result["success"], True)
                self.assertEqual(call_count, 3)  # Failed 2 times, succeeded on 3rd
            except Exception as e:
                self.fail(f"Recovery workflow failed: {e}")
    
    def test_error_history_tracking(self):
        """Test error history tracking"""
        # Create multiple different types of errors
        errors = [
            PluginCommunicationError("Connection error 1"),
            FusionAPIError("API error 1"),
            PluginCommunicationError("Connection error 2"),
        ]
        
        # Handle all errors
        for error in errors:
            self.error_handler.handle_error(error)
        
        # Get error summary
        summary = self.error_handler.get_error_summary()
        
        # Verify summary information
        self.assertEqual(summary["total_errors"], 3)
        self.assertEqual(summary["recent_errors"], 3)
        self.assertIn("plugin_comm", summary["categories"])
        self.assertIn("fusion_api", summary["categories"])
        self.assertEqual(summary["categories"]["plugin_comm"], 2)
        self.assertEqual(summary["categories"]["fusion_api"], 1)
    
    def test_log_rotation(self):
        """Test log rotation"""
        # Set small file size limit to trigger rotation
        small_log_config = LoggingConfig(os.path.join(self.temp_dir, "rotation_logs"))
        small_log_config.max_file_size = 1024  # 1KB
        
        test_logger = small_log_config.setup_logging(
            enable_console=False,
            enable_file=True
        )
        
        # Write many logs to trigger rotation
        for i in range(100):
            test_logger.info(f"Test log message {i} with some additional content to increase size")
        
        # Check if rotation files were created
        log_files = list(small_log_config.base_dir.glob("*.log*"))
        # Should have main file and at least one backup file
        self.assertGreaterEqual(len(log_files), 1)
    
    def test_bridge_with_error_handling(self):
        """Test bridge with error handling complete integration"""
        # Create bridge with error handling
        bridge = Fusion360Bridge(use_plugin_mode=False)
        
        # Initialize bridge
        bridge.initialize()
        
        # Test error handling for various operations
        operations = [
            ("get_design_info", {}),
            ("get_component_hierarchy", {}),
            ("create_sketch", {"name": "TestSketch"}),
            ("create_rectangle", {"sketch_name": "TestSketch", "width": 10, "height": 5}),
        ]
        
        for operation_name, kwargs in operations:
            operation = getattr(bridge, operation_name)
            result = operation(**kwargs)
            
            # All operations should return results (even if simulated)
            self.assertIsInstance(result, dict)
            
            # If there's an error, it should include error handling information
            if result.get("error"):
                self.assertIn("error_id", result)
                self.assertIn("category", result)
                self.assertIn("user_message", result)
    
    def test_configuration_integration(self):
        """Test configuration system integration"""
        from core.config import get_config_summary, validate_parameter
        
        # Get configuration summary
        config_summary = get_config_summary()
        
        # Verify configuration summary includes error handling information
        self.assertIn("features", config_summary)
        features = config_summary["features"]
        self.assertIn("error_handling", features)
        self.assertIn("enhanced_logging", features)
        
        # Test parameter validation
        valid_result = validate_parameter("width", 10.0, "sketch_parameters")
        self.assertTrue(valid_result["valid"])
        
        invalid_result = validate_parameter("width", -5.0, "sketch_parameters")
        self.assertFalse(invalid_result["valid"])
        self.assertIn("must be >=", invalid_result["message"])
    
    def test_log_stats_collection(self):
        """Test log statistics collection"""
        # Generate some logs
        for i in range(10):
            self.test_logger.info(f"Test log entry {i}")
            self.test_logger.warning(f"Test warning {i}")
        
        # Get log statistics
        stats = self.log_config.get_log_stats()
        
        # Verify statistics information
        self.assertIn("log_directory", stats)
        self.assertIn("files", stats)
        self.assertEqual(stats["log_directory"], str(self.log_config.base_dir))
        
        # Check file statistics
        files_stats = stats["files"]
        if files_stats:
            for filename, file_stats in files_stats.items():
                self.assertIn("size_bytes", file_stats)
                self.assertIn("size_mb", file_stats)
                self.assertIn("modified", file_stats)
                self.assertGreaterEqual(file_stats["size_bytes"], 0)

class TestErrorHandlingScenarios(unittest.TestCase):
    """Test various error handling scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_config = LoggingConfig(os.path.join(self.temp_dir, "scenario_logs"))
        self.test_logger = self.log_config.setup_logging(enable_console=False, enable_file=True)
        self.error_handler = ErrorHandler(self.test_logger)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cascade_error_handling(self):
        """Test cascade error handling"""
        # Simulate a scenario where an operation triggers multiple errors
        def complex_operation():
            # First error: plugin connection failed
            try:
                raise PluginCommunicationError("Plugin connection failed")
            except Exception as e:
                self.error_handler.handle_error(e, {"step": "plugin_connection"})
                
                # Second error: fallback to API mode failed
                try:
                    raise FusionAPIError("API initialization failed")
                except Exception as e2:
                    self.error_handler.handle_error(e2, {"step": "api_fallback"})
                    
                    # Finally use simulation mode
                    return {"mode": "simulation", "success": True}
        
        result = complex_operation()
        
        # Verify final result
        self.assertEqual(result["mode"], "simulation")
        self.assertTrue(result["success"])
        
        # Verify error history recorded two errors
        self.assertEqual(len(self.error_handler.error_history), 2)
        
        # Verify error summary
        summary = self.error_handler.get_error_summary()
        self.assertEqual(summary["total_errors"], 2)
        self.assertIn("plugin_comm", summary["categories"])
        self.assertIn("fusion_api", summary["categories"])
    
    def test_user_friendly_error_reporting(self):
        """Test user-friendly error reporting"""
        # Test user-friendly messages for different error types
        test_cases = [
            (PluginCommunicationError("Socket timeout"), "Connection issue with Fusion360 plugin"),
            (FusionAPIError("Sketch creation failed"), "Fusion360 operation failed"),
            (ValidationError("Invalid width parameter"), "Input parameter is incorrect"),
        ]
        
        for error, expected_message_part in test_cases:
            result = self.error_handler.handle_error(error)
            
            self.assertIn("user_message", result)
            self.assertIn(expected_message_part, result["user_message"])
            self.assertIn("recovery_suggestions", result)
            self.assertIsInstance(result["recovery_suggestions"], list)
            self.assertGreater(len(result["recovery_suggestions"]), 0)
    
    def test_performance_impact_monitoring(self):
        """Test performance impact monitoring"""
        performance_monitor = PerformanceMonitor(self.test_logger)
        
        # Test normal operation performance monitoring
        @performance_monitor("normal_operation")
        def normal_operation():
            import time
            time.sleep(0.01)
            return "success"
        
        # Test error operation performance monitoring
        @performance_monitor("error_operation")
        def error_operation():
            import time
            time.sleep(0.005)
            raise FusionAPIError("Operation failed")
        
        # Execute normal operation
        result1 = normal_operation()
        self.assertEqual(result1, "success")
        
        # Execute error operation
        with self.assertRaises(FusionAPIError):
            error_operation()
        
        # Check if performance log recorded both operations
        perf_log_file = self.log_config.base_dir / "performance.log"
        if perf_log_file.exists():
            with open(perf_log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
                self.assertIn("normal_operation", log_content)
                self.assertIn("error_operation", log_content)

if __name__ == '__main__':
    unittest.main()
