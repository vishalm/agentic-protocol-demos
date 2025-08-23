#!/usr/bin/env python3
"""
Test script for MESH MCP functions
Run this to verify all functions work correctly before testing with MCP Inspector
"""

import sys
import os

# Add current directory to path to import the MCP server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mesh_prompt():
    """Test the mesh prompt function"""
    print("🧪 Testing mesh prompt function...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_test", os.path.join(os.path.dirname(__file__), "mcp-server-test.py"))
        mcp_server_test = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_test)
        mesh = mcp_server_test.mesh
        result = mesh("Test User", "Software Developer")
        print(f"✅ Prompt generated successfully ({len(result)} characters)")
        print(f"   Preview: {result[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Error testing mesh prompt: {e}")
        return False

def test_email_draft():
    """Test the email draft function"""
    print("\n🧪 Testing email draft function...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_test", os.path.join(os.path.dirname(__file__), "mcp-server-test.py"))
        mcp_server_test = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_test)
        write_email_draft = mcp_server_test.write_email_draft
        result = write_email_draft(
            "test@example.com",
            "Test Subject",
            "This is a test email body for testing purposes."
        )
        print(f"✅ Email draft created successfully")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Error testing email draft: {e}")
        return False

def test_contact_info():
    """Test the contact info function"""
    print("\n🧪 Testing contact info function...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_test", os.path.join(os.path.dirname(__file__), "mcp-server-test.py"))
        mcp_server_test = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_test)
        get_contact_info = mcp_server_test.get_contact_info
        
        # Test getting all contacts
        all_contacts = get_contact_info()
        print(f"✅ All contacts retrieved successfully")
        print(f"   Count: {all_contacts.get('count', 0)} contacts")
        
        # Test searching for a specific contact
        if all_contacts.get('count', 0) > 0:
            first_contact = all_contacts.get('contacts', [{}])[0]
            search_name = first_contact.get('Name', 'Test').split()[0]  # Get first name
            search_result = get_contact_info(search_name)
            print(f"✅ Contact search successful for '{search_name}'")
            print(f"   Found: {search_result.get('count', 0)} matching contacts")
        
        return True
    except Exception as e:
        print(f"❌ Error testing contact info: {e}")
        return False

def test_email_template():
    """Test the email template suggestion function"""
    print("\n🧪 Testing email template suggestions...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_test", os.path.join(os.path.dirname(__file__), "mcp-server-test.py"))
        mcp_server_test = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_test)
        suggest_email_template = mcp_server_test.suggest_email_template
        
        # Test different contexts
        contexts = ["introduction", "follow-up", "networking", "general"]
        
        for context in contexts:
            result = suggest_email_template(context)
            print(f"✅ {context.title()} template generated successfully")
            print(f"   Status: {result.get('status')}")
            if 'template' in result:
                print(f"   Template length: {len(result['template'])} characters")
        
        return True
    except Exception as e:
        print(f"❌ Error testing email templates: {e}")
        return False

def test_resources():
    """Test the resource functions"""
    print("\n🧪 Testing resource functions...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server_test", os.path.join(os.path.dirname(__file__), "mcp-server-test.py"))
        mcp_server_test = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mcp_server_test)
        write_3way_intro = mcp_server_test.write_3way_intro
        write_call_followup = mcp_server_test.write_call_followup
        get_directory = mcp_server_test.get_directory
        
        # Test 3-way intro resource
        intro_resource = write_3way_intro()
        print(f"✅ 3-way intro resource loaded ({len(intro_resource)} characters)")
        
        # Test call follow-up resource
        followup_resource = write_call_followup()
        print(f"✅ Call follow-up resource loaded ({len(followup_resource)} characters)")
        
        # Test directory resource
        directory_resource = get_directory()
        print(f"✅ Directory resource loaded ({len(directory_resource)} characters)")
        
        return True
    except Exception as e:
        print(f"❌ Error testing resources: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 MESH MCP Function Test Suite")
    print("=" * 40)
    
    tests = [
        test_mesh_prompt,
        test_email_draft,
        test_contact_info,
        test_email_template,
        test_resources
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server is ready for testing with MCP Inspector.")
        print("\n💡 Next steps:")
        print("   1. Install MCP Inspector: pip install mcp-inspector")
        print("   2. Run: mcp-inspector")
        print("   3. Configure to use: python mcp-server-test.py")
        print("   4. Test the server functionality")
    else:
        print("⚠️  Some tests failed. Please fix the issues before testing with MCP Inspector.")
        sys.exit(1)

if __name__ == "__main__":
    main()
