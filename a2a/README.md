# A2A (Agent-to-Agent) Protocol Implementation

## 🤝 Overview

The A2A folder contains the Agent-to-Agent protocol implementation for MESH, enabling multi-agent collaboration and workflow orchestration through HTTP and WebSocket transport.

## 📁 Files

- **`a2a_server.py`** - Main A2A protocol server
- **`a2a_config.py`** - A2A server configuration and settings

## 🚀 Quick Start

### **Start A2A Server**
```bash
# From project root
python a2a/a2a_server.py

# Server will be available at http://127.0.0.1:8080
```

### **Check Server Status**
```bash
# Health check
curl http://127.0.0.1:8080/health

# Agent card
curl http://127.0.0.1:8080/.well-known/agent-card
```

## 🌐 Endpoints

### **Core A2A Endpoints**
- **`/`** - Main A2A protocol endpoint (POST)
- **`/.well-known/agent-card`** - Agent capabilities and skills (GET)
- **`/health`** - Server health check (GET)
- **`/ws`** - WebSocket for real-time communication

### **Protocol Endpoints**
- **`/a2a`** - A2A protocol handler
- **`/agents`** - Agent discovery and management
- **`/workflows`** - Workflow orchestration

## 🔧 Configuration

### **Server Settings**
```python
# Default configuration in a2a_config.py
default_server_config = ServerConfig(
    host="127.0.0.1",
    port=8080,
    registry_url="http://127.0.0.1:8081",
    heartbeat_interval=30,
    discovery_enabled=True
)
```

### **Environment Variables**
```bash
# Custom port
export A2A_PORT=8081

# Custom host
export A2A_HOST=0.0.0.0

# Registry URL
export A2A_REGISTRY_URL=http://localhost:8081
```

## 🧪 Testing with A2A Inspector

### **Setup A2A Inspector**
1. Navigate to: [A2A Inspector](https://a2aprotocol.ai/inspector)
2. Enter server URL: `http://127.0.0.1:8080`
3. Click **Connect**

### **Test Communication**
```json
{
  "jsonrpc": "2.0",
  "id": "test-1",
  "method": "message/send",
  "params": {
    "message": "Hello from A2A Inspector!",
    "recipient": "mesh_agent"
  }
}
```

## 🔍 Agent Capabilities

### **Core Skills**
- **Email Management**: Compose and manage professional emails
- **Contact Management**: Search and manage contact database
- **Template System**: Access and suggest email templates
- **Workflow Orchestration**: Coordinate multi-agent tasks

### **Agent Discovery**
- Automatic agent registration
- Capability-based discovery
- Health monitoring and status tracking

## 🔄 Workflow Orchestration

### **Task Delegation**
```python
# Example workflow
workflow = {
    "type": "email_composition",
    "steps": [
        "contact_lookup",
        "template_selection",
        "content_generation",
        "tone_analysis"
    ],
    "agents": ["contact_agent", "template_agent", "writing_agent"]
}
```

### **Agent Coordination**
- Parallel task execution
- Result aggregation
- Error handling and retry logic
- Progress tracking

## 🔗 Integration

### **With MCP Protocol**
- A2A workflows can be triggered by MCP tool calls
- Shared resource access between protocols
- Unified agent management

### **With ACP Protocol**
- Agent registration and discovery
- Task routing and execution
- Message history and analytics

### **With External Systems**
- RESTful API for integration
- WebSocket for real-time updates
- Standardized message formats

## 📊 Monitoring

### **Health Checks**
```bash
# Server health
curl http://127.0.0.1:8080/health

# Agent status
curl http://127.0.0.1:8080/agents/status
```

### **Logging**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python a2a/a2a_server.py
```

## 🚨 Troubleshooting

### **Common Issues**
- **Port conflicts**: Change port with `export A2A_PORT=8081`
- **Connection refused**: Ensure server is running
- **Agent discovery**: Check registry connectivity

### **Debug Commands**
```bash
# Check server process
ps aux | grep a2a_server

# Test connectivity
telnet 127.0.0.1 8080

# View logs
tail -f a2a_server.log
```

## 🔒 Security

### **Authentication**
- Agent registration validation
- Message signing and verification
- Rate limiting and access control

### **Network Security**
- CORS configuration
- Input validation
- Error message sanitization

## 📈 Performance

### **Optimizations**
- Connection pooling
- Message batching
- Async processing
- Caching strategies

### **Scalability**
- Horizontal scaling support
- Load balancing ready
- Stateless design

---

**For more information, see the [main README](../README.md) or [shared components](../shared/README.md).**
