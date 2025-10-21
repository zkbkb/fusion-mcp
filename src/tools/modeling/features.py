"""
Basic Feature Tools

Contains basic modeling features such as extrude, revolve, sweep, loft
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
logger = logging.getLogger("fusion360-mcp.modeling.features")

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

async def create_extrude(
    sketch_name: str,
    distance: float,
    operation: str = "new_body"
) -> Dict[str, Any]:
    """
    Extrude sketch to create 3D feature
    
    Args:
        sketch_name: Name of sketch to extrude
        distance: Extrusion distance
        operation: Extrusion operation type (new_body, join, cut, intersect)
    """
    parameters = {
        "sketch_name": sketch_name,
        "distance": distance,
        "operation": operation
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("create_extrude", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Find sketch
        sketch = None
        for i in range(root_comp.sketches.count):
            s = root_comp.sketches.item(i)
            if s.name == sketch_name:
                sketch = s
                break
        
        if not sketch:
            result = {"error": f"Sketch not found: {sketch_name}"}
            _log_tool_execution("create_extrude", parameters, result)
            return result
        
        # Get sketch profile
        if sketch.profiles.count == 0:
            result = {"error": "Sketch has no extrudable profiles"}
            _log_tool_execution("create_extrude", parameters, result)
            return result
        
        profile = sketch.profiles.item(0)
        
        # Set extrude operation type
        operation_type = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        if operation == "join":
            operation_type = adsk.fusion.FeatureOperations.JoinFeatureOperation
        elif operation == "cut":
            operation_type = adsk.fusion.FeatureOperations.CutFeatureOperation
        elif operation == "intersect":
            operation_type = adsk.fusion.FeatureOperations.IntersectFeatureOperation
        
        # Create extrude input
        extrudes = root_comp.features.extrudeFeatures
        ext_input = extrudes.createInput(profile, operation_type)
        
        # Set extrude distance
        distance_value = adsk.core.ValueInput.createByReal(distance)
        ext_input.setDistanceExtent(False, distance_value)
        ext_input.isSolid = True
        
        # Create extrude feature
        extrude = extrudes.add(ext_input)
        
        result = {
            "success": True,
            "extrude_id": extrude.entityToken,
            "sketch_name": sketch_name,
            "distance": distance,
            "operation": operation,
            "bodies_created": extrude.bodies.count
        }
        
        _log_tool_execution("create_extrude", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_extrude", parameters, result)
        return result

async def create_revolve(
    sketch_name: str,
    axis_point: List[float],
    axis_direction: List[float],
    angle: float,
    operation: str = "new_body"
) -> Dict[str, Any]:
    """
    Revolve sketch to create 3D feature
    
    Args:
        sketch_name: Name of sketch to revolve
        axis_point: Point on rotation axis [x, y, z]
        axis_direction: Rotation axis direction [x, y, z]
        angle: Rotation angle (radians)
        operation: Revolve operation type (new_body, join, cut, intersect)
    """
    parameters = {
        "sketch_name": sketch_name,
        "axis_point": axis_point,
        "axis_direction": axis_direction,
        "angle": angle,
        "operation": operation
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("create_revolve", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Find sketch
        sketch = None
        for i in range(root_comp.sketches.count):
            s = root_comp.sketches.item(i)
            if s.name == sketch_name:
                sketch = s
                break
        
        if not sketch:
            result = {"error": f"Sketch not found: {sketch_name}"}
            _log_tool_execution("create_revolve", parameters, result)
            return result
        
        # Get sketch profile
        if sketch.profiles.count == 0:
            result = {"error": "Sketch has no revolvable profiles"}
            _log_tool_execution("create_revolve", parameters, result)
            return result
        
        profile = sketch.profiles.item(0)
        
        # Set revolve operation type
        operation_type = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        if operation == "join":
            operation_type = adsk.fusion.FeatureOperations.JoinFeatureOperation
        elif operation == "cut":
            operation_type = adsk.fusion.FeatureOperations.CutFeatureOperation
        elif operation == "intersect":
            operation_type = adsk.fusion.FeatureOperations.IntersectFeatureOperation
        
        # Create rotation axis
        axis_point_3d = adsk.core.Point3D.create(axis_point[0], axis_point[1], axis_point[2])
        axis_direction_3d = adsk.core.Vector3D.create(axis_direction[0], axis_direction[1], axis_direction[2])
        axis_line = adsk.core.InfiniteLine3D.create(axis_point_3d, axis_direction_3d)
        
        # Create revolve input
        revolves = root_comp.features.revolveFeatures
        rev_input = revolves.createInput(profile, axis_line, operation_type)
        
        # Set revolve angle
        angle_value = adsk.core.ValueInput.createByReal(angle)
        rev_input.setAngleExtent(False, angle_value)
        rev_input.isSolid = True
        
        # Create revolve feature
        revolve = revolves.add(rev_input)
        
        result = {
            "success": True,
            "revolve_id": revolve.entityToken,
            "sketch_name": sketch_name,
            "axis_point": axis_point,
            "axis_direction": axis_direction,
            "angle": angle,
            "operation": operation,
            "bodies_created": revolve.bodies.count
        }
        
        _log_tool_execution("create_revolve", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_revolve", parameters, result)
        return result

async def create_sweep(
    profile_sketch_name: str,
    path_sketch_name: str,
    operation: str = "new_body",
    twist_angle: float = 0.0
) -> Dict[str, Any]:
    """
    Sweep sketch to create 3D feature
    
    Args:
        profile_sketch_name: Profile sketch name
        path_sketch_name: Path sketch name
        operation: Sweep operation type (new_body, join, cut, intersect)
        twist_angle: Twist angle (radians)
    """
    parameters = {
        "profile_sketch_name": profile_sketch_name,
        "path_sketch_name": path_sketch_name,
        "operation": operation,
        "twist_angle": twist_angle
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("create_sweep", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Find profile sketch
        profile_sketch = None
        for i in range(root_comp.sketches.count):
            s = root_comp.sketches.item(i)
            if s.name == profile_sketch_name:
                profile_sketch = s
                break
        
        if not profile_sketch:
            result = {"error": f"Profile sketch not found: {profile_sketch_name}"}
            _log_tool_execution("create_sweep", parameters, result)
            return result
        
        # Find path sketch
        path_sketch = None
        for i in range(root_comp.sketches.count):
            s = root_comp.sketches.item(i)
            if s.name == path_sketch_name:
                path_sketch = s
                break
        
        if not path_sketch:
            result = {"error": f"Path sketch not found: {path_sketch_name}"}
            _log_tool_execution("create_sweep", parameters, result)
            return result
        
        # Get profile
        if profile_sketch.profiles.count == 0:
            result = {"error": "Profile sketch has no sweepable profiles"}
            _log_tool_execution("create_sweep", parameters, result)
            return result
        
        profile = profile_sketch.profiles.item(0)
        
        # Get path
        if path_sketch.sketchCurves.count == 0:
            result = {"error": "Path sketch has no curves"}
            _log_tool_execution("create_sweep", parameters, result)
            return result
        
        path = path_sketch.sketchCurves.item(0)
        
        # Set sweep operation type
        operation_type = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        if operation == "join":
            operation_type = adsk.fusion.FeatureOperations.JoinFeatureOperation
        elif operation == "cut":
            operation_type = adsk.fusion.FeatureOperations.CutFeatureOperation
        elif operation == "intersect":
            operation_type = adsk.fusion.FeatureOperations.IntersectFeatureOperation
        
        # Create sweep input
        sweeps = root_comp.features.sweepFeatures
        sweep_input = sweeps.createInput(profile, path, operation_type)
        sweep_input.isSolid = True
        
        # Set twist angle
        if twist_angle != 0.0:
            twist_value = adsk.core.ValueInput.createByReal(twist_angle)
            sweep_input.twistAngle = twist_value
        
        # Create sweep feature
        sweep = sweeps.add(sweep_input)
        
        result = {
            "success": True,
            "sweep_id": sweep.entityToken,
            "profile_sketch_name": profile_sketch_name,
            "path_sketch_name": path_sketch_name,
            "operation": operation,
            "twist_angle": twist_angle,
            "bodies_created": sweep.bodies.count
        }
        
        _log_tool_execution("create_sweep", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_sweep", parameters, result)
        return result

async def create_loft(
    profile_sketch_names: List[str],
    operation: str = "new_body",
    guide_rails: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Loft sketches to create 3D feature
    
    Args:
        profile_sketch_names: Profile sketch names list
        operation: Loft operation type (new_body, join, cut, intersect)
        guide_rails: Guide rail sketch names list (optional)
    """
    parameters = {
        "profile_sketch_names": profile_sketch_names,
        "operation": operation,
        "guide_rails": guide_rails
    }
    
    if not FUSION_AVAILABLE or not fusion_bridge.design:
        result = {"error": "Fusion 360 not available or no active design"}
        _log_tool_execution("create_loft", parameters, result)
        return result
    
    try:
        root_comp = fusion_bridge.design.rootComponent
        
        # Find profile sketches and get profiles
        profiles = []
        for sketch_name in profile_sketch_names:
            sketch = None
            for i in range(root_comp.sketches.count):
                s = root_comp.sketches.item(i)
                if s.name == sketch_name:
                    sketch = s
                    break
            
            if not sketch:
                result = {"error": f"Profile sketch not found: {sketch_name}"}
                _log_tool_execution("create_loft", parameters, result)
                return result
            
            if sketch.profiles.count == 0:
                result = {"error": f"Sketch {sketch_name} has no loftable profiles"}
                _log_tool_execution("create_loft", parameters, result)
                return result
            
            profiles.append(sketch.profiles.item(0))
        
        if len(profiles) < 2:
            result = {"error": "Loft requires at least 2 section profiles"}
            _log_tool_execution("create_loft", parameters, result)
            return result
        
        # Set loft operation type
        operation_type = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        if operation == "join":
            operation_type = adsk.fusion.FeatureOperations.JoinFeatureOperation
        elif operation == "cut":
            operation_type = adsk.fusion.FeatureOperations.CutFeatureOperation
        elif operation == "intersect":
            operation_type = adsk.fusion.FeatureOperations.IntersectFeatureOperation
        
        # Create loft input
        lofts = root_comp.features.loftFeatures
        loft_input = lofts.createInput(operation_type)
        loft_input.isSolid = True
        
        # Add section profiles
        for profile in profiles:
            loft_input.loftSections.add(profile)
        
        # Create loft feature
        loft = lofts.add(loft_input)
        
        result = {
            "success": True,
            "loft_id": loft.entityToken,
            "profile_sketch_names": profile_sketch_names,
            "operation": operation,
            "sections_count": len(profiles),
            "bodies_created": loft.bodies.count
        }
        
        _log_tool_execution("create_loft", parameters, result)
        return result
        
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("create_loft", parameters, result)
        return result

def register_tools(mcp_instance):
    """Register all basic feature tools to MCP server"""
    mcp_instance.tool()(create_extrude)
    mcp_instance.tool()(create_revolve)
    mcp_instance.tool()(create_sweep)
    mcp_instance.tool()(create_loft)
