"""
Component Management Tools

Contains tools for creating components, inserting components, getting assembly information, etc.
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
logger = logging.getLogger("fusion360-mcp.assembly.components")

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

async def create_component(
    name: str,
    description: str = "",
    activate: bool = True
) -> Dict[str, Any]:
    """
    Create new component
    
    Args:
        name: Component name
        description: Component description
        activate: Whether to activate component
    """
    parameters = {
        "name": name,
        "description": description,
        "activate": activate
    }
    
    if not fusion_bridge.design:
        result = {"error": "No active design"}
        _log_tool_execution("create_component", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Create new component
        occurrence_input = root_comp.occurrences.createInput()
        new_occurrence = root_comp.occurrences.add(occurrence_input)
        
        # Set component name
        new_occurrence.component.name = name
        
        # Activate component if needed
        if activate:
            new_occurrence.activate()
        
        # Add to context manager
        component = context_manager.add_component(
            name=name,
            description=description,
            properties={
                "fusion_occurrence_id": new_occurrence.entityToken,
                "activated": activate
            }
        )
        
        result = {
            "success": True,
            "component_name": new_occurrence.component.name,
            "occurrence_id": new_occurrence.entityToken,
            "component_id": component.component_id,
            "activated": activate
        }
        
        _log_tool_execution("create_component", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_component", parameters, result)
        return result

async def insert_component_from_file(
    file_path: str,
    name: Optional[str] = None,
    transform_matrix: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Insert component from file
    
    Args:
        file_path: Component file path
        name: Component name (optional)
        transform_matrix: Transform matrix (list of 16 elements)
    """
    parameters = {
        "file_path": file_path,
        "name": name,
        "transform_matrix": transform_matrix
    }
    
    if not fusion_bridge.design:
        result = {"error": "No active design"}
        _log_tool_execution("insert_component_from_file", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Create insert input
        insert_input = root_comp.occurrences.createInputFromFile(file_path)
        
        # Set transform matrix
        if transform_matrix and len(transform_matrix) == 16:
            matrix = adsk.core.Matrix3D.create()
            matrix.setData(transform_matrix)
            insert_input.transform = matrix
        
        # Insert component
        new_occurrence = root_comp.occurrences.add(insert_input)
        
        # Set name
        if name:
            new_occurrence.component.name = name
        
        result = {
            "success": True,
            "component_name": new_occurrence.component.name,
            "occurrence_id": new_occurrence.entityToken,
            "file_path": file_path
        }
        
        _log_tool_execution("insert_component_from_file", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("insert_component_from_file", parameters, result)
        return result

async def get_assembly_info() -> Dict[str, Any]:
    """
    Get assembly information
    """
    parameters = {}
    
    if not fusion_bridge.design:
        result = {"error": "No active design"}
        _log_tool_execution("get_assembly_info", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Collect assembly information
        components = []
        for i in range(root_comp.occurrences.count):
            occurrence = root_comp.occurrences.item(i)
            components.append({
                "name": occurrence.component.name,
                "occurrence_id": occurrence.entityToken,
                "is_visible": occurrence.isVisible,
                "is_grounded": occurrence.isGrounded,
                "bodies_count": occurrence.component.bRepBodies.count,
                "sketches_count": occurrence.component.sketches.count,
                "features_count": occurrence.component.features.count
            })
        
        joints = []
        for i in range(root_comp.joints.count):
            joint = root_comp.joints.item(i)
            joints.append({
                "name": joint.name,
                "joint_id": joint.entityToken,
                "joint_type": str(joint.jointMotion.jointType),
                "is_suppressed": joint.isSuppressed
            })
        
        # Get assembly relationships from context
        context_hierarchy = context_manager.get_assembly_hierarchy()
        
        result = {
            "success": True,
            "total_components": len(components),
            "total_joints": len(joints),
            "components": components,
            "joints": joints,
            "context_hierarchy": context_hierarchy,
            "design_name": fusion_bridge.design.name
        }
        
        _log_tool_execution("get_assembly_info", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("get_assembly_info", parameters, result)
        return result

def register_tools(mcp_instance):
    """Register all component management tools to MCP server"""
    mcp_instance.tool()(create_component)
    mcp_instance.tool()(insert_component_from_file)
    mcp_instance.tool()(get_assembly_info)
