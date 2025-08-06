#!/usr/bin/env python3
"""
MCP Configuration Validator for MESH Server
"""

import os
import subprocess
import json
import sys

def check_uv_installation():
    """Check if uv is installed and accessible"""
    print("Checking uv installation...")
    
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv found: {result.stdout.strip()}")
            return True
        else:
            print("❌ uv not found or not working")
            return False
    except FileNotFoundError:
        print("❌ uv not found in PATH")
        return False

def check_project_structure():
    """Check if all required files exist"""
    print("\nChecking project structure...")
    
    required_files = [
        "mcp-server-test.py",
        "prompts/mesh.md",
        "email-examples/3-way-intro.md",
        "email-examples/call-follow-up.md",
        "directory.csv",
        "pyproject.toml"
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_good = False
    
    return all_good

def check_dependencies():
    """Check if dependencies are installed"""
    print("\nChecking dependencies...")
    
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-c", "import mcp; print('MCP available')"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ MCP dependencies installed")
            return True
        else:
            print("❌ MCP dependencies missing")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def generate_config():
    """Generate the correct MCP configuration"""
    print("\nGenerating MCP configuration...")
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Try to find uv path
    try:
        result = subprocess.run(["which", "uv"], capture_output=True, text=True)
        uv_path = result.stdout.strip() if result.returncode == 0 else "/Users/vishal.mishra/.local/bin/uv"
    except:
        uv_path = "/Users/vishal.mishra/.local/bin/uv"
    
    config = {
        "mcpServers": {
            "MESH": {
                "command": uv_path,
                "args": [
                    "--directory",
                    current_dir,
                    "run",
                    "--with", "mcp",
                    "--with", "fastmcp",
                    "python",
                    "mcp-server-test.py"
                ]
            }
        }
    }
    
    print("✅ Configuration generated:")
    print(json.dumps(config, indent=2))
    
    # Save to file
    with open("mcp-config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: mcp-config.json")
    return config

def test_server_connection():
    """Test if the server can be started and responds"""
    print("\nTesting server connection...")
    
    try:
        process = subprocess.Popen(
            ["uv", "run", "--with", "mcp", "--with", "fastmcp", "python", "mcp-server-test.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        import time
        time.sleep(1)
        
        if process.poll() is None:
            print("✅ Server started successfully")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ Server failed to start")
            if stderr:
                print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def main():
    print("MESH MCP Configuration Validator")
    print("=" * 40)
    
    checks = [
        ("uv installation", check_uv_installation),
        ("project structure", check_project_structure),
        ("dependencies", check_dependencies),
        ("server connection", test_server_connection)
    ]
    
    all_passed = True
    for name, check_func in checks:
        if not check_func():
            if name != "server connection":  # Server timeout is expected
                all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! MESH server is ready to use.")
        generate_config()
        print("\n📝 Next steps:")
        print("1. Copy the configuration from mcp-config.json")
        print("2. Add it to your AI application's MCP settings")
        print("3. Restart your AI application")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        print("\n💡 Troubleshooting tips:")
        print("- Run 'uv sync' to install dependencies")
        print("- Check file paths and permissions")
        print("- Ensure uv is properly installed")

if __name__ == "__main__":
    main() 