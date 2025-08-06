#!/usr/bin/env python3
"""
Test script to verify MESH server startup and basic MCP protocol
"""

import subprocess
import json
import time
import sys

def test_server_startup():
    """Test if the MESH server can start properly"""
    print("Testing MESH server startup...")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [
                "uv", "run", "--with", "mcp", "--with", "fastmcp", 
                "python", "mcp-server-test.py"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(1)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully")
            
            # Send a simple MCP initialization message
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            try:
                # Send the message
                process.stdin.write(json.dumps(init_message) + "\n")
                process.stdin.flush()
                
                # Wait for response
                time.sleep(0.5)
                
                # Check for response
                if process.stdout.readable():
                    response = process.stdout.readline()
                    if response:
                        print("✅ Server responded to MCP protocol")
                        print(f"Response: {response.strip()}")
                    else:
                        print("⚠️ No response from server")
                
            except Exception as e:
                print(f"⚠️ Error testing MCP protocol: {e}")
            
            # Clean up
            process.terminate()
            process.wait(timeout=5)
            print("✅ Server shutdown cleanly")
            
        else:
            # Process exited
            stdout, stderr = process.communicate()
            print("❌ Server failed to start")
            print(f"Exit code: {process.returncode}")
            if stderr:
                print(f"Stderr: {stderr}")
            if stdout:
                print(f"Stdout: {stdout}")
                
    except Exception as e:
        print(f"❌ Error testing server: {e}")

def test_direct_import():
    """Test if the server module can be imported directly"""
    print("\nTesting direct module import...")
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_test", "mcp-server-test.py")
        mcp_server_test = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_test)
        
        print("✅ Server module imported successfully")
        print(f"✅ Server name: {mcp_server_test.mcp.name}")
        print(f"✅ Available tools: {len(mcp_server_test.mcp.tools)}")
        print(f"✅ Available resources: {len(mcp_server_test.mcp.resources)}")
        print(f"✅ Available prompts: {len(mcp_server_test.mcp.prompts)}")
        
    except Exception as e:
        print(f"❌ Error importing server module: {e}")

if __name__ == "__main__":
    print("MESH Server Startup Test")
    print("=" * 40)
    
    test_direct_import()
    test_server_startup()
    
    print("\n" + "=" * 40)
    print("Test completed!") 