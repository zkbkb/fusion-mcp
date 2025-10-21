"""
Modeling Tools Module

Contains 3D modeling related tools:
- features: Basic features (extrude, revolve, sweep, loft)
- advanced: Advanced modeling tools (chamfer, fillet, shell, boolean operations)
- patterns: Pattern and mirror tools
"""

from . import features
from . import advanced
from . import patterns

def initialize_modeling_tools(fusion_bridge_instance, context_manager_instance, mcp_instance):
    """Initialize modeling tool module, set global dependencies"""
    # Set features module global variables
    features.fusion_bridge = fusion_bridge_instance
    features.context_manager = context_manager_instance
    features.mcp = mcp_instance
    
    # Set advanced module global variables
    advanced.fusion_bridge = fusion_bridge_instance
    advanced.context_manager = context_manager_instance
    advanced.mcp = mcp_instance
    
    # Set patterns module global variables
    patterns.fusion_bridge = fusion_bridge_instance
    patterns.context_manager = context_manager_instance
    patterns.mcp = mcp_instance

def register_all_tools(mcp_instance):
    """Register all modeling tools to MCP server"""
    features.register_tools(mcp_instance)
    advanced.register_tools(mcp_instance)
    patterns.register_tools(mcp_instance)

# Import all tool functions from submodules
from .features import (
    create_extrude,
    create_revolve, 
    create_sweep,
    create_loft,
)

from .advanced import (
    create_fillet,
    create_chamfer,
    create_shell,
    boolean_operation,
    split_body,
)

from .patterns import (
    create_pattern_rectangular,
    create_pattern_circular,
    create_mirror
)

__all__ = [
    # Initialization functions
    'initialize_modeling_tools',
    'register_all_tools',
    
    # Basic features
    'create_extrude',
    'create_revolve', 
    'create_sweep',
    'create_loft',
    
    # Advanced modeling
    'create_fillet',
    'create_chamfer',
    'create_shell',
    'boolean_operation',
    'split_body',
    
    # Patterns and mirrors
    'create_pattern_rectangular',
    'create_pattern_circular',
    'create_mirror'
]
