#!/usr/bin/env python3
"""
MCP Configuration Validator for MESH
This script helps generate the correct MCP configuration for your system
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def get_uv_path():
    """Get the path to uv executable"""
    try:
        # Try to find uv in PATH
        result = subprocess.run(['which', 'uv'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        
        # Try common installation paths
        home = os.path.expanduser("~")
        common_paths = [
            os.path.join(home, ".local", "bin", "uv"),
            os.path.join(home, ".cargo", "bin", "uv"),
            "/usr/local/bin/uv",
            "/opt/homebrew/bin/uv"
        ]
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
                
        return None
    except Exception:
        return None

def get_project_directory():
    """Get the current project directory"""
    return os.getcwd()

def get_python_path():
    """Get the path to Python executable"""
    return sys.executable

def generate_mcp_config():
    """Generate MCP configuration for different applications"""
    uv_path = get_uv_path()
    project_dir = get_project_directory()
    python_path = get_python_path()
    
    print("🔧 MESH MCP Configuration Generator")
    print("=" * 50)
    
    if not uv_path:
        print("⚠️  uv not found in PATH or common locations")
        print("   Please install uv first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        print()
    
    print(f"📁 Project Directory: {project_dir}")
    print(f"🐍 Python Path: {python_path}")
    print(f"⚡ UV Path: {uv_path or 'Not found'}")
    print()
    
    # Generate configuration for different MCP clients
    print("📋 MCP Configuration for Claude Desktop:")
    print("-" * 40)
    
    if uv_path:
        config = {
            "mcpServers": {
                "MESH": {
                    "command": uv_path,
                    "args": [
                        "--directory",
                        project_dir,
                        "run",
                        "--with", "mcp",
                        "--with", "fastmcp",
                        "python",
                        "mcp-server-test.py"
                    ]
                }
            }
        }
        print(json.dumps(config, indent=2))
    else:
        # Fallback to direct Python execution
        config = {
            "mcpServers": {
                "MESH": {
                    "command": python_path,
                    "args": [
                        "-m", "mcp.server.fastmcp",
                        "mcp-server-test.py"
                    ],
                    "cwd": project_dir
                }
            }
        }
        print(json.dumps(config, indent=2))
    
    print()
    print("📋 MCP Configuration for Cursor:")
    print("-" * 40)
    
    if uv_path:
        config = {
            "mcpServers": {
                "MESH": {
                    "command": uv_path,
                    "args": [
                        "--directory",
                        project_dir,
                        "run",
                        "--with", "mcp",
                        "--with", "fastmcp",
                        "python",
                        "mcp-server-test.py"
                    ]
                }
            }
        }
        print(json.dumps(config, indent=2))
    else:
        # Fallback to direct Python execution
        config = {
            "mcpServers": {
                "MESH": {
                    "command": python_path,
                    "args": [
                        "-m", "mcp.server.fastmcp",
                        "mcp-server-test.py"
                    ],
                    "cwd": project_dir
                }
            }
        }
        print(json.dumps(config, indent=2))
    
    print()
    print("📋 MCP Configuration for MCP Inspector:")
    print("-" * 40)
    print("Transport: STDIO")
    print(f"Command: {python_path}")
    print(f"Arguments: mcp-server-test.py")
    print(f"Working Directory: {project_dir}")
    
    print()
    print("💡 Installation Instructions:")
    print("1. Install MCP Inspector: pip install mcp-inspector")
    print("2. Run: mcp-inspector")
    print("3. Use the configuration above")
    print("4. Test the connection")
    
    print()
    print("🧪 Test the server first:")
    print(f"   python test-mcp-functions.py")

if __name__ == "__main__":
    try:
        import json
        generate_mcp_config()
    except ImportError:
        print("❌ Error: json module not available")
        print("   This script requires Python 3.6+")
        sys.exit(1)
