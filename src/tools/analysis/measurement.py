"""
Measurement Tools

Contains measurement tools for distance, angle, area, volume, mass properties, etc.
"""

from typing import Any, Dict, List, Optional
import logging
import math

# Fusion 360 API import
try:
    import adsk.core
    import adsk.fusion
    FUSION_AVAILABLE = True
except ImportError:
    FUSION_AVAILABLE = False

# Configure logging
logger = logging.getLogger("fusion360-mcp.analysis.measurement")

# Global variables will be set when main module initializes
fusion_bridge = None
context_manager = None
mcp = None

def _log_tool_execution(tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Log tool execution to history"""
    if context_manager:
        context_manager.add_history_entry(
            action_type=tool_name,
            action_description=f"Execute tool: {tool_name}",
            parameters=parameters,
            result=result,
            user_context="MCP tool call"
        )

async def measure_distance(
    point1: List[float],
    point2: List[float],
    measurement_type: str = "linear"
) -> Dict[str, Any]:
    """
    Measure distance between two points
    
    Args:
        point1: First point coordinates [x, y, z]
        point2: Second point coordinates [x, y, z]
        measurement_type: Measurement type (linear, delta_x, delta_y, delta_z)
    """
    parameters = {
        "point1": point1,
        "point2": point2,
        "measurement_type": measurement_type
    }
    
    try:
        # Calculate distance - pure mathematical calculation, doesn't need Fusion 360
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        dz = point2[2] - point1[2]
        
        if measurement_type == "linear":
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
        elif measurement_type == "delta_x":
            distance = abs(dx)
        elif measurement_type == "delta_y":
            distance = abs(dy)
        elif measurement_type == "delta_z":
            distance = abs(dz)
        else:
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
        
        result = {
            "success": True,
            "distance": distance,
            "delta_x": dx,
            "delta_y": dy,
            "delta_z": dz,
            "measurement_type": measurement_type,
            "units": "mm"
        }
        
        _log_tool_execution("measure_distance", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("measure_distance", parameters, result)
        return result

async def measure_angle(
    point1: List[float],
    vertex: List[float],
    point2: List[float]
) -> Dict[str, Any]:
    """
    Measure angle
    
    Args:
        point1: First point coordinates [x, y, z]
        vertex: Vertex coordinates [x, y, z]
        point2: Second point coordinates [x, y, z]
    """
    parameters = {
        "point1": point1,
        "vertex": vertex,
        "point2": point2
    }
    
    try:
        # Calculate angle - pure mathematical calculation, doesn't need Fusion 360
        vec1 = [point1[0] - vertex[0], point1[1] - vertex[1], point1[2] - vertex[2]]
        vec2 = [point2[0] - vertex[0], point2[1] - vertex[1], point2[2] - vertex[2]]
        
        # Calculate vector lengths
        len1 = math.sqrt(vec1[0]**2 + vec1[1]**2 + vec1[2]**2)
        len2 = math.sqrt(vec2[0]**2 + vec2[1]**2 + vec2[2]**2)
        
        if len1 == 0 or len2 == 0:
            result = {"error": "Unable to calculate angle: vector length is zero"}
            _log_tool_execution("measure_angle", parameters, result)
            return result
        
        # Calculate dot product
        dot_product = vec1[0]*vec2[0] + vec1[1]*vec2[1] + vec1[2]*vec2[2]
        
        # Calculate angle
        cos_angle = dot_product / (len1 * len2)
        cos_angle = max(-1, min(1, cos_angle))  # Ensure in [-1, 1] range
        angle_radians = math.acos(cos_angle)
        angle_degrees = math.degrees(angle_radians)
        
        result = {
            "success": True,
            "angle_radians": angle_radians,
            "angle_degrees": angle_degrees,
            "vertex": vertex,
            "vector1_length": len1,
            "vector2_length": len2
        }
        
        _log_tool_execution("measure_angle", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("measure_angle", parameters, result)
        return result

async def measure_area(
    entity_id: str,
    entity_type: str = "face"
) -> Dict[str, Any]:
    """
    Measure area
    
    Args:
        entity_id: Entity ID
        entity_type: Entity type (face, sketch, region)
    """
    parameters = {
        "entity_id": entity_id,
        "entity_type": entity_type
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("measure_area", parameters, result)
        return result
    
    try:
        # Need to find actual face based on entity_id and calculate area
        # Specific entity selection logic needs to be implemented in Fusion 360 environment
        result = {"error": "Area measurement feature requires specific entity selection logic in Fusion 360 environment"}
        _log_tool_execution("measure_area", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("measure_area", parameters, result)
        return result

async def measure_volume(
    body_id: str
) -> Dict[str, Any]:
    """
    Measure volume
    
    Args:
        body_id: Body ID
    """
    parameters = {
        "body_id": body_id
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("measure_volume", parameters, result)
        return result
    
    try:
        # Need to find actual body based on body_id and calculate volume
        # Specific entity selection logic needs to be implemented in Fusion 360 environment
        result = {"error": "Volume measurement feature requires specific entity selection logic in Fusion 360 environment"}
        _log_tool_execution("measure_volume", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("measure_volume", parameters, result)
        return result

async def calculate_mass_properties(
    body_ids: List[str],
    material_density: float = 7.85,  # Steel density g/cm³
    units: str = "metric"
) -> Dict[str, Any]:
    """
    Calculate mass properties
    
    Args:
        body_ids: Body ID list
        material_density: Material density (g/cm³)
        units: Unit system (metric, imperial)
    """
    parameters = {
        "body_ids": body_ids,
        "material_density": material_density,
        "units": units
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("calculate_mass_properties", parameters, result)
        return result
    
    try:
        # Need to find actual bodies based on body_ids and calculate mass properties
        # Specific entity selection logic needs to be implemented in Fusion 360 environment
        result = {"error": "Mass properties calculation feature requires specific entity selection logic in Fusion 360 environment"}
        _log_tool_execution("calculate_mass_properties", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("calculate_mass_properties", parameters, result)
        return result

def register_tools(mcp_instance):
    """Register all measurement tools to MCP server"""
    mcp_instance.tool()(measure_distance)
    mcp_instance.tool()(measure_angle)
    mcp_instance.tool()(measure_area)
    mcp_instance.tool()(measure_volume)
    mcp_instance.tool()(calculate_mass_properties)
