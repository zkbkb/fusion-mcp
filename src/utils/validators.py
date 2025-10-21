#!/usr/bin/env python3
"""
Parameter Validator Module

Contains various parameter validation functions
"""

from typing import Dict, Any, List, Tuple, Optional

# Try to import configuration, use defaults if fails
try:
    from ..core.config import CONSTRAINT_TYPES, DEFAULT_MATERIAL_PROPERTIES
except ImportError:
    # Default constraint types
    CONSTRAINT_TYPES = {
        "geometric": ["coincident", "parallel", "perpendicular", "tangent", "concentricity", "symmetry"],
        "dimensional": ["distance", "angle", "radius", "diameter"],
        "assembly": ["rigid", "revolute", "slider", "cylindrical", "pin_slot", "planar", "ball"]
    }
    
    # Default material properties
    DEFAULT_MATERIAL_PROPERTIES = {
        "steel": {
            "elastic_modulus": 200000,
            "poisson_ratio": 0.3,
            "density": 7.85,
            "thermal_conductivity": 45,
            "specific_heat": 460,
            "yield_strength": 400,
        }
    }

def validate_sketch_name(sketch_name: str) -> Tuple[bool, str]:
    """Validate sketch name
    
    Args:
        sketch_name: Sketch name
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    if not isinstance(sketch_name, str):
        return False, "Sketch name must be a string"
    
    if not sketch_name.strip():
        return False, "Sketch name cannot be empty"
    
    if len(sketch_name) > 255:
        return False, "Sketch name length cannot exceed 255 characters"
    
    # Check for invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in sketch_name:
            return False, f"Sketch name cannot contain character: {char}"
    
    return True, ""

def validate_operation_type(operation: str, valid_operations: List[str]) -> Tuple[bool, str]:
    """Validate operation type
    
    Args:
        operation: Operation type
        valid_operations: List of valid operations
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    if not isinstance(operation, str):
        return False, "Operation type must be a string"
    
    if operation not in valid_operations:
        return False, f"Invalid operation type: {operation}, valid options: {', '.join(valid_operations)}"
    
    return True, ""

