"""
Assembly Tools Module

Contains assembly related tools:
- components: Component management (create component, insert component, assembly info)
- constraints: Assembly constraints (mate constraints, joints)
- motion: Motion analysis (motion studies, interference check, exploded view, assembly animation)
"""

from . import components
from . import constraints
from . import motion

def initialize_assembly_tools(fusion_bridge_instance, context_manager_instance, mcp_instance):
    """Initialize assembly tool module, set global dependencies"""
    # Set components module global variables
    components.fusion_bridge = fusion_bridge_instance
    components.context_manager = context_manager_instance
    components.mcp = mcp_instance
    
    # Set constraints module global variables
    constraints.fusion_bridge = fusion_bridge_instance
    constraints.context_manager = context_manager_instance
    constraints.mcp = mcp_instance
    
    # Set motion module global variables
    motion.fusion_bridge = fusion_bridge_instance
    motion.context_manager = context_manager_instance
    motion.mcp = mcp_instance

def register_all_tools(mcp_instance):
    """Register all assembly tools to MCP server"""
    components.register_tools(mcp_instance)
    constraints.register_tools(mcp_instance)
    motion.register_tools(mcp_instance)

# Import all tool functions from submodules
from .components import (
    create_component,
    insert_component_from_file,
    get_assembly_info,
)

from .constraints import (
    create_mate_constraint,
    create_joint,
)

from .motion import (
    create_motion_study,
    check_interference,
    create_exploded_view,
    animate_assembly
)

__all__ = [
    # Initialization functions
    'initialize_assembly_tools',
    'register_all_tools',
    
    # Component management
    'create_component',
    'insert_component_from_file',
    'get_assembly_info',
    
    # Assembly constraints
    'create_mate_constraint',
    'create_joint',
    
    # Motion analysis
    'create_motion_study',
    'check_interference',
    'create_exploded_view',
    'animate_assembly'
]
