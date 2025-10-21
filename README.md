# Fusion MCP
A Model Context Protocol (MCP) server for interacting with Autodesk Fusion 360

**Drive Fusion360 CAD Modeling with Natural Language**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Core Features](#core-features)
- [Quick Start](#quick-start)
- [Configuration Guide](#configuration-guide)
- [Tool Reference](#tool-reference)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## System Architecture

This project uses a dual-mode architecture, supporting full functionality in production and simulation mode for development and testing.

### Architecture Diagram

```
Plugin Mode Architecture (Recommended for Production)
┌─────────────────┐    TCP Socket   ┌─────────────────┐    MCP         ┌─────────────────┐
│   Fusion 360    │◄────:8765──────►│   MCP Server    │◄──────────────►│   AI Client     │
│   + Plugin      │                 │   (FastMCP)     │                │ (Cursor/Claude) │
│  (Real API)     │                 │                 │                │                 │
└─────────────────┘                 └─────────────────┘                └─────────────────┘
        ↑                                    ↑                                  ↑
        │                                    │                                  │
    Fusion API                      Socket Bridge                         MCP Protocol
                                    + Tool Modules                     (JSON-RPC 2.0)

Simulation Mode Architecture (Development & Testing)
┌─────────────────┐    MCP         ┌─────────────────┐
│   MCP Server    │◄──────────────►│   AI Client     │
│  (Mock Data)    │                │ (Cursor/Claude) │
│                 │                │                 │
└─────────────────┘                └─────────────────┘
```

### Core Components

| Component | File Path | Description |
|------|---------|---------|
| **MCP Server** | `src/mcp_server.py` | FastMCP server, registers 44 CAD tools |
| **Socket Bridge** | `Fusion360SocketBridge` class | TCP communication bridge between MCP server and Fusion360 plugin |
| **Fusion360 Plugin** | `src/fusion360/addin.py` | Plugin running inside Fusion360, provides real API access |
| **Tool Modules** | `src/tools/` | Modular tool implementations, organized by functionality |
| **Context Manager** | `src/context/persistence.py` | Design intent persistence management |
| **Core Bridge** | `src/core/bridge.py` | API communication layer, supports three-mode switching |

### Communication Flow

```
AI Command → MCP Client → stdio → MCP Server → TCP Socket → Fusion360 Plugin → Fusion360 API → CAD Operation
```

---

## Core Features

### Main Capabilities

- **AI Natural Language Modeling**: Create 3D models directly from natural language descriptions
- **Dual-Mode Operation**: Supports plugin mode (full functionality) and simulation mode (development/testing)
- **44 Professional Tools**: Covers complete workflow from sketching to modeling, assembly, and analysis
- **Design Intent Persistence**: Automatically saves design history and parameters
- **Intelligent Mode Switching**: Automatically detects environment and selects optimal operating mode
- **Asynchronous Architecture**: High-performance async implementation based on FastMCP
- **Robust Error Handling**: Comprehensive exception handling and automatic degradation mechanisms

### Technical Specifications

| Feature | Description |
|-----|------|
| **MCP Protocol Version** | Model Context Protocol (Official Specification) |
| **Python Version** | 3.8+ |
| **Fusion360 Version** | v1.1.0+ |
| **Communication Protocol** | TCP Socket (localhost:8765) + stdio (MCP) |
| **Total Tools** | 44 professional CAD tools |

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Autodesk Fusion 360 installed
- MCP Client (Cursor/Claude Desktop)

### Step 1: Clone Project and Install Dependencies

```bash
# Clone the repository
git clone https://github.com/zkbkb/fusion-mcp.git
cd fusion-mcp

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Install Fusion360 Plugin

```bash
# Run plugin installation script
python install_addin.py
```

**Expected Output:**
```
Using fixed manifest file
Fusion360 plugin installed to: /Users/.../Autodesk/Fusion 360/API/AddIns/FusionMCP
Plugin features:
   - Fixed shebang issue
   - Improved global variable initialization
   - Simplified error handling
   - runOnStartup: false (manual start)
   - Full feature set included
```

### Step 3: Start Fusion360 Plugin

1. **Open Fusion 360**
2. **Access Plugin Manager**:
   - Menu: `Tools` → `Add-Ins and Scripts` → `Add-Ins`
3. **Start Plugin**:
   - Find `FusionMCP v1.1.0`
   - Click `Run`
4. **Confirm Successful Start**:
   - See message: "MCP communication server started on localhost:8765"

### Step 4: Configure MCP Client

#### Example: Claude Desktop
Edit configuration file: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fusion360": {
      "command": "python",
      "args": ["<PROJECT_PATH>/src/mcp_server.py"],
      "env": {
        "PYTHONPATH": "<PROJECT_PATH>/src"
      }
    }
  }
}
```

**Note**: Replace `<PROJECT_PATH>` with the actual absolute path to the project.

### Step 5: Verify Installation

Restart the AI client, then test the connection:

```bash
# Run complete system test
python tests/integration/test_fusion360_integration.py
```

**Expected Output:**
```
Starting Fusion360 MCP complete system test
Socket connection successful
Sketch created successfully
Circle drawn successfully
Rectangle drawn successfully
Test complete! You can now view the created geometry in Fusion 360
```

---

## Configuration Guide

### Environment Variables

Optional environment variable configuration:

```bash
# Custom Socket port (default: 8765)
export FUSION_MCP_PORT=8765

# Custom Socket host (default: localhost)
export FUSION_MCP_HOST=localhost

# Enable debug logging
export MCP_DEBUG=true
```

### Plugin Configuration

Plugin configuration file: `src/fusion360/FusionMCP.manifest`

```json
{
    "autodeskProduct": "Fusion360",
    "type": "addin",
    "id": "com.autodesk.FusionMCP",
    "version": "1.1.0",
    "runOnStartup": false,
    "supportedOS": ["windows", "mac"]
}
```

**Important Note**: `runOnStartup: false` means the plugin needs to be started manually.

---

## Tool Reference

This system provides 44 professional CAD tools, organized into the following categories:

### Sketch Tools (9 tools)

| Tool Name | Function | Parameters |
|---------|------|------|
| `create_sketch` | Create 2D sketch | plane, name |
| `draw_line` | Draw line | start_x, start_y, end_x, end_y, sketch_name |
| `draw_circle` | Draw circle | radius, center_x, center_y, sketch_name |
| `draw_rectangle` | Draw rectangle | width, height, center_x, center_y, sketch_name |
| `draw_arc` | Draw arc | center_x, center_y, radius, start_angle, end_angle |
| `draw_polygon` | Draw polygon | sides, radius, center_x, center_y, sketch_name |
| `add_geometric_constraint` | Add geometric constraint | constraint_type, entities, sketch_name |
| `add_dimensional_constraint` | Add dimensional constraint | dimension_type, value, entities, sketch_name |
| `get_sketch_info` | Get sketch information | sketch_name |

### Modeling Tools (12 tools)

| Tool Name | Function | Parameters |
|---------|------|------|
| `create_extrude` | Extrude feature | sketch_name, distance, operation |
| `create_revolve` | Revolve feature | sketch_name, axis, angle |
| `create_sweep` | Sweep feature | profile, path |
| `create_loft` | Loft feature | profiles, rails |
| `create_fillet` | Fillet feature | edges, radius |
| `create_chamfer` | Chamfer feature | edges, distance |
| `create_shell` | Shell feature | faces, thickness |
| `boolean_operation` | Boolean operation | operation, target_body, tool_body |
| `split_body` | Split body | body, splitting_tool |
| `create_pattern_rectangular` | Rectangular pattern | features, x_count, y_count, x_spacing, y_spacing |
| `create_pattern_circular` | Circular pattern | features, axis, count, angle |
| `create_mirror` | Mirror feature | features, mirror_plane |

### Assembly Tools (9 tools)

| Tool Name | Function | Parameters |
|---------|------|------|
| `create_component` | Create component | name, description |
| `insert_component_from_file` | Insert component from file | file_path, transform |
| `get_assembly_info` | Get assembly information | - |
| `create_mate_constraint` | Create mate constraint | constraint_type, entity1, entity2 |
| `create_joint` | Create joint | joint_type, component1, component2 |
| `create_motion_study` | Motion study | name, study_type, duration |
| `check_interference` | Interference check | components |
| `create_exploded_view` | Exploded view | name, scale |
| `animate_assembly` | Assembly animation | joint_name, start_value, end_value, duration |

### Analysis Tools (10 tools)

| Tool Name | Function | Parameters |
|---------|------|------|
| `measure_distance` | Measure distance | entity1, entity2 |
| `measure_angle` | Measure angle | entity1, entity2, entity3 |
| `measure_area` | Measure area | face |
| `measure_volume` | Measure volume | body |
| `calculate_mass_properties` | Calculate mass properties | body, material |
| `create_section_analysis` | Section analysis | plane, bodies |
| `perform_stress_analysis` | Stress analysis | study_name, loads, constraints |
| `perform_modal_analysis` | Modal analysis | study_name, modes_count |
| `perform_thermal_analysis` | Thermal analysis | study_name, heat_sources, temperature |
| `generate_analysis_report` | Generate analysis report | study_name, report_type |

### General Tools (4 tools)

| Tool Name | Function | Parameters |
|---------|------|------|
| `connect_fusion360` | Connect to Fusion360 environment | - |
| `create_parameter` | Create parametric variable | name, value, units, comment |
| `get_design_info` | Get design basic information | - |
| `get_features_info` | Get features list information | - |

---

## Development Guide

### Development Environment Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install development tools
pip install black flake8 mypy pytest pytest-cov
```

### Project Structure

```
fusion-mcp/
├── src/                          # Source code directory
│   ├── mcp_server.py            # MCP server main entry (FastMCP)
│   ├── tools/                   # Modular tool implementations
│   │   ├── sketch/              # Sketch tool modules
│   │   │   ├── basic.py        # Basic drawing tools
│   │   │   ├── advanced.py     # Advanced drawing tools
│   │   │   └── constraints.py  # Constraint tools
│   │   ├── modeling/            # Modeling tool modules
│   │   │   ├── features.py     # Feature tools
│   │   │   ├── patterns.py     # Pattern tools
│   │   │   └── advanced.py     # Advanced modeling tools
│   │   ├── assembly/            # Assembly tool modules
│   │   │   ├── components.py   # Component management
│   │   │   ├── constraints.py  # Assembly constraints
│   │   │   └── motion.py       # Motion studies
│   │   ├── analysis/            # Analysis tool modules
│   │   │   ├── measurement.py  # Measurement tools
│   │   │   ├── simulation.py   # Simulation analysis
│   │   │   └── reporting.py    # Report generation
│   │   └── utils.py            # Shared utility functions
│   ├── core/                    # Core components
│   │   ├── bridge.py           # API communication bridge layer
│   │   ├── config.py           # Configuration management
│   │   └── resources.py        # Resource management
│   ├── context/                 # Context management
│   │   ├── persistence.py      # Design intent persistence
│   │   └── tools.py            # Context tools
│   ├── fusion360/               # Fusion360 plugin source code
│   │   ├── addin.py            # Plugin main file
│   │   └── FusionMCP.manifest  # Plugin manifest
│   └── utils/                   # Utility functions
│       ├── error_handler.py    # Error handling
│       ├── helpers.py          # Helper functions
│       ├── logging_config.py   # Logging configuration
│       └── validators.py       # Parameter validation
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── performance/            # Performance tests
│   ├── platform/               # Platform compatibility tests
│   └── fixtures/               # Test fixtures
├── install_addin.py            # Plugin installation script
├── mcp_config.json             # MCP client configuration example
├── requirements.txt            # Python dependencies
├── setup.py                    # Package installation configuration
├── LICENSE                     # License file
└── README.md                   # This file
```

### Adding New Tools

#### Step 1: Implement Tool Function

Create a new function in the appropriate tool module:

```python
# src/tools/sketch/basic.py

async def draw_ellipse(
    center_x: float,
    center_y: float,
    major_radius: float,
    minor_radius: float,
    sketch_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Draw an ellipse in a sketch

    Args:
        center_x: Ellipse center X coordinate
        center_y: Ellipse center Y coordinate
        major_radius: Major axis radius
        minor_radius: Minor axis radius
        sketch_name: Target sketch name

    Returns:
        Dictionary containing operation result
    """
    # Implement ellipse drawing logic
    pass
```

#### Step 2: Export Tool Function

Export in the module's `__init__.py`:

```python
# src/tools/sketch/__init__.py

from .basic import (
    draw_line,
    draw_circle,
    draw_rectangle,
    draw_ellipse,  # New addition
)
```

#### Step 3: Register in MCP Server

```python
# src/mcp_server.py

@mcp.tool()
async def draw_ellipse(
    center_x: float,
    center_y: float,
    major_radius: float,
    minor_radius: float,
    sketch_name: Optional[str] = None
) -> str:
    """Draw an ellipse in a sketch"""
    parameters = {
        "center_x": center_x,
        "center_y": center_y,
        "major_radius": major_radius,
        "minor_radius": minor_radius,
        "sketch_name": sketch_name
    }

    try:
        result = fusion_bridge.send_command("draw_ellipse", parameters)
        _log_tool_execution("draw_ellipse", parameters, result)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        result = {"error": str(e)}
        _log_tool_execution("draw_ellipse", parameters, result)
        return json.dumps(result, ensure_ascii=False)
```

#### Step 4: Add Unit Tests

```python
# tests/unit/test_sketch_tools.py

@pytest.mark.asyncio
async def test_draw_ellipse():
    """Test ellipse drawing functionality"""
    result = await draw_ellipse(
        center_x=0,
        center_y=0,
        major_radius=10,
        minor_radius=5,
        sketch_name="TestSketch"
    )
    assert "error" not in result
    assert result["success"] == True
```

### Plugin Development

The plugin file is located at `src/fusion360/addin.py`, key points:

- **Global Variable Initialization**: All global variables (`app`, `ui`, `handlers`, `mcp_server`) are initialized in the `run()` function
- **Socket Server**: Uses daemon thread to run TCP server listening on port 8765
- **Error Handling**: All API calls are wrapped in try-except blocks
- **Command Processing**: Receives and responds to commands via JSON protocol

After modifying the plugin, reinstall it:

```bash
python install_addin.py
```

Then restart the plugin in Fusion 360.

### Reference Documentation

The following resources are useful when developing this project:

#### Fusion 360 API Documentation

Complete Fusion 360 API reference documentation, including all available classes, methods, and properties:

**Documentation URL**: [Fusion 360 API Reference](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)

Main content:
- `adsk.core` - Core functionality (application, UI, geometry)
- `adsk.fusion` - Fusion 360 specific functionality (design, modeling, assembly)
- `adsk.cam` - CAM functionality (toolpaths, tools)
- API object model and inheritance relationships
- Code examples and best practices

#### MCP Python SDK

Official Model Context Protocol Python SDK, this project is built on FastMCP:

**GitHub Repository**: [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)

Main content:
- MCP protocol implementation
- FastMCP rapid development framework
- Client and server examples
- Tool, resource, and prompt registration methods
- Asynchronous programming patterns

#### MCP Protocol Documentation

Official documentation and specifications for Model Context Protocol:

**Documentation URL**: [MCP Server Development Guide](https://modelcontextprotocol.io/docs/develop/build-server#python)

Main content:
- MCP protocol specification (JSON-RPC 2.0)
- Server building guide (Python section)
- Design patterns for Tools, Resources, Prompts
- Client integration methods (Cursor, Claude Desktop, etc.)
- Best practices and security guidelines

### Code Style

This project follows these code standards:

```bash
# Code formatting
black src/ tests/

# Code linting
flake8 src/ tests/

# Type checking
mypy src/

# Import sorting
isort src/ tests/
```

Recommended editor settings (VS Code):

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests
pytest tests/unit/

# Run integration tests (requires Fusion360 plugin running)
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_sketch_tools.py

# Run coverage tests
pytest --cov=src --cov-report=html

# Run performance tests
pytest tests/performance/
```

### Test Categories

| Test Type | Directory | Dependencies | Purpose |
|---------|------|------|------|
| **Unit Tests** | `tests/unit/` | None | Test independent tool function logic |
| **Integration Tests** | `tests/integration/` | Fusion360 + Plugin | Test complete workflows |
| **Performance Tests** | `tests/performance/` | None | Test response time and resource usage |
| **Platform Tests** | `tests/platform/` | None | Test cross-platform compatibility |

### Test Coverage Goals

- Unit test coverage: > 80%
- Critical path coverage: 100%
- Integration tests: All major workflows

---

## Troubleshooting

### Common Issue 1: Plugin Connection Failure

**Symptoms:**
```
Connection to Fusion 360 plugin failed: [Errno 61] Connection refused
Tool module initialization failed, using built-in implementation
```

**Solutions:**

1. **Confirm Fusion 360 is Running**
   ```bash
   # Check Fusion 360 process
   ps aux | grep Fusion  # macOS/Linux
   ```

2. **Manually Start Plugin**
   - In Fusion 360: `Tools` → `Add-Ins and Scripts` → `Add-Ins`
   - Find `FusionMCP v1.1.0`
   - Click `Run`
   - Confirm seeing: "MCP communication server started on localhost:8765"

3. **Check Port Occupancy**
   ```bash
   # macOS/Linux
   lsof -i :8765

   # Windows
   netstat -an | findstr :8765
   ```

4. **Reinstall Plugin**
   ```bash
   python install_addin.py
   ```

### Common Issue 2: MCP Client Cannot Connect

**Symptoms:**
AI client (Cursor/Claude) cannot see Fusion 360 tools

**Solutions:**

1. **Verify Configuration File Path**
   - Confirm `<PROJECT_PATH>` has been replaced with actual path
   - Check that path contains no special characters or spaces

2. **Verify JSON Syntax**
   ```bash
   # Use jq to verify JSON format
   cat mcp_config.json | jq .
   ```

3. **Check Python Environment**
   ```bash
   # Confirm Python version
   python --version  # Should be 3.8+

   # Confirm dependencies are installed
   pip list | grep mcp
   pip list | grep pydantic
   ```

4. **Restart AI Client**
   - Completely exit Cursor/Claude Desktop
   - Restart application

5. **View MCP Logs**
   ```bash
   # Cursor log location (example)
   tail -f ~/Library/Application\ Support/Cursor/logs/*.log
   ```

### Common Issue 3: Operation Execution Failure

**Symptoms:**
```json
{
  "error": "No active design found",
  "success": false
}
```

**Solutions:**

1. **Ensure Active Design Exists**
   - Create or open a design document in Fusion 360

2. **Check Parameter Format**
   - Confirm all required parameters are provided
   - Confirm parameter types are correct (numbers, strings, etc.)

3. **View Detailed Error Logs**
   ```python
   # Enable DEBUG logging in mcp_server.py
   logging.basicConfig(level=logging.DEBUG)
   ```

4. **Check Fusion 360 Status**
   - Confirm no modal dialogs are open
   - Confirm design is in editable state

### Common Issue 4: Plugin Cannot Start

**Symptoms:**
Plugin shows error in Fusion 360 plugin list

**Solutions:**

1. **Check Manifest File**
   ```bash
   cat src/fusion360/FusionMCP.manifest
   # Confirm JSON format is correct
   ```

2. **Check Python Path**
   - Python path in manifest must be correct
   - Default uses system Python

3. **View Fusion 360 Logs**
   ```
   # macOS
   ~/Library/Application Support/Autodesk/Webdeploy/Production/[version]/logs/

   # Windows
   %LOCALAPPDATA%\Autodesk\Webdeploy\Production\[version]\logs\
   ```

4. **Manually Debug Plugin**
   ```bash
   # Directly run plugin script for testing
   cd src/fusion360
   python addin.py
   ```

### System Diagnostics

Run complete diagnostic checks:

```bash
# Test MCP server
python -m src.mcp_server

# Test Socket connection
python test_mcp_connection.py

# Run platform compatibility tests
pytest tests/platform/test_compatibility.py -v

# Run complete system test
python tests/integration/test_fusion360_integration.py
```

### Getting Help

If the above methods cannot resolve the issue:

1. **View Log Files**
   - `logs/fusion360_mcp.log` - MCP server logs
   - `logs/error.log` - Error logs
   - `logs/performance.log` - Performance logs

2. **Submit Issue**
   - Include complete error information
   - Include operating system and version information
   - Include Fusion 360 version
   - Include reproduction steps

3. **Community Support**
   - GitHub Discussions
   - MCP community forums

---

## Version History

### v1.1.0 - Current Version

**Release Date**: 2024

**Main Updates**:
- Integrated 44 complete CAD tools
- Fixed plugin stability issues
- Simplified installation and configuration process
- Complete error handling and fallback mechanisms
- Modular architecture refactoring
- Added design intent persistence
- Optimized Socket communication performance
- Improved test coverage

**Tool Statistics**:
- Sketch tools: 9
- Modeling tools: 12
- Assembly tools: 9
- Analysis tools: 10
- General tools: 4

### v1.0.0 - Initial Version

**Release Date**: 2023

**Initial Features**:
- Basic MCP server implementation
- Fusion 360 plugin basic functionality
- Core CAD tool implementation
- Socket communication bridging
- Basic error handling

---

## Contributing

We welcome all forms of contribution!

### Contribution Process

1. **Fork the Project**
   ```bash
   git clone https://github.com/yourusername/fusion-mcp.git
   cd fusion-mcp
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

3. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

4. **Commit Changes**
   ```bash
   # Follow conventional commits specification
   git commit -m "feat(sketch): add ellipse drawing tool"
   ```

5. **Push Branch**
   ```bash
   git push origin feature/amazing-new-feature
   ```

6. **Create Pull Request**
   - Describe changes
   - Link related issues
   - Wait for code review

### Commit Specification

This project follows [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code formatting adjustment
- `refactor`: Code refactoring
- `test`: Test-related
- `chore`: Build tools or auxiliary tool changes

**Examples**:
```bash
feat(modeling): add boolean union operation
fix(sketch): resolve constraint calculation error
docs(readme): update installation instructions
```

### Code Review Standards

- Pass all unit tests
- Code coverage does not decrease
- Follow project code style
- Include appropriate docstrings
- Update related documentation

---

## License

This project is licensed under **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**

### You May:

- **Share** - Copy and redistribute this project
- **Adapt** - Modify and create derivative works
- **Non-Commercial Use** - Use for personal learning and research

### You Must:

- **Attribution** - Give appropriate credit, provide license link, and indicate if modifications were made
- **Non-Commercial** - May not use this work for commercial purposes

### Detailed Information

For the complete license text, see the [LICENSE](LICENSE) file or visit:
https://creativecommons.org/licenses/by-nc/4.0/

---

## Related Links

### Official Resources

- [Model Context Protocol Official Website](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Fusion 360 API Documentation](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)
- [Claude Desktop MCP Configuration](https://claude.ai/docs/mcp)

### Community Resources

- [MCP Server Examples](https://github.com/modelcontextprotocol/servers)
- [Cursor MCP Integration Guide](https://docs.cursor.com/mcp)
- [Fusion 360 Developer Community](https://forums.autodesk.com/t5/fusion-360-api-and-scripts/bd-p/22)

### Learning Resources

- [MCP Quick Start Tutorial](https://modelcontextprotocol.io/quickstart)
- [Fusion 360 API Getting Started Guide](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-7B5A90C8-E94C-48DA-B16B-430729B734DC)
- [FastMCP Development Documentation](https://github.com/modelcontextprotocol/python-sdk/tree/main/docs)

[Back to Top](#fusion360-mcp-server)
