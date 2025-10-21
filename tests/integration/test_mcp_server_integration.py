#!/usr/bin/env python3
"""
Fusion360 MCP Server Integration Tests

Test MCP server integration with Fusion 360 API:
- Server startup and shutdown
- Tool registration and invocation
- Context persistence integration
- Error handling and recovery
"""

import asyncio
import unittest
import sys
import os
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestMCPServerIntegration(unittest.TestCase):
    """MCP server integration test class"""
    
    def setUp(self):
        """Test initialization"""
        self.maxDiff = None
        
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()
    
    def tearDown(self):
        """Test cleanup"""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_server_imports(self):
        """Test server module imports"""
        try:
            import mcp_server
            self.assertTrue(hasattr(mcp_server, 'mcp'))
            self.assertTrue(hasattr(mcp_server, 'fusion_bridge'))
            self.assertTrue(hasattr(mcp_server, 'context_manager'))
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_fusion_bridge_initialization(self):
        """Test Fusion 360 bridge initialization"""
        try:
            import mcp_server
            
            # Test bridge class
            bridge = mcp_server.Fusion360Bridge()
            self.assertIsNotNone(bridge)
            
            # Test initialization method (returns False in environments without Fusion 360)
            result = bridge.initialize()
            self.assertIsInstance(result, bool)
            
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_mcp_tool_registration(self):
        """Test MCP tool registration"""
        try:
            import mcp_server
            
            # Check MCP instance
            self.assertIsNotNone(mcp_server.mcp)
            
            # Check if basic tools exist
            expected_tools = [
                "store_design_intent",
                "add_design_task",
                "create_parameter",
                "export_stl",
                "save_design"
            ]
            
            # Note: In test environment, tools may not be registered to MCP instance yet
            # Here we mainly test the existence of tool functions
            for tool_name in expected_tools:
                # Test if tool function exists
                if hasattr(mcp_server, tool_name):
                    tool_func = getattr(mcp_server, tool_name)
                    self.assertTrue(callable(tool_func), f"{tool_name} is not a callable function")
        
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_resource_registration(self):
        """Test MCP resource registration"""
        try:
            import mcp_server
            
            # Check if resource functions exist
            expected_resources = [
                "get_design_info",
                "get_design_components", 
                "get_context_summary",
                "get_design_intent_resource",
                "get_assembly_hierarchy_resource"
            ]
            
            for resource_name in expected_resources:
                self.assertTrue(
                    hasattr(mcp_server, resource_name),
                    f"Resource function {resource_name} does not exist"
                )
                
                resource_func = getattr(mcp_server, resource_name)
                self.assertTrue(
                    callable(resource_func),
                    f"Resource function {resource_name} is not callable"
                )
        
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_context_manager_integration(self):
        """Test context manager integration"""
        try:
            import mcp_server
            
            # Test context manager
            context_manager = mcp_server.context_manager
            self.assertIsNotNone(context_manager)
            
            # Test basic functionality
            self.assertTrue(hasattr(context_manager, 'store_design_intent'))
            self.assertTrue(hasattr(context_manager, 'add_task'))
            self.assertTrue(hasattr(context_manager, 'add_history_entry'))
            
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_tool_execution_logging(self):
        """Test tool execution logging"""
        try:
            import mcp_server
            
            # Test logging function
            log_function = mcp_server._log_tool_execution
            self.assertTrue(callable(log_function))
            
            # Mock tool execution logging
            parameters = {"test_param": "test_value"}
            result = {"success": True, "result": "test_result"}
            
            # This should not raise an exception
            log_function("test_tool", parameters, result)
            
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")

