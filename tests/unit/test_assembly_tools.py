#!/usr/bin/env python3
"""
Fusion360 MCP Server Assembly Tools Unit Tests

Test assembly functionality:
- Component creation and management
- Constraint system
- Motion analysis
- Interference check
- Exploded view
- Assembly animation
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestAssemblyTools(unittest.TestCase):
    """Assembly tools test class"""
    
    def test_create_component_params(self):
        """Test component creation parameters"""
        params = {
            "name": "GearBox",
            "description": "Gearbox assembly",
            "activate": True
        }
        
        # Test parameter structure
        self.assertIn("name", params)
        self.assertIn("description", params)
        self.assertIn("activate", params)
        
        # Test parameter types
        self.assertIsInstance(params["name"], str)
        self.assertIsInstance(params["description"], str)
        self.assertIsInstance(params["activate"], bool)
        
        # Test parameter values
        self.assertGreater(len(params["name"]), 0)
    
    def test_insert_component_params(self):
        """Test component insertion parameters"""
        params = {
            "file_path": "/path/to/gear.f3d",
            "name": "MainGear",
            "transform_matrix": [
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1
            ]
        }
        
        # Test parameter structure
        self.assertIn("file_path", params)
        self.assertIn("name", params)
        
        # Test file path
        self.assertIsInstance(params["file_path"], str)
        self.assertGreater(len(params["file_path"]), 0)
        
        # Test transform matrix
        if "transform_matrix" in params:
            self.assertIsInstance(params["transform_matrix"], list)
            self.assertEqual(len(params["transform_matrix"]), 16)
            for value in params["transform_matrix"]:
                self.assertIsInstance(value, (int, float))
    
    def test_mate_constraint_params(self):
        """Test mate constraint parameters"""
        params = {
            "constraint_type": "coincident",
            "entity1_id": "face_001",
            "entity2_id": "face_002",
            "offset": 0.0,
            "angle": 0.0
        }
        
        # Test parameter structure
        required_params = ["constraint_type", "entity1_id", "entity2_id"]
        for param in required_params:
            self.assertIn(param, params)
        
        # Test constraint type
        valid_constraints = [
            "coincident", "parallel", "perpendicular", 
            "tangent", "concentricity", "symmetry",
            "distance", "angle"
        ]
        self.assertIn(params["constraint_type"], valid_constraints)
        
        # Test offset and angle
        if "offset" in params:
            self.assertIsInstance(params["offset"], (int, float))
        if "angle" in params:
            self.assertIsInstance(params["angle"], (int, float))
    
    def test_joint_params(self):
        """Test joint connection parameters"""
        params = {
            "joint_type": "revolute",
            "origin_entity_id": "component_001",
            "origin_point": [0, 0, 0],
            "origin_axis": [0, 0, 1],
            "target_entity_id": "component_002", 
            "target_point": [10, 0, 0],
            "target_axis": [0, 0, 1],
            "limits": {
                "min_angle": -180,
                "max_angle": 180
            }
        }
        
        # Test parameter structure
        required_params = [
            "joint_type", "origin_entity_id", "origin_point", "origin_axis",
            "target_entity_id", "target_point", "target_axis"
        ]
        for param in required_params:
            self.assertIn(param, params)
        
        # Test joint type
        valid_joint_types = [
            "revolute", "prismatic", "ball", "pin_slot",
            "planar", "cylindrical"
        ]
        self.assertIn(params["joint_type"], valid_joint_types)
        
        # Test points and axis vectors
        for key in ["origin_point", "origin_axis", "target_point", "target_axis"]:
            self.assertIsInstance(params[key], list)
            self.assertEqual(len(params[key]), 3)
        
        # Test limit conditions
        if "limits" in params:
            self.assertIsInstance(params["limits"], dict)
    
    def test_motion_study_params(self):
        """Test motion analysis parameters"""
        params = {
            "name": "GearBoxMotion",
            "joint_ids": ["joint_001", "joint_002"],
            "duration": 10.0,
            "steps": 100
        }
        
        # Test parameter structure
        self.assertIn("name", params)
        self.assertIn("joint_ids", params)
        self.assertIn("duration", params)
        self.assertIn("steps", params)
        
        # Test joint list
        self.assertIsInstance(params["joint_ids"], list)
        self.assertGreater(len(params["joint_ids"]), 0)
        
        # Test time and steps
        self.assertIsInstance(params["duration"], (int, float))
        self.assertGreater(params["duration"], 0)
        self.assertIsInstance(params["steps"], int)
        self.assertGreater(params["steps"], 0)
    
    def test_interference_check_params(self):
        """Test interference check parameters"""
        params = {
            "component_ids": ["comp_001", "comp_002", "comp_003"],
            "tolerance": 0.001
        }
        
        # Test parameter structure
        self.assertIn("tolerance", params)
        
        # Test component list
        if "component_ids" in params:
            self.assertIsInstance(params["component_ids"], list)
            self.assertGreater(len(params["component_ids"]), 1)
        
        # Test tolerance
        self.assertIsInstance(params["tolerance"], (int, float))
        self.assertGreater(params["tolerance"], 0)
    
    def test_exploded_view_params(self):
        """Test exploded view parameters"""
        params = {
            "name": "AssemblyExploded",
            "explosion_direction": [0, 0, 1],
            "explosion_distance": 100.0,
            "component_ids": ["comp_001", "comp_002"]
        }
        
        # Test parameter structure
        self.assertIn("name", params)
        self.assertIn("explosion_direction", params)
        self.assertIn("explosion_distance", params)
        
        # Test explosion direction
        self.assertIsInstance(params["explosion_direction"], list)
        self.assertEqual(len(params["explosion_direction"]), 3)
        
        # Test explosion distance
        self.assertIsInstance(params["explosion_distance"], (int, float))
        self.assertGreater(params["explosion_distance"], 0)
        
        # Test component list
        if "component_ids" in params:
            self.assertIsInstance(params["component_ids"], list)
    
    def test_assembly_animation_params(self):
        """Test assembly animation parameters"""
        params = {
            "name": "AssemblySequence",
            "keyframes": [
                {
                    "time": 0.0,
                    "component_id": "comp_001",
                    "position": [0, 0, 0],
                    "rotation": [0, 0, 0]
                },
                {
                    "time": 2.0,
                    "component_id": "comp_001", 
                    "position": [0, 0, 50],
                    "rotation": [0, 0, 90]
                }
            ],
            "duration": 5.0,
            "loop": False
        }
        
        # Test parameter structure
        self.assertIn("name", params)
        self.assertIn("keyframes", params)
        self.assertIn("duration", params)
        self.assertIn("loop", params)
        
        # Test keyframes
        self.assertIsInstance(params["keyframes"], list)
        self.assertGreaterEqual(len(params["keyframes"]), 2)
        
        for keyframe in params["keyframes"]:
            self.assertIn("time", keyframe)
            self.assertIn("component_id", keyframe)
            self.assertIsInstance(keyframe["time"], (int, float))
            self.assertIsInstance(keyframe["component_id"], str)
        
        # Test duration and loop
        self.assertIsInstance(params["duration"], (int, float))
        self.assertGreater(params["duration"], 0)
        self.assertIsInstance(params["loop"], bool)

class TestAssemblyWorkflow(unittest.TestCase):
    """Assembly workflow test class"""
    
    def test_assembly_tool_availability(self):
        """Test assembly tool availability"""
        try:
            # Test assembly tool module imports
            from tools.assembly import (
                create_component, insert_component_from_file, get_assembly_info,
                create_mate_constraint, create_joint, create_motion_study,
                check_interference, create_exploded_view, animate_assembly
            )
            
            # Verify tool functions are available
            assembly_tools = [
                create_component, insert_component_from_file, get_assembly_info,
                create_mate_constraint, create_joint, create_motion_study,
                check_interference, create_exploded_view, animate_assembly
            ]
            
            for tool in assembly_tools:
                self.assertTrue(callable(tool), f"Assembly tool {tool.__name__} is not callable")
        
        except ImportError:
            self.skipTest("Assembly tool modules not available")
    
    def test_assembly_sequence_workflow(self):
        """Test assembly sequence workflow"""
        assembly_sequence = [
            ("create_component", "Create main assembly"),
            ("insert_component_from_file", "Insert base component"),
            ("insert_component_from_file", "Insert gear component"),
            ("create_mate_constraint", "Create mate constraint"),
            ("create_joint", "Create revolute joint"),
            ("check_interference", "Check interference"),
            ("create_motion_study", "Create motion analysis"),
            ("create_exploded_view", "Create exploded view"),
            ("animate_assembly", "Create assembly animation")
        ]
        
        # Verify assembly sequence is reasonable
        self.assertGreater(len(assembly_sequence), 6)
        
        # Check completeness of each step
        for step in assembly_sequence:
            self.assertEqual(len(step), 2)
            tool_name, description = step
            self.assertIsInstance(tool_name, str)
            self.assertIsInstance(description, str)
            self.assertGreater(len(tool_name), 0)
            self.assertGreater(len(description), 0)
    
    def test_constraint_hierarchy(self):
        """Test constraint hierarchy"""
        constraint_hierarchy = {
            "Basic constraints": ["coincident", "parallel", "perpendicular"],
            "Geometric constraints": ["tangent", "concentricity", "symmetry"],
            "Dimensional constraints": ["distance", "angle"],
            "Motion constraints": ["revolute", "prismatic", "ball"]
        }
        
        # Verify constraint classification
        self.assertIn("Basic constraints", constraint_hierarchy)
        self.assertIn("Geometric constraints", constraint_hierarchy)
        self.assertIn("Dimensional constraints", constraint_hierarchy)
        self.assertIn("Motion constraints", constraint_hierarchy)
        
        # Verify each category has constraint types
        for category, constraints in constraint_hierarchy.items():
            self.assertIsInstance(constraints, list)
            self.assertGreater(len(constraints), 0)
            for constraint in constraints:
                self.assertIsInstance(constraint, str)
                self.assertGreater(len(constraint), 0)


class TestAssemblyToolsModular(unittest.TestCase):
    """Test assembly tools modular structure"""
    
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
    
    def test_assembly_module_imports(self):
        """Test assembly module imports"""
        try:
            from tools.assembly import components, constraints, motion
            from tools.assembly import initialize_assembly_tools
            self.assertTrue(True, "Module import successful")
        except ImportError as e:
            self.fail(f"Module import failed: {e}")
    
    def test_assembly_module_initialization(self):
        """Test assembly module initialization"""
        from tools.assembly import initialize_assembly_tools
        from tools.assembly import components, constraints, motion
        
        # Initialize module
        initialize_assembly_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Verify global variable settings
        self.assertEqual(components.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(components.context_manager, self.mock_context_manager)
        self.assertEqual(components.mcp, self.mock_mcp)
        
        self.assertEqual(constraints.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(constraints.context_manager, self.mock_context_manager)
        self.assertEqual(constraints.mcp, self.mock_mcp)
        
        self.assertEqual(motion.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(motion.context_manager, self.mock_context_manager)
        self.assertEqual(motion.mcp, self.mock_mcp)
    
    def test_components_tools_available(self):
        """Test component management tool function availability"""
        from tools.assembly.components import (
            create_component, insert_component_from_file, get_assembly_info
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(create_component))
        self.assertTrue(callable(insert_component_from_file))
        self.assertTrue(callable(get_assembly_info))
    
    def test_constraints_tools_available(self):
        """Test constraint tool function availability"""
        from tools.assembly.constraints import (
            create_mate_constraint, create_joint
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(create_mate_constraint))
        self.assertTrue(callable(create_joint))
    
    def test_motion_tools_available(self):
        """Test motion analysis tool function availability"""
        from tools.assembly.motion import (
            create_motion_study, check_interference,
            create_exploded_view, animate_assembly
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(create_motion_study))
        self.assertTrue(callable(check_interference))
        self.assertTrue(callable(create_exploded_view))
        self.assertTrue(callable(animate_assembly))
    
    @patch('tools.assembly.components.adsk')
    async def test_create_component_functionality(self, mock_adsk):
        """Test create_component functionality"""
        from tools.assembly import initialize_assembly_tools
        from tools.assembly.components import create_component
        
        # Set up mock objects
        mock_occurrence = Mock()
        mock_occurrence.entityToken = "occurrence_123"
        mock_component = Mock()
        mock_component.name = "TestComponent"
        mock_occurrence.component = mock_component
        
        mock_occurrence_input = Mock()
        self.mock_root_comp.occurrences.createInput.return_value = mock_occurrence_input
        self.mock_root_comp.occurrences.add.return_value = mock_occurrence
        
        # Mock context manager
        mock_context_component = Mock()
        mock_context_component.component_id = "comp_123"
        self.mock_context_manager.add_component.return_value = mock_context_component
        
        # Initialize module
        initialize_assembly_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test create_component
        result = await create_component(name="TestComponent", description="Test component")
        
        # Verify result
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("component_name"), "TestComponent")
        self.assertEqual(result.get("occurrence_id"), "occurrence_123")
        self.assertEqual(result.get("component_id"), "comp_123")
    
    async def test_error_handling_no_design(self):
        """Test error handling when no design is active"""
        from tools.assembly import initialize_assembly_tools
        from tools.assembly.components import create_component
        
        # Set fusion_bridge with no design
        self.mock_fusion_bridge.design = None
        
        # Initialize module
        initialize_assembly_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test create_component
        result = await create_component(name="TestComponent")
        
        # Verify error handling
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No active design")


class TestAssemblyToolsIntegration(unittest.TestCase):
    """Test assembly tools integration"""
    
    def test_all_tools_import_from_main_module(self):
        """Test all tools can be imported from main module"""
        try:
            from tools.assembly import (
                create_component, insert_component_from_file, get_assembly_info,
                create_mate_constraint, create_joint,
                create_motion_study, check_interference,
                create_exploded_view, animate_assembly,
                initialize_assembly_tools
            )
            self.assertTrue(True, "All tools imported successfully")
        except ImportError as e:
            self.fail(f"Tool import failed: {e}")
    
    def test_module_structure(self):
        """Test module structure completeness"""
        import tools.assembly
        
        # Verify __all__ attribute exists
        self.assertTrue(hasattr(tools.assembly, '__all__'))
        
        # Verify key functions in __all__
        expected_functions = [
            'initialize_assembly_tools', 'create_component', 'insert_component_from_file',
            'get_assembly_info', 'create_mate_constraint', 'create_joint',
            'create_motion_study', 'check_interference', 'create_exploded_view',
            'animate_assembly'
        ]
        
        for func_name in expected_functions:
            self.assertIn(func_name, tools.assembly.__all__, 
                         f"{func_name} not in __all__")


def run_assembly_tests():
    """Run assembly tool tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_assembly_tests()
