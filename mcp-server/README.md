# MCP (Model Context Protocol) Implementation

## 🔌 Overview

The MCP folder contains the Model Context Protocol implementation for MESH, providing direct integration with AI applications through STDIO transport.

## 📁 Files

- **`mcp-server-test.py`** - Main MCP server implementation
- **`test-mcp-functions.py`** - MCP function testing and validation
- **`validate-config.py`** - MCP configuration generator
- **`mcp-config.json`** - MCP configuration template

## 🚀 Quick Start

### **Start MCP Server**
```bash
# From project root
python mcp/mcp-server-test.py

# Or with uv
uv run python mcp/mcp-server-test.py
```

### **Test MCP Functions**
```bash
# Test all MCP functions
python mcp/test-mcp-functions.py

# Validate configuration
python mcp/validate-config.py
```

## 🛠️ Available Tools

### **Email Management**
- `write_email_draft()` - Create professional email drafts
- `get_email_templates()` - Access email template resources

### **Contact Management**
- `search_contacts()` - Search contact directory
- `get_directory()` - Access full contact database

### **Template System**
- `get_templates()` - Access email templates
- `suggest_templates()` - AI-powered template suggestions

## 📚 Resources

### **Email Templates**
- `email-examples://3-way-intro` - 3-way introduction template
- `email-examples://call-follow-up` - Call follow-up template

### **Contact Directory**
- `directory://all` - Complete contact database

### **System Prompts**
- `prompts://mesh` - MESH assistant prompt template

## 🔧 Configuration

### **MCP Config for AI Applications**
```json
{
  "mcpServers": {
    "MESH": {
      "command": "/path/to/python",
      "args": [
        "mcp/mcp-server-test.py"
      ]
    }
  }
}
```

### **Generate Custom Config**
```bash
python mcp/validate-config.py
```

## 🧪 Testing with MCP Inspector

### **Setup MCP Inspector**
1. Install: `pip install mcp-inspector`
2. Launch: `mcp-inspector`
3. Configure:
   - Transport: STDIO
   - Command: `python mcp/mcp-server-test.py`
   - Working Directory: Project root

### **Test Commands**
```bash
# List tools
tools/list

# List resources
resources/list

# Test email tool
tools/call
{
  "name": "write_email_draft",
  "arguments": {
    "recipient_email": "test@example.com",
    "subject": "Test Email",
    "body": "Hello from MESH!"
  }
}
```

## 🔍 Debugging

### **Common Issues**
- **Import errors**: Ensure FastMCP is installed (`pip install fastmcp`)
- **File not found**: Check relative paths from project root
- **Tool execution**: Verify tool parameters match expected schema

### **Logging**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python mcp/mcp-server-test.py
```

## 🔗 Integration

### **With AI Applications**
- **Claude Desktop**: Add to MCP configuration
- **Cursor**: Integrate via MCP settings
- **Custom Apps**: Use MCP client libraries

### **With Other Protocols**
- MCP tools can trigger A2A workflows
- MCP resources shared with ACP agents
- Unified through shared core services

## 📊 Performance

### **Optimizations**
- Lazy loading of templates and contacts
- Cached prompt processing
- Efficient tool execution

### **Monitoring**
- Tool execution time tracking
- Resource access patterns
- Error rate monitoring

---

**For more information, see the [main README](../README.md) or [shared components](../shared/README.md).**
