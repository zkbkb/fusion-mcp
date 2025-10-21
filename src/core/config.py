#!/usr/bin/env python3
"""
Fusion360 MCP Server Configuration Module

Contains server configuration, constant definitions and enhanced logging setup
"""

import sys
from typing import Dict, Any

# Import enhanced logging system
try:
    from ..utils.logging_config import setup_logging, get_logger
    from ..utils.error_handler import ErrorHandler
    
    # Setup enhanced logging system
    logger = setup_logging(
        enable_console=True,
        enable_file=True,
        enable_json=True,
        console_level='INFO',
        file_level='DEBUG'
    )
    
    # Create error handler
    error_handler = ErrorHandler(logger)
    
    ENHANCED_LOGGING_AVAILABLE = True
    
except ImportError as e:
    # If enhanced logging system is not available, use basic configuration
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("fusion360-mcp")
    error_handler = None
    ENHANCED_LOGGING_AVAILABLE = False
    logger.warning(f"Enhanced logging not available, using basic logging: {e}")

# Fusion 360 API detection
try:
    import adsk.core
    import adsk.fusion
    import adsk.cam
    FUSION_AVAILABLE = True
    logger.info("Fusion 360 API available")
except ImportError:
    FUSION_AVAILABLE = False
    logger.warning("Fusion 360 API not available. Running in simulation mode.")

# Server configuration
SERVER_CONFIG = {
    "name": "Fusion360 MCP Server",
    "version": "0.2.0",  # Increment version
    "description": "Fusion 360 MCP server implementation based on official MCP Python SDK with enhanced error handling and logging system",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "timeout": 30,  # 30 seconds
    "retry_attempts": 3,  # Retry attempts
    "retry_delay": 1.0,  # Retry delay (seconds)
}

# Error handling configuration
ERROR_CONFIG = {
    "max_error_history": 100,
    "error_log_level": "WARNING",
    "auto_recovery_enabled": True,
    "user_friendly_messages": True,
    "detailed_tracebacks": False,  # Set to False in production
}

# Logging configuration
LOG_CONFIG = {
    "max_file_size_mb": 10,
    "backup_count": 5,
    "console_level": "INFO",
    "file_level": "DEBUG",
    "enable_performance_logging": True,
    "enable_json_format": True,
    "log_directory": "logs",
}

# Performance monitoring configuration
PERFORMANCE_CONFIG = {
    "enable_monitoring": True,
    "slow_operation_threshold_ms": 1000,  # Slow operation threshold
    "memory_monitoring": True,
    "api_call_monitoring": True,
}

# Default material properties
DEFAULT_MATERIAL_PROPERTIES = {
    "steel": {
        "elastic_modulus": 200000,  # MPa
        "poisson_ratio": 0.3,
        "density": 7.85,  # g/cm³
        "thermal_conductivity": 45,  # W/m·K
        "specific_heat": 460,  # J/kg·K
        "yield_strength": 400,  # MPa
    },
    "aluminum": {
        "elastic_modulus": 70000,
        "poisson_ratio": 0.33,
        "density": 2.7,
        "thermal_conductivity": 237,
        "specific_heat": 900,
        "yield_strength": 276,
    },
    "titanium": {
        "elastic_modulus": 116000,
        "poisson_ratio": 0.32,
        "density": 4.43,
        "thermal_conductivity": 7.0,
        "specific_heat": 523,
        "yield_strength": 880,
    }
}

# Analysis default settings
ANALYSIS_DEFAULTS = {
    "mesh_size": 2.0,  # mm
    "mesh_element_type": "tetrahedron",
    "convergence_tolerance": 1e-6,
    "max_iterations": 100,
    "safety_factor_threshold": 2.0,
    "adaptive_meshing": True,
    "mesh_refinement_levels": 3,
}

# Constraint type mapping
CONSTRAINT_TYPES = {
    "geometric": ["coincident", "parallel", "perpendicular", "tangent", "concentricity", "symmetry"],
    "dimensional": ["distance", "angle", "radius", "diameter"],
    "assembly": ["rigid", "revolute", "slider", "cylindrical", "pin_slot", "planar", "ball"]
}

