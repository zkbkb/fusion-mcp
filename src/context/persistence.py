#!/usr/bin/env python3
"""
Fusion360 MCP Server - Context Persistence System

This module provides design context persistence functionality, including:
- Design intent storage
- Task status tracking
- Design history recording
- Assembly relationship graph management

Usage:
    context_manager = ContextPersistenceManager()
    context_manager.store_design_intent("Create robotic arm base", {...})
    status = context_manager.get_task_status()
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("context_persistence")


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DesignIntent:
    """Design intent data structure"""
    project_name: str
    description: str
    requirements: List[str]
    constraints: List[str]
    performance_metrics: Dict[str, Any]
    final_assembly_description: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Task:
    """Task data structure"""
    task_id: str
    title: str
    description: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    dependencies: List[str] = None
    outputs: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.outputs is None:
            self.outputs = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class HistoryEntry:
    """History entry"""
    entry_id: str
    timestamp: datetime
    action_type: str
    action_description: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]
    user_context: str = ""
    rollback_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.rollback_data is None:
            self.rollback_data = {}


@dataclass
class Component:
    """Component data structure"""
    component_id: str
    name: str
    description: str
    parent_id: Optional[str]
    children_ids: List[str]
    properties: Dict[str, Any]
    constraints: List[str]
    interfaces: List[str]
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []
        if self.constraints is None:
            self.constraints = []
        if self.interfaces is None:
            self.interfaces = []


@dataclass
class AssemblyRelationship:
    """Assembly relationship data structure"""
    relationship_id: str
    parent_component_id: str
    child_component_id: str
    relationship_type: str
    constraints: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []


class ContextPersistenceManager:
    """Context persistence manager"""
    
    def __init__(self, storage_path: str = "design_context.json"):
        """
        Initialize context persistence manager
        
        Args:
            storage_path: Storage file path
        """
        self.storage_path = Path(storage_path)
        self.data = {
            "design_intent": None,
            "tasks": {},
            "history": [],
            "components": {},
            "assembly_relationships": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from file"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
                logger.info(f"Successfully loaded context data: {self.storage_path}")
            else:
                logger.info("No existing context file found, will create new context")
        except Exception as e:
            logger.error(f"Failed to load context data: {e}")
    
    def _save_data(self) -> None:
        """Save data to file"""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert datetime objects to ISO format strings
            serializable_data = self._make_serializable(self.data.copy())
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Context data saved: {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save context data: {e}")
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (TaskStatus, Enum)):
            return obj.value
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(asdict(obj))
        else:
            return obj
    
    # === Design Intent Storage Functions ===
    
    def store_design_intent(
        self,
        project_name: str,
        description: str,
        requirements: List[str] = None,
        constraints: List[str] = None,
        performance_metrics: Dict[str, Any] = None,
        final_assembly_description: str = "",
        tags: List[str] = None
    ) -> DesignIntent:
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
            
        Returns:
            DesignIntent: Design intent object
        """
        now = datetime.now()
        intent = DesignIntent(
            project_name=project_name,
            description=description,
            requirements=requirements or [],
            constraints=constraints or [],
            performance_metrics=performance_metrics or {},
            final_assembly_description=final_assembly_description,
            created_at=now,
            updated_at=now,
            tags=tags or []
        )
        
        self.data["design_intent"] = asdict(intent)
        self._save_data()
        
        logger.info(f"Design intent stored: {project_name}")
        return intent
    
    def get_design_intent(self) -> Optional[DesignIntent]:
        """Get current design intent"""
        intent_data = self.data.get("design_intent")
        if intent_data:
            # Convert string time to datetime objects
            intent_data = intent_data.copy()
            
            # Safely convert datetime fields
            for date_field in ['created_at', 'updated_at']:
                if date_field in intent_data:
                    date_value = intent_data[date_field]
                    if isinstance(date_value, str):
                        intent_data[date_field] = datetime.fromisoformat(date_value)
                    elif isinstance(date_value, datetime):
                        # Already datetime object, no conversion needed
                        pass
                    else:
                        # If neither string nor datetime, use current time
                        intent_data[date_field] = datetime.now()
            
            return DesignIntent(**intent_data)
        return None
    
    def update_design_intent(self, **kwargs) -> Optional[DesignIntent]:
        """Update design intent"""
        intent = self.get_design_intent()
        if not intent:
            logger.warning("No existing design intent found, cannot update")
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(intent, key):
                setattr(intent, key, value)
        
        intent.updated_at = datetime.now()
        self.data["design_intent"] = asdict(intent)
        self._save_data()
        
        logger.info("Design intent updated")
        return intent
    
    # === Task Status Tracking Functions ===
    
    def add_task(
        self,
        title: str,
        description: str,
        dependencies: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Task:
        """
        Add new task
        
        Args:
            title: Task title
            description: Task description
            dependencies: Dependent task ID list
            metadata: Task metadata
            
        Returns:
            Task: Task object
        """
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        self.data["tasks"][task_id] = asdict(task)
        self._save_data()
        
        logger.info(f"Task added: {title} (ID: {task_id})")
        return task
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        outputs: List[str] = None
    ) -> Optional[Task]:
        """
        Update task status
        
        Args:
            task_id: Task ID
            status: New status
            outputs: Task outputs
            
        Returns:
            Task: Updated task object
        """
        if task_id not in self.data["tasks"]:
            logger.warning(f"Task not found: {task_id}")
            return None
        
        task_data = self.data["tasks"][task_id].copy()
        task_data['updated_at'] = datetime.now().isoformat()
        task_data['status'] = status.value
        
        if outputs:
            task_data['outputs'].extend(outputs)
        
        self.data["tasks"][task_id] = task_data
        self._save_data()
        
        logger.info(f"Task status updated: {task_id} -> {status.value}")
        
        # Convert to Task object for return
        task_data['created_at'] = datetime.fromisoformat(task_data['created_at']) if isinstance(task_data['created_at'], str) else task_data['created_at']
        task_data['updated_at'] = datetime.fromisoformat(task_data['updated_at']) if isinstance(task_data['updated_at'], str) else task_data['updated_at']
        task_data['status'] = TaskStatus(task_data['status'])
        return Task(**task_data)
    
    def get_task_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get task status
        
        Args:
            task_id: Task ID (optional, if empty returns all task statuses)
            
        Returns:
            Dict: Task status information
        """
        if task_id:
            if task_id in self.data["tasks"]:
                return self.data["tasks"][task_id]
            else:
                return {"error": f"Task not found: {task_id}"}
        else:
            # Return status statistics for all tasks
            tasks = self.data["tasks"]
            total = len(tasks)
            status_counts = {}
            
            for task_data in tasks.values():
                status = task_data["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "total_tasks": total,
                "status_breakdown": status_counts,
                "tasks": tasks
            }
    
    def get_completed_tasks(self) -> List[Dict[str, Any]]:
        """Get completed tasks list"""
        completed = []
        for task_data in self.data["tasks"].values():
            if task_data["status"] == TaskStatus.COMPLETED.value:
                completed.append(task_data)
        return completed
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks list"""
        pending = []
        for task_data in self.data["tasks"].values():
            if task_data["status"] == TaskStatus.PENDING.value:
                pending.append(task_data)
        return pending
    
    # === Design History Recording Functions ===
    
    def add_history_entry(
        self,
        action_type: str,
        action_description: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        user_context: str = "",
        rollback_data: Dict[str, Any] = None
    ) -> HistoryEntry:
        """
        Add history entry
        
        Args:
            action_type: Operation type
            action_description: Operation description
            parameters: Operation parameters
            result: Operation result
            user_context: User context
            rollback_data: Rollback data
            
        Returns:
            HistoryEntry: History entry
        """
        entry_id = str(uuid.uuid4())
        entry = HistoryEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            action_type=action_type,
            action_description=action_description,
            parameters=parameters,
            result=result,
            user_context=user_context,
            rollback_data=rollback_data or {}
        )
        
        self.data["history"].append(asdict(entry))
        self._save_data()
        
        logger.debug(f"History entry added: {action_type} - {action_description}")
        return entry
    
    def get_design_history(
        self,
        limit: Optional[int] = None,
        action_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get design history
        
        Args:
            limit: Limit number of returned entries
            action_type: Filter specific operation type
            
        Returns:
            List: History entry list
        """
        history = self.data["history"]
        
        # Filter by operation type
        if action_type:
            history = [entry for entry in history if entry["action_type"] == action_type]
        
        # Sort by time in descending order
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit return count
        if limit:
            history = history[:limit]
        
        return history
    
    def get_rollback_data(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get rollback data for specified history entry"""
        for entry in self.data["history"]:
            if entry["entry_id"] == entry_id:
                return entry.get("rollback_data", {})
        return None
    
    # === Assembly Relationship Graph Management Functions ===
    
    def add_component(
        self,
        name: str,
        description: str = "",
        parent_id: Optional[str] = None,
        properties: Dict[str, Any] = None
    ) -> Component:
        """
        Add component
        
        Args:
            name: Component name
            description: Component description
            parent_id: Parent component ID
            properties: Component properties
            
        Returns:
            Component: Component object
        """
        component_id = str(uuid.uuid4())
        now = datetime.now()
        
        component = Component(
            component_id=component_id,
            name=name,
            description=description,
            parent_id=parent_id,
            children_ids=[],
            properties=properties or {},
            constraints=[],
            interfaces=[],
            created_at=now,
            updated_at=now
        )
        
        # If has parent component, update parent's children list
        if parent_id and parent_id in self.data["components"]:
            parent_data = self.data["components"][parent_id]
            if component_id not in parent_data["children_ids"]:
                parent_data["children_ids"].append(component_id)
                parent_data["updated_at"] = now.isoformat()
        
        self.data["components"][component_id] = asdict(component)
        self._save_data()
        
        logger.info(f"Component added: {name} (ID: {component_id})")
        return component
    
    def add_assembly_relationship(
        self,
        parent_component_id: str,
        child_component_id: str,
        relationship_type: str,
        constraints: List[Dict[str, Any]] = None,
        parameters: Dict[str, Any] = None
    ) -> AssemblyRelationship:
        """
        Add assembly relationship
        
        Args:
            parent_component_id: Parent component ID
            child_component_id: Child component ID
            relationship_type: Relationship type
            constraints: Constraints list
            parameters: Relationship parameters
            
        Returns:
            AssemblyRelationship: Assembly relationship object
        """
        relationship_id = str(uuid.uuid4())
        
        relationship = AssemblyRelationship(
            relationship_id=relationship_id,
            parent_component_id=parent_component_id,
            child_component_id=child_component_id,
            relationship_type=relationship_type,
            constraints=constraints or [],
            parameters=parameters or {},
            created_at=datetime.now()
        )
        
        self.data["assembly_relationships"][relationship_id] = asdict(relationship)
        self._save_data()
        
        logger.info(f"Assembly relationship added: {parent_component_id} -> {child_component_id}")
        return relationship
    
    def get_assembly_hierarchy(self) -> Dict[str, Any]:
        """Get assembly hierarchy"""
        components = self.data["components"]
        relationships = self.data["assembly_relationships"]
        
        # Build hierarchy
        hierarchy = {
            "root_components": [],
            "component_tree": {},
            "relationships": relationships
        }
        
        for comp_id, comp_data in components.items():
            if not comp_data["parent_id"]:
                hierarchy["root_components"].append(comp_id)
            
            hierarchy["component_tree"][comp_id] = {
                "data": comp_data,
                "children": comp_data["children_ids"],
                "relationships": []
            }
            
            # Add related assembly relationships
            for rel_id, rel_data in relationships.items():
                if (rel_data["parent_component_id"] == comp_id or 
                    rel_data["child_component_id"] == comp_id):
                    hierarchy["component_tree"][comp_id]["relationships"].append(rel_data)
        
        return hierarchy
    
    def get_component_relationships(self, component_id: str) -> List[Dict[str, Any]]:
        """Get all relationships of a component"""
        relationships = []
        for rel_data in self.data["assembly_relationships"].values():
            if (rel_data["parent_component_id"] == component_id or 
                rel_data["child_component_id"] == component_id):
                relationships.append(rel_data)
        return relationships
    
    # === General Functions ===
    
    def clear_all_data(self) -> None:
        """Clear all data"""
        self.data = {
            "design_intent": None,
            "tasks": {},
            "history": [],
            "components": {},
            "assembly_relationships": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        self._save_data()
        logger.info("All context data cleared")
    
    def export_context(self, export_path: str) -> None:
        """Export context data"""
        export_file = Path(export_path)
        serializable_data = self._make_serializable(self.data.copy())
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Context data exported: {export_path}")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get context summary"""
        intent = self.get_design_intent()
        task_status = self.get_task_status()
        
        # Ensure keys in status_breakdown are strings, not enums
        status_breakdown = {}
        if "status_breakdown" in task_status:
            for status, count in task_status["status_breakdown"].items():
                # If status is TaskStatus enum, convert to string value
                if isinstance(status, TaskStatus):
                    status_key = status.value
                else:
                    status_key = str(status)
                status_breakdown[status_key] = count
        
        return {
            "design_intent": {
                "project_name": intent.project_name if intent else None,
                "description": intent.description if intent else None,
                "last_updated": intent.updated_at.isoformat() if intent else None
            },
            "task_summary": {
                "total_tasks": task_status["total_tasks"],
                "status_breakdown": status_breakdown
            },
            "history_count": len(self.data["history"]),
            "component_count": len(self.data["components"]),
            "relationship_count": len(self.data["assembly_relationships"]),
            "storage_path": str(self.storage_path),
            "last_saved": self.data["metadata"].get("created_at")
        }
