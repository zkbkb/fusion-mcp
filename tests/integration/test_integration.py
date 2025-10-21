"""
Fusion360 MCP Server - Integration Test Script

This script performs end-to-end integration tests to verify MCP server communication with Fusion360 plugin and functionality.
"""

import os
import sys
import asyncio
import json
import logging
import argparse
import websockets
import uuid
from typing import Dict, Any, List

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('integration_test.log')
    ]
)

logger = logging.getLogger("integration_test")

class IntegrationTest:
    """Integration test class"""
    
    def __init__(self, server_url: str):
        """
        Initialize integration test
        
        Args:
            server_url: MCP server WebSocket URL
        """
        self.server_url = server_url
        self.websocket = None
        self.test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
    
    async def connect(self):
        """Connect to MCP server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info(f"Connected to MCP server: {self.server_url}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from MCP server")
    
    async def send_command(self, command_type: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send command to MCP server
        
        Args:
            command_type: Command type
            args: Command arguments
            
        Returns:
            Command execution result
        """
        if not self.websocket:
            raise RuntimeError("Not connected to MCP server")
        
        # Generate command ID
        command_id = str(uuid.uuid4())
        
        # Construct command message
        message = {
            "id": command_id,
            "type": command_type,
            "args": args
        }
        
        # Send command
        await self.websocket.send(json.dumps(message))
        logger.info(f"Sent command: {command_type}")
        
        # Receive response
        response = await self.websocket.recv()
        response_data = json.loads(response)
        
        logger.info(f"Received response: {response_data.get('status')}")
        
        return response_data
    
    async def run_test(self, test_name: str, command_type: str, args: Dict[str, Any], expected_status: str = "success"):
        """
        Run single test
        
        Args:
            test_name: Test name
            command_type: Command type
            args: Command arguments
            expected_status: Expected status
        """
        self.test_results["total"] += 1
        
        try:
            # Send command
            response = await self.send_command(command_type, args)
            
            # Check response status
            actual_status = response.get("status")
            
            if actual_status == expected_status:
                logger.info(f"Test passed: {test_name}")
                self.test_results["passed"] += 1
                result = "passed"
            else:
                logger.error(f"Test failed: {test_name}, expected status: {expected_status}, actual status: {actual_status}")
                self.test_results["failed"] += 1
                result = "failed"
            
            # Record test details
            self.test_results["details"].append({
                "name": test_name,
                "command_type": command_type,
                "args": args,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "result": result,
                "response": response
            })
            
        except Exception as e:
            logger.exception(f"Test error: {test_name}, error: {str(e)}")
            self.test_results["failed"] += 1
            
            # Record test details
            self.test_results["details"].append({
                "name": test_name,
                "command_type": command_type,
                "args": args,
                "expected_status": expected_status,
                "actual_status": "error",
                "result": "failed",
                "error": str(e)
            })
    
    async def run_all_tests(self):
        """Run all tests"""
        try:
            # Connect to MCP server
            if not await self.connect():
                logger.error("Unable to connect to MCP server, tests aborted")
                return
            
            # Run sketch tool tests
            await self.run_sketch_tool_tests()
            
            # Run modeling tool tests
            await self.run_modeling_tool_tests()
            
            # Run assembly tool tests
            await self.run_assembly_tool_tests()
            
            # Run parametric tool tests
            await self.run_parametric_tool_tests()
            
            # Run file tool tests
            await self.run_file_tool_tests()
            
            # Run analysis tool tests
            await self.run_analysis_tool_tests()
            
            # Run natural language tests
            await self.run_natural_language_tests()
            
            # Disconnect
            await self.disconnect()
            
            # Output test results summary
            self.print_test_summary()
            
        except Exception as e:
            logger.exception(f"Error running tests: {str(e)}")
            
            # Try to disconnect
            await self.disconnect()
    
    async def run_sketch_tool_tests(self):
        """Run sketch tool tests"""
        logger.info("Starting sketch tool tests")
        
        # Test create sketch
        await self.run_test(
            "Create sketch",
            "sketch.create_sketch",
            {"plane": "XY"}
        )
        
        # Test create line
        await self.run_test(
            "Create line",
            "sketch.create_line",
            {"start_point": [0, 0, 0], "end_point": [10, 10, 0]}
        )
        
        # Test create circle
        await self.run_test(
            "Create circle",
            "sketch.create_circle",
            {"center_point": [0, 0, 0], "radius": 5.0}
        )
        
        # Test create rectangle
        await self.run_test(
            "Create rectangle",
            "sketch.create_rectangle",
            {"corner_point": [0, 0, 0], "width": 10.0, "height": 5.0}
        )
        
        logger.info("Sketch tool tests complete")
    
    async def run_modeling_tool_tests(self):
        """Run modeling tool tests"""
        logger.info("Starting modeling tool tests")
        
        # Test extrude feature
        await self.run_test(
            "Create extrude feature",
            "modeling.extrude",
            {
                "profile_ids": ["profile1"],
                "operation": "new_body",
                "extent_type": "distance",
                "extent_value": 10.0,
                "direction": "positive"
            }
        )
        
        # Test revolve feature
        await self.run_test(
            "Create revolve feature",
            "modeling.revolve",
            {
                "profile_ids": ["profile1"],
                "operation": "new_body",
                "angle": 360.0,
                "axis_origin": [0, 0, 0],
                "axis_direction": [0, 0, 1]
            }
        )
        
        # Test fillet feature
        await self.run_test(
            "Create fillet feature",
            "modeling.fillet",
            {"edge_ids": ["edge1", "edge2"], "radius": 2.0}
        )
        
        logger.info("Modeling tool tests complete")
    
    async def run_assembly_tool_tests(self):
        """Run assembly tool tests"""
        logger.info("Starting assembly tool tests")
        
        # Test create component
        await self.run_test(
            "Create component",
            "assembly.create_component",
            {"name": "Test component", "is_active": True}
        )
        
        # Test add component instance
        await self.run_test(
            "Add component instance",
            "assembly.add_component_instance",
            {
                "component_id": "component1",
                "position": [0, 0, 0],
                "rotation": [0, 0, 0]
            }
        )
        
        # Test add rigid constraint
        await self.run_test(
            "Add rigid constraint",
            "assembly.add_rigid_joint",
            {
                "component1_id": "component1",
                "component2_id": "component2",
                "offset": [0, 0, 0]
            }
        )
        
        logger.info("Assembly tool tests complete")
    
    async def run_parametric_tool_tests(self):
        """Run parametric tool tests"""
        logger.info("Starting parametric tool tests")
        
        # Test create user parameter
        await self.run_test(
            "Create user parameter",
            "parametric.create_user_parameter",
            {"name": "width", "value": 10.0, "unit": "mm", "comment": "Width parameter"}
        )
        
        # Test modify user parameter
        await self.run_test(
            "Modify user parameter",
            "parametric.modify_user_parameter",
            {"name": "width", "value": 15.0}
        )
        
        # Test create equation
        await self.run_test(
            "Create equation",
            "parametric.create_equation",
            {"target_parameter": "height", "equation": "width * 2"}
        )
        
        logger.info("Parametric tool tests complete")
    
    async def run_file_tool_tests(self):
        """Run file tool tests"""
        logger.info("Starting file tool tests")
        
        # Test save model
        await self.run_test(
            "Save model",
            "file.save_model",
            {"filename": "test_model", "format": "f3d"}
        )
        
        # Test export model
        await self.run_test(
            "Export model",
            "file.export_model",
            {"filename": "test_export", "format": "step", "options": {}}
        )
        
        # Test create new document
        await self.run_test(
            "Create new document",
            "file.create_new_document",
            {"document_type": "design"}
        )
        
        logger.info("File tool tests complete")
    
    async def run_analysis_tool_tests(self):
        """Run analysis tool tests"""
        logger.info("Starting analysis tool tests")
        
        # Test analyze mass properties
        await self.run_test(
            "Analyze mass properties",
            "analysis.analyze_mass_properties",
            {"body_ids": ["body1", "body2"]}
        )
        
        # Test analyze bounding box
        await self.run_test(
            "Analyze bounding box",
            "analysis.analyze_bounding_box",
            {"body_ids": ["body1"]}
        )
        
        # Test check interference
        await self.run_test(
            "Check interference",
            "analysis.check_interference",
            {"body_ids": ["body1", "body2"]}
        )
        
        logger.info("Analysis tool tests complete")
    
    async def run_natural_language_tests(self):
        """Run natural language tests"""
        logger.info("Starting natural language tests")
        
        # Test simple natural language command
        await self.run_test(
            "Natural language - Create simple part",
            "natural_language.process",
            {"text": "Create a 10mm x 20mm x 5mm rectangular box"}
        )
        
        # Test complex natural language command
        await self.run_test(
            "Natural language - Create complex part",
            "natural_language.process",
            {"text": "Create a cylinder with diameter 30mm and height 50mm, and add a 5mm fillet at the top"}
        )
        
        # Test assembly natural language command
        await self.run_test(
            "Natural language - Create assembly",
            "natural_language.process",
            {"text": "Create a simple assembly consisting of a shaft and bearing, shaft diameter 10mm, bearing inner diameter 10mm, outer diameter 20mm"}
        )
        
        logger.info("Natural language tests complete")
    
    def print_test_summary(self):
        """Print test results summary"""
        logger.info("=" * 50)
        logger.info("Test Results Summary")
        logger.info("=" * 50)
        logger.info(f"Total tests: {self.test_results['total']}")
        logger.info(f"Passed tests: {self.test_results['passed']}")
        logger.info(f"Failed tests: {self.test_results['failed']}")
        logger.info(f"Pass rate: {self.test_results['passed'] / self.test_results['total'] * 100:.2f}%")
        logger.info("=" * 50)
        
        # Output failed test details
        if self.test_results["failed"] > 0:
            logger.info("Failed test details:")
            for detail in self.test_results["details"]:
                if detail["result"] == "failed":
                    logger.info(f"- {detail['name']}")
                    logger.info(f"  Command type: {detail['command_type']}")
                    logger.info(f"  Arguments: {detail['args']}")
                    logger.info(f"  Expected status: {detail['expected_status']}")
                    logger.info(f"  Actual status: {detail['actual_status']}")
                    if "error" in detail:
                        logger.info(f"  Error: {detail['error']}")
                    logger.info("-" * 30)
        
        # Save test results to file
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Test results saved to: test_results.json")

async def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fusion360 MCP Server Integration Test')
    parser.add_argument('--url', default='ws://localhost:8080', help='MCP server WebSocket URL')
    
    args = parser.parse_args()
    
    # Create integration test instance
    test = IntegrationTest(args.url)
    
    # Run all tests
    await test.run_all_tests()

if __name__ == "__main__":
    # Run main function
    asyncio.run(main())
