#!/usr/bin/env python3
"""
MCP Resource Definition Module

Defines all MCP resource endpoints and handler functions
"""

import json
from typing import Any
from mcp.server.fastmcp import FastMCP
from .config import logger

def register_resources(mcp: FastMCP, fusion_bridge, context_manager):
    """Register all MCP resources
    
    Args:
        mcp: FastMCP application instance
        fusion_bridge: Fusion360 bridge instance
        context_manager: Context manager instance
    """
    
    @mcp.resource("fusion360://design/info")
    def get_design_info() -> str:
        """Get current design information"""
        try:
            info = fusion_bridge.get_design_info()
            return json.dumps(info, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to get design info: {e}")
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

    @mcp.resource("fusion360://design/components")
    def get_design_components() -> str:
        """Get design components list"""
        try:
            hierarchy = context_manager.get_assembly_hierarchy()
            return json.dumps(hierarchy, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to get components list: {e}")
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

    @mcp.resource("fusion360://context/summary")
    def get_context_summary() -> str:
        """Get context summary"""
        try:
            summary = context_manager.get_context_summary()
            return json.dumps(summary, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to get context summary: {e}")
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

    @mcp.resource("fusion360://context/design_intent")
    def get_design_intent_resource() -> str:
        """Get design intent resource"""
        try:
            intent = context_manager.get_design_intent()
            if intent:
                intent_dict = {
                    "project_name": intent.project_name,
                    "description": intent.description,
                    "requirements": intent.requirements,
                    "constraints": intent.constraints,
                    "performance_metrics": intent.performance_metrics,
                    "final_assembly_description": intent.final_assembly_description,
                    "tags": intent.tags,
                    "created_at": intent.created_at.isoformat(),
                    "updated_at": intent.updated_at.isoformat()
                }
                return json.dumps(intent_dict, indent=2, ensure_ascii=False)
            else:
                return json.dumps({"message": "No design intent data"}, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to get design intent: {e}")
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

    @mcp.resource("fusion360://context/assembly_hierarchy") 
    def get_assembly_hierarchy_resource() -> str:
        """Get assembly hierarchy resource"""
        try:
            hierarchy = context_manager.get_assembly_hierarchy()
            return json.dumps(hierarchy, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to get assembly hierarchy: {e}")
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

    @mcp.resource("fusion360://design/features")
    def get_design_features() -> str:
        """Get design features list"""
        try:
            if not fusion_bridge.has_active_design:
                return json.dumps({"error": "No active design"}, indent=2, ensure_ascii=False)
            
            root_comp = fusion_bridge.design.rootComponent
            features_info = {
                "extrude_features": [],
                "revolve_features": [],
                "sweep_features": [],
                "loft_features": [],
                "fillet_features": [],
                "chamfer_features": []
            }
            
            # Collect extrude features
            for i in range(root_comp.features.extrudeFeatures.count):
                feature = root_comp.features.extrudeFeatures.item(i)
                features_info["extrude_features"].append({
                    "name": feature.name,
                    "is_suppressed": feature.isSuppressed,
                    "bodies_count": feature.bodies.count
                })
            
            # Collect revolve features
            for i in range(root_comp.features.revolveFeatures.count):
                feature = root_comp.features.revolveFeatures.item(i)
                features_info["revolve_features"].append({
                    "name": feature.name,
                    "is_suppressed": feature.isSuppressed,
                    "bodies_count": feature.bodies.count
                })
            
            # Add summary info
            features_info["summary"] = {
                "total_features": sum(len(features) for features in features_info.values() if isinstance(features, list)),
                "feature_types": len([k for k, v in features_info.items() if isinstance(v, list) and v])
            }
            
            return json.dumps(features_info, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Failed to get design features: {e}")
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

    @mcp.resource("fusion360://design/sketches")
    def get_design_sketches() -> str:
        """Get design sketches list"""
        try:
            if not fusion_bridge.has_active_design:
                return json.dumps({"error": "No active design"}, indent=2, ensure_ascii=False)
            
            root_comp = fusion_bridge.design.rootComponent
            sketches_info = {
                "sketches": [],
                "summary": {
                    "total_sketches": root_comp.sketches.count,
                    "total_curves": 0,
                    "total_profiles": 0
                }
            }
            
            for i in range(root_comp.sketches.count):
                sketch = root_comp.sketches.item(i)
                sketch_info = {
                    "name": sketch.name,
                    "is_visible": sketch.isVisible,
                    "curves_count": sketch.sketchCurves.count,
                    "profiles_count": sketch.profiles.count,
                    "plane": sketch.referencePlane.name if sketch.referencePlane else "Custom"
                }
                sketches_info["sketches"].append(sketch_info)
                
                # Accumulate statistics
                sketches_info["summary"]["total_curves"] += sketch_info["curves_count"]
                sketches_info["summary"]["total_profiles"] += sketch_info["profiles_count"]
            
            return json.dumps(sketches_info, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Failed to get design sketches: {e}")
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

    @mcp.resource("fusion360://system/status")
    def get_system_status() -> str:
        """Get system status"""
        try:
            from .config import get_platform_info, SERVER_CONFIG
            
            status = {
                "server_info": SERVER_CONFIG,
                "platform_info": get_platform_info(),
                "fusion_bridge": {
                    "initialized": fusion_bridge.is_initialized,
                    "has_active_design": fusion_bridge.has_active_design
                },
                "context_manager": {
                    "tasks_count": len(context_manager.get_task_summary().get("tasks", [])),
                    "components_count": len(context_manager.get_assembly_hierarchy().get("components", [])),
                    "history_entries": len(context_manager.get_design_history())
                }
            }
            
            return json.dumps(status, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)

    logger.info("All MCP resources registered successfully")
