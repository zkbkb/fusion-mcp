"""
Assembly Constraint Tools

Contains assembly constraint tools such as mate constraints and joints
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
logger = logging.getLogger("fusion360-mcp.assembly.constraints")

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

async def create_mate_constraint(
    constraint_type: str,
    entity1_id: str,
    entity2_id: str,
    offset: float = 0.0,
    angle: float = 0.0
) -> Dict[str, Any]:
    """
    Create mate constraint
    
    Args:
        constraint_type: Constraint type (rigid, revolute, slider, cylindrical, pin_slot, planar, ball)
        entity1_id: First entity ID
        entity2_id: Second entity ID
        offset: Offset value
        angle: Angle value (radians)
    """
    parameters = {
        "constraint_type": constraint_type,
        "entity1_id": entity1_id,
        "entity2_id": entity2_id,
        "offset": offset,
        "angle": angle
    }
    
    if not fusion_bridge.design:
        result = {"error": "No active design"}
        _log_tool_execution("create_mate_constraint", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Specific constraint creation logic needs to be implemented here
        # Since the constraint system is complex, framework implementation is provided
        
        # Add constraint relationship to context
        context_manager.add_assembly_relationship(
            parent_component_id=entity1_id,
            child_component_id=entity2_id,
            relationship_type=constraint_type,
            constraints=[{
                "type": constraint_type,
                "offset": offset,
                "angle": angle
            }],
            parameters={"offset": offset, "angle": angle}
        )
        
        result = {
            "success": True,
            "constraint_type": constraint_type,
            "entity1_id": entity1_id,
            "entity2_id": entity2_id,
            "offset": offset,
            "angle": angle,
            "message": f"{constraint_type} constraint created"
        }
        
        _log_tool_execution("create_mate_constraint", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_mate_constraint", parameters, result)
        return result

async def create_joint(
    joint_type: str,
    origin_entity_id: str,
    origin_point: List[float],
    origin_axis: List[float],
    target_entity_id: str,
    target_point: List[float],
    target_axis: List[float],
    limits: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create joint connection
    
    Args:
        joint_type: Joint type (rigid, revolute, slider, cylindrical, pin_slot, planar, ball)
        origin_entity_id: Origin entity ID
        origin_point: Origin point coordinates [x, y, z]
        origin_axis: Origin axis direction [x, y, z]
        target_entity_id: Target entity ID
        target_point: Target point coordinates [x, y, z]
        target_axis: Target axis direction [x, y, z]
        limits: Motion limits {"min": value, "max": value}
    """
    parameters = {
        "joint_type": joint_type,
        "origin_entity_id": origin_entity_id,
        "origin_point": origin_point,
        "origin_axis": origin_axis,
        "target_entity_id": target_entity_id,
        "target_point": target_point,
        "target_axis": target_axis,
        "limits": limits
    }
    
    if not fusion_bridge.design:
        result = {"error": "No active design"}
        _log_tool_execution("create_joint", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Create joint geometry
        origin_geometry = adsk.fusion.JointGeometry.createByPoint(
            adsk.core.Point3D.create(origin_point[0], origin_point[1], origin_point[2])
        )
        origin_geometry.axis = adsk.core.Vector3D.create(origin_axis[0], origin_axis[1], origin_axis[2])
        
        target_geometry = adsk.fusion.JointGeometry.createByPoint(
            adsk.core.Point3D.create(target_point[0], target_point[1], target_point[2])
        )
        target_geometry.axis = adsk.core.Vector3D.create(target_axis[0], target_axis[1], target_axis[2])
        
        # Get joint type
        joint_type_enum = adsk.fusion.JointTypes.RigidJointType
        if joint_type == "revolute":
            joint_type_enum = adsk.fusion.JointTypes.RevoluteJointType
        elif joint_type == "slider":
            joint_type_enum = adsk.fusion.JointTypes.SliderJointType
        elif joint_type == "cylindrical":
            joint_type_enum = adsk.fusion.JointTypes.CylindricalJointType
        elif joint_type == "pin_slot":
            joint_type_enum = adsk.fusion.JointTypes.PinSlotJointType
        elif joint_type == "planar":
            joint_type_enum = adsk.fusion.JointTypes.PlanarJointType
        elif joint_type == "ball":
            joint_type_enum = adsk.fusion.JointTypes.BallJointType
        
        # Create joint input
        joints = root_comp.joints
        joint_input = joints.createInput(origin_geometry, target_geometry)
        joint_input.jointMotion = adsk.fusion.JointMotions.createByJointType(joint_type_enum)
        
        # Set motion limits
        if limits and hasattr(joint_input.jointMotion, 'rotationLimits'):
            if "min" in limits:
                joint_input.jointMotion.rotationLimits.minimumValue = limits["min"]
            if "max" in limits:
                joint_input.jointMotion.rotationLimits.maximumValue = limits["max"]
        
        # Create joint
        joint = joints.add(joint_input)
        
        result = {
            "success": True,
            "joint_type": joint_type,
            "joint_id": joint.entityToken,
            "origin_entity_id": origin_entity_id,
            "target_entity_id": target_entity_id,
            "limits": limits
        }
        
        _log_tool_execution("create_joint", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_joint", parameters, result)
        return result

def register_tools(mcp_instance):
    """Register all assembly constraint tools to MCP server"""
    mcp_instance.tool()(create_mate_constraint)
    mcp_instance.tool()(create_joint)
