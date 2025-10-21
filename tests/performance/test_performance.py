"""
Fusion360 MCP Server - Performance Test Script

This script tests the performance of the MCP server under different loads.
"""

import os
import sys
import time
import logging
import argparse
import json
import asyncio
import websockets
import uuid
import statistics
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('performance_test.log')
    ]
)

logger = logging.getLogger("performance_test")

class PerformanceTest:
    """Performance test class"""
    
    def __init__(self, server_url: str):
        """
        Initialize performance test
        
        Args:
            server_url: MCP server WebSocket URL
        """
        self.server_url = server_url
        self.test_results = {
            "latency_tests": {},
            "throughput_tests": {},
            "concurrency_tests": {},
            "stability_tests": {}
        }
    
    async def connect(self):
        """Connect to MCP server"""
        try:
            websocket = await websockets.connect(self.server_url)
            return websocket
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {str(e)}")
            return None
    
    async def send_command(self, websocket, command_type: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send command to MCP server
        
        Args:
            websocket: WebSocket connection
            command_type: Command type
            args: Command arguments
            
        Returns:
            Command execution result and response time
        """
        # Generate command ID
        command_id = str(uuid.uuid4())
        
        # Construct command message
        message = {
            "id": command_id,
            "type": command_type,
            "args": args
        }
        
        # Record start time
        start_time = time.time()
        
        # Send command
        await websocket.send(json.dumps(message))
        
        # Receive response
        response = await websocket.recv()
        
        # Record end time
        end_time = time.time()
        
        # Calculate response time (milliseconds)
        response_time = (end_time - start_time) * 1000
        
        # Parse response
        response_data = json.loads(response)
        
        return {
            "response": response_data,
            "response_time": response_time
        }
    
    async def test_latency(self, command_type: str, args: Dict[str, Any], iterations: int = 10):
        """
        Test command latency
        
        Args:
            command_type: Command type
            args: Command arguments
            iterations: Number of iterations
        """
        logger.info(f"Starting latency test: {command_type}, iterations: {iterations}")
        
        # Connect to MCP server
        websocket = await self.connect()
        if not websocket:
            logger.error("Unable to connect to MCP server, test aborted")
            return
        
        try:
            # Execute commands multiple times and record response times
            response_times = []
            
            for i in range(iterations):
                result = await self.send_command(websocket, command_type, args)
                response_times.append(result["response_time"])
                logger.info(f"Iteration {i+1}/{iterations}: response time = {result['response_time']:.2f} ms")
            
            # Calculate statistics
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            median_response_time = statistics.median(response_times)
            stdev_response_time = statistics.stdev(response_times) if len(response_times) > 1 else 0
            
            # Record test results
            self.test_results["latency_tests"][command_type] = {
                "iterations": iterations,
                "avg_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time,
                "median_response_time": median_response_time,
                "stdev_response_time": stdev_response_time,
                "all_response_times": response_times
            }
            
            logger.info(f"Latency test complete: {command_type}")
            logger.info(f"Average response time: {avg_response_time:.2f} ms")
            logger.info(f"Min response time: {min_response_time:.2f} ms")
            logger.info(f"Max response time: {max_response_time:.2f} ms")
            logger.info(f"Median response time: {median_response_time:.2f} ms")
            logger.info(f"Standard deviation: {stdev_response_time:.2f} ms")
            
        except Exception as e:
            logger.exception(f"Error during latency test: {str(e)}")
        finally:
            # Close connection
            await websocket.close()
    
    async def test_throughput(self, command_type: str, args: Dict[str, Any], duration: int = 10):
        """
        Test command throughput
        
        Args:
            command_type: Command type
            args: Command arguments
            duration: Test duration (seconds)
        """
        logger.info(f"Starting throughput test: {command_type}, duration: {duration}s")
        
        # Connect to MCP server
        websocket = await self.connect()
        if not websocket:
            logger.error("Unable to connect to MCP server, test aborted")
            return
        
        try:
            # Record start time
            start_time = time.time()
            end_time = start_time + duration
            
            # Execute commands until duration is reached
            command_count = 0
            response_times = []
            
            while time.time() < end_time:
                result = await self.send_command(websocket, command_type, args)
                response_times.append(result["response_time"])
                command_count += 1
            
            # Calculate actual duration
            actual_duration = time.time() - start_time
            
            # Calculate throughput (commands per second)
            throughput = command_count / actual_duration
            
            # Calculate statistics
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            # Record test results
            self.test_results["throughput_tests"][command_type] = {
                "duration": actual_duration,
                "command_count": command_count,
                "throughput": throughput,
                "avg_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time
            }
            
            logger.info(f"Throughput test complete: {command_type}")
            logger.info(f"Command count: {command_count}")
            logger.info(f"Throughput: {throughput:.2f} commands/s")
            logger.info(f"Average response time: {avg_response_time:.2f} ms")
            
        except Exception as e:
            logger.exception(f"Error during throughput test: {str(e)}")
        finally:
            # Close connection
            await websocket.close()
    
    async def test_concurrency(self, command_type: str, args: Dict[str, Any], concurrent_clients: int = 5, commands_per_client: int = 10):
        """
        Test concurrency performance
        
        Args:
            command_type: Command type
            args: Command arguments
            concurrent_clients: Number of concurrent clients
            commands_per_client: Number of commands per client
        """
        logger.info(f"Starting concurrency test: {command_type}, concurrent clients: {concurrent_clients}, commands per client: {commands_per_client}")
        
        async def client_task(client_id):
            """Single client task"""
            # Connect to MCP server
            websocket = await self.connect()
            if not websocket:
                logger.error(f"Client {client_id}: Unable to connect to MCP server")
                return []
            
            try:
                # Execute commands multiple times and record response times
                response_times = []
                
                for i in range(commands_per_client):
                    result = await self.send_command(websocket, command_type, args)
                    response_times.append(result["response_time"])
                    logger.debug(f"Client {client_id}, command {i+1}/{commands_per_client}: response time = {result['response_time']:.2f} ms")
                
                return response_times
                
            except Exception as e:
                logger.exception(f"Client {client_id} error executing task: {str(e)}")
                return []
            finally:
                # Close connection
                await websocket.close()
        
        try:
            # Create concurrent client tasks
            tasks = [client_task(i) for i in range(concurrent_clients)]
            
            # Record start time
            start_time = time.time()
            
            # Wait for all tasks to complete
            all_response_times = await asyncio.gather(*tasks)
            
            # Record end time
            end_time = time.time()
            
            # Calculate total duration
            total_duration = end_time - start_time
            
            # Merge all response times
            all_times = [time for client_times in all_response_times for time in client_times]
            
            # Calculate statistics
            total_commands = len(all_times)
            throughput = total_commands / total_duration
            avg_response_time = statistics.mean(all_times) if all_times else 0
            min_response_time = min(all_times) if all_times else 0
            max_response_time = max(all_times) if all_times else 0
            
            # Record test results
            self.test_results["concurrency_tests"][command_type] = {
                "concurrent_clients": concurrent_clients,
                "commands_per_client": commands_per_client,
                "total_commands": total_commands,
                "total_duration": total_duration,
                "throughput": throughput,
                "avg_response_time": avg_response_time,
                "min_response_time": min_response_time,
                "max_response_time": max_response_time
            }
            
            logger.info(f"Concurrency test complete: {command_type}")
            logger.info(f"Total commands: {total_commands}")
            logger.info(f"Total duration: {total_duration:.2f} s")
            logger.info(f"Throughput: {throughput:.2f} commands/s")
            logger.info(f"Average response time: {avg_response_time:.2f} ms")
            
        except Exception as e:
            logger.exception(f"Error during concurrency test: {str(e)}")
    
    async def test_stability(self, command_type: str, args: Dict[str, Any], duration: int = 60, interval: float = 1.0):
        """
        Test stability
        
        Args:
            command_type: Command type
            args: Command arguments
            duration: Test duration (seconds)
            interval: Command interval time (seconds)
        """
        logger.info(f"Starting stability test: {command_type}, duration: {duration}s, interval: {interval}s")
        
        # Connect to MCP server
        websocket = await self.connect()
        if not websocket:
            logger.error("Unable to connect to MCP server, test aborted")
            return
        
        try:
            # Record start time
            start_time = time.time()
            end_time = start_time + duration
            
            # Execute commands until duration is reached
            command_count = 0
            error_count = 0
            response_times = []
            
            while time.time() < end_time:
                try:
                    result = await self.send_command(websocket, command_type, args)
                    response_times.append(result["response_time"])
                    command_count += 1
                    
                    # Check response status
                    if result["response"].get("status") != "success":
                        error_count += 1
                        logger.warning(f"Command execution failed: {result['response']}")
                    
                    # Wait for interval time
                    await asyncio.sleep(interval)
                    
                except Exception as cmd_error:
                    error_count += 1
                    logger.error(f"Error executing command: {str(cmd_error)}")
                    
                    # Try to reconnect
                    try:
                        await websocket.close()
                        websocket = await self.connect()
                        if not websocket:
                            logger.error("Unable to reconnect to MCP server, test aborted")
                            break
                    except:
                        logger.exception("Error during reconnection")
                        break
            
            # Calculate actual duration
            actual_duration = time.time() - start_time
            
            # Calculate statistics
            success_rate = (command_count - error_count) / command_count if command_count > 0 else 0
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            # Record test results
            self.test_results["stability_tests"][command_type] = {
                "duration": actual_duration,
                "command_count": command_count,
                "error_count": error_count,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time
            }
            
            logger.info(f"Stability test complete: {command_type}")
            logger.info(f"Command count: {command_count}")
            logger.info(f"Error count: {error_count}")
            logger.info(f"Success rate: {success_rate * 100:.2f}%")
            logger.info(f"Average response time: {avg_response_time:.2f} ms")
            
        except Exception as e:
            logger.exception(f"Error during stability test: {str(e)}")
        finally:
            # Close connection
            await websocket.close()
    
    async def run_all_tests(self):
        """Run all performance tests"""
        try:
            logger.info("Starting performance tests")
            
            # Test sketch command latency
            await self.test_latency(
                "sketch.create_circle",
                {"center_point": [0, 0, 0], "radius": 5.0},
                iterations=20
            )
            
            # Test modeling command latency
            await self.test_latency(
                "modeling.extrude",
                {
                    "profile_ids": ["profile1"],
                    "operation": "new_body",
                    "extent_type": "distance",
                    "extent_value": 10.0,
                    "direction": "positive"
                },
                iterations=20
            )
            
            # Test sketch command throughput
            await self.test_throughput(
                "sketch.create_line",
                {"start_point": [0, 0, 0], "end_point": [10, 10, 0]},
                duration=10
            )
            
            # Test concurrency performance
            await self.test_concurrency(
                "sketch.create_rectangle",
                {"corner_point": [0, 0, 0], "width": 10.0, "height": 5.0},
                concurrent_clients=5,
                commands_per_client=10
            )
            
            # Test stability
            await self.test_stability(
                "sketch.create_circle",
                {"center_point": [0, 0, 0], "radius": 5.0},
                duration=30,
                interval=1.0
            )
            
            # Save test results
            self.save_test_results()
            
            logger.info("Performance tests complete")
            
        except Exception as e:
            logger.exception(f"Error running performance tests: {str(e)}")
    
    def save_test_results(self):
        """Save test results to file"""
        try:
            # Save test results to JSON file
            with open("performance_test_results.json", "w") as f:
                json.dump(self.test_results, f, indent=2)
            
            logger.info("Test results saved to: performance_test_results.json")
            
            # Generate test report
            self.generate_test_report()
            
        except Exception as e:
            logger.exception(f"Error saving test results: {str(e)}")
    
    def generate_test_report(self):
        """Generate test report"""
        try:
            # Create HTML report
            html_report = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Fusion360 MCP Server Performance Test Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    h2 { color: #666; margin-top: 30px; }
                    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                </style>
            </head>
            <body>
                <h1>Fusion360 MCP Server Performance Test Report</h1>
                <p>Test time: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """</p>
            """
            
            # Add latency test results
            html_report += """
                <h2>Latency Test Results</h2>
                <table>
                    <tr>
                        <th>Command Type</th>
                        <th>Iterations</th>
                        <th>Avg Response Time (ms)</th>
                        <th>Min Response Time (ms)</th>
                        <th>Max Response Time (ms)</th>
                        <th>Median Response Time (ms)</th>
                        <th>Std Dev (ms)</th>
                    </tr>
            """
            
            for command_type, result in self.test_results["latency_tests"].items():
                html_report += f"""
                    <tr>
                        <td>{command_type}</td>
                        <td>{result["iterations"]}</td>
                        <td>{result["avg_response_time"]:.2f}</td>
                        <td>{result["min_response_time"]:.2f}</td>
                        <td>{result["max_response_time"]:.2f}</td>
                        <td>{result["median_response_time"]:.2f}</td>
                        <td>{result["stdev_response_time"]:.2f}</td>
                    </tr>
                """
            
            html_report += """
                </table>
            """
            
            # Add throughput test results
            html_report += """
                <h2>Throughput Test Results</h2>
                <table>
                    <tr>
                        <th>Command Type</th>
                        <th>Duration (s)</th>
                        <th>Command Count</th>
                        <th>Throughput (commands/s)</th>
                        <th>Avg Response Time (ms)</th>
                    </tr>
            """
            
            for command_type, result in self.test_results["throughput_tests"].items():
                html_report += f"""
                    <tr>
                        <td>{command_type}</td>
                        <td>{result["duration"]:.2f}</td>
                        <td>{result["command_count"]}</td>
                        <td>{result["throughput"]:.2f}</td>
                        <td>{result["avg_response_time"]:.2f}</td>
                    </tr>
                """
            
            html_report += """
                </table>
            """
            
            # Add concurrency test results
            html_report += """
                <h2>Concurrency Test Results</h2>
                <table>
                    <tr>
                        <th>Command Type</th>
                        <th>Concurrent Clients</th>
                        <th>Commands Per Client</th>
                        <th>Total Commands</th>
                        <th>Total Duration (s)</th>
                        <th>Throughput (commands/s)</th>
                        <th>Avg Response Time (ms)</th>
                    </tr>
            """
            
            for command_type, result in self.test_results["concurrency_tests"].items():
                html_report += f"""
                    <tr>
                        <td>{command_type}</td>
                        <td>{result["concurrent_clients"]}</td>
                        <td>{result["commands_per_client"]}</td>
                        <td>{result["total_commands"]}</td>
                        <td>{result["total_duration"]:.2f}</td>
                        <td>{result["throughput"]:.2f}</td>
                        <td>{result["avg_response_time"]:.2f}</td>
                    </tr>
                """
            
            html_report += """
                </table>
            """
            
            # Add stability test results
            html_report += """
                <h2>Stability Test Results</h2>
                <table>
                    <tr>
                        <th>Command Type</th>
                        <th>Duration (s)</th>
                        <th>Command Count</th>
                        <th>Error Count</th>
                        <th>Success Rate (%)</th>
                        <th>Avg Response Time (ms)</th>
                    </tr>
            """
            
            for command_type, result in self.test_results["stability_tests"].items():
                html_report += f"""
                    <tr>
                        <td>{command_type}</td>
                        <td>{result["duration"]:.2f}</td>
                        <td>{result["command_count"]}</td>
                        <td>{result["error_count"]}</td>
                        <td>{result["success_rate"] * 100:.2f}</td>
                        <td>{result["avg_response_time"]:.2f}</td>
                    </tr>
                """
            
            html_report += """
                </table>
            </body>
            </html>
            """
            
            # Save HTML report
            with open("performance_test_report.html", "w") as f:
                f.write(html_report)
            
            logger.info("Test report generated: performance_test_report.html")
            
        except Exception as e:
            logger.exception(f"Error generating test report: {str(e)}")

async def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fusion360 MCP Server Performance Test')
    parser.add_argument('--url', default='ws://localhost:8080', help='MCP server WebSocket URL')
    
    args = parser.parse_args()
    
    # Create performance test instance
    test = PerformanceTest(args.url)
    
    # Run all tests
    await test.run_all_tests()

if __name__ == "__main__":
    # Run main function
    asyncio.run(main())
