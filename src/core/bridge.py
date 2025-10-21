#!/usr/bin/env python3
"""
Fusion360 Bridge Module

Provides interface to Fusion 360 application, handles design information retrieval and API calls
Supports two modes:
1. Direct API mode: Used when running inside Fusion360
2. Plugin communication mode: Communicates with Fusion360 plugin via Socket
"""

from typing import Dict, Any
from .config import FUSION_AVAILABLE, logger, get_error_handler

# Try to import plugin client
try:
    from ..fusion360 import Fusion360PluginClient
    PLUGIN_CLIENT_AVAILABLE = True
except ImportError:
    PLUGIN_CLIENT_AVAILABLE = False
    logger.warning("Plugin client not available")

# Try to import error handler
try:
    from ..utils.error_handler import error_handler_decorator, PluginCommunicationError, FusionAPIError
    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    ERROR_HANDLING_AVAILABLE = False
    logger.warning("Error handler not available")

if FUSION_AVAILABLE:
    import adsk.core
    import adsk.fusion
    import adsk.cam

class Fusion360Bridge:
    """Fusion 360 Bridge
    
    Provides interface to Fusion 360 application, including:
    - Application connection management
    - Design information retrieval
    - API call encapsulation
    
    Supports three running modes:
    1. Direct API mode: FUSION_AVAILABLE=True
    2. Plugin communication mode: Uses Fusion360PluginClient
    3. Simulation mode: Mock responses when both unavailable
    """
    
    def __init__(self, use_plugin_mode=True):
        """Initialize bridge
        
        Args:
            use_plugin_mode: Whether to prioritize plugin mode
        """
        self.app = None
        self.ui = None
        self.design = None
        self._initialized = False
        self._mode = "unknown"
        self.plugin_client = None
        self.use_plugin_mode = use_plugin_mode
        self.error_handler = get_error_handler()
        
    def initialize(self) -> bool:
        """Initialize Fusion 360 connection
        
        Returns:
            bool: Whether initialization succeeded
        """
        try:
            # Try plugin mode first
            if self.use_plugin_mode and PLUGIN_CLIENT_AVAILABLE:
                return self._initialize_plugin_mode()
            
            # Then try direct API mode
            if FUSION_AVAILABLE:
                return self._initialize_direct_mode()
            
            # Finally use simulation mode
            logger.warning("Running in simulation mode")
            self._mode = "simulation"
            self._initialized = True
            return True
            
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "bridge_initialization"})
                logger.error(f"Bridge initialization failed: {error_result}")
            else:
                logger.error(f"Bridge initialization failed: {e}")
            return False
    
    def _initialize_plugin_mode(self) -> bool:
        """Initialize plugin communication mode"""
        try:
            self.plugin_client = Fusion360PluginClient()
            if self.plugin_client.test_connection():
                self._mode = "plugin"
                self._initialized = True
                logger.info("Plugin communication mode initialized successfully")
                return True
            else:
                logger.warning("Plugin communication mode initialization failed, trying other modes")
                return False
        except Exception as e:
            if ERROR_HANDLING_AVAILABLE:
                raise PluginCommunicationError(f"Plugin communication initialization failed: {str(e)}")
            else:
                logger.error(f"Plugin communication mode initialization failed: {e}")
                return False
    
    def _initialize_direct_mode(self) -> bool:
        """Initialize direct API mode"""
        try:
            self.app = adsk.core.Application.get()
            self.ui = self.app.userInterface
            
            # Get active design
            product = self.app.activeProduct
            if product:
                self.design = adsk.fusion.Design.cast(product)
            
            self._mode = "direct"
            self._initialized = True
            logger.info("Direct API mode initialized successfully")
            return True
            
        except Exception as e:
            if ERROR_HANDLING_AVAILABLE:
                raise FusionAPIError(f"Direct API initialization failed: {str(e)}")
            else:
                logger.error(f"Direct API mode initialization failed: {e}")
                return False
    
    @property
    def is_initialized(self) -> bool:
        """Check if initialized"""
        return self._initialized
    
    @property
    def has_active_design(self) -> bool:
        """Check if active design exists"""
        try:
            if self._mode == "plugin":
                result = self.plugin_client.get_design_info()
                return result.get("success", False)
            elif self._mode == "direct":
                return self.design is not None
            else:  # simulation mode
                return True
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, {"operation": "check_active_design"})
            return False
    
    @property
    def mode(self) -> str:
        """Get current running mode"""
        return self._mode
    
    def get_design_info(self) -> Dict[str, Any]:
        """Get current design information
        
        Returns:
            Dict[str, Any]: Design information dictionary
        """
        try:
            if self._mode == "plugin":
                return self.plugin_client.get_design_info()
            elif self._mode == "direct":
                return self._get_design_info_direct()
            else:  # simulation mode
                return self._get_design_info_simulation()
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "get_design_info", "mode": self._mode})
                return {"error": True, **error_result}
            else:
                return {"error": str(e)}
    
    def _get_design_info_direct(self) -> Dict[str, Any]:
        """Get design information in direct API mode"""
        if not self.design:
            return {"error": "No active design"}
            
        try:
            root_comp = self.design.rootComponent
            return {
                "success": True,
                "name": self.design.name,
                "rootComponent": root_comp.name,
                "components": root_comp.occurrences.count,
                "features": root_comp.features.count,
                "sketches": root_comp.sketches.count,
                "bodies": root_comp.bRepBodies.count,
                "materials": self.design.materials.count,
                "parameters": self.design.userParameters.count,
                "isParametric": self.design.designType == adsk.fusion.DesignTypes.ParametricDesignType,
                "mode": "direct"
            }
        except Exception as e:
            if ERROR_HANDLING_AVAILABLE:
                raise FusionAPIError(f"Failed to get design info: {str(e)}")
            else:
                logger.error(f"Failed to get design info: {e}")
                return {"error": str(e)}
    
    def _get_design_info_simulation(self) -> Dict[str, Any]:
        """Get design information in simulation mode"""
        return {
            "success": True,
            "name": "Simulated Design",
            "rootComponent": "Simulated Root Component",
            "components": 5,
            "features": 8,
            "sketches": 3,
            "bodies": 2,
            "materials": 1,
            "parameters": 10,
            "isParametric": True,
            "mode": "simulation"
        }
    
    def get_component_hierarchy(self) -> Dict[str, Any]:
        """Get component hierarchy
        
        Returns:
            Dict[str, Any]: Component hierarchy
        """
        try:
            if self._mode == "plugin":
                return self.plugin_client.get_component_hierarchy()
            elif self._mode == "direct":
                return self._get_component_hierarchy_direct()
            else:  # simulation mode
                return self._get_component_hierarchy_simulation()
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "get_component_hierarchy", "mode": self._mode})
                return {"error": True, **error_result}
            else:
                return {"error": str(e)}
    
    def _get_component_hierarchy_direct(self) -> Dict[str, Any]:
        """Get component hierarchy in direct API mode"""
        if not self.design:
            return {"error": "No active design"}
        
        try:
            root_comp = self.design.rootComponent
            
            def build_component_tree(component, level=0):
                """Recursively build component tree"""
                comp_info = {
                    "name": component.name,
                    "level": level,
                    "isVisible": component.isVisible if hasattr(component, 'isVisible') else True,
                    "bodies": component.bRepBodies.count,
                    "sketches": component.sketches.count,
                    "features": component.features.count,
                    "children": []
                }
                
                # Add child components
                if hasattr(component, 'occurrences'):
                    for i in range(component.occurrences.count):
                        occurrence = component.occurrences.item(i)
                        child_info = build_component_tree(occurrence.component, level + 1)
                        comp_info["children"].append(child_info)
                
                return comp_info
            
            hierarchy = build_component_tree(root_comp)
            return {
                "success": True,
                "root_component": hierarchy,
                "total_components": self._count_total_components(hierarchy),
                "mode": "direct"
            }
            
        except Exception as e:
            if ERROR_HANDLING_AVAILABLE:
                raise FusionAPIError(f"Failed to get component hierarchy: {str(e)}")
            else:
                logger.error(f"Failed to get component hierarchy: {e}")
                return {"error": str(e)}
    
    def _get_component_hierarchy_simulation(self) -> Dict[str, Any]:
        """Get component hierarchy in simulation mode"""
        return {
            "success": True,
            "root_component": {
                "name": "Simulated Root Component",
                "level": 0,
                "isVisible": True,
                "bodies": 2,
                "sketches": 3,
                "features": 5,
                "children": [
                    {
                        "name": "Child Component 1",
                        "level": 1,
                        "isVisible": True,
                        "bodies": 1,
                        "sketches": 1,
                        "features": 2,
                        "children": []
                    }
                ]
            },
            "total_components": 2,
            "mode": "simulation"
        }
    
    def _count_total_components(self, component_tree: Dict[str, Any]) -> int:
        """Recursively count total components"""
        count = 1  # Current component
        for child in component_tree.get("children", []):
            count += self._count_total_components(child)
        return count
    
    def create_sketch(self, name: str = None, plane: str = "XY") -> Dict[str, Any]:
        """Create sketch"""
        try:
            if self._mode == "plugin":
                return self.plugin_client.create_sketch(name, plane)
            elif self._mode == "direct":
                return self._create_sketch_direct(name, plane)
            else:  # simulation mode
                return self._create_sketch_simulation(name, plane)
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "create_sketch", "name": name, "plane": plane})
                return {"error": True, **error_result}
            else:
                return {"error": str(e)}
    
    def _create_sketch_direct(self, name: str = None, plane: str = "XY") -> Dict[str, Any]:
        """Create sketch in direct API mode"""
        try:
            if not self.design:
                return {"error": "No active design"}
            
            root_comp = self.design.rootComponent
            
            # Get sketch plane
            if plane == 'XY':
                sketch_plane = root_comp.xYConstructionPlane
            elif plane == 'XZ':
                sketch_plane = root_comp.xZConstructionPlane
            elif plane == 'YZ':
                sketch_plane = root_comp.yZConstructionPlane
            else:
                return {"error": f"Unsupported plane: {plane}"}
            
            # Create sketch
            sketch = root_comp.sketches.add(sketch_plane)
            if name:
                sketch.name = name
            
            return {
                "success": True,
                "sketch_name": sketch.name,
                "plane": plane,
                "mode": "direct"
            }
            
        except Exception as e:
            if ERROR_HANDLING_AVAILABLE:
                raise FusionAPIError(f"Failed to create sketch: {str(e)}")
            else:
                return {"error": f"Failed to create sketch: {str(e)}"}
    
    def _create_sketch_simulation(self, name: str = None, plane: str = "XY") -> Dict[str, Any]:
        """Create sketch in simulation mode"""
        sketch_name = name or f"Sketch{len([])}"  # Simulated counter
        return {
            "success": True,
            "sketch_name": sketch_name,
            "plane": plane,
            "mode": "simulation"
        }
    
    def create_rectangle(self, sketch_name: str, width: float = 10.0, height: float = 10.0, 
                        center_x: float = 0.0, center_y: float = 0.0) -> Dict[str, Any]:
        """Create rectangle in sketch"""
        try:
            if self._mode == "plugin":
                return self.plugin_client.create_rectangle(sketch_name, width, height, center_x, center_y)
            elif self._mode == "direct":
                # Direct API rectangle creation can be implemented here
                return {"error": "Rectangle creation in direct API mode not yet implemented"}
            else:  # simulation mode
                return {
                    "success": True,
                    "sketch_name": sketch_name,
                    "rectangle_created": True,
                    "width": width,
                    "height": height,
                    "center": [center_x, center_y],
                    "mode": "simulation"
                }
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "create_rectangle", "sketch_name": sketch_name})
                return {"error": True, **error_result}
            else:
                return {"error": str(e)}
    
    def create_circle(self, sketch_name: str, radius: float = 5.0, 
                     center_x: float = 0.0, center_y: float = 0.0) -> Dict[str, Any]:
        """Create circle in sketch"""
        try:
            if self._mode == "plugin":
                return self.plugin_client.create_circle(sketch_name, radius, center_x, center_y)
            elif self._mode == "direct":
                # Direct API circle creation can be implemented here
                return {"error": "Circle creation in direct API mode not yet implemented"}
            else:  # simulation mode
                return {
                    "success": True,
                    "sketch_name": sketch_name,
                    "circle_created": True,
                    "radius": radius,
                    "center": [center_x, center_y],
                    "mode": "simulation"
                }
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "create_circle", "sketch_name": sketch_name})
                return {"error": True, **error_result}
            else:
                return {"error": str(e)}
    
    def create_extrude(self, sketch_name: str, distance: float = 10.0, 
                      operation: str = "new") -> Dict[str, Any]:
        """Create extrude feature"""
        try:
            if self._mode == "plugin":
                return self.plugin_client.create_extrude(sketch_name, distance, operation)
            elif self._mode == "direct":
                # Direct API extrude creation can be implemented here
                return {"error": "Extrude creation in direct API mode not yet implemented"}
            else:  # simulation mode
                return {
                    "success": True,
                    "sketch_name": sketch_name,
                    "extrude_created": True,
                    "distance": distance,
                    "operation": operation,
                    "feature_name": f"Extrude{len([])}",  # Simulated counter
                    "mode": "simulation"
                }
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "create_extrude", "sketch_name": sketch_name})
                return {"error": True, **error_result}
            else:
                return {"error": str(e)}
    
    def get_sketches(self) -> Dict[str, Any]:
        """Get all sketches information"""
        try:
            if self._mode == "plugin":
                return self.plugin_client.get_sketches()
            elif self._mode == "direct":
                # Direct API sketch retrieval can be implemented here
                return {"error": "Sketch retrieval in direct API mode not yet implemented"}
            else:  # simulation mode
                return {
                    "success": True,
                    "sketches": [
                        {"name": "Sketch1", "isVisible": True, "profiles": 1, "curves": 4},
                        {"name": "Sketch2", "isVisible": True, "profiles": 0, "curves": 1}
                    ],
                    "total_count": 2,
                    "mode": "simulation"
                }
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "get_sketches"})
                return {"error": True, **error_result}
            else:
                return {"error": str(e)}
    
    def get_features(self) -> Dict[str, Any]:
        """Get all features information"""
        try:
            if self._mode == "plugin":
                return self.plugin_client.get_features()
            elif self._mode == "direct":
                # Direct API feature retrieval can be implemented here
                return {"error": "Feature retrieval in direct API mode not yet implemented"}
            else:  # simulation mode
                return {
                    "success": True,
                    "features": [
                        {"name": "Extrude1", "type": "extrude", "isVisible": True},
                        {"name": "Extrude2", "type": "extrude", "isVisible": True}
                    ],
                    "total_count": 2,
                    "mode": "simulation"
                }
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "get_features"})
                return {"error": True, **error_result}
            else:
                return {"error": str(e)}

    def get_sketch_by_name(self, sketch_name: str):
        """Get sketch object by name (direct API mode only)"""
        if self._mode != "direct" or not self.design:
            return None
        
        try:
            root_comp = self.design.rootComponent
            for i in range(root_comp.sketches.count):
                sketch = root_comp.sketches.item(i)
                if sketch.name == sketch_name:
                    return sketch
            return None
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, {"operation": "get_sketch_by_name", "sketch_name": sketch_name})
            else:
                logger.error(f"Failed to get sketch: {e}")
            return None
    
    def get_feature_by_name(self, feature_name: str):
        """Get feature object by name (direct API mode only)"""
        if self._mode != "direct" or not self.design:
            return None
        
        try:
            root_comp = self.design.rootComponent
            features = root_comp.features
            
            # Check various feature types
            feature_collections = [
                features.extrudeFeatures,
                features.revolveFeatures,
                features.sweepFeatures,
                features.loftFeatures,
                features.filletFeatures,
                features.chamferFeatures
            ]
            
            for collection in feature_collections:
                for i in range(collection.count):
                    feature = collection.item(i)
                    if feature.name == feature_name:
                        return feature
            
            return None
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, {"operation": "get_feature_by_name", "feature_name": feature_name})
            else:
                logger.error(f"Failed to get feature: {e}")
            return None
    
    def validate_operation(self, operation_type: str, **kwargs) -> Dict[str, Any]:
        """Validate if operation can be executed
        
        Args:
            operation_type: Operation type
            **kwargs: Operation parameters
            
        Returns:
            Dict[str, Any]: Validation result
        """
        try:
            if not self.is_initialized:
                return {"valid": False, "error": "Fusion 360 not initialized"}
            
            if not self.has_active_design:
                return {"valid": False, "error": "No active design"}
            
            # Perform specific validation based on operation type
            if operation_type == "sketch_operation":
                sketch_name = kwargs.get("sketch_name")
                if sketch_name and self._mode == "direct":
                    if not self.get_sketch_by_name(sketch_name):
                        return {"valid": False, "error": f"Sketch not found: {sketch_name}"}
            
            elif operation_type == "extrude_operation":
                sketch_name = kwargs.get("sketch_name")
                if sketch_name and self._mode == "direct":
                    sketch = self.get_sketch_by_name(sketch_name)
                    if not sketch:
                        return {"valid": False, "error": f"Sketch not found: {sketch_name}"}
                    if sketch.profiles.count == 0:
                        return {"valid": False, "error": "Sketch has no extrudable profiles"}
            
            return {"valid": True, "mode": self._mode}
            
        except Exception as e:
            if self.error_handler:
                error_result = self.error_handler.handle_error(e, {"operation": "validate_operation", "operation_type": operation_type})
                return {"valid": False, "error": error_result.get("user_message", str(e))}
            else:
                return {"valid": False, "error": str(e)}
    
    def refresh_design(self) -> bool:
        """Refresh design state
        
        Returns:
            bool: Whether refresh succeeded
        """
        try:
            if self._mode == "plugin":
                # Test connection in plugin mode
                return self.plugin_client.test_connection()
            elif self._mode == "direct":
                if self.app:
                    product = self.app.activeProduct
                    if product:
                        self.design = adsk.fusion.Design.cast(product)
                        return True
                return False
            else:  # simulation mode
                return True
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, {"operation": "refresh_design"})
            else:
                logger.error(f"Failed to refresh design state: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.plugin_client:
                self.plugin_client.disconnect()
            self._initialized = False
            logger.info("Bridge resources cleaned up")
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, {"operation": "cleanup"})
            else:
                logger.error(f"Failed to cleanup resources: {e}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        if self.error_handler:
            return self.error_handler.get_error_summary()
        else:
            return {"error": "Error handler not available"}