def validate_material_properties(properties: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate material properties
    
    Args:
        properties: Material properties dictionary
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    if not isinstance(properties, dict):
        return False, "Material properties must be a dictionary"
    
    # Required properties
    required_props = ["elastic_modulus", "poisson_ratio", "density"]
    
    for prop in required_props:
        if prop not in properties:
            return False, f"Missing required material property: {prop}"
        
        try:
            value = float(properties[prop])
            if value <= 0:
                return False, f"Material property {prop} must be greater than 0"
        except (ValueError, TypeError):
            return False, f"Material property {prop} must be a number"
    
    # Validate Poisson's ratio range
    poisson_ratio = float(properties["poisson_ratio"])
    if not (0 <= poisson_ratio < 0.5):
        return False, "Poisson's ratio must be between 0 and 0.5"
    
    return True, ""

def validate_analysis_parameters(params: Dict[str, Any], analysis_type: str) -> Tuple[bool, str]:
    """Validate analysis parameters
    
    Args:
        params: Analysis parameters
        analysis_type: Analysis type
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    if not isinstance(params, dict):
        return False, "Analysis parameters must be a dictionary"
    
    # Validate specific parameters based on analysis type
    if analysis_type == "stress":
        return _validate_stress_analysis_params(params)
    elif analysis_type == "modal":
        return _validate_modal_analysis_params(params)
    elif analysis_type == "thermal":
        return _validate_thermal_analysis_params(params)
    else:
        return False, f"Unsupported analysis type: {analysis_type}"

def _validate_stress_analysis_params(params: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate stress analysis parameters"""
    required_keys = ["body_ids", "material_properties", "loads", "constraints"]
    
    for key in required_keys:
        if key not in params:
            return False, f"Missing required parameter: {key}"
    
    # Validate body ID list
    if not isinstance(params["body_ids"], list) or not params["body_ids"]:
        return False, "body_ids must be a non-empty list"
    
    # Validate material properties
    is_valid, error_msg = validate_material_properties(params["material_properties"])
    if not is_valid:
        return False, f"Material properties validation failed: {error_msg}"
    
    # Validate loads
    if not isinstance(params["loads"], list) or not params["loads"]:
        return False, "loads must be a non-empty list"
    
    for i, load in enumerate(params["loads"]):
        if not isinstance(load, dict):
            return False, f"Load {i+1} must be a dictionary"
        
        if "type" not in load or "magnitude" not in load:
            return False, f"Load {i+1} missing type or magnitude parameter"
    
    # Validate constraints
    if not isinstance(params["constraints"], list) or not params["constraints"]:
        return False, "constraints must be a non-empty list"
    
    return True, ""

def _validate_modal_analysis_params(params: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate modal analysis parameters"""
    required_keys = ["body_ids", "material_properties", "constraints"]
    
    for key in required_keys:
        if key not in params:
            return False, f"Missing required parameter: {key}"
    
    # Validate mode count
    if "number_of_modes" in params:
        try:
            modes = int(params["number_of_modes"])
            if modes < 1 or modes > 50:
                return False, "Mode count must be between 1 and 50"
        except (ValueError, TypeError):
            return False, "Mode count must be an integer"
    
    return True, ""

def _validate_thermal_analysis_params(params: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate thermal analysis parameters"""
    required_keys = ["body_ids", "material_properties", "thermal_loads", "thermal_constraints"]
    
    for key in required_keys:
        if key not in params:
            return False, f"Missing required parameter: {key}"
    
    # Validate thermal material properties
    material_props = params["material_properties"]
    thermal_props = ["thermal_conductivity", "specific_heat", "density"]
    
    for prop in thermal_props:
        if prop not in material_props:
            return False, f"Missing thermal material property: {prop}"
        
        try:
            value = float(material_props[prop])
            if value <= 0:
                return False, f"Thermal material property {prop} must be greater than 0"
        except (ValueError, TypeError):
            return False, f"Thermal material property {prop} must be a number"
    
    return True, ""

def validate_constraint_type(constraint_type: str, category: str = None) -> Tuple[bool, str]:
    """Validate constraint type
    
    Args:
        constraint_type: Constraint type
        category: Constraint category (optional)
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    if not isinstance(constraint_type, str):
        return False, "Constraint type must be a string"
    
    # Check if in any category
    all_constraints = []
    for constraints in CONSTRAINT_TYPES.values():
        all_constraints.extend(constraints)
    
    if constraint_type not in all_constraints:
        return False, f"Invalid constraint type: {constraint_type}"
    
    # If category specified, check if belongs to that category
    if category and category in CONSTRAINT_TYPES:
        if constraint_type not in CONSTRAINT_TYPES[category]:
            return False, f"Constraint type {constraint_type} does not belong to category {category}"
    
    return True, ""

def validate_numeric_range(value: Any, min_value: float = None, max_value: float = None, 
                         param_name: str = "parameter") -> Tuple[bool, str]:
    """Validate numeric range
    
    Args:
        value: Value to validate
        min_value: Minimum value (optional)
        max_value: Maximum value (optional)
        param_name: Parameter name
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return False, f"{param_name} must be a number"
    
    if min_value is not None and num_value < min_value:
        return False, f"{param_name} cannot be less than {min_value}"
    
    if max_value is not None and num_value > max_value:
        return False, f"{param_name} cannot be greater than {max_value}"
    
    return True, ""

def validate_list_parameter(param: Any, param_name: str, min_length: int = None, 
                          max_length: int = None, element_type: type = None) -> Tuple[bool, str]:
    """Validate list parameter
    
    Args:
        param: Parameter to validate
        param_name: Parameter name
        min_length: Minimum length
        max_length: Maximum length
        element_type: Element type
        
    Returns:
        Tuple[bool, str]: (is valid, error message)
    """
    if not isinstance(param, list):
        return False, f"{param_name} must be a list"
    
    if min_length is not None and len(param) < min_length:
        return False, f"{param_name} length cannot be less than {min_length}"
    
    if max_length is not None and len(param) > max_length:
        return False, f"{param_name} length cannot exceed {max_length}"
    
    if element_type is not None:
        for i, element in enumerate(param):
            if not isinstance(element, element_type):
                return False, f"{param_name}[{i}] must be of type {element_type.__name__}"
    
    return True, ""
