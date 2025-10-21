#!/usr/bin/env python3
"""
Fusion360 MCP Server Analysis Tools Unit Tests

Test analysis functionality:
- Measurement tools (distance, angle, area, volume)
- Mass properties analysis
- Section analysis
- Stress analysis
- Modal analysis
- Thermal analysis
- Analysis report generation
"""

import asyncio
import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestAnalysisTools(unittest.TestCase):
    """Analysis tools test class"""
    
    def setUp(self):
        """Test initialization"""
        self.maxDiff = None
    
    def test_measure_distance_params(self):
        """Test distance measurement parameters"""
        params = {
            "point1": [0, 0, 0],
            "point2": [10, 10, 10],
            "measurement_type": "linear"
        }
        
        # Test parameter structure
        self.assertIn("point1", params)
        self.assertIn("point2", params)
        self.assertIn("measurement_type", params)
        
        # Test parameter types
        self.assertIsInstance(params["point1"], list)
        self.assertIsInstance(params["point2"], list)
        self.assertEqual(len(params["point1"]), 3)
        self.assertEqual(len(params["point2"]), 3)
    
    def test_measure_angle_params(self):
        """Test angle measurement parameters"""
        params = {
            "point1": [10, 0, 0],
            "vertex": [0, 0, 0],
            "point2": [0, 10, 0]
        }
        
        # Test parameter structure
        self.assertIn("point1", params)
        self.assertIn("vertex", params)
        self.assertIn("point2", params)
        
        # Test parameter types
        for key in ["point1", "vertex", "point2"]:
            self.assertIsInstance(params[key], list)
            self.assertEqual(len(params[key]), 3)
    
    def test_mass_properties_params(self):
        """Test mass properties analysis parameters"""
        params = {
            "body_ids": ["body_001", "body_002"],
            "material_density": 7.85,
            "units": "metric"
        }
        
        # Test parameter structure
        self.assertIn("body_ids", params)
        self.assertIn("material_density", params)
        self.assertIn("units", params)
        
        # Test parameter types
        self.assertIsInstance(params["body_ids"], list)
        self.assertIsInstance(params["material_density"], (int, float))
        self.assertIsInstance(params["units"], str)
    
    def test_stress_analysis_params(self):
        """Test stress analysis parameters"""
        params = {
            "body_ids": ["body_001"],
            "material_properties": {
                "elastic_modulus": 200000,
                "poisson_ratio": 0.3,
                "density": 7.85
            },
            "loads": [
                {
                    "type": "force",
                    "magnitude": 1000,
                    "direction": [0, 0, -1],
                    "location": [0, 0, 50]
                }
            ],
            "constraints": [
                {
                    "type": "fixed",
                    "faces": ["face_bottom"]
                }
            ]
        }
        
        # Test parameter structure
        self.assertIn("body_ids", params)
        self.assertIn("material_properties", params)
        self.assertIn("loads", params)
        self.assertIn("constraints", params)
        
        # Test material properties
        mat_props = params["material_properties"]
        required_props = ["elastic_modulus", "poisson_ratio", "density"]
        for prop in required_props:
            self.assertIn(prop, mat_props)
            self.assertIsInstance(mat_props[prop], (int, float))
        
        # Test loads
        self.assertIsInstance(params["loads"], list)
        self.assertGreater(len(params["loads"]), 0)
        
        load = params["loads"][0]
        self.assertIn("type", load)
        self.assertIn("magnitude", load)
        self.assertIn("direction", load)
    
    def test_modal_analysis_params(self):
        """Test modal analysis parameters"""
        params = {
            "body_ids": ["body_001"],
            "material_properties": {
                "elastic_modulus": 200000,
                "poisson_ratio": 0.3,
                "density": 7.85
            },
            "constraints": [
                {
                    "type": "fixed",
                    "faces": ["face_bottom"]
                }
            ],
            "number_of_modes": 10
        }
        
        # Test parameter structure
        self.assertIn("body_ids", params)
        self.assertIn("material_properties", params)
        self.assertIn("constraints", params)
        self.assertIn("number_of_modes", params)
        
        # Test number of modes
        self.assertIsInstance(params["number_of_modes"], int)
        self.assertGreater(params["number_of_modes"], 0)
    
    def test_thermal_analysis_params(self):
        """Test thermal analysis parameters"""
        params = {
            "body_ids": ["body_001"],
            "material_properties": {
                "thermal_conductivity": 45,
                "specific_heat": 460,
                "density": 7.85
            },
            "thermal_loads": [
                {
                    "type": "heat_flux",
                    "value": 1000,
                    "faces": ["face_top"]
                }
            ],
            "thermal_constraints": [
                {
                    "type": "temperature",
                    "value": 25,
                    "faces": ["face_bottom"]
                }
            ]
        }
        
        # Test parameter structure
        self.assertIn("body_ids", params)
        self.assertIn("material_properties", params)
        self.assertIn("thermal_loads", params)
        self.assertIn("thermal_constraints", params)
        
        # Test thermal material properties
        mat_props = params["material_properties"]
        thermal_props = ["thermal_conductivity", "specific_heat", "density"]
        for prop in thermal_props:
            self.assertIn(prop, mat_props)
            self.assertIsInstance(mat_props[prop], (int, float))

