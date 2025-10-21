"""
Fusion360 MCP Server - Cross-Platform Compatibility Test Script

This script verifies MCP server compatibility on Windows and macOS platforms.
"""

import os
import sys
import platform
import logging
import argparse
import json
import subprocess
import asyncio
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
        logging.FileHandler('platform_compatibility_test.log')
    ]
)

logger = logging.getLogger("platform_compatibility_test")

class PlatformCompatibilityTest:
    """Cross-platform compatibility test class"""
    
    def __init__(self):
        """Initialize cross-platform compatibility test"""
        self.system = platform.system()
        self.test_results = {
            "platform": self.system,
            "python_version": platform.python_version(),
            "tests": {
                "environment_check": {"status": "pending"},
                "server_start": {"status": "pending"},
                "addin_installation": {"status": "pending"},
                "websocket_connection": {"status": "pending"},
                "basic_functionality": {"status": "pending"}
            }
        }
    
    async def run_all_tests(self):
        """Run all tests"""
        try:
            logger.info(f"Starting compatibility tests on {self.system} platform")
            
            # Check environment
            await self.check_environment()
            
            # Test server startup
            await self.test_server_start()
            
            # Test plugin installation
            await self.test_addin_installation()
            
            # Test WebSocket connection
            await self.test_websocket_connection()
            
            # Test basic functionality
            await self.test_basic_functionality()
            
            # Output test results summary
            self.print_test_summary()
            
        except Exception as e:
            logger.exception(f"Error running tests: {str(e)}")
    
    async def check_environment(self):
        """Check environment"""
        try:
            logger.info("Checking environment...")
            
            # Check Python version
            python_version = platform.python_version_tuple()
            python_version_ok = int(python_version[0]) >= 3 and int(python_version[1]) >= 8
            
            # Check necessary Python packages
            required_packages = ["websockets", "asyncio", "pydantic", "fastapi", "uvicorn"]
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            # Check Fusion360 installation
            fusion360_installed = False
            
            if self.system == "Windows":
                fusion360_paths = [
                    os.path.join(os.environ.get("ProgramFiles", ""), "Autodesk", "Fusion 360"),
                    os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Autodesk", "Fusion 360")
                ]
                for path in fusion360_paths:
                    if os.path.exists(path):
                        fusion360_installed = True
                        break
            elif self.system == "Darwin":  # macOS
                fusion360_path = "/Applications/Autodesk Fusion 360.app"
                if os.path.exists(fusion360_path):
                    fusion360_installed = True
            
            # Update test results
            self.test_results["tests"]["environment_check"] = {
                "status": "passed" if python_version_ok and not missing_packages else "failed",
                "details": {
                    "python_version_ok": python_version_ok,
                    "python_version": ".".join(python_version),
                    "missing_packages": missing_packages,
                    "fusion360_installed": fusion360_installed
                }
            }
            
            if python_version_ok and not missing_packages:
                logger.info("Environment check passed")
            else:
                logger.warning("Environment check failed")
                if not python_version_ok:
                    logger.warning(f"Python version does not meet requirements: {'.'.join(python_version)}, requires >= 3.8")
                if missing_packages:
                    logger.warning(f"Missing necessary Python packages: {', '.join(missing_packages)}")
            
            if not fusion360_installed:
                logger.warning("Fusion360 installation not detected")
            
        except Exception as e:
            logger.exception(f"Error checking environment: {str(e)}")
            self.test_results["tests"]["environment_check"] = {
                "status": "error",
                "error": str(e)
            }
    
    async def test_server_start(self):
        """Test server startup"""
        try:
            logger.info("Testing server startup...")
            
            # Get project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Build startup command
            server_script = os.path.join(project_root, "run_server.py")
            
            # Start server using subprocess
            process = subprocess.Popen(
                [sys.executable, server_script, "--host", "localhost", "--port", "8080", "--debug"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                server_started = True
                logger.info("Server started successfully")
            else:
                server_started = False
                stdout, stderr = process.communicate()
                logger.error(f"Server startup failed: {stderr}")
            
            # Update test results
            self.test_results["tests"]["server_start"] = {
                "status": "passed" if server_started else "failed",
                "details": {
                    "server_started": server_started
                }
            }
            
            # Terminate server process
            if server_started:
                process.terminate()
                process.wait()
                logger.info("Server process terminated")
            
        except Exception as e:
            logger.exception(f"Error testing server startup: {str(e)}")
            self.test_results["tests"]["server_start"] = {
                "status": "error",
                "error": str(e)
            }
    
    async def test_addin_installation(self):
        """Test plugin installation"""
        try:
            logger.info("Testing plugin installation...")
            
            # Get project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Build installation command
            install_script = os.path.join(project_root, "install_addin.py")
            
            # Run installation script using subprocess
            process = subprocess.Popen(
                [sys.executable, install_script, "--name", "Fusion360MCPAddinTest"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for installation to complete
            stdout, stderr = process.communicate()
            
            # Check installation result
            if process.returncode == 0:
                installation_success = True
                logger.info("Plugin installed successfully")
            else:
                installation_success = False
                logger.error(f"Plugin installation failed: {stderr}")
            
            # Check if plugin directory exists
            addin_path = None
            if self.system == "Windows":
                home_dir = os.path.expanduser("~")
                addin_path = os.path.join(home_dir, "AppData", "Roaming", "Autodesk", "Autodesk Fusion 360", "API", "AddIns", "Fusion360MCPAddinTest")
            elif self.system == "Darwin":  # macOS
                home_dir = os.path.expanduser("~")
                addin_path = os.path.join(home_dir, "Library", "Application Support", "Autodesk", "Autodesk Fusion 360", "API", "AddIns", "Fusion360MCPAddinTest")
            
            addin_exists = addin_path and os.path.exists(addin_path)
            
            # Update test results
            self.test_results["tests"]["addin_installation"] = {
                "status": "passed" if installation_success and addin_exists else "failed",
                "details": {
                    "installation_success": installation_success,
                    "addin_exists": addin_exists,
                    "addin_path": addin_path
                }
            }
            
        except Exception as e:
            logger.exception(f"Error testing plugin installation: {str(e)}")
            self.test_results["tests"]["addin_installation"] = {
                "status": "error",
                "error": str(e)
            }
    
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        try:
            logger.info("Testing WebSocket connection...")
            
            # Get project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Build startup command
            server_script = os.path.join(project_root, "run_server.py")
            
            # Start server using subprocess
            process = subprocess.Popen(
                [sys.executable, server_script, "--host", "localhost", "--port", "8080", "--debug"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Try to connect to WebSocket server
            connection_success = False
            try:
                websocket = await websockets.connect("ws://localhost:8080")
                connection_success = True
                logger.info("Successfully connected to WebSocket server")
                
                # Send simple ping message
                await websocket.send(json.dumps({
                    "id": str(uuid.uuid4()),
                    "type": "ping",
                    "args": {}
                }))
                
                # Receive response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                # Close connection
                await websocket.close()
                
            except Exception as conn_error:
                logger.error(f"Error connecting to WebSocket server: {str(conn_error)}")
            
            # Update test results
            self.test_results["tests"]["websocket_connection"] = {
                "status": "passed" if connection_success else "failed",
                "details": {
                    "connection_success": connection_success
                }
            }
            
            # Terminate server process
            process.terminate()
            process.wait()
            logger.info("Server process terminated")
            
        except Exception as e:
            logger.exception(f"Error testing WebSocket connection: {str(e)}")
            self.test_results["tests"]["websocket_connection"] = {
                "status": "error",
                "error": str(e)
            }
            
            # Ensure server process is terminated
            if 'process' in locals():
                process.terminate()
                process.wait()
    
    async def test_basic_functionality(self):
        """Test basic functionality"""
        try:
            logger.info("Testing basic functionality...")
            
            # Get project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Build startup command
            server_script = os.path.join(project_root, "run_server.py")
            
            # Start server using subprocess
            process = subprocess.Popen(
                [sys.executable, server_script, "--host", "localhost", "--port", "8080", "--debug"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Test basic functionality
            functionality_results = {}
            
            try:
                # Connect to WebSocket server
                websocket = await websockets.connect("ws://localhost:8080")
                
                # Test sketch creation
                await websocket.send(json.dumps({
                    "id": str(uuid.uuid4()),
                    "type": "sketch.create_sketch",
                    "args": {"plane": "XY"}
                }))
                sketch_response = await asyncio.wait_for(websocket.recv(), timeout=5)
                sketch_data = json.loads(sketch_response)
                functionality_results["sketch_creation"] = sketch_data.get("status") == "success"
                
                # Test line creation
                await websocket.send(json.dumps({
                    "id": str(uuid.uuid4()),
                    "type": "sketch.create_line",
                    "args": {"start_point": [0, 0, 0], "end_point": [10, 10, 0]}
                }))
                line_response = await asyncio.wait_for(websocket.recv(), timeout=5)
                line_data = json.loads(line_response)
                functionality_results["line_creation"] = line_data.get("status") == "success"
                
                # Test extrude feature
                await websocket.send(json.dumps({
                    "id": str(uuid.uuid4()),
                    "type": "modeling.extrude",
                    "args": {
                        "profile_ids": ["profile1"],
                        "operation": "new_body",
                        "extent_type": "distance",
                        "extent_value": 10.0,
                        "direction": "positive"
                    }
                }))
                extrude_response = await asyncio.wait_for(websocket.recv(), timeout=5)
                extrude_data = json.loads(extrude_response)
                functionality_results["extrude_creation"] = extrude_data.get("status") == "success"
                
                # Close connection
                await websocket.close()
                
            except Exception as func_error:
                logger.error(f"Error testing basic functionality: {str(func_error)}")
            
            # Update test results
            all_passed = all(functionality_results.values()) if functionality_results else False
            self.test_results["tests"]["basic_functionality"] = {
                "status": "passed" if all_passed else "failed",
                "details": functionality_results
            }
            
            # Terminate server process
            process.terminate()
            process.wait()
            logger.info("Server process terminated")
            
        except Exception as e:
            logger.exception(f"Error testing basic functionality: {str(e)}")
            self.test_results["tests"]["basic_functionality"] = {
                "status": "error",
                "error": str(e)
            }
            
            # Ensure server process is terminated
            if 'process' in locals():
                process.terminate()
                process.wait()
    
    def print_test_summary(self):
        """Print test results summary"""
        logger.info("=" * 50)
        logger.info(f"{self.system} Platform Compatibility Test Results Summary")
        logger.info("=" * 50)
        
        all_passed = True
        for test_name, test_result in self.test_results["tests"].items():
            status = test_result["status"]
            logger.info(f"{test_name}: {status}")
            if status != "passed":
                all_passed = False
        
        logger.info("=" * 50)
        logger.info(f"Overall result: {'Passed' if all_passed else 'Failed'}")
        logger.info("=" * 50)
        
        # Save test results to file
        result_filename = f"platform_compatibility_test_{self.system.lower()}.json"
        with open(result_filename, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Test results saved to: {result_filename}")

async def main():
    """Main function"""
    # Create cross-platform compatibility test instance
    test = PlatformCompatibilityTest()
    
    # Run all tests
    await test.run_all_tests()

if __name__ == "__main__":
    # Run main function
    asyncio.run(main())
