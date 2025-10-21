"""
Analysis Tools Module

Contains analysis and measurement related tools:
- measurement: Measurement tools (distance, angle, area, volume, mass properties)
- simulation: Simulation analysis (section analysis, stress analysis, modal analysis, thermal analysis)
- reporting: Report generation (analysis report generation)
"""

from . import measurement
from . import simulation
from . import reporting

def initialize_analysis_tools(fusion_bridge_instance, context_manager_instance, mcp_instance):
    """Initialize analysis tool module, set global dependencies"""
    # Set measurement module global variables
    measurement.fusion_bridge = fusion_bridge_instance
    measurement.context_manager = context_manager_instance
    measurement.mcp = mcp_instance
    
    # Set simulation module global variables
    simulation.fusion_bridge = fusion_bridge_instance
    simulation.context_manager = context_manager_instance
    simulation.mcp = mcp_instance
    
    # Set reporting module global variables
    reporting.fusion_bridge = fusion_bridge_instance
    reporting.context_manager = context_manager_instance
    reporting.mcp = mcp_instance

def register_all_tools(mcp_instance):
    """Register all analysis tools to MCP server"""
    measurement.register_tools(mcp_instance)
    simulation.register_tools(mcp_instance)
    reporting.register_tools(mcp_instance)

# Import all tool functions from submodules
from .measurement import (
    measure_distance,
    measure_angle,
    measure_area,
    measure_volume,
    calculate_mass_properties,
)

from .simulation import (
    create_section_analysis,
    perform_stress_analysis,
    perform_modal_analysis,
    perform_thermal_analysis,
)

from .reporting import (
    generate_analysis_report
)

__all__ = [
    # Initialization functions
    'initialize_analysis_tools',
    'register_all_tools',
    
    # Measurement tools
    'measure_distance',
    'measure_angle',
    'measure_area', 
    'measure_volume',
    'calculate_mass_properties',
    
    # Simulation analysis
    'create_section_analysis',
    'perform_stress_analysis',
    'perform_modal_analysis',
    'perform_thermal_analysis',
    
    # Report generation
    'generate_analysis_report'
]