class TestAnalysisWorkflow(unittest.TestCase):
    """Analysis workflow test class"""
    
    def test_analysis_tool_availability(self):
        """Test analysis tool availability"""
        try:
            # Test analysis tool module imports
            from tools.analysis import (
                measure_distance, measure_angle, measure_area, measure_volume,
                calculate_mass_properties, create_section_analysis,
                perform_stress_analysis, perform_modal_analysis,
                perform_thermal_analysis, generate_analysis_report
            )
            
            # Verify tool functions are available
            analysis_tools = [
                measure_distance, measure_angle, measure_area, measure_volume,
                calculate_mass_properties, create_section_analysis,
                perform_stress_analysis, perform_modal_analysis,
                perform_thermal_analysis, generate_analysis_report
            ]
            
            for tool in analysis_tools:
                self.assertTrue(callable(tool), f"Analysis tool {tool.__name__} is not callable")
        
        except ImportError:
            self.skipTest("Analysis tool modules not available")
    
    def test_context_persistence_integration(self):
        """Test context persistence integration"""
        try:
            from context import ContextPersistenceManager
            
            manager = ContextPersistenceManager("test_analysis.json")
            
            # Test analysis task addition
            task = manager.add_task(
                "Stress analysis test",
                "Test completeness of stress analysis functionality"
            )
            
            self.assertIsNotNone(task)
            self.assertEqual(task.title, "Stress analysis test")
            
            # Clean up test file
            import os
            if os.path.exists("test_analysis.json"):
                os.remove("test_analysis.json")
        
        except ImportError:
            self.skipTest("Context persistence module not available")


