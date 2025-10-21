"""
Sketch Tools Unit Tests

Test sketch tool module functionality and modular structure
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src path to sys.path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

class TestSketchToolsModular(unittest.TestCase):
    """Test sketch tools modular structure"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock Fusion 360 API
        self.mock_app = Mock()
        self.mock_design = Mock()
        self.mock_root_comp = Mock()
        
        # Mock context manager
        self.mock_context_manager = Mock()
        
        # Mock MCP instance
        self.mock_mcp = Mock()
        
        # Mock fusion_bridge
        self.mock_fusion_bridge = Mock()
        self.mock_fusion_bridge.design = self.mock_design
        self.mock_fusion_bridge.app = self.mock_app
        
        self.mock_design.rootComponent = self.mock_root_comp
    
    def test_sketch_module_imports(self):
        """Test sketch module imports"""
        try:
            from tools.sketch import basic, constraints, advanced
            from tools.sketch import initialize_sketch_tools
            self.assertTrue(True, "Module import successful")
        except ImportError as e:
            self.fail(f"Module import failed: {e}")
    
    def test_sketch_module_initialization(self):
        """Test sketch module initialization"""
        from tools.sketch import initialize_sketch_tools
        from tools.sketch import basic, constraints, advanced
        
        # Initialize module
        initialize_sketch_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Verify global variable settings
        self.assertEqual(basic.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(basic.context_manager, self.mock_context_manager)
        self.assertEqual(basic.mcp, self.mock_mcp)
        
        self.assertEqual(constraints.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(constraints.context_manager, self.mock_context_manager)
        self.assertEqual(constraints.mcp, self.mock_mcp)
    
    def test_basic_tools_available(self):
        """Test basic tool function availability"""
        from tools.sketch.basic import (
            create_sketch, draw_line, draw_circle, 
            draw_rectangle, draw_arc, draw_polygon
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(create_sketch))
        self.assertTrue(callable(draw_line))
        self.assertTrue(callable(draw_circle))
        self.assertTrue(callable(draw_rectangle))
        self.assertTrue(callable(draw_arc))
        self.assertTrue(callable(draw_polygon))
    
    def test_constraint_tools_available(self):
        """Test constraint tool function availability"""
        from tools.sketch.constraints import (
            add_geometric_constraint, add_dimensional_constraint
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(add_geometric_constraint))
        self.assertTrue(callable(add_dimensional_constraint))
    
    @patch('tools.sketch.basic.adsk')
    async def test_create_sketch_functionality(self, mock_adsk):
        """Test create_sketch functionality"""
        from tools.sketch import initialize_sketch_tools
        from tools.sketch.basic import create_sketch
        
        # Set up mock objects
        mock_sketch = Mock()
        mock_sketch.entityToken = "sketch_123"
        mock_sketch.name = "TestSketch"
        
        mock_plane = Mock()
        self.mock_root_comp.xYConstructionPlane = mock_plane
        self.mock_root_comp.sketches.add.return_value = mock_sketch
        
        # Initialize module
        initialize_sketch_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test create_sketch
        result = await create_sketch(plane="xy", name="TestSketch")
        
        # Verify result
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("sketch_id"), "sketch_123")
        self.assertEqual(result.get("name"), "TestSketch")
        self.assertEqual(result.get("plane"), "xy")
    
    @patch('tools.sketch.basic.adsk')
    async def test_draw_circle_functionality(self, mock_adsk):
        """Test draw_circle functionality"""
        from tools.sketch import initialize_sketch_tools
        from tools.sketch.basic import draw_circle
        
        # Set up mock objects
        mock_sketch = Mock()
        mock_sketch.name = "TestSketch"
        
        mock_circle = Mock()
        mock_circle.entityToken = "circle_123"
        
        mock_circles = Mock()
        mock_circles.addByCenterRadius.return_value = mock_circle
        mock_sketch.sketchCurves.sketchCircles = mock_circles
        
        self.mock_root_comp.sketches.add.return_value = mock_sketch
        
        # Mock Point3D
        mock_point = Mock()
        mock_adsk.core.Point3D.create.return_value = mock_point
        
        # Initialize module
        initialize_sketch_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test draw_circle
        result = await draw_circle(radius=10.0, center_x=0.0, center_y=0.0)
        
        # Verify result
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("circle_id"), "circle_123")
        self.assertEqual(result.get("radius"), 10.0)
        self.assertEqual(result.get("center"), [0.0, 0.0])
    
    async def test_error_handling_no_design(self):
        """Test error handling when no design is active"""
        from tools.sketch import initialize_sketch_tools
        from tools.sketch.basic import create_sketch
        
        # Set fusion_bridge with no design
        self.mock_fusion_bridge.design = None
        
        # Initialize module
        initialize_sketch_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test create_sketch
        result = await create_sketch()
        
        # Verify error handling
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No active design")


class TestSketchToolsIntegration(unittest.TestCase):
    """Test sketch tools integration"""
    
    def test_all_tools_import_from_main_module(self):
        """Test all tools can be imported from main module"""
        try:
            from tools.sketch import (
                create_sketch, draw_line, draw_circle, draw_rectangle,
                draw_arc, draw_polygon, add_geometric_constraint,
                add_dimensional_constraint, initialize_sketch_tools
            )
            self.assertTrue(True, "All tools imported successfully")
        except ImportError as e:
            self.fail(f"Tool import failed: {e}")
    
    def test_module_structure(self):
        """Test module structure completeness"""
        import tools.sketch
        
        # Verify __all__ attribute exists
        self.assertTrue(hasattr(tools.sketch, '__all__'))
        
        # Verify key functions in __all__
        expected_functions = [
            'initialize_sketch_tools', 'create_sketch', 'draw_line',
            'draw_circle', 'draw_rectangle', 'draw_arc', 'draw_polygon',
            'add_geometric_constraint', 'add_dimensional_constraint'
        ]
        
        for func_name in expected_functions:
            self.assertIn(func_name, tools.sketch.__all__, 
                         f"{func_name} not in __all__")
    
    def test_advanced_module_structure(self):
        """Test advanced module structure (currently empty, but module should exist)"""
        try:
            from tools.sketch import advanced
            # Advanced module should exist but not contain tool functions
            self.assertTrue(hasattr(advanced, 'register_tools'))
        except ImportError as e:
            self.fail(f"Advanced module import failed: {e}")


if __name__ == '__main__':
    unittest.main()
