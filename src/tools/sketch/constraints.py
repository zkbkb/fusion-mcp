"""
Constraint Tools

Contains geometric constraint and dimensional constraint related tools
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
logger = logging.getLogger("fusion360-mcp.sketch.constraints")

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

async def add_geometric_constraint(
    constraint_type: str,
    entities: List[str],
    sketch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add geometric constraint
    
    Args:
        constraint_type: Constraint type (coincident, parallel, perpendicular, tangent, equal, etc.)
        entities: List of entity IDs to constrain
        sketch_name: Target sketch name
    """
    parameters = {
        "constraint_type": constraint_type,
        "entities": entities,
        "sketch_name": sketch_name
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("add_geometric_constraint", parameters, result)
        return result
    
    try:
        # Specific constraint addition logic needs to be implemented
        # Since constraint system is complex, specific entity selection logic needs to be implemented in Fusion 360 environment
        result = {"error": "Geometric constraint feature requires specific entity selection logic in Fusion 360 environment"}
        _log_tool_execution("add_geometric_constraint", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("add_geometric_constraint", parameters, result)
        return result

async def add_dimensional_constraint(
    dimension_type: str,
    entities: List[str],
    value: float,
    sketch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add dimensional constraint
    
    Args:
        dimension_type: Dimension type (distance, radius, diameter, angle, etc.)
        entities: List of entity IDs to constrain
        value: Dimension value
        sketch_name: Target sketch name
    """
    parameters = {
        "dimension_type": dimension_type,
        "entities": entities,
        "value": value,
        "sketch_name": sketch_name
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("add_dimensional_constraint", parameters, result)
        return result
    
    try:
        # Specific dimensional constraint addition logic needs to be implemented
        result = {"error": "Dimensional constraint feature requires specific entity selection logic in Fusion 360 environment"}
        _log_tool_execution("add_dimensional_constraint", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("add_dimensional_constraint", parameters, result)
        return result

def register_tools(mcp_instance):
    """Register all constraint tools to MCP server"""
    mcp_instance.tool()(add_geometric_constraint)
    mcp_instance.tool()(add_dimensional_constraint)