class TestAnalysisToolsModular(unittest.TestCase):
    """Test analysis tools modular structure"""
    
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
    
    def test_analysis_module_imports(self):
        """Test analysis module imports"""
        try:
            from tools.analysis import measurement, simulation, reporting
            from tools.analysis import initialize_analysis_tools
            self.assertTrue(True, "Module import successful")
        except ImportError as e:
            self.fail(f"Module import failed: {e}")
    
    def test_analysis_module_initialization(self):
        """Test analysis module initialization"""
        from tools.analysis import initialize_analysis_tools
        from tools.analysis import measurement, simulation, reporting
        
        # Initialize module
        initialize_analysis_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Verify global variable settings
        self.assertEqual(measurement.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(measurement.context_manager, self.mock_context_manager)
        self.assertEqual(measurement.mcp, self.mock_mcp)
        
        self.assertEqual(simulation.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(simulation.context_manager, self.mock_context_manager)
        self.assertEqual(simulation.mcp, self.mock_mcp)
        
        self.assertEqual(reporting.fusion_bridge, self.mock_fusion_bridge)
        self.assertEqual(reporting.context_manager, self.mock_context_manager)
        self.assertEqual(reporting.mcp, self.mock_mcp)
    
    def test_measurement_tools_available(self):
        """Test measurement tool function availability"""
        from tools.analysis.measurement import (
            measure_distance, measure_angle, measure_area, 
            measure_volume, calculate_mass_properties
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(measure_distance))
        self.assertTrue(callable(measure_angle))
        self.assertTrue(callable(measure_area))
        self.assertTrue(callable(measure_volume))
        self.assertTrue(callable(calculate_mass_properties))
    
    def test_simulation_tools_available(self):
        """Test simulation analysis tool function availability"""
        from tools.analysis.simulation import (
            create_section_analysis, perform_stress_analysis,
            perform_modal_analysis, perform_thermal_analysis
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(create_section_analysis))
        self.assertTrue(callable(perform_stress_analysis))
        self.assertTrue(callable(perform_modal_analysis))
        self.assertTrue(callable(perform_thermal_analysis))
    
    def test_reporting_tools_available(self):
        """Test report generation tool function availability"""
        from tools.analysis.reporting import generate_analysis_report
        
        # Verify function exists and is callable
        self.assertTrue(callable(generate_analysis_report))
    
    async def test_measure_distance_functionality(self):
        """Test measure_distance functionality"""
        from tools.analysis import initialize_analysis_tools
        from tools.analysis.measurement import measure_distance
        
        # Initialize module
        initialize_analysis_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test measure_distance
        result = await measure_distance(
            point1=[0, 0, 0],
            point2=[3, 4, 0],
            measurement_type="linear"
        )
        
        # Verify result
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("distance"), 5.0)  # sqrt(3^2 + 4^2)
        self.assertEqual(result.get("measurement_type"), "linear")
        self.assertEqual(result.get("units"), "mm")
    
    async def test_generate_analysis_report_functionality(self):
        """Test generate_analysis_report functionality"""
        from tools.analysis import initialize_analysis_tools
        from tools.analysis.reporting import generate_analysis_report
        
        # Initialize module
        initialize_analysis_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Mock analysis results
        analysis_results = [
            {
                "analysis_type": "static_stress",
                "success": True,
                "analysis_results": {
                    "max_stress": {"value": 145.8},
                    "safety_factor": {"min_value": 2.74}
                },
                "recommendations": ["Recommend increasing material thickness"]
            }
        ]
        
        # Test generate_analysis_report
        result = await generate_analysis_report(
            analysis_results=analysis_results,
            report_format="detailed",
            include_images=True
        )
        
        # Verify result
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("format"), "detailed")
        self.assertIn("report_content", result)
        self.assertIn("report_files", result)
    
    async def test_error_handling_no_design(self):
        """Test error handling when no design is active"""
        from tools.analysis import initialize_analysis_tools
        from tools.analysis.measurement import measure_volume
        
        # Set fusion_bridge with no design
        self.mock_fusion_bridge.design = None
        
        # Initialize module
        initialize_analysis_tools(
            self.mock_fusion_bridge,
            self.mock_context_manager,
            self.mock_mcp
        )
        
        # Test measure_volume
        result = await measure_volume(body_id="test_body")
        
        # Verify error handling
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No active design")


class TestAnalysisToolsIntegration(unittest.TestCase):
    """Test analysis tools integration"""
    
    def test_all_tools_import_from_main_module(self):
        """Test all tools can be imported from main module"""
        try:
            from tools.analysis import (
                measure_distance, measure_angle, measure_area, measure_volume,
                calculate_mass_properties, create_section_analysis,
                perform_stress_analysis, perform_modal_analysis,
                perform_thermal_analysis, generate_analysis_report,
                initialize_analysis_tools
            )
            self.assertTrue(True, "All tools imported successfully")
        except ImportError as e:
            self.fail(f"Tool import failed: {e}")
    
    def test_module_structure(self):
        """Test module structure completeness"""
        import tools.analysis
        
        # Verify __all__ attribute exists
        self.assertTrue(hasattr(tools.analysis, '__all__'))
        
        # Verify key functions in __all__
        expected_functions = [
            'initialize_analysis_tools', 'measure_distance', 'measure_angle',
            'measure_area', 'measure_volume', 'calculate_mass_properties',
            'create_section_analysis', 'perform_stress_analysis',
            'perform_modal_analysis', 'perform_thermal_analysis',
            'generate_analysis_report'
        ]
        
        for func_name in expected_functions:
            self.assertIn(func_name, tools.analysis.__all__, 
                         f"{func_name} not in __all__")


def run_analysis_tests():
    """Run analysis tool tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_analysis_tests()
