#!/usr/bin/env python3
"""
Fusion360 Plugin Communication Client

Responsible for Socket communication with plugin running inside Fusion360
"""

import socket
import json
import time
from typing import Dict, Any, Optional
from ..core.config import logger


class Fusion360PluginClient:
    """Fusion360 Plugin Communication Client
    
    Communicates with Fusion360 plugin via Socket, sends commands and receives responses
    """
    
    def __init__(self, host='localhost', port=8765, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to Fusion360 plugin
        
        Returns:
            bool: Whether connection succeeded
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))
            self._connected = True
            logger.info(f"Connected to Fusion360 plugin {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Fusion360 plugin: {e}")
            self._connected = False
            return False
    
    def disconnect(self):
        """Disconnect"""
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
        self._connected = False
        logger.info("Disconnected from Fusion360 plugin")
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected and self._socket is not None
    
    def send_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send command to Fusion360 plugin
        
        Args:
            command: Command name
            params: Command parameters
            
        Returns:
            Dict[str, Any]: Plugin response
        """
        if not self.is_connected():
            if not self.connect():
                return {"error": "Unable to connect to Fusion360 plugin"}
        
        request = {
            "command": command,
            "params": params or {}
        }
        
        try:
            # Send request
            request_data = json.dumps(request).encode('utf-8')
            self._socket.send(request_data)
            
            # Receive response
            response_data = self._socket.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            self.disconnect()
            return {"error": f"Communication error: {str(e)}"}
    
    def get_design_info(self) -> Dict[str, Any]:
        """Get design information"""
        return self.send_command("get_design_info")
    
    def get_component_hierarchy(self) -> Dict[str, Any]:
        """Get component hierarchy"""
        return self.send_command("get_component_hierarchy")
    
    def create_sketch(self, name: str = None, plane: str = "XY") -> Dict[str, Any]:
        """Create sketch"""
        params = {"plane": plane}
        if name:
            params["name"] = name
        return self.send_command("create_sketch", params)
    
    def create_rectangle(self, sketch_name: str, width: float = 10.0, height: float = 10.0, 
                        center_x: float = 0.0, center_y: float = 0.0) -> Dict[str, Any]:
        """Create rectangle in sketch"""
        params = {
            "sketch_name": sketch_name,
            "width": width,
            "height": height,
            "center_x": center_x,
            "center_y": center_y
        }
        return self.send_command("create_rectangle", params)
    
    def create_circle(self, sketch_name: str, radius: float = 5.0, 
                     center_x: float = 0.0, center_y: float = 0.0) -> Dict[str, Any]:
        """Create circle in sketch"""
        params = {
            "sketch_name": sketch_name,
            "radius": radius,
            "center_x": center_x,
            "center_y": center_y
        }
        return self.send_command("create_circle", params)
    
    def create_extrude(self, sketch_name: str, distance: float = 10.0, 
                      operation: str = "new") -> Dict[str, Any]:
        """Create extrude feature"""
        params = {
            "sketch_name": sketch_name,
            "distance": distance,
            "operation": operation
        }
        return self.send_command("create_extrude", params)
    
    def get_sketches(self) -> Dict[str, Any]:
        """Get all sketches information"""
        return self.send_command("get_sketches")
    
    def get_features(self) -> Dict[str, Any]:
        """Get all features information"""
        return self.send_command("get_features")
    
    def test_connection(self) -> bool:
        """Test if connection is working"""
        try:
            result = self.get_design_info()
            return "error" not in result or "No active product" in result.get("error", "")
        except:
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
