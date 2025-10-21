"""
Sketch Tools Module

Contains sketch drawing and constraint related tools:
- basic: Basic sketch tools
- advanced: Advanced sketch tools (in development, see docs/FUTURE_FEATURES.md)
- constraints: Constraint tools
"""

from . import basic
from . import advanced
from . import constraints

def initialize_sketch_tools(fusion_bridge_instance, context_manager_instance, mcp_instance):
    """Initialize sketch tool module, set global dependencies"""
    # Set basic module global variables
    basic.fusion_bridge = fusion_bridge_instance
    basic.context_manager = context_manager_instance
    basic.mcp = mcp_instance
    
    # Set constraints module global variables
    constraints.fusion_bridge = fusion_bridge_instance
    constraints.context_manager = context_manager_instance
    constraints.mcp = mcp_instance
    
    # Set advanced module global variables
    advanced.fusion_bridge = fusion_bridge_instance
    advanced.context_manager = context_manager_instance
    advanced.mcp = mcp_instance

def register_all_tools(mcp_instance):
    """Register all sketch tools to MCP server"""
    basic.register_tools(mcp_instance)
    constraints.register_tools(mcp_instance)
    advanced.register_tools(mcp_instance)

# Import all tool functions from submodules
from .basic import (
    create_sketch,
    draw_line, 
    draw_circle,
    draw_rectangle,
    draw_arc,
    draw_polygon,
    get_sketch_info,
)

from .constraints import (
    add_geometric_constraint,
    add_dimensional_constraint
)

# Advanced tools not yet implemented, see docs/FUTURE_FEATURES.md

__all__ = [
    # Initialization functions
    'initialize_sketch_tools',
    'register_all_tools',
    
    # Basic sketch tools
    'create_sketch',
    'draw_line', 
    'draw_circle',
    'draw_rectangle',
    'draw_arc',
    'draw_polygon',
    'get_sketch_info',
    
    # Constraint tools
    'add_geometric_constraint',
    'add_dimensional_constraint'
]
