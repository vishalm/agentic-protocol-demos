#!/usr/bin/env python3
"""
Test script for MESH ACP functions
Run this to verify all ACP functions work correctly
"""

import asyncio
import sys
import os

# Add current directory to path to import the ACP modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_acp_server_import():
    """Test that the ACP server can be imported"""
    print("🧪 Testing ACP server import...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("acp_server", "acp_server.py")
        acp_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(acp_server)
        print("✅ ACP server imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing ACP server: {e}")
        return False

async def test_acp_client_import():
    """Test that the ACP client can be imported"""
    print("\n🧪 Testing ACP client import...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("acp_client", "acp_client.py")
        acp_client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(acp_client)
        print("✅ ACP client imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing ACP client: {e}")
        return False

async def test_acp_models():
    """Test ACP data models"""
    print("\n🧪 Testing ACP data models...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("acp_server", "acp_server.py")
        acp_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(acp_server)
        
        # Test message creation
        from datetime import datetime, timezone
        
        # Test TaskMessage
        task_msg = acp_server.TaskMessage(
            sender="test-client",
            task_type="email_draft",
            parameters={"test": "value"}
        )
        print(f"✅ TaskMessage created: {task_msg.id}")
        
        # Test ResponseMessage
        response_msg = acp_server.ResponseMessage(
            sender="test-server",
            recipient="test-client",
            task_id=task_msg.id,
            result={"status": "success"}
        )
        print(f"✅ ResponseMessage created: {response_msg.id}")
        
        # Test ErrorMessage
        error_msg = acp_server.ErrorMessage(
            sender="test-server",
            recipient="test-client",
            task_id=task_msg.id,
            error_code="TEST_ERROR",
            error_details="Test error message"
        )
        print(f"✅ ErrorMessage created: {error_msg.id}")
        
        # Test AgentManifest
        manifest = acp_server.AgentManifest(
            id="test-agent",
            name="Test Agent",
            description="A test agent",
            version="1.0.0"
        )
        print(f"✅ AgentManifest created: {manifest.id}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing ACP models: {e}")
        return False

async def test_acp_server_creation():
    """Test ACP server creation"""
    print("\n🧪 Testing ACP server creation...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("acp_server", "acp_server.py")
        acp_server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(acp_server)
        
        # Create server instance
        server = acp_server.ACPServer()
        print(f"✅ ACP server created successfully")
        print(f"   FastAPI app: {server.app.title}")
        print(f"   Routes: {len(server.app.routes)} registered")
        
        return True
    except Exception as e:
        print(f"❌ Error testing ACP server creation: {e}")
        return False

async def test_acp_client_creation():
    """Test ACP client creation"""
    print("\n🧪 Testing ACP client creation...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("acp_client", "acp_client.py")
        acp_client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(acp_client)
        
        # Create client instance
        client = acp_client.ACPClient("http://127.0.0.1:8081")
        print(f"✅ ACP client created successfully")
        print(f"   Client ID: {client.client_id}")
        print(f"   Base URL: {client.base_url}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing ACP client creation: {e}")
        return False

async def test_acp_agent_manifest():
    """Test ACP agent manifest"""
    print("\n🧪 Testing ACP agent manifest...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("acp_client", "acp_client.py")
        acp_client = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(acp_client)
        
        # Test manifest structure
        manifest = acp_client.EXAMPLE_AGENT_MANIFEST
        print(f"✅ Example agent manifest loaded")
        print(f"   Agent ID: {manifest['id']}")
        print(f"   Name: {manifest['name']}")
        print(f"   Capabilities: {len(manifest['capabilities'])}")
        print(f"   Supported Tasks: {len(manifest['supported_tasks'])}")
        
        # Validate required fields
        required_fields = ['id', 'name', 'description', 'version']
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ All required fields present")
        return True
    except Exception as e:
        print(f"❌ Error testing ACP agent manifest: {e}")
        return False

async def main():
    """Run all ACP tests"""
    print("🚀 MESH ACP Function Test Suite")
    print("=" * 50)
    
    tests = [
        test_acp_server_import,
        test_acp_client_import,
        test_acp_models,
        test_acp_server_creation,
        test_acp_client_creation,
        test_acp_agent_manifest
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ACP server is ready for testing.")
        print("\n💡 Next steps:")
        print("   1. Start the ACP server: python acp_server.py")
        print("   2. Test with the client: python acp_client.py")
        print("   3. Explore the REST API at http://127.0.0.1:8081")
        print("   4. Check the interactive docs at http://127.0.0.1:8081/docs")
    else:
        print("⚠️  Some tests failed. Please fix the issues before testing the ACP server.")
        sys.exit(1)

if __name__ == "__main__":
    # Run all tests
    asyncio.run(main())
