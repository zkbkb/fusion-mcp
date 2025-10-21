"""
Context Management Module

Contains context persistence and related MCP tools:
- persistence: Context persistence manager
- tools: Context-related MCP tools
"""

from .persistence import (
    ContextPersistenceManager,
    TaskStatus,
    DesignIntent,
    Task,
    HistoryEntry,
    Component,
    AssemblyRelationship
)

from . import tools

def initialize_context_tools(context_manager_instance, mcp_instance):
    """Initialize context tool module, set global dependencies"""
    # Set tools module global variables
    tools.context_manager = context_manager_instance
    tools.mcp = mcp_instance

def register_all_tools(mcp_instance):
    """Register all context tools to MCP server"""
    tools.register_tools(mcp_instance)

# Import all tool functions from submodules
from .tools import (
    store_design_intent,
    add_design_task,
)

__all__ = [
    # Persistence classes
    'ContextPersistenceManager',
    'TaskStatus',
    'DesignIntent',
    'Task',
    'HistoryEntry',
    'Component',
    'AssemblyRelationship',
    
    # Initialization functions
    'initialize_context_tools',
    'register_all_tools',
    
    # Tool functions
    'store_design_intent',
    'add_design_task',
]
