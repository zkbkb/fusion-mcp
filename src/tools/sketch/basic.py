"""
Basic Sketch Tools

Contains basic sketch drawing tools using Fusion360 bridge API
"""

from typing import Any, Dict, List, Optional
import logging

# Fusion 360 API import
try:
    import adsk.core
    import adsk.fusion
    FUSION_AVAILABLE = True
except ImportError:
    FUSION_AVAILABLE = False

# Configure logging
logger = logging.getLogger("fusion360-mcp.sketch.basic")

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

async def create_sketch(
    plane: str = "XY",
    name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create new sketch
    
    Args:
        plane: Sketch plane (XY, XZ, YZ)
        name: Sketch name (optional)
    """
    parameters = {"plane": plane, "name": name}
    
    if not FUSION_AVAILABLE or not fusion_bridge.is_initialized:
        result = {"error": "Fusion 360 not available or bridge not initialized"}
        _log_tool_execution("create_sketch", parameters, result)
        return result
    
    try:
        # Use bridge method
        result = fusion_bridge.create_sketch(name, plane)
        _log_tool_execution("create_sketch", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_sketch", parameters, result)
        return result

async def draw_line(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    sketch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Draw line in sketch
    
    Args:
        start_x: Start point X coordinate
        start_y: Start point Y coordinate
        end_x: End point X coordinate
        end_y: End point Y coordinate
        sketch_name: Target sketch name (if empty, use active sketch)
    """
    parameters = {
        "start_x": start_x, "start_y": start_y,
        "end_x": end_x, "end_y": end_y,
        "sketch_name": sketch_name
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.is_initialized:
        result = {"error": "Fusion 360 not available or bridge not initialized"}
        _log_tool_execution("draw_line", parameters, result)
        return result
    
    try:
        # If no sketch name specified, create a sketch first
        if not sketch_name:
            sketch_result = fusion_bridge.create_sketch()
            if not sketch_result.get("success"):
                result = {"error": f"Failed to create sketch: {sketch_result.get('error', 'unknown error')}"}
                _log_tool_execution("draw_line", parameters, result)
                return result
            sketch_name = sketch_result["sketch_name"]
        
        # Draw line directly using Fusion 360 API
        sketch = fusion_bridge.get_sketch_by_name(sketch_name)
        if not sketch:
            result = {"error": f"Sketch not found: {sketch_name}"}
            _log_tool_execution("draw_line", parameters, result)
            return result
        
        # Create start and end points
        start_point = adsk.core.Point3D.create(start_x, start_y, 0)
        end_point = adsk.core.Point3D.create(end_x, end_y, 0)
        
        # Draw line
        lines = sketch.sketchCurves.sketchLines
        line = lines.addByTwoPoints(start_point, end_point)
        
        result = {
            "success": True,
            "sketch_name": sketch_name,
            "line_id": line.entityToken,
            "start_point": [start_x, start_y],
            "end_point": [end_x, end_y],
            "length": line.length
        }
        
        _log_tool_execution("draw_line", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("draw_line", parameters, result)
        return result

async def draw_circle(
    radius: float,
    center_x: float = 0.0,
    center_y: float = 0.0,
    sketch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Draw circle in sketch
    
    Args:
        radius: Circle radius
        center_x: Center X coordinate
        center_y: Center Y coordinate
        sketch_name: Target sketch name (if empty, use active sketch)
    """
    parameters = {
        "radius": radius, "center_x": center_x,
        "center_y": center_y, "sketch_name": sketch_name
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.is_initialized:
        result = {"error": "Fusion 360 not available or bridge not initialized"}
        _log_tool_execution("draw_circle", parameters, result)
        return result
    
    try:
        # If no sketch name specified, create a sketch first
        if not sketch_name:
            sketch_result = fusion_bridge.create_sketch()
            if not sketch_result.get("success"):
                result = {"error": f"Failed to create sketch: {sketch_result.get('error', 'unknown error')}"}
                _log_tool_execution("draw_circle", parameters, result)
                return result
            sketch_name = sketch_result["sketch_name"]
        
        # Use bridge's circle creation method
        result = fusion_bridge.create_circle(sketch_name, radius, center_x, center_y)
        _log_tool_execution("draw_circle", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("draw_circle", parameters, result)
        return result

async def draw_rectangle(
    width: float,
    height: float,
    center_x: float = 0.0,
    center_y: float = 0.0,
    sketch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Draw rectangle in sketch
    
    Args:
        width: Rectangle width
        height: Rectangle height
        center_x: Center point X coordinate
        center_y: Center point Y coordinate
        sketch_name: Target sketch name (if empty, use active sketch)
    """
    parameters = {
        "width": width, "height": height,
        "center_x": center_x, "center_y": center_y,
        "sketch_name": sketch_name
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.is_initialized:
        result = {"error": "Fusion 360 not available or bridge not initialized"}
        _log_tool_execution("draw_rectangle", parameters, result)
        return result
    
    try:
        # If no sketch name specified, create a sketch first
        if not sketch_name:
            sketch_result = fusion_bridge.create_sketch()
            if not sketch_result.get("success"):
                result = {"error": f"Failed to create sketch: {sketch_result.get('error', 'unknown error')}"}
                _log_tool_execution("draw_rectangle", parameters, result)
                return result
            sketch_name = sketch_result["sketch_name"]
        
        # Use bridge's rectangle creation method
        result = fusion_bridge.create_rectangle(sketch_name, width, height, center_x, center_y)
        _log_tool_execution("draw_rectangle", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("draw_rectangle", parameters, result)
        return result

async def draw_arc(
    center_x: float,
    center_y: float,
    radius: float,
    start_angle: float,
    end_angle: float,
    sketch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Draw arc in sketch
    
    Args:
        center_x: Center X coordinate
        center_y: Center Y coordinate
        radius: Radius
        start_angle: Start angle (radians)
        end_angle: End angle (radians)
        sketch_name: Target sketch name (if empty, use active sketch)
    """
    parameters = {
        "center_x": center_x, "center_y": center_y,
        "radius": radius, "start_angle": start_angle,
        "end_angle": end_angle, "sketch_name": sketch_name
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.is_initialized:
        result = {"error": "Fusion 360 not available or bridge not initialized"}
        _log_tool_execution("draw_arc", parameters, result)
        return result
    
    try:
        # If no sketch name specified, create a sketch first
        if not sketch_name:
            sketch_result = fusion_bridge.create_sketch()
            if not sketch_result.get("success"):
                result = {"error": f"Failed to create sketch: {sketch_result.get('error', 'unknown error')}"}
                _log_tool_execution("draw_arc", parameters, result)
                return result
            sketch_name = sketch_result["sketch_name"]
        
        # Draw arc directly using Fusion 360 API
        sketch = fusion_bridge.get_sketch_by_name(sketch_name)
        if not sketch:
            result = {"error": f"Sketch not found: {sketch_name}"}
            _log_tool_execution("draw_arc", parameters, result)
            return result
        
        import math
        
        # Create center point
        center_point = adsk.core.Point3D.create(center_x, center_y, 0)
        
        # Calculate start and end points
        start_x = center_x + radius * math.cos(start_angle)
        start_y = center_y + radius * math.sin(start_angle)
        end_x = center_x + radius * math.cos(end_angle)
        end_y = center_y + radius * math.sin(end_angle)
        
        start_point = adsk.core.Point3D.create(start_x, start_y, 0)
        end_point = adsk.core.Point3D.create(end_x, end_y, 0)
        
        # Draw arc
        arcs = sketch.sketchCurves.sketchArcs
        arc = arcs.addByCenterStartEnd(center_point, start_point, end_point)
        
        result = {
            "success": True,
            "sketch_name": sketch_name,
            "arc_id": arc.entityToken,
            "center": [center_x, center_y],
            "radius": radius,
            "start_angle": start_angle,
            "end_angle": end_angle
        }
        
        _log_tool_execution("draw_arc", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("draw_arc", parameters, result)
        return result

async def draw_polygon(
    center_x: float,
    center_y: float,
    radius: float,
    sides: int,
    sketch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Draw regular polygon in sketch
    
    Args:
        center_x: Center X coordinate
        center_y: Center Y coordinate
        radius: Circumscribed circle radius
        sides: Number of sides
        sketch_name: Target sketch name (if empty, use active sketch)
    """
    parameters = {
        "center_x": center_x, "center_y": center_y,
        "radius": radius, "sides": sides,
        "sketch_name": sketch_name
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.is_initialized:
        result = {"error": "Fusion 360 not available or bridge not initialized"}
        _log_tool_execution("draw_polygon", parameters, result)
        return result
    
    if sides < 3:
        result = {"error": "Polygon must have at least 3 sides"}
        _log_tool_execution("draw_polygon", parameters, result)
        return result
    
    try:
        # If no sketch name specified, create a sketch first
        if not sketch_name:
            sketch_result = fusion_bridge.create_sketch()
            if not sketch_result.get("success"):
                result = {"error": f"Failed to create sketch: {sketch_result.get('error', 'unknown error')}"}
                _log_tool_execution("draw_polygon", parameters, result)
                return result
            sketch_name = sketch_result["sketch_name"]
        
        # Draw polygon directly using Fusion 360 API
        sketch = fusion_bridge.get_sketch_by_name(sketch_name)
        if not sketch:
            result = {"error": f"Sketch not found: {sketch_name}"}
            _log_tool_execution("draw_polygon", parameters, result)
            return result
        
        import math
        
        # Calculate polygon vertices
        points = []
        lines = []
        
        for i in range(sides):
            angle = 2 * math.pi * i / sides
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(adsk.core.Point3D.create(x, y, 0))
        
        # Draw polygon edges
        lines_collection = sketch.sketchCurves.sketchLines
        for i in range(sides):
            start_point = points[i]
            end_point = points[(i + 1) % sides]
            line = lines_collection.addByTwoPoints(start_point, end_point)
            lines.append(line.entityToken)
        
        result = {
            "success": True,
            "sketch_name": sketch_name,
            "polygon_lines": lines,
            "center": [center_x, center_y],
            "radius": radius,
            "sides": sides
        }
        
        _log_tool_execution("draw_polygon", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("draw_polygon", parameters, result)
        return result

async def get_sketch_info(sketch_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get sketch information
    
    Args:
        sketch_name: Sketch name (if empty, get all sketches)
    """
    parameters = {"sketch_name": sketch_name}
    
    if not FUSION_AVAILABLE or not fusion_bridge.is_initialized:
        result = {"error": "Fusion 360 not available or bridge not initialized"}
        _log_tool_execution("get_sketch_info", parameters, result)
        return result
    
    try:
        if sketch_name:
            # Get specific sketch info
            sketch = fusion_bridge.get_sketch_by_name(sketch_name)
            if sketch:
                result = {
                    "success": True,
                    "sketch": {
                        "name": sketch.name,
                        "isVisible": sketch.isVisible,
                        "profiles": sketch.profiles.count,
                        "curves": sketch.sketchCurves.count,
                        "entityToken": sketch.entityToken
                    }
                }
            else:
                result = {"error": f"Sketch not found: {sketch_name}"}
        else:
            # Get all sketches info
            result = fusion_bridge.get_sketches()
        
        _log_tool_execution("get_sketch_info", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("get_sketch_info", parameters, result)
        return result

def register_tools(mcp_instance):
    """Register all basic sketch tools to MCP server"""
    mcp_instance.tool()(create_sketch)
    mcp_instance.tool()(draw_line)
    mcp_instance.tool()(draw_circle)
    mcp_instance.tool()(draw_rectangle)
    mcp_instance.tool()(draw_arc)
    mcp_instance.tool()(draw_polygon)
    mcp_instance.tool()(get_sketch_info)