# Supported file formats
SUPPORTED_EXPORT_FORMATS = {
    "stl": {"name": "STL", "extension": ".stl", "description": "3D printing format", "binary": True},
    "step": {"name": "STEP", "extension": ".step", "description": "Standard engineering format", "binary": False},
    "iges": {"name": "IGES", "extension": ".iges", "description": "Universal CAD format", "binary": False},
    "obj": {"name": "OBJ", "extension": ".obj", "description": "3D model format", "binary": False},
    "f3d": {"name": "Fusion360", "extension": ".f3d", "description": "Fusion360 native format", "binary": True}
}

# Plugin communication configuration
PLUGIN_CONFIG = {
    "host": "localhost",
    "port": 8765,
    "timeout": 30,
    "max_retry_attempts": 3,
    "heartbeat_interval": 60,  # Heartbeat interval (seconds)
    "reconnect_delay": 5,  # Reconnect delay (seconds)
}

# Validation rules
VALIDATION_RULES = {
    "sketch_parameters": {
        "width": {"min": 0.001, "max": 10000, "unit": "mm"},
        "height": {"min": 0.001, "max": 10000, "unit": "mm"},
        "radius": {"min": 0.001, "max": 5000, "unit": "mm"},
        "angle": {"min": -360, "max": 360, "unit": "degrees"},
    },
    "modeling_parameters": {
        "extrude_distance": {"min": 0.001, "max": 10000, "unit": "mm"},
        "revolve_angle": {"min": 0.1, "max": 360, "unit": "degrees"},
        "fillet_radius": {"min": 0.001, "max": 100, "unit": "mm"},
    }
}

def get_platform_info() -> Dict[str, Any]:
    """Get platform information"""
    return {
        "platform": sys.platform,
        "python_version": sys.version,
        "fusion_available": FUSION_AVAILABLE,
        "enhanced_logging": ENHANCED_LOGGING_AVAILABLE,
        "server_version": SERVER_CONFIG["version"]
    }

def validate_parameter(param_name: str, value: Any, category: str = "sketch_parameters") -> Dict[str, Any]:
    """Validate parameter value
    
    Args:
        param_name: Parameter name
        value: Parameter value
        category: Parameter category
        
    Returns:
        Validation result
    """
    try:
        rules = VALIDATION_RULES.get(category, {})
        rule = rules.get(param_name)
        
        if not rule:
            return {"valid": True, "message": "No validation rule found"}
        
        if not isinstance(value, (int, float)):
            return {"valid": False, "message": f"Parameter {param_name} must be a number"}
        
        if value < rule["min"]:
            return {"valid": False, "message": f"Parameter {param_name} must be >= {rule['min']} {rule['unit']}"}
        
        if value > rule["max"]:
            return {"valid": False, "message": f"Parameter {param_name} must be <= {rule['max']} {rule['unit']}"}
        
        return {"valid": True, "message": "Valid"}
        
    except Exception as e:
        logger.error(f"Parameter validation error: {e}")
        return {"valid": False, "message": f"Validation error: {str(e)}"}

def get_error_handler():
    """Get error handler"""
    return error_handler

def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary"""
    return {
        "server": SERVER_CONFIG,
        "platform": get_platform_info(),
        "features": {
            "fusion_api": FUSION_AVAILABLE,
            "enhanced_logging": ENHANCED_LOGGING_AVAILABLE,
            "error_handling": error_handler is not None,
            "performance_monitoring": PERFORMANCE_CONFIG["enable_monitoring"],
        },
        "log_config": LOG_CONFIG,
        "error_config": ERROR_CONFIG
    }

# Initialize logging info
logger.info("Configuration loaded successfully")
logger.info(f"Server version: {SERVER_CONFIG['version']}")
logger.info(f"Platform: {get_platform_info()}")

if error_handler:
    logger.info("Enhanced error handling enabled")
else:
    logger.warning("Enhanced error handling not available")
