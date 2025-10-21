#!/usr/bin/env python3
"""
Fusion360 MCP Server Integration Tests

For comprehensive testing of all 41 MCP tools' functionality, performance and stability in a real Fusion360 environment
Includes detailed performance benchmarking, error handling verification and compatibility checks
"""

import asyncio
import json
import logging
import time
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fusion360_integration_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fusion360-integration-test")

class TestResult:
    """Test result data structure"""
    def __init__(self, tool_name: str, success: bool, execution_time: float, 
                 error_message: Optional[str] = None, performance_data: Optional[Dict] = None):
        self.tool_name = tool_name
        self.success = success
        self.execution_time = execution_time
        self.error_message = error_message
        self.performance_data = performance_data or {}
        self.timestamp = datetime.now()

class Fusion360IntegrationTester:
    """Fusion360 integration tester"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.fusion_available = False
        self.test_design_name = f"MCP_Test_Design_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Import MCP server modules
        try:
            sys.path.insert(0, str(Path(__file__).parent / "src"))
            from mcp_server import fusion_bridge, context_manager
            # Import specific functions instead of wildcard imports
            from tools.sketch.basic import create_sketch, draw_line, draw_circle, draw_rectangle, draw_arc, draw_polygon
            from tools.sketch.constraints import add_geometric_constraint, add_dimensional_constraint
            from tools.modeling.features import create_extrude, create_revolve, create_sweep, create_loft
            from tools.modeling.modifications import create_fillet, create_chamfer, create_shell
            from tools.modeling.operations import boolean_operation, split_body
            from tools.modeling.patterns import create_pattern_rectangular, create_pattern_circular, create_mirror
            from tools.assembly.components import create_component, insert_component_from_file
            from tools.assembly.info import get_assembly_info
            from tools.assembly.constraints import create_mate_constraint
            from tools.assembly.joints import create_joint
            from tools.assembly.motion import create_motion_study
            from tools.assembly.analysis import check_interference
            from tools.assembly.views import create_exploded_view
            from tools.assembly.animation import animate_assembly
            from tools.analysis.measurement import measure_distance, measure_angle, measure_area, measure_volume
            from tools.analysis.properties import calculate_mass_properties
            from tools.analysis.section import create_section_analysis
            from tools.analysis.simulation import perform_stress_analysis, perform_modal_analysis, perform_thermal_analysis
            from tools.analysis.reports import generate_analysis_report
            from context.tools import store_design_intent, add_design_task
            
            self.fusion_bridge = fusion_bridge
            self.context_manager = context_manager
            logger.info("MCP server modules imported successfully")
        except ImportError as e:
            logger.error(f"MCP server module import failed: {e}")
            sys.exit(1)

    async def initialize_fusion(self) -> bool:
        """Initialize Fusion360 connection"""
        try:
            logger.info("Initializing Fusion360 connection...")
            self.fusion_available = self.fusion_bridge.initialize()
            
            if self.fusion_available:
                # Create new test design
                app = self.fusion_bridge.app
                doc = app.documents.add(1)  # 1 = Design document type
                doc.name = self.test_design_name
                logger.info(f"Created test design: {self.test_design_name}")
                return True
            else:
                logger.warning("Fusion360 unavailable, running tests in simulation mode")
                return False
                
        except Exception as e:
            logger.error(f"Fusion360 initialization failed: {e}")
            return False

    async def cleanup_test_environment(self):
        """Clean up test environment"""
        try:
            if self.fusion_available and self.fusion_bridge.app:
                # Close test design
                doc = self.fusion_bridge.app.activeDocument
                if doc and doc.name == self.test_design_name:
                    doc.close(False)  # False = don't save
                    logger.info("Test design cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up test environment: {e}")

    def measure_performance(self, func):
        """Performance measurement decorator"""
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            start_memory = self._get_memory_usage()
            
            try:
                result = await func(*args, **kwargs)
                success = True
                error_msg = None
            except Exception as e:
                result = {"error": str(e)}
                success = False
                error_msg = str(e)
                logger.error(f"Tool execution failed: {func.__name__} - {e}")
            
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()
            execution_time = end_time - start_time
            
            performance_data = {
                "execution_time": execution_time,
                "memory_usage_delta": end_memory - start_memory,
                "start_memory": start_memory,
                "end_memory": end_memory
            }
            
            test_result = TestResult(
                tool_name=func.__name__,
                success=success,
                execution_time=execution_time,
                error_message=error_msg,
                performance_data=performance_data
            )
            self.test_results.append(test_result)
            
            logger.info(f"Tool {func.__name__}: {'success' if success else 'failed'} "
                       f"(execution time: {execution_time:.3f}s)")
            
            return result
        return wrapper

    def _get_memory_usage(self) -> float:
        """Get current memory usage (MB)"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    # =========================
    # Sketch Tool Tests
    # =========================
    
    async def test_sketch_tools(self):
        """Test sketch tool set"""
        logger.info("Starting sketch tool tests...")
        
        # Test sketch creation
        await self._test_create_sketch()
        
        # Test basic drawing tools
        await self._test_draw_line()
        await self._test_draw_circle()
        await self._test_draw_rectangle()
        await self._test_draw_arc()
        await self._test_draw_polygon()
        
        # Test constraint tools
        await self._test_add_geometric_constraint()
        await self._test_add_dimensional_constraint()

    @measure_performance
    async def _test_create_sketch(self):
        """Test create sketch"""
        from tools.sketch.basic import create_sketch
        return await create_sketch(
            plane="XY",
            name="test_sketch_1"
        )

    @measure_performance  
    async def _test_draw_line(self):
        """Test draw line"""
        from tools.sketch.basic import draw_line
        return await draw_line(
            start_point=[0, 0],
            end_point=[50, 0],
            sketch_name="test_sketch_1"
        )

    @measure_performance
    async def _test_draw_circle(self):
        """Test draw circle"""
        from tools.sketch.basic import draw_circle
        return await draw_circle(
            center_point=[25, 25],
            radius=10,
            sketch_name="test_sketch_1"
        )

    @measure_performance
    async def _test_draw_rectangle(self):
        """Test draw rectangle"""
        from tools.sketch.basic import draw_rectangle
        return await draw_rectangle(
            start_point=[0, 50],
            end_point=[30, 80],
            sketch_name="test_sketch_1"
        )

    @measure_performance
    async def _test_draw_arc(self):
        """Test draw arc"""
        from tools.sketch.basic import draw_arc
        return await draw_arc(
            center_point=[50, 50],
            start_point=[45, 50],
            end_point=[55, 50],
            sketch_name="test_sketch_1"
        )

    @measure_performance
    async def _test_draw_polygon(self):
        """Test draw polygon"""
        from tools.sketch.basic import draw_polygon
        return await draw_polygon(
            center_point=[75, 25],
            sides=6,
            radius=8,
            sketch_name="test_sketch_1"
        )

    @measure_performance
    async def _test_add_geometric_constraint(self):
        """Test add geometric constraint"""
        from tools.sketch.constraints import add_geometric_constraint
        return await add_geometric_constraint(
            constraint_type="horizontal",
            entities=["line_1"],
            sketch_name="test_sketch_1"
        )

    @measure_performance
    async def _test_add_dimensional_constraint(self):
        """Test add dimensional constraint"""
        from tools.sketch.constraints import add_dimensional_constraint
        return await add_dimensional_constraint(
            constraint_type="distance",
            value=50,
            entities=["line_1"],
            sketch_name="test_sketch_1"
        )

    # =========================
    # Modeling Tool Tests
    # =========================
    
    async def test_modeling_tools(self):
        """Test modeling tool set"""
        logger.info("Starting modeling tool tests...")
        
        # Test basic modeling operations
        await self._test_create_extrude()
        await self._test_create_revolve()
        await self._test_create_sweep()
        await self._test_create_loft()
        
        # Test modification features
        await self._test_create_fillet()
        await self._test_create_chamfer()
        await self._test_create_shell()
        
        # Test boolean operations and patterns
        await self._test_boolean_operation()
        await self._test_split_body()
        await self._test_create_pattern_rectangular()
        await self._test_create_pattern_circular()
        await self._test_create_mirror()

    @measure_performance
    async def _test_create_extrude(self):
        """Test extrude feature"""
        from tools.modeling.features import create_extrude
        return await create_extrude(
            profile_name="test_sketch_1",
            distance=20,
            direction="positive"
        )

    @measure_performance
    async def _test_create_revolve(self):
        """Test revolve feature"""
        from tools.modeling.features import create_revolve
        return await create_revolve(
            profile_name="test_sketch_1",
            axis_line="line_1",
            angle=360
        )

    @measure_performance
    async def _test_create_sweep(self):
        """Test sweep feature"""
        from tools.modeling.features import create_sweep
        return await create_sweep(
            profile_name="test_sketch_1",
            path_name="path_line",
            operation="new_body"
        )

    @measure_performance
    async def _test_create_loft(self):
        """Test loft feature"""
        from tools.modeling.features import create_loft
        return await create_loft(
            profiles=["profile_1", "profile_2"],
            operation="new_body"
        )

    @measure_performance
    async def _test_create_fillet(self):
        """Test fillet feature"""
        from tools.modeling.modifications import create_fillet
        return await create_fillet(
            edges=["edge_1", "edge_2"],
            radius=2
        )

    @measure_performance
    async def _test_create_chamfer(self):
        """Test chamfer feature"""
        from tools.modeling.modifications import create_chamfer
        return await create_chamfer(
            edges=["edge_3", "edge_4"],
            distance=1.5
        )

    @measure_performance
    async def _test_create_shell(self):
        """Test shell feature"""
        from tools.modeling.modifications import create_shell
        return await create_shell(
            faces=["face_1"],
            thickness=2,
            direction="inside"
        )

    @measure_performance
    async def _test_boolean_operation(self):
        """Test boolean operation"""
        from tools.modeling.operations import boolean_operation
        return await boolean_operation(
            operation="union",
            target_body="body_1",
            tool_body="body_2"
        )

    @measure_performance
    async def _test_split_body(self):
        """Test split body"""
        from tools.modeling.operations import split_body
        return await split_body(
            body_name="target_body",
            splitting_plane="XY"
        )

    @measure_performance
    async def _test_create_pattern_rectangular(self):
        """Test rectangular pattern"""
        from tools.modeling.patterns import create_pattern_rectangular
        return await create_pattern_rectangular(
            features=["extrude_1"],
            x_count=3,
            y_count=2,
            x_distance=30,
            y_distance=25
        )

    @measure_performance
    async def _test_create_pattern_circular(self):
        """Test circular pattern"""
        from tools.modeling.patterns import create_pattern_circular
        return await create_pattern_circular(
            features=["extrude_1"],
            count=6,
            axis_line="axis_1"
        )

    @measure_performance
    async def _test_create_mirror(self):
        """Test mirror feature"""
        from tools.modeling.patterns import create_mirror
        return await create_mirror(
            features=["extrude_1"],
            mirror_plane="YZ"
        )

    # =========================
    # Assembly Tool Tests
    # =========================
    
    async def test_assembly_tools(self):
        """Test assembly tool set"""
        logger.info("Starting assembly tool tests...")
        
        await self._test_create_component()
        await self._test_insert_component_from_file()
        await self._test_get_assembly_info()
        await self._test_create_mate_constraint()
        await self._test_create_joint()
        await self._test_create_motion_study()
        await self._test_check_interference()
        await self._test_create_exploded_view()
        await self._test_animate_assembly()

    @measure_performance
    async def _test_create_component(self):
        """Test create component"""
        from tools.assembly.components import create_component
        return await create_component(
            name="test_component_1",
            activate=True
        )

    @measure_performance
    async def _test_insert_component_from_file(self):
        """Test insert component from file"""
        from tools.assembly.components import insert_component_from_file
        return await insert_component_from_file(
            file_path="test_component.f3d",
            position=[0, 0, 0]
        )

    @measure_performance
    async def _test_get_assembly_info(self):
        """Test get assembly info"""
        from tools.assembly.info import get_assembly_info
        return await get_assembly_info()

    @measure_performance
    async def _test_create_mate_constraint(self):
        """Test create mate constraint"""
        from tools.assembly.constraints import create_mate_constraint
        return await create_mate_constraint(
            constraint_type="coincident",
            entity1="face_1",
            entity2="face_2"
        )

    @measure_performance
    async def _test_create_joint(self):
        """Test create joint"""
        from tools.assembly.joints import create_joint
        return await create_joint(
            joint_type="revolute",
            component1="comp_1",
            component2="comp_2"
        )

    @measure_performance
    async def _test_create_motion_study(self):
        """Test create motion study"""
        from tools.assembly.motion import create_motion_study
        return await create_motion_study(
            name="motion_study_1",
            joint_name="revolute_joint_1"
        )

    @measure_performance
    async def _test_check_interference(self):
        """Test interference check"""
        from tools.assembly.analysis import check_interference
        return await check_interference(
            components=["comp_1", "comp_2"]
        )

    @measure_performance
    async def _test_create_exploded_view(self):
        """Test create exploded view"""
        from tools.assembly.views import create_exploded_view
        return await create_exploded_view(
            name="exploded_view_1",
            components=["comp_1", "comp_2"]
        )

    @measure_performance
    async def _test_animate_assembly(self):
        """Test assembly animation"""
        from tools.assembly.animation import animate_assembly
        return await animate_assembly(
            motion_study="motion_study_1",
            duration=5.0
        )

    # =========================
    # Analysis Tool Tests
    # =========================
    
    async def test_analysis_tools(self):
        """Test analysis tool set"""
        logger.info("Starting analysis tool tests...")
        
        await self._test_measure_distance()
        await self._test_measure_angle()
        await self._test_measure_area()
        await self._test_measure_volume()
        await self._test_calculate_mass_properties()
        await self._test_create_section_analysis()
        await self._test_perform_stress_analysis()
        await self._test_perform_modal_analysis()
        await self._test_perform_thermal_analysis()
        await self._test_generate_analysis_report()

    @measure_performance
    async def _test_measure_distance(self):
        """Test distance measurement"""
        from tools.analysis.measurement import measure_distance
        return await measure_distance(
            entity1="point_1",
            entity2="point_2"
        )

    @measure_performance
    async def _test_measure_angle(self):
        """Test angle measurement"""
        from tools.analysis.measurement import measure_angle
        return await measure_angle(
            entity1="line_1",
            entity2="line_2"
        )

    @measure_performance
    async def _test_measure_area(self):
        """Test area measurement"""
        from tools.analysis.measurement import measure_area
        return await measure_area(
            face_name="face_1"
        )

    @measure_performance
    async def _test_measure_volume(self):
        """Test volume measurement"""
        from tools.analysis.measurement import measure_volume
        return await measure_volume(
            body_name="body_1"
        )

    @measure_performance
    async def _test_calculate_mass_properties(self):
        """Test mass properties calculation"""
        from tools.analysis.properties import calculate_mass_properties
        return await calculate_mass_properties(
            body_name="body_1",
            material="aluminum"
        )

    @measure_performance
    async def _test_create_section_analysis(self):
        """Test section analysis"""
        from tools.analysis.section import create_section_analysis
        return await create_section_analysis(
            plane="XY",
            offset=10
        )

    @measure_performance
    async def _test_perform_stress_analysis(self):
        """Test stress analysis"""
        from tools.analysis.simulation import perform_stress_analysis
        return await perform_stress_analysis(
            body_name="body_1",
            load_type="force",
            load_value=1000
        )

    @measure_performance
    async def _test_perform_modal_analysis(self):
        """Test modal analysis"""
        from tools.analysis.simulation import perform_modal_analysis
        return await perform_modal_analysis(
            body_name="body_1",
            modes_count=5
        )

    @measure_performance
    async def _test_perform_thermal_analysis(self):
        """Test thermal analysis"""
        from tools.analysis.simulation import perform_thermal_analysis
        return await perform_thermal_analysis(
            body_name="body_1",
            temperature=100
        )

    @measure_performance
    async def _test_generate_analysis_report(self):
        """Test generate analysis report"""
        from tools.analysis.reports import generate_analysis_report
        return await generate_analysis_report(
            analysis_type="stress",
            include_images=True
        )

    # =========================
    # Context Tool Tests
    # =========================
    
    async def test_context_tools(self):
        """Test context tool set"""
        logger.info("Starting context tool tests...")
        
        await self._test_store_design_intent()
        await self._test_add_design_task()

    @measure_performance
    async def _test_store_design_intent(self):
        """Test store design intent"""
        from context.tools import store_design_intent
        return await store_design_intent(
            project_name="Integration Test Project",
            description="Test project for verifying MCP server functionality",
            requirements=["High strength", "Lightweight", "Easy to manufacture"],
            constraints=["Material: Aluminum alloy", "Max size: 100x100x50mm"]
        )

    @measure_performance
    async def _test_add_design_task(self):
        """Test add design task"""
        from context.tools import add_design_task
        return await add_design_task(
            title="Create main structure",
            description="Design the main structural components of the product",
            priority="high"
        )

    # =========================
    # Core Tool Tests
    # =========================
    
    async def test_core_tools(self):
        """Test core tools"""
        logger.info("Starting core tool tests...")
        
        await self._test_create_parameter()
        await self._test_export_stl()
        await self._test_save_design()

    @measure_performance
    async def _test_create_parameter(self):
        """Test create parameter"""
        # Import from main server
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from mcp_server import create_parameter
        return await create_parameter(
            name="test_height",
            value=25.0,
            units="mm",
            comment="Test height parameter"
        )

    @measure_performance
    async def _test_export_stl(self):
        """Test STL export"""
        from mcp_server import export_stl
        return await export_stl(
            filename="test_export.stl",
            mesh_refinement="medium"
        )

    @measure_performance
    async def _test_save_design(self):
        """Test save design"""
        from mcp_server import save_design
        return await save_design(
            filename=f"{self.test_design_name}.f3d"
        )

    # =========================
    # Main Test Execution Flow
    # =========================
    
    async def run_comprehensive_test(self):
        """Run comprehensive integration test"""
        logger.info("Starting Fusion360 MCP server comprehensive integration test")
        
        # Initialize test environment
        if not await self.initialize_fusion():
            logger.warning("Running tests in simulation mode")
        
        try:
            # Test by module in order
            await self.test_context_tools()
            await self.test_sketch_tools()
            await self.test_modeling_tools()
            await self.test_assembly_tools()
            await self.test_analysis_tools()
            await self.test_core_tools()
            
        except Exception as e:
            logger.error(f"Error during test execution: {e}")
            logger.error(traceback.format_exc())
        
        finally:
            # Clean up test environment
            await self.cleanup_test_environment()
            
            # Generate test report
            self.generate_test_report()

    def generate_test_report(self):
        """Generate detailed test report"""
        logger.info("Generating test report...")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - successful_tests
        
        # Calculate performance statistics
        execution_times = [result.execution_time for result in self.test_results if result.success]
        avg_execution_time = statistics.mean(execution_times) if execution_times else 0
        max_execution_time = max(execution_times) if execution_times else 0
        min_execution_time = min(execution_times) if execution_times else 0
        
        # Group statistics by module
        modules = {}
        for result in self.test_results:
            module = self._get_tool_module(result.tool_name)
            if module not in modules:
                modules[module] = {"success": 0, "failed": 0, "total": 0}
            modules[module]["total"] += 1
            if result.success:
                modules[module]["success"] += 1
            else:
                modules[module]["failed"] += 1
        
        # Generate report
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "test_timestamp": datetime.now().isoformat(),
                "fusion_available": self.fusion_available
            },
            "performance_metrics": {
                "average_execution_time": avg_execution_time,
                "max_execution_time": max_execution_time,
                "min_execution_time": min_execution_time,
                "total_execution_time": sum(execution_times)
            },
            "module_statistics": modules,
            "detailed_results": [
                {
                    "tool_name": result.tool_name,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "error_message": result.error_message,
                    "performance_data": result.performance_data,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in self.test_results
            ],
            "failed_tests": [
                {
                    "tool_name": result.tool_name,
                    "error_message": result.error_message,
                    "execution_time": result.execution_time
                }
                for result in self.test_results if not result.success
            ]
        }
        
        # Save report to JSON file
        report_filename = f"fusion360_integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Output test summary
        logger.info("=" * 60)
        logger.info("FUSION360 MCP SERVER INTEGRATION TEST REPORT")
        logger.info("=" * 60)
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Successful tests: {successful_tests}")
        logger.info(f"Failed tests: {failed_tests}")
        logger.info(f"Success rate: {successful_tests / total_tests * 100:.1f}%")
        logger.info(f"Average execution time: {avg_execution_time:.3f}s")
        logger.info(f"Fusion360 availability: {'Yes' if self.fusion_available else 'No (simulation mode)'}")
        logger.info("=" * 60)
        
        # Display results by module
        for module, stats in modules.items():
            success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
            logger.info(f"{module}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        if failed_tests > 0:
            logger.info("Failed tests:")
            for result in self.test_results:
                if not result.success:
                    logger.error(f"  - {result.tool_name}: {result.error_message}")
        
        logger.info(f"Detailed report saved to: {report_filename}")

    def _get_tool_module(self, tool_name: str) -> str:
        """Determine module based on tool name"""
        sketch_tools = ["create_sketch", "draw_line", "draw_circle", "draw_rectangle", 
                       "draw_arc", "draw_polygon", "add_geometric_constraint", "add_dimensional_constraint"]
        modeling_tools = ["create_extrude", "create_revolve", "create_sweep", "create_loft",
                         "create_fillet", "create_chamfer", "create_shell", "boolean_operation",
                         "split_body", "create_pattern_rectangular", "create_pattern_circular", "create_mirror"]
        assembly_tools = ["create_component", "insert_component_from_file", "get_assembly_info",
                         "create_mate_constraint", "create_joint", "create_motion_study",
                         "check_interference", "create_exploded_view", "animate_assembly"]
        analysis_tools = ["measure_distance", "measure_angle", "measure_area", "measure_volume",
                         "calculate_mass_properties", "create_section_analysis", "perform_stress_analysis",
                         "perform_modal_analysis", "perform_thermal_analysis", "generate_analysis_report"]
        context_tools = ["store_design_intent", "add_design_task"]
        core_tools = ["create_parameter", "export_stl", "save_design"]
        
        if tool_name in sketch_tools:
            return "Sketch Tools"
        elif tool_name in modeling_tools:
            return "Modeling Tools"
        elif tool_name in assembly_tools:
            return "Assembly Tools"
        elif tool_name in analysis_tools:
            return "Analysis Tools"
        elif tool_name in context_tools:
            return "Context Tools"
        elif tool_name in core_tools:
            return "Core Tools"
        else:
            return "Unknown Module"

async def main():
    """Main function"""
    tester = Fusion360IntegrationTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    # Set event loop policy (needed for Windows)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run tests
    asyncio.run(main())
