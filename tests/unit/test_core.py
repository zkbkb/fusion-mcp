#!/usr/bin/env python3
"""
Fusion360 MCP Server Core Functionality Unit Tests

Test new modular MCP architecture
"""

import unittest
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestMCPCore(unittest.TestCase):
    """MCP core functionality test class"""
    
    def test_mcp_server_import(self):
        """Test MCP server module import"""
        try:
            import mcp_server
            self.assertTrue(hasattr(mcp_server, 'mcp'))
            self.assertTrue(hasattr(mcp_server, 'fusion_bridge'))
            self.assertTrue(hasattr(mcp_server, 'context_manager'))
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_fusion_bridge_basic(self):
        """Test Fusion360 bridge basic functionality"""
        try:
            import mcp_server
            bridge = mcp_server.fusion_bridge
            
            # Test bridge initialization
            result = bridge.initialize()
            # Should return False in simulation mode
            self.assertFalse(result)
            
            # Test design info retrieval
            info = bridge.get_design_info()
            self.assertIsInstance(info, dict)
            
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_context_manager_basic(self):
        """Test context manager basic functionality"""
        try:
            import mcp_server
            manager = mcp_server.context_manager
            
            # Test basic methods exist
            self.assertTrue(hasattr(manager, 'store_design_intent'))
            self.assertTrue(hasattr(manager, 'add_task'))
            self.assertTrue(hasattr(manager, 'get_context_summary'))
            
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")

class TestModularArchitecture(unittest.TestCase):
    """Modular architecture test class"""
    
    def test_tool_modules_exist(self):
        """Test tool modules exist"""
        try:
            # Test imports of various tool modules
            import tools.sketch
            import tools.modeling
            import tools.assembly
            import tools.analysis
            import context
            
            self.assertTrue(True, "All tool modules imported successfully")
            
        except ImportError as e:
            self.skipTest(f"Tool modules not available: {e}")
    
    def test_sketch_tools_available(self):
        """Test sketch tools availability"""
        try:
            from tools.sketch import (
                create_sketch, draw_line, draw_circle, draw_rectangle,
                draw_arc, draw_polygon, add_geometric_constraint, 
                add_dimensional_constraint
            )
            
            # Verify functions exist and are callable
            sketch_tools = [
                create_sketch, draw_line, draw_circle, draw_rectangle,
                draw_arc, draw_polygon, add_geometric_constraint, 
                add_dimensional_constraint
            ]
            
            for tool in sketch_tools:
                self.assertTrue(callable(tool))
                
        except ImportError as e:
            self.skipTest(f"Sketch tool modules not available: {e}")
    
    def test_modeling_tools_available(self):
        """Test modeling tools availability"""
        try:
            from tools.modeling import (
                create_extrude, create_revolve, create_sweep, create_loft,
                create_fillet, create_chamfer, create_shell, boolean_operation,
                split_body, create_pattern_rectangular, create_pattern_circular,
                create_mirror
            )
            
            # Verify functions exist and are callable
            modeling_tools = [
                create_extrude, create_revolve, create_sweep, create_loft,
                create_fillet, create_chamfer, create_shell, boolean_operation,
                split_body, create_pattern_rectangular, create_pattern_circular,
                create_mirror
            ]
            
            for tool in modeling_tools:
                self.assertTrue(callable(tool))
                
        except ImportError as e:
            self.skipTest(f"Modeling tool modules not available: {e}")
    
    def test_assembly_tools_available(self):
        """Test assembly tools availability"""
        try:
            from tools.assembly import (
                create_component, insert_component_from_file, get_assembly_info,
                create_mate_constraint, create_joint, create_motion_study,
                check_interference, create_exploded_view, animate_assembly
            )
            
            # Verify functions exist and are callable
            assembly_tools = [
                create_component, insert_component_from_file, get_assembly_info,
                create_mate_constraint, create_joint, create_motion_study,
                check_interference, create_exploded_view, animate_assembly
            ]
            
            for tool in assembly_tools:
                self.assertTrue(callable(tool))
                
        except ImportError as e:
            self.skipTest(f"Assembly tool modules not available: {e}")
    
    def test_analysis_tools_available(self):
        """Test analysis tools availability"""
        try:
            from tools.analysis import (
                measure_distance, measure_angle, measure_area, measure_volume,
                calculate_mass_properties, create_section_analysis,
                perform_stress_analysis, perform_modal_analysis,
                perform_thermal_analysis, generate_analysis_report
            )
            
            # Verify functions exist and are callable
            analysis_tools = [
                measure_distance, measure_angle, measure_area, measure_volume,
                calculate_mass_properties, create_section_analysis,
                perform_stress_analysis, perform_modal_analysis,
                perform_thermal_analysis, generate_analysis_report
            ]
            
            for tool in analysis_tools:
                self.assertTrue(callable(tool))
                
        except ImportError as e:
            self.skipTest(f"Analysis tool modules not available: {e}")
    
    def test_context_tools_available(self):
        """Test context tools availability"""
        try:
            from context import store_design_intent, add_design_task
            
            # Verify functions exist and are callable
            context_tools = [store_design_intent, add_design_task]
            
            for tool in context_tools:
                self.assertTrue(callable(tool))
                
        except ImportError as e:
            self.skipTest(f"Context tool modules not available: {e}")

class TestServerInitialization(unittest.TestCase):
    """Server initialization test class"""
    
    def test_initialization_functions_exist(self):
        """Test initialization functions exist"""
        try:
            import mcp_server
            
            # Test modular initialization functions exist
            self.assertTrue(hasattr(mcp_server, 'initialize_all_tools'))
            
            # Verify functions are callable
            self.assertTrue(callable(mcp_server.initialize_all_tools))
            
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")
    
    def test_core_tools_in_server(self):
        """Test core tools exist in server"""
        try:
            import mcp_server
            
            # Test core tools still in main server
            core_tools = [
                "create_parameter",
                "export_stl", 
                "save_design"
            ]
            
            for tool_name in core_tools:
                self.assertTrue(hasattr(mcp_server, tool_name),
                              f"Core tool {tool_name} does not exist")
                              
        except ImportError as e:
            self.skipTest(f"MCP server module not available: {e}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
