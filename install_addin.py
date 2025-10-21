"""
Fusion360 MCP Server - Installation Script

This script installs the Fusion360 plugin by copying necessary files to the Fusion360 addins directory.
"""

import os
import sys
import shutil
import platform
import argparse

def get_fusion360_addins_path():
    """Get Fusion360 addins directory path"""
    system = platform.system()
    home_dir = os.path.expanduser("~")

    if system == "Windows":
        return os.path.join(home_dir, "AppData", "Roaming", "Autodesk", "Autodesk Fusion 360", "API", "AddIns")
    elif system == "Darwin":  # macOS
        return os.path.join(home_dir, "Library", "Application Support", "Autodesk", "Autodesk Fusion 360", "API", "AddIns")
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

def install_addin(addin_name="FusionMCP"):
    """
    Install Fusion360 addin

    Parameters:
        addin_name: Name of the addin
    """
    try:
        # Get script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Get Fusion360 addins directory
        fusion360_addins_path = get_fusion360_addins_path()

        # Create addin directory
        addin_path = os.path.join(fusion360_addins_path, addin_name)
        os.makedirs(addin_path, exist_ok=True)

        # Copy addin files
        src_addin_dir = os.path.join(script_dir, "src", "fusion360")

        # Copy addin.py as main addin file
        src_addin_file = os.path.join(src_addin_dir, "addin.py")
        dst_addin_file = os.path.join(addin_path, f"{addin_name}.py")
        shutil.copy(src_addin_file, dst_addin_file)

        # Copy manifest file (if exists)
        src_manifest = os.path.join(src_addin_dir, f"{addin_name}.manifest")
        dst_manifest = os.path.join(addin_path, f"{addin_name}.manifest")

        if os.path.exists(src_manifest):
            shutil.copy(src_manifest, dst_manifest)
            print(f"Using fixed manifest file")
        else:
            # Create fixed manifest file
            with open(dst_manifest, "w") as f:
                f.write(f"""{{
    "autodeskProduct": "Fusion360",
    "type": "addin",
    "id": "com.autodesk.{addin_name}",
    "author": "MCP Server Developer",
    "description": {{
        "": "Fusion360 MCP Server Addin - Fixed Complete Version"
    }},
    "version": "1.1.0",
    "runOnStartup": false,
    "supportedOS": ["windows", "mac"],
    "editEnabled": true
}}""")
            print(f"Created fixed manifest file")

        print(f"Fusion360 addin installed to: {addin_path}")
        print("Addin features:")
        print("   - Fixed shebang issue")
        print("   - Improved global variable initialization")
        print("   - Simplified error handling")
        print("   - runOnStartup: false (manual start)")
        print("   - Complete feature set included")
        print("\nPlease restart in Fusion360:")
        print("   1. Stop current addin (if running)")
        print("   2. Restart addin in Scripts and Add-Ins panel")

    except Exception as e:
        print(f"Error occurred while installing addin: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Install Fusion360 MCP Addin')
    parser.add_argument('--name', default='FusionMCP', help='Addin name')

    args = parser.parse_args()

    # Install addin
    install_addin(args.name)
