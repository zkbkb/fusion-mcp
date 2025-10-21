"""
Fusion360 MCP Server Core Module

Contains:
- Fusion360 bridge
- MCP resource definitions  
- Configuration management
"""

from .bridge import Fusion360Bridge
from .resources import register_resources
from .config import FUSION_AVAILABLE, logger

__all__ = [
    'Fusion360Bridge',
    'register_resources', 
    'FUSION_AVAILABLE',
    'logger'
]
