#!/usr/bin/env python3
"""
Fusion360 MCP Server Context Persistence System Unit Tests

Test functionality:
- Design intent storage and retrieval
- Task status tracking
- Design history recording
- Assembly relationship graph management
- Data serialization and deserialization
"""

import unittest
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestContextPersistence(unittest.TestCase):
    """Context persistence basic functionality tests"""
    
    def setUp(self):
        """Test initialization"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()
    
    def tearDown(self):
        """Test cleanup"""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)

class TestDesignIntentStorage(TestContextPersistence):
    """Design intent storage tests"""
    
    def test_store_and_retrieve_design_intent(self):
        """Test design intent storage and retrieval"""
        from context import ContextPersistenceManager
        
        manager = ContextPersistenceManager(self.temp_file_path)
        
        # Store design intent
        intent = manager.store_design_intent(
            project_name="Robot base design",
            description="Design a stable robot base",
            requirements=["Load capacity 50kg", "Shock resistant"],
            constraints=["Size limit 200x200mm", "Weight not exceeding 5kg"],
            performance_metrics={"Strength": ">=400MPa", "Weight": "<=5kg"},
            final_assembly_description="Final assembly includes base and mounting bolts"
        )
        
        # Verify returned design intent
        self.assertEqual(intent.project_name, "Robot base design")
        self.assertEqual(intent.description, "Design a stable robot base")
        self.assertEqual(len(intent.requirements), 2)
        self.assertEqual(len(intent.constraints), 2)
        
        # Retrieve design intent
        retrieved_intent = manager.get_design_intent()
        self.assertIsNotNone(retrieved_intent)
        self.assertEqual(retrieved_intent.project_name, "Robot base design")
        self.assertEqual(retrieved_intent.description, "Design a stable robot base")

class TestTaskTracking(TestContextPersistence):
    """Task tracking tests"""
    
    def test_add_and_track_tasks(self):
        """Test task addition and tracking"""
        from context import ContextPersistenceManager, TaskStatus
        
        manager = ContextPersistenceManager(self.temp_file_path)
        
        # Add tasks
        task1 = manager.add_task(
            title="Create sketch",
            description="Create base sketch on XY plane",
            metadata={"plane": "xy", "estimated_time": "30min"}
        )
        
        task2 = manager.add_task(
            title="Extrude feature",
            description="Extrude sketch to 3D solid",
            dependencies=[task1.task_id],
            metadata={"height": "20mm"}
        )
        
        # Verify task creation
        self.assertEqual(task1.title, "Create sketch")
        self.assertEqual(task1.status, TaskStatus.PENDING)
        self.assertEqual(task2.dependencies, [task1.task_id])
        
        # Update task status
        updated_task = manager.update_task_status(
            task1.task_id, 
            TaskStatus.COMPLETED,
            outputs=["sketch_001"]
        )
        
        self.assertEqual(updated_task.status, TaskStatus.COMPLETED)
        self.assertIn("sketch_001", updated_task.outputs)
        
        # Get task status
        status = manager.get_task_status()
        self.assertEqual(status["total_tasks"], 2)
        self.assertEqual(status["status_breakdown"][TaskStatus.COMPLETED.value], 1)
        self.assertEqual(status["status_breakdown"][TaskStatus.PENDING.value], 1)

class TestHistoryTracking(TestContextPersistence):
    """History recording tracking tests"""
    
    def test_add_and_retrieve_history(self):
        """Test history record addition and retrieval"""
        from context import ContextPersistenceManager
        
        manager = ContextPersistenceManager(self.temp_file_path)
        
        # Add history record
        entry = manager.add_history_entry(
            action_type="create_sketch",
            action_description="Create XY plane sketch",
            parameters={"plane": "xy", "name": "BaseSketch"},
            result={"success": True, "sketch_id": "sketch_001"},
            user_context="Design base"
        )
        
        # Verify history record
        self.assertEqual(entry.action_type, "create_sketch")
        self.assertEqual(entry.parameters["plane"], "xy")
        self.assertTrue(entry.result["success"])
        
        # Retrieve history records
        history = manager.get_design_history(limit=5)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action_type"], "create_sketch")

class TestComponentAndAssemblyManagement(TestContextPersistence):
    """Component and assembly management tests"""
    
    def test_component_management(self):
        """Test component management"""
        from context import ContextPersistenceManager
        
        manager = ContextPersistenceManager(self.temp_file_path)
        
        # Add components
        base_component = manager.add_component(
            name="RobotBase",
            description="Robot base body",
            properties={"material": "Aluminum", "weight": 2.5}
        )
        
        mount_component = manager.add_component(
            name="MotorMount",
            description="Motor mounting bracket",
            parent_id=base_component.component_id,
            properties={"material": "Steel", "bolt_pattern": "4x M6"}
        )
        
        # Verify component hierarchy
        self.assertEqual(base_component.name, "RobotBase")
        self.assertEqual(mount_component.parent_id, base_component.component_id)
        self.assertIn(mount_component.component_id, base_component.children_ids)
        
        # Test assembly relationship
        relationship = manager.add_assembly_relationship(
            parent_component_id=base_component.component_id,
            child_component_id=mount_component.component_id,
            relationship_type="fixed_joint",
            constraints=[{"type": "coincident", "entity1": "face1", "entity2": "face2"}],
            parameters={"offset": 0.0}
        )
        
        self.assertEqual(relationship.relationship_type, "fixed_joint")
        self.assertEqual(len(relationship.constraints), 1)

class TestDataPersistence(TestContextPersistence):
    """Data persistence tests"""
    
    def test_data_serialization_and_loading(self):
        """Test data serialization and loading"""
        from context import ContextPersistenceManager
        
        # First manager instance - write data
        manager1 = ContextPersistenceManager(self.temp_file_path)
        
        intent1 = manager1.store_design_intent(
            project_name="Test project",
            description="Test data persistence",
            requirements=["Requirement 1", "Requirement 2"]
        )
        
        task1 = manager1.add_task(
            title="Test task",
            description="Test task description"
        )
        
        # Second manager instance - read data
        manager2 = ContextPersistenceManager(self.temp_file_path)
        
        intent2 = manager2.get_design_intent()
        status2 = manager2.get_task_status()
        
        # Verify data persistence
        self.assertEqual(intent2.project_name, intent1.project_name)
        self.assertEqual(intent2.description, intent1.description)
        self.assertEqual(status2["total_tasks"], 1)
        
        # Verify JSON file content
        with open(self.temp_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn("design_intent", data)
            self.assertIn("tasks", data)
            self.assertEqual(data["design_intent"]["project_name"], "Test project")

class TestContextSerialization(TestContextPersistence):
    """Context serialization tests"""
    
    def test_datetime_serialization(self):
        """Test datetime object serialization"""
        from context import DesignIntent
        
        # Create design intent with datetime
        now = datetime.now()
        intent = DesignIntent(
            project_name="datetime test",
            description="Test datetime serialization",
            requirements=[],
            constraints=[],
            performance_metrics={},
            final_assembly_description="",
            created_at=now,
            updated_at=now
        )
        
        # Verify datetime objects
        self.assertIsInstance(intent.created_at, datetime)
        self.assertIsInstance(intent.updated_at, datetime)

class TestTaskStatusEnum(unittest.TestCase):
    """Task status enum tests"""
    
    def test_task_status_values(self):
        """Test task status enum values"""
        from context import Task, TaskStatus
        
        # Test all status values
        expected_statuses = [
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED
        ]
        
        for status in expected_statuses:
            self.assertIsInstance(status, TaskStatus)
            self.assertIsInstance(status.value, str)

def run_context_tests():
    """Run context persistence tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_context_tests()
