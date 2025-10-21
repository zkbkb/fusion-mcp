"""
Context Management Tools

Contains context-related MCP tools such as design intent storage and task management
"""

from typing import Any, Dict, List, Optional
import logging

# Configure logging
logger = logging.getLogger("fusion360-mcp.context.tools")

# Global variables will be set when main module initializes
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

async def store_design_intent(
    project_name: str,
    description: str,
    requirements: List[str] = None,
    constraints: List[str] = None,
    performance_metrics: Dict[str, Any] = None,
    final_assembly_description: str = "",
    tags: List[str] = None
) -> Dict[str, Any]:
    """
    Store design intent
    
    Args:
        project_name: Project name
        description: Project description  
        requirements: Requirements list
        constraints: Constraints list
        performance_metrics: Performance metrics
        final_assembly_description: Final assembly description
        tags: Tags list
    """
    try:
        intent = context_manager.store_design_intent(
            project_name=project_name,
            description=description,
            requirements=requirements or [],
            constraints=constraints or [],
            performance_metrics=performance_metrics or {},
            final_assembly_description=final_assembly_description,
            tags=tags or []
        )
        
        result = {
            "success": True,
            "project_name": intent.project_name,
            "description": intent.description,
            "created_at": intent.created_at.isoformat()
        }
        
        _log_tool_execution("store_design_intent", 
                          {"project_name": project_name, "description": description}, 
                          result)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to store design intent: {e}")
        return {"error": str(e)}

async def add_design_task(
    title: str,
    description: str,
    dependencies: List[str] = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Add design task
    
    Args:
        title: Task title
        description: Task description
        dependencies: Dependent task ID list
        metadata: Task metadata
    """
    try:
        task = context_manager.add_task(
            title=title,
            description=description,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        result = {
            "success": True,
            "task_id": task.task_id,
            "title": task.title,
            "status": task.status.value,
            "created_at": task.created_at.isoformat()
        }
        
        _log_tool_execution("add_design_task", 
                          {"title": title, "description": description}, 
                          result)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to add task: {e}")
        return {"error": str(e)}

def register_tools(mcp_instance):
    """Register all context tools to MCP server"""
    mcp_instance.tool()(store_design_intent)
    mcp_instance.tool()(add_design_task)
