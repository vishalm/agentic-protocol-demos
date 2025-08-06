#!/usr/bin/env python3
"""
Test MCP server functions directly without running the full server
"""

import sys
import os
import importlib.util

# Add current directory to path so we can import the server functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the functions from the MCP server
spec = importlib.util.spec_from_file_location("mcp_server_test", "mcp-server-test.py")
mcp_server_test = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_server_test)

# Extract functions
mesh = mcp_server_test.mesh
write_3way_intro = mcp_server_test.write_3way_intro
write_call_followup = mcp_server_test.write_call_followup
get_directory = mcp_server_test.get_directory
write_email_draft = mcp_server_test.write_email_draft
get_contact_info = mcp_server_test.get_contact_info
suggest_email_template = mcp_server_test.suggest_email_template

def test_prompt():
    """Test the MESH prompt function"""
    print("Testing MESH prompt...")
    try:
        result = mesh("Test User", "Software Engineer")
        print(f"✅ Prompt generated successfully ({len(result)} characters)")
        print(f"First 100 chars: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error testing prompt: {e}")

def test_resources():
    """Test the resource functions"""
    print("\nTesting resources...")
    
    # Test 3-way intro
    try:
        result = write_3way_intro()
        print(f"✅ 3-way intro template loaded ({len(result)} characters)")
    except Exception as e:
        print(f"❌ Error loading 3-way intro: {e}")
    
    # Test call follow-up
    try:
        result = write_call_followup()
        print(f"✅ Call follow-up template loaded ({len(result)} characters)")
    except Exception as e:
        print(f"❌ Error loading call follow-up: {e}")
    
    # Test directory
    try:
        result = get_directory()
        print(f"✅ Directory loaded ({len(result)} characters)")
    except Exception as e:
        print(f"❌ Error loading directory: {e}")

def test_tools():
    """Test the tool functions"""
    print("\nTesting tools...")
    
    # Test email draft
    try:
        result = write_email_draft("test@example.com", "Test Subject", "Test body content")
        print(f"✅ Email draft created: {result['status']}")
        print(f"   Recipient: {result['recipient']}")
        print(f"   Subject: {result['subject']}")
    except Exception as e:
        print(f"❌ Error creating email draft: {e}")
    
    # Test contact info
    try:
        result = get_contact_info()
        print(f"✅ Contact info retrieved: {result['count']} contacts")
        if result['count'] > 0:
            print(f"   First contact: {result['contacts'][0].get('Name', 'N/A')}")
    except Exception as e:
        print(f"❌ Error getting contact info: {e}")
    
    # Test email template suggestion
    try:
        result = suggest_email_template("introduction")
        print(f"✅ Template suggestion: {result.get('suggested_template', {}).get('description', 'None')}")
    except Exception as e:
        print(f"❌ Error suggesting template: {e}")

if __name__ == "__main__":
    print("MESH MCP Server Function Test")
    print("=" * 50)
    
    test_prompt()
    test_resources()
    test_tools()
    
    print("\n" + "=" * 50)
    print("All function tests completed!") 