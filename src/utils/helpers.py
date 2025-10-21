#!/usr/bin/env python3
"""
Helper Functions Module

Contains common helper functions used in MCP tools
"""

import math
from typing import Dict, Any, List, Tuple

# Try to import logger, use basic logging if fails
try:
    from ..core.config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

def _log_tool_execution(tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any], context_manager=None) -> None:
    """Log tool execution to history
    
    Args:
        tool_name: Tool name
        parameters: Input parameters
        result: Execution result
        context_manager: Context manager instance
    """
    try:
        if context_manager:
            context_manager.add_history_entry(
                action_type=tool_name,
                action_description=f"Execute tool: {tool_name}",
                parameters=parameters,
                result=result,
                user_context="MCP tool call"
            )
        
        # Log to logger
        status = "success" if result.get("success", False) else "failed"
        logger.info(f"Tool execution {tool_name}: {status}")
        
        if not result.get("success", False) and "error" in result:
            logger.error(f"Tool {tool_name} error: {result['error']}")
            
    except Exception as e:
        logger.error(f"Failed to log tool execution history: {e}")

def validate_point_3d(point: List[float]) -> Tuple[bool, str]:
    """Validate 3D point coordinates
    
    Args:
        point: Point coordinates [x, y, z]
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    if not isinstance(point, list):
        return False, "Point coordinates must be a list"
    
    if len(point) != 3:
        return False, "Point coordinates must contain 3 elements [x, y, z]"
    
    try:
        for i, coord in enumerate(point):
            float(coord)  # Try to convert to float
    except (ValueError, TypeError):
        return False, f"Point coordinate elements must be numbers"
    
    return True, ""

def validate_vector_3d(vector: List[float]) -> Tuple[bool, str]:
    """Validate 3D vector
    
    Args:
        vector: Vector [x, y, z]
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    if not isinstance(vector, list):
        return False, "Vector must be a list"
    
    if len(vector) != 3:
        return False, "Vector must contain 3 elements [x, y, z]"
    
    try:
        coords = [float(v) for v in vector]
        
        # Check if zero vector
        magnitude = math.sqrt(sum(c**2 for c in coords))
        if magnitude < 1e-10:
            return False, "Vector cannot be a zero vector"
            
    except (ValueError, TypeError):
        return False, "Vector elements must be numbers"
    
    return True, ""

def normalize_vector(vector: List[float]) -> List[float]:
    """Normalize vector
    
    Args:
        vector: Input vector [x, y, z]
        
    Returns:
        List[float]: Normalized vector
    """
    coords = [float(v) for v in vector]
    magnitude = math.sqrt(sum(c**2 for c in coords))
    
    if magnitude < 1e-10:
        return [0.0, 0.0, 1.0]  # Default to Z-axis direction
    
    return [c / magnitude for c in coords]

def calculate_distance_3d(point1: List[float], point2: List[float]) -> float:
    """Calculate distance between two 3D points
    
    Args:
        point1: First point [x, y, z]
        point2: Second point [x, y, z]
        
    Returns:
        float: Distance
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    dz = point2[2] - point1[2]
    
    return math.sqrt(dx**2 + dy**2 + dz**2)

def calculate_angle_between_vectors(vec1: List[float], vec2: List[float]) -> float:
    """Calculate angle between two vectors
    
    Args:
        vec1: First vector [x, y, z]
        vec2: Second vector [x, y, z]
        
    Returns:
        float: Angle (radians)
    """
    # Normalize vectors
    norm_vec1 = normalize_vector(vec1)
    norm_vec2 = normalize_vector(vec2)
    
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(norm_vec1, norm_vec2))
    
    # Ensure dot product is in valid range
    dot_product = max(-1.0, min(1.0, dot_product))
    
    # Calculate angle
    return math.acos(dot_product)

def format_error_response(error_message: str, error_code: str = None) -> Dict[str, Any]:
    """Format error response
    
    Args:
        error_message: Error message
        error_code: Error code (optional)
        
    Returns:
        Dict[str, Any]: Standardized error response
    """
    response = {
        "success": False,
        "error": error_message
    }
    
    if error_code:
        response["error_code"] = error_code
    
    return response

def format_success_response(data: Dict[str, Any] = None, message: str = None) -> Dict[str, Any]:
    """Format success response
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Dict[str, Any]: Standardized success response
    """
    response = {"success": True}
    
    if data:
        response.update(data)
    
    if message:
        response["message"] = message
    
    return response

def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """Unit conversion
    
    Args:
        value: Numeric value
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        float: Converted value
    """
    # Length unit conversion (unified to mm)
    length_units = {
        "mm": 1.0,
        "cm": 10.0,
        "m": 1000.0,
        "in": 25.4,
        "ft": 304.8
    }
    
    # Angle unit conversion (unified to radians)
    angle_units = {
        "rad": 1.0,
        "deg": math.pi / 180.0,
        "grad": math.pi / 200.0
    }
    
    # Select appropriate conversion table
    if from_unit in length_units and to_unit in length_units:
        # Length unit conversion
        mm_value = value * length_units[from_unit]
        return mm_value / length_units[to_unit]
    
    elif from_unit in angle_units and to_unit in angle_units:
        # Angle unit conversion
        rad_value = value * angle_units[from_unit]
        return rad_value / angle_units[to_unit]
    
    else:
        # Unsupported unit conversion
        logger.warning(f"Unsupported unit conversion: {from_unit} -> {to_unit}")
        return value

def generate_unique_name(base_name: str, existing_names: List[str]) -> str:
    """Generate unique name
    
    Args:
        base_name: Base name
        existing_names: List of existing names
        
    Returns:
        str: Unique name
    """
    if base_name not in existing_names:
        return base_name
    
    counter = 1
    while True:
        new_name = f"{base_name}_{counter}"
        if new_name not in existing_names:
            return new_name
        counter += 1

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value when dividing by zero
        
    Returns:
        float: Division result
    """
    try:
        if abs(denominator) < 1e-10:
            return default
        return numerator / denominator
    except (ZeroDivisionError, TypeError):
        return default

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value within specified range
    
    Args:
        value: Input value
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        float: Clamped value
    """
    return max(min_value, min(max_value, value))

def interpolate_linear(start: float, end: float, t: float) -> float:
    """Linear interpolation
    
    Args:
        start: Start value
        end: End value
        t: Interpolation parameter [0, 1]
        
    Returns:
        float: Interpolation result
    """
    t = clamp(t, 0.0, 1.0)
    return start + (end - start) * t
