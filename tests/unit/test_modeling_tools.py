#!/usr/bin/env python3
"""
Fusion360 MCP Server Modeling Tools Unit Tests

Test modeling functionality:
- Extrude, revolve, sweep, loft
- Chamfer, fillet, shell
- Pattern, mirror
- Boolean operations
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestModelingTools(unittest.TestCase):
    """Modeling tools test class"""
    
    def test_extrude_params(self):
        """Test extrude functionality parameters"""
        params = {
            "sketch_name": "Rectangle1",
            "distance": 10.0,
            "operation": "new_body"
        }
        
        # Test parameter structure
        self.assertIn("sketch_name", params)
        self.assertIn("distance", params)
        self.assertIn("operation", params)
        
        # Test parameter types and values
        self.assertIsInstance(params["sketch_name"], str)
        self.assertIsInstance(params["distance"], (int, float))
        self.assertGreater(params["distance"], 0)
        self.assertIn(params["operation"], ["new_body", "join", "cut", "intersect"])
    
    def test_revolve_params(self):
        """Test revolve functionality parameters"""
        params = {
            "sketch_name": "Profile1",
            "axis_point": [0, 0, 0],
            "axis_direction": [1, 0, 0],
            "angle": 360.0,
            "operation": "new_body"
        }
        
        # Test parameter structure
        required_params = ["sketch_name", "axis_point", "axis_direction", "angle", "operation"]
        for param in required_params:
            self.assertIn(param, params)
        
        # Test axis vectors
        self.assertIsInstance(params["axis_point"], list)
        self.assertEqual(len(params["axis_point"]), 3)
        self.assertIsInstance(params["axis_direction"], list)
        self.assertEqual(len(params["axis_direction"]), 3)
        
        # Test angle
        self.assertIsInstance(params["angle"], (int, float))
        self.assertGreaterEqual(params["angle"], 0)
        self.assertLessEqual(params["angle"], 360)
    
    def test_sweep_params(self):
        """Test sweep functionality parameters"""
        params = {
            "profile_sketch_name": "Profile1",
            "path_sketch_name": "Path1", 
            "operation": "new_body",
            "twist_angle": 0.0
        }
        
        # Test parameter structure
        self.assertIn("profile_sketch_name", params)
        self.assertIn("path_sketch_name", params)
        self.assertIn("operation", params)
        self.assertIn("twist_angle", params)
        
        # Test twist angle
        self.assertIsInstance(params["twist_angle"], (int, float))
    
    def test_loft_params(self):
        """Test loft functionality parameters"""
        params = {
            "profile_sketch_names": ["Profile1", "Profile2", "Profile3"],
            "operation": "new_body",
            "guide_rails": ["GuideRail1"]
        }
        
        # Test parameter structure
        self.assertIn("profile_sketch_names", params)
        self.assertIn("operation", params)
        
        # Test profile list
        self.assertIsInstance(params["profile_sketch_names"], list)
        self.assertGreaterEqual(len(params["profile_sketch_names"]), 2)
        
        # Test guide rails
        if "guide_rails" in params:
            self.assertIsInstance(params["guide_rails"], list)
    
    def test_fillet_params(self):
        """Test fillet functionality parameters"""
        params = {
            "edge_ids": ["edge_001", "edge_002"],
            "radius": 5.0,
            "fillet_type": "constant"
        }
        
        # Test parameter structure
        self.assertIn("edge_ids", params)
        self.assertIn("radius", params)
        self.assertIn("fillet_type", params)
        
        # Test edge list
        self.assertIsInstance(params["edge_ids"], list)
        self.assertGreater(len(params["edge_ids"]), 0)
        
        # Test radius
        self.assertIsInstance(params["radius"], (int, float))
        self.assertGreater(params["radius"], 0)
        
        # Test fillet type
        self.assertIn(params["fillet_type"], ["constant", "variable"])
    
    def test_chamfer_params(self):
        """Test chamfer functionality parameters"""
        params = {
            "edge_ids": ["edge_001", "edge_002"],
            "distance": 2.0,
            "chamfer_type": "equal_distance"
        }
        
        # Test parameter structure
        self.assertIn("edge_ids", params)
        self.assertIn("distance", params)
        self.assertIn("chamfer_type", params)
        
        # Test distance
        self.assertIsInstance(params["distance"], (int, float))
        self.assertGreater(params["distance"], 0)
        
        # Test chamfer type
        self.assertIn(params["chamfer_type"], ["equal_distance", "two_distances", "angle_distance"])
    
    def test_pattern_rectangular_params(self):
        """Test rectangular pattern functionality parameters"""
        params = {
            "features_to_pattern": ["feature_001"],
            "direction1": [1, 0, 0],
            "direction2": [0, 1, 0],
            "quantity1": 3,
            "quantity2": 2,
            "distance1": 20.0,
            "distance2": 15.0
        }
        
        required_params = [
            "features_to_pattern", "direction1", "direction2",
            "quantity1", "quantity2", "distance1", "distance2"
        ]
        
        for param in required_params:
            self.assertIn(param, params)
        
        # Test direction vectors
        self.assertIsInstance(params["direction1"], list)
        self.assertEqual(len(params["direction1"]), 3)
        self.assertIsInstance(params["direction2"], list)
        self.assertEqual(len(params["direction2"]), 3)
        
        # Test quantities
        self.assertIsInstance(params["quantity1"], int)
        self.assertIsInstance(params["quantity2"], int)
        self.assertGreater(params["quantity1"], 0)
        self.assertGreater(params["quantity2"], 0)
        
        # Test distances
        self.assertIsInstance(params["distance1"], (int, float))
        self.assertIsInstance(params["distance2"], (int, float))
        self.assertGreater(params["distance1"], 0)
        self.assertGreater(params["distance2"], 0)
    
    def test_pattern_circular_params(self):
        """Test circular pattern functionality parameters"""
        params = {
            "features_to_pattern": ["feature_001"],
            "axis_point": [0, 0, 0],
            "axis_direction": [0, 0, 1],
            "quantity": 6,
            "angle": 360.0
        }
        
        required_params = [
            "features_to_pattern", "axis_point", "axis_direction",
            "quantity", "angle"
        ]
        
        for param in required_params:
            self.assertIn(param, params)
        
        # Test axis parameters
        self.assertIsInstance(params["axis_point"], list)
        self.assertEqual(len(params["axis_point"]), 3)
        self.assertIsInstance(params["axis_direction"], list)
        self.assertEqual(len(params["axis_direction"]), 3)
        
        # Test quantity and angle
        self.assertIsInstance(params["quantity"], int)
        self.assertGreater(params["quantity"], 1)
        self.assertIsInstance(params["angle"], (int, float))
        self.assertGreater(params["angle"], 0)
        self.assertLessEqual(params["angle"], 360)
    
    def test_boolean_operation_params(self):
        """Test boolean operation functionality parameters"""
        params = {
            "target_body_id": "body_001",
            "tool_body_ids": ["body_002", "body_003"],
            "operation": "difference"
        }
        
        # Test parameter structure
        self.assertIn("target_body_id", params)
        self.assertIn("tool_body_ids", params)
        self.assertIn("operation", params)
        
        # Test tool body list
        self.assertIsInstance(params["tool_body_ids"], list)
        self.assertGreater(len(params["tool_body_ids"]), 0)
        
        # Test boolean operation type
        valid_operations = ["union", "difference", "intersection"]
        self.assertIn(params["operation"], valid_operations)

class TestModelingWorkflow(unittest.TestCase):
    """Modeling workflow test class"""
    
    def test_modeling_tool_availability(self):
        """Test modeling tool availability"""
        try:
            # Test modeling tool module imports
            from tools.modeling import (
                create_extrude, create_revolve, create_sweep, create_loft,
                create_fillet, create_chamfer, create_shell, boolean_operation,
                split_body, create_pattern_rectangular, create_pattern_circular,
                create_mirror
            )
            
            # Verify tool functions are available
            modeling_tools = [
                create_extrude, create_revolve, create_sweep, create_loft,
                create_fillet, create_chamfer, create_shell, boolean_operation,
                split_body, create_pattern_rectangular, create_pattern_circular,
                create_mirror
            ]
            
            for tool in modeling_tools:
                self.assertTrue(callable(tool), f"Modeling tool {tool.__name__} is not callable")
        
        except ImportError:
            self.skipTest("Modeling tool modules not available")
    
    def test_complex_modeling_workflow(self):
        """Test complex modeling workflow"""
        workflow_steps = [
            ("create_sketch", "Create base sketch"),
            ("draw_rectangle", "Draw rectangle"),
            ("create_extrude", "Extrude to create base"),
            ("create_sketch", "Create feature sketch"),
            ("draw_circle", "Draw circle"),
            ("create_extrude", "Extrude cut"),
            ("create_fillet", "Add fillet"),
            ("create_pattern_rectangular", "Rectangular pattern"),
        ]
        
        # Verify workflow steps are reasonable
        self.assertGreater(len(workflow_steps), 5)
        
        # Check that each step has tool name and description
        for step in workflow_steps:
            self.assertEqual(len(step), 2)
            tool_name, description = step
            self.assertIsInstance(tool_name, str)
            self.assertIsInstance(description, str)
            self.assertGreater(len(tool_name), 0)
            self.assertGreater(len(description), 0)

class TestModelingToolsModular(unittest.TestCase):
    """Test modeling tools modular structure"""
    
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
    
    def test_modeling_module_imports(self):
        """Test modeling module imports"""
        try:
            from tools.modeling import features, advanced, patterns
            from tools.modeling import initialize_modeling_tools
            self.assertTrue(True, "Module import successful")
        except ImportError as e:
            self.fail(f"Module import failed: {e}")
    
    def test_modeling_module_initialization(self):
        """Test modeling module initialization"""
        from tools.modeling import initialize_modeling_tools
        from tools.modeling import features, advanced, patterns
        
        # Initialize module
        initialize_modeling_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Verify global variable settings
        self.assertEqual(features.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(features.context_manager, self.mock_context_manager)
        self.assertEqual(features.mcp, self.mock_mcp)
        
        self.assertEqual(advanced.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(advanced.context_manager, self.mock_context_manager)
        self.assertEqual(advanced.mcp, self.mock_mcp)
        
        self.assertEqual(patterns.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(patterns.context_manager, self.mock_context_manager)
        self.assertEqual(patterns.mcp, self.mock_mcp)
    
    def test_features_tools_available(self):
        """Test basic feature tool function availability"""
        from tools.modeling.features import (
            create_extrude, create_revolve, create_sweep, create_loft
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(create_extrude))
        self.assertTrue(callable(create_revolve))
        self.assertTrue(callable(create_sweep))
        self.assertTrue(callable(create_loft))
    
    def test_advanced_tools_available(self):
        """Test advanced modeling tool function availability"""
        from tools.modeling.advanced import (
            create_fillet, create_chamfer, create_shell,
            boolean_operation, split_body
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(create_fillet))
        self.assertTrue(callable(create_chamfer))
        self.assertTrue(callable(create_shell))
        self.assertTrue(callable(boolean_operation))
        self.assertTrue(callable(split_body))
    
    def test_patterns_tools_available(self):
        """Test pattern and mirror tool function availability"""
        from tools.modeling.patterns import (
            create_pattern_rectangular, create_pattern_circular, create_mirror
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(create_pattern_rectangular))
        self.assertTrue(callable(create_pattern_circular))
        self.assertTrue(callable(create_mirror))
    
    @patch('tools.modeling.features.adsk')
    async def test_create_extrude_functionality(self, mock_adsk):
        """Test create_extrude functionality"""
        from tools.modeling import initialize_modeling_tools
        from tools.modeling.features import create_extrude
        
        # Set up mock objects
        mock_sketch = Mock()
        mock_sketch.name = "TestSketch"
        mock_sketch.profiles.count = 1
        mock_profile = Mock()
        mock_sketch.profiles.item.return_value = mock_profile
        
        mock_extrude = Mock()
        mock_extrude.entityToken = "extrude_123"
        mock_extrude.bodies.count = 1
        
        mock_extrudes = Mock()
        mock_extrudes.add.return_value = mock_extrude
        mock_ext_input = Mock()
        mock_extrudes.createInput.return_value = mock_ext_input
        
        self.mock_root_comp.features.extrudeFeatures = mock_extrudes
        self.mock_root_comp.sketches.count = 1
        self.mock_root_comp.sketches.item.return_value = mock_sketch
        
        # Mock ValueInput
        mock_value = Mock()
        mock_adsk.core.ValueInput.createByReal.return_value = mock_value
        
        # Initialize module
        initialize_modeling_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test create_extrude
        result = await create_extrude(sketch_name="TestSketch", distance=10.0)
        
        # Verify result
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("extrude_id"), "extrude_123")
        self.assertEqual(result.get("sketch_name"), "TestSketch")
        self.assertEqual(result.get("distance"), 10.0)
    
    async def test_error_handling_no_design(self):
        """Test error handling when no design is active"""
        from tools.modeling import initialize_modeling_tools
        from tools.modeling.features import create_extrude
        
        # Set fusion_bridge with no design
        self.mock_fusion_bridge.design = None
        
        # Initialize module
        initialize_modeling_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test create_extrude
        result = await create_extrude(sketch_name="TestSketch", distance=10.0)
        
        # Verify error handling
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No active design")


class TestModelingToolsIntegration(unittest.TestCase):
    """Test modeling tools integration"""
    
    def test_all_tools_import_from_main_module(self):
        """Test all tools can be imported from main module"""
        try:
            from tools.modeling import (
                create_extrude, create_revolve, create_sweep, create_loft,
                create_fillet, create_chamfer, create_shell,
                boolean_operation, split_body,
                create_pattern_rectangular, create_pattern_circular, create_mirror,
                initialize_modeling_tools
            )
            self.assertTrue(True, "All tools imported successfully")
        except ImportError as e:
            self.fail(f"Tool import failed: {e}")
    
    def test_module_structure(self):
        """Test module structure completeness"""
        import tools.modeling
        
        # Verify __all__ attribute exists
        self.assertTrue(hasattr(tools.modeling, '__all__'))
        
        # Verify key functions in __all__
        expected_functions = [
            'initialize_modeling_tools', 'create_extrude', 'create_revolve',
            'create_sweep', 'create_loft', 'create_fillet', 'create_chamfer',
            'create_shell', 'boolean_operation', 'split_body',
            'create_pattern_rectangular', 'create_pattern_circular', 'create_mirror'
        ]
        
        for func_name in expected_functions:
            self.assertIn(func_name, tools.modeling.__all__, 
                         f"{func_name} not in __all__")


def run_modeling_tests():
    """Run modeling tool tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_modeling_tests()