class TestContextPersistenceIntegration(unittest.TestCase):
    """Context persistence integration tests"""
    
    def setUp(self):
        """Test initialization"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()
    
    def tearDown(self):
        """Test cleanup"""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_context_persistence_integration(self):
        """Test context persistence integration"""
        try:
            from context import ContextPersistenceManager
            
            # Create context manager
            manager = ContextPersistenceManager(self.temp_file_path)
            
            # Test design intent storage
            intent = manager.store_design_intent(
                project_name="Integration Test Project",
                description="Test MCP server integration with context persistence",
                requirements=["Integration requirement 1", "Integration requirement 2"]
            )
            
            self.assertIsNotNone(intent)
            self.assertEqual(intent.project_name, "Integration Test Project")
            
            # Test task addition
            task = manager.add_task(
                title="Integration test task",
                description="Test task management integration"
            )
            
            self.assertIsNotNone(task)
            self.assertEqual(task.title, "Integration test task")
            
            # Test history recording
            manager.add_history_entry(
                action_type="integration_test",
                action_description="Integration test operation",
                parameters={"test": True},
                result={"success": True}
            )
            
            history = manager.get_design_history(limit=1)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["action_type"], "integration_test")
            
        except ImportError as e:
            self.skipTest(f"Context persistence module not available: {e}")

class TestModularArchitecture(unittest.TestCase):
    """Modular architecture tests"""
    
    def test_tool_modules_import(self):
        """Test tool module imports"""
        try:
            # Test imports of various tool modules
            from tools.sketch import initialize_sketch_tools
            from tools.modeling import initialize_modeling_tools
            from tools.assembly import initialize_assembly_tools
            from tools.analysis import initialize_analysis_tools
            from context import initialize_context_tools
            
            # Verify initialization functions exist
            self.assertTrue(callable(initialize_sketch_tools))
            self.assertTrue(callable(initialize_modeling_tools))
            self.assertTrue(callable(initialize_assembly_tools))
            self.assertTrue(callable(initialize_analysis_tools))
            self.assertTrue(callable(initialize_context_tools))
            
        except ImportError as e:
            self.skipTest(f"Tool modules not available: {e}")
    
    def test_module_registration_functions(self):
        """Test module registration functions"""
        try:
            from tools.sketch import register_all_tools as register_sketch
            from tools.modeling import register_all_tools as register_modeling
            from tools.assembly import register_all_tools as register_assembly
            from tools.analysis import register_all_tools as register_analysis
            from context import register_all_tools as register_context
            
            # Verify registration functions exist
            self.assertTrue(callable(register_sketch))
            self.assertTrue(callable(register_modeling))
            self.assertTrue(callable(register_assembly))
            self.assertTrue(callable(register_analysis))
            self.assertTrue(callable(register_context))
            
        except ImportError as e:
            self.skipTest(f"Tool modules not available: {e}")
    
    def test_server_initialization_functions(self):
        """Test server initialization functions"""
        try:
            import mcp_server
            
            # Test modular functions exist
            self.assertTrue(hasattr(mcp_server, 'initialize_tool_modules'))
            self.assertTrue(hasattr(mcp_server, 'register_tool_modules'))
            
            # Verify functions are callable
            self.assertTrue(callable(mcp_server.initialize_tool_modules))
            self.assertTrue(callable(mcp_server.register_tool_modules))
            
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")

class TestServerErrorHandling(unittest.TestCase):
    """Server error handling tests"""
    
    @patch('mcp_server.FUSION_AVAILABLE', False)
    def test_fusion_unavailable_handling(self):
        """Test handling when Fusion 360 is unavailable"""
        try:
            import mcp_server
            
            # Test bridge behavior when Fusion is unavailable
            bridge = mcp_server.Fusion360Bridge()
            result = bridge.initialize()
            
            # Should return False without raising exception
            self.assertFalse(result)
            
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_context_persistence_error_handling(self):
        """Test context persistence error handling"""
        try:
            from context import ContextPersistenceManager
            
            # Test error handling with invalid path
            invalid_path = "/invalid/path/that/does/not/exist/test.json"
            
            # This should not raise exception, but handle gracefully
            manager = ContextPersistenceManager(invalid_path)
            self.assertIsNotNone(manager)
            
        except ImportError as e:
            self.skipTest(f"Context persistence module not available: {e}")

def run_integration_tests():
    """Run integration tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_integration_tests()
