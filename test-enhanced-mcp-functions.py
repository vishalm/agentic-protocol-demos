#!/usr/bin/env python3
"""
Test script for MESH Enhanced MCP functions
Tests all MCP features: Ping, Sampling, Elicitations, Roots, Auth, Logging
"""

import asyncio
import sys
import os
import json

# Add current directory to path to import the MCP server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_ping():
    """Test ping functionality"""
    print("🧪 Testing Ping functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # Test ping
        result = await mcp_server_enhanced.ping()
        print(f"✅ Ping successful: {result['status']}")
        print(f"   Server: {result['server']} v{result['version']}")
        return True
    except Exception as e:
        print(f"❌ Error testing ping: {e}")
        return False

async def test_sampling():
    """Test sampling functionality"""
    print("\n🧪 Testing Sampling functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # Test text sampling
        result = await mcp_server_enhanced.sample_text(
            "Write a professional email introduction",
            max_tokens=200,
            temperature=0.7,
            model="demo-model"
        )
        print(f"✅ Text sampling successful ({len(result)} characters)")
        print(f"   Preview: {result[:100]}...")
        
        # Test image sampling
        image_result = await mcp_server_enhanced.sample_image(
            "Professional business card design",
            size="1024x1024",
            quality="high"
        )
        print(f"✅ Image sampling successful")
        print(f"   Result: {image_result}")
        return True
    except Exception as e:
        print(f"❌ Error testing sampling: {e}")
        return False

async def test_elicitation():
    """Test elicitation functionality"""
    print("\n🧪 Testing Elicitation functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # Test elicitation
        result = await mcp_server_enhanced.elicit_user_input(
            "What is your preferred communication style?",
            input_type="select",
            required=True,
            options=["Formal", "Casual", "Professional", "Friendly"]
        )
        print(f"✅ Elicitation successful")
        print(f"   ID: {result['id']}")
        print(f"   Message: {result['message']}")
        print(f"   Type: {result['input_type']}")
        print(f"   Options: {result.get('options', [])}")
        return True
    except Exception as e:
        print(f"❌ Error testing elicitation: {e}")
        return False

async def test_roots():
    """Test roots functionality"""
    print("\n🧪 Testing Roots functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # Test get roots
        roots = await mcp_server_enhanced.get_roots()
        print(f"✅ Get roots successful: {len(roots)} roots found")
        for root in roots:
            print(f"   - {root['name']}: {root['uri']} ({root['type']})")
        
        # Test add root
        add_result = await mcp_server_enhanced.add_root("test_root", f"file://{os.getcwd()}")
        print(f"✅ Add root successful: {add_result['status']}")
        return True
    except Exception as e:
        print(f"❌ Error testing roots: {e}")
        return False

async def test_auth():
    """Test authentication functionality"""
    print("\n🧪 Testing Authentication functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # Test authentication
        auth_result = await mcp_server_enhanced.authenticate({
            "username": "testuser",
            "password": "testpass"
        })
        print(f"✅ Authentication successful: {auth_result['status']}")
        print(f"   User: {auth_result['user_id']}")
        print(f"   Session: {auth_result['session_id']}")
        print(f"   Permissions: {auth_result['permissions']}")
        
        # Test auth check
        check_result = await mcp_server_enhanced.check_auth()
        print(f"✅ Auth check successful: {check_result['authenticated']}")
        
        # Test logout
        logout_result = await mcp_server_enhanced.logout()
        print(f"✅ Logout successful: {logout_result['status']}")
        return True
    except Exception as e:
        print(f"❌ Error testing auth: {e}")
        return False

async def test_logging():
    """Test logging functionality"""
    print("\n🧪 Testing Logging functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # Import LoggingLevel
        from mcp.types import LoggingLevel
        
        # Test logging
        log_result = await mcp_server_enhanced.log_message(
            LoggingLevel.INFO,
            "Test log message from enhanced MCP server",
            {"test_data": "sample_value", "timestamp": "2024-01-01T00:00:00Z"}
        )
        print(f"✅ Logging successful: {log_result['status']}")
        print(f"   Level: {log_result['level']}")
        print(f"   Timestamp: {log_result['timestamp']}")
        return True
    except Exception as e:
        print(f"❌ Error testing logging: {e}")
        return False

async def test_enhanced_tools():
    """Test enhanced tools functionality"""
    print("\n🧪 Testing Enhanced Tools functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # First authenticate
        await mcp_server_enhanced.authenticate({
            "username": "testuser",
            "password": "testpass"
        })
        
        # Test enhanced email draft
        email_result = mcp_server_enhanced.write_email_draft_enhanced(
            "test@example.com",
            "Test Subject",
            "Test body content",
            template_type="introduction",
            priority="high",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"]
        )
        print(f"✅ Enhanced email draft successful: {email_result['status']}")
        print(f"   Draft ID: {email_result['draft']['draft_id']}")
        print(f"   Priority: {email_result['draft']['priority']}")
        
        # Test enhanced contact search
        contact_result = mcp_server_enhanced.get_contact_info_enhanced(
            name="Sarah",
            company="AI",
            expertise="machine learning",
            limit=5
        )
        print(f"✅ Enhanced contact search successful: {contact_result['status']}")
        print(f"   Found: {contact_result['count']} contacts")
        print(f"   Filters: {contact_result['filters_applied']}")
        
        # Test enhanced template suggestion
        template_result = mcp_server_enhanced.suggest_email_template_enhanced(
            context="introduction",
            recipient_type="client",
            urgency="high",
            tone="professional"
        )
        print(f"✅ Enhanced template suggestion successful: {template_result['status']}")
        print(f"   Context: {template_result['context']}")
        print(f"   Tone: {template_result['tone']}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing enhanced tools: {e}")
        return False

async def test_enhanced_prompts():
    """Test enhanced prompts functionality"""
    print("\n🧪 Testing Enhanced Prompts functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # Test enhanced prompt
        prompt_result = mcp_server_enhanced.mesh_enhanced(
            "Test User",
            "Software Developer",
            "Working on AI integration project"
        )
        print(f"✅ Enhanced prompt successful ({len(prompt_result)} characters)")
        print(f"   Preview: {prompt_result[:150]}...")
        return True
    except Exception as e:
        print(f"❌ Error testing enhanced prompts: {e}")
        return False

async def test_enhanced_resources():
    """Test enhanced resources functionality"""
    print("\n🧪 Testing Enhanced Resources functionality...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_enhanced", "mcp-server-enhanced.py")
        mcp_server_enhanced = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_enhanced)
        
        # Test enhanced 3-way intro
        intro_result = mcp_server_enhanced.get_3way_intro()
        print(f"✅ Enhanced 3-way intro successful ({len(intro_result)} characters)")
        print(f"   Contains metadata: {'---' in intro_result}")
        
        # Test enhanced follow-up
        followup_result = mcp_server_enhanced.get_call_followup()
        print(f"✅ Enhanced follow-up successful ({len(followup_result)} characters)")
        print(f"   Contains metadata: {'---' in followup_result}")
        
        # Test enhanced contacts
        contacts_result = mcp_server_enhanced.get_contacts()
        print(f"✅ Enhanced contacts successful ({len(contacts_result)} characters)")
        print(f"   Contains search help: {'Search Instructions' in contacts_result}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing enhanced resources: {e}")
        return False

async def main():
    """Run all enhanced MCP tests"""
    print("🚀 MESH Enhanced MCP Function Test Suite")
    print("=" * 60)
    
    tests = [
        ("Ping", test_ping),
        ("Sampling", test_sampling),
        ("Elicitation", test_elicitation),
        ("Roots", test_roots),
        ("Authentication", test_auth),
        ("Logging", test_logging),
        ("Enhanced Tools", test_enhanced_tools),
        ("Enhanced Prompts", test_enhanced_prompts),
        ("Enhanced Resources", test_enhanced_resources)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if await test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced MCP tests passed! Server is ready for MCP Inspector.")
        print("\n💡 Next steps:")
        print("   1. Start the enhanced server: python mcp-server-enhanced.py")
        print("   2. Open MCP Inspector")
        print("   3. Configure with: python mcp-server-enhanced.py")
        print("   4. Test all features: Ping, Sampling, Elicitations, Roots, Auth")
    else:
        print("⚠️  Some tests failed. Please fix the issues before testing with MCP Inspector.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
