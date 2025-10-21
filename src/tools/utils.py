"""
Common Tools Module

Contains common tools such as user parameter creation
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
logger = logging.getLogger("fusion360-mcp.utils")

# Global variables will be set when main module initializes
fusion_bridge = None
context_manager = None
mcp = None

def _log_tool_execution(tool_name: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Log tool execution to history"""
    if context_manager:
        try:
            context_manager.add_history_entry(
                action_type=tool_name,
                action_description=f"Execute tool: {tool_name}",
                parameters=parameters,
                result=result,
                user_context="MCP tool call"
            )
        except Exception as e:
            logger.warning(f"Failed to log tool execution history: {e}")

async def create_parameter(
    name: str,
    value: float,
    units: str = "mm",
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create user parameter
    
    Args:
        name: Parameter name
        value: Parameter value
        units: Units
        comment: Comment (optional)
    """
    parameters = {"name": name, "value": value, "units": units, "comment": comment}
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("create_parameter", parameters, result)
        return result
    
    try:
        user_params = fusion_bridge.design.userParameters
        
        # Check if parameter with same name already exists
        existing_param = None
        for i in range(user_params.count):
            param = user_params.item(i)
            if param.name == name:
                existing_param = param
                break
        
        if existing_param:
            # Update existing parameter
            existing_param.value = value
            if comment:
                existing_param.comment = comment
            param_id = existing_param.name
            action = "updated"
        else:
            # Create new parameter
            value_input = adsk.core.ValueInput.createByReal(value)
            param = user_params.add(name, value_input, units, comment or "")
            param_id = param.name
            action = "created"
        
        result = {
            "success": True,
            "parameter_id": param_id,
            "name": name,
            "value": value,
            "units": units,
            "comment": comment,
            "action": action
        }
        
        _log_tool_execution("create_parameter", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_parameter", parameters, result)
        return result

def register_tools(mcp_instance):
    """Register all common tools to MCP server"""
    mcp_instance.tool()(create_parameter)
