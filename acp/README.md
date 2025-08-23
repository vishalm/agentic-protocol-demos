# ACP (Agent Communication Protocol) Implementation

## 🌐 Overview

The ACP folder contains the Agent Communication Protocol implementation for MESH, providing standardized agent interoperability through a RESTful HTTP API.

## 📁 Files

- **`acp_server.py`** - Main ACP protocol server
- **`acp_client.py`** - ACP client for testing and integration
- **`test-acp-functions.py`** - ACP function testing and validation

## 🚀 Quick Start

### **Start ACP Server**
```bash
# From project root
python acp/acp_server.py

# Server will be available at http://127.0.0.1:8081
# Interactive API docs at http://127.0.0.1:8081/docs
```

### **Test ACP Functions**
```bash
# Run comprehensive tests
python acp/test-acp-functions.py

# Test client-server communication
python acp/acp_client.py
```

## 🌐 API Endpoints

### **Core Endpoints**
- **`GET /health`** - Server health check
- **`POST /agents/register`** - Register new agents
- **`GET /agents`** - List all registered agents
- **`POST /messages`** - Send messages to agents
- **`GET /tasks`** - List and monitor tasks
- **`DELETE /tasks/{id}`** - Cancel running tasks

### **API Documentation**
- **Swagger UI**: http://127.0.0.1:8081/docs
- **ReDoc**: http://127.0.0.1:8081/redoc
- **OpenAPI Schema**: http://127.0.0.1:8081/openapi.json

## 🔧 Configuration

### **Server Settings**
```python
# Default configuration
ACP_HOST = "127.0.0.1"
ACP_PORT = 8081
ACP_DEBUG = True
ACP_LOG_LEVEL = "INFO"
```

### **Environment Variables**
```bash
# Custom port
export ACP_PORT=8082

# Custom host
export ACP_HOST=0.0.0.0

# Debug mode
export ACP_DEBUG=true
```

## 🧪 Testing

### **Quick API Tests**
```bash
# Health check
curl http://127.0.0.1:8081/health

# List agents
curl http://127.0.0.1:8081/agents

# Send test task
curl -X POST http://127.0.0.1:8081/messages \
  -H "Content-Type: application/json" \
  -d '{
    "type": "task",
    "sender": "test-client",
    "task_type": "email_draft",
    "parameters": {
      "recipient_email": "test@example.com",
      "subject": "Test Email",
      "body": "This is a test email."
    }
  }'
```

### **Python Client Testing**
```python
import asyncio
from acp_client import ACPClient, EXAMPLE_AGENT_MANIFEST

async def test_acp():
    async with ACPClient() as client:
        # Register agent
        result = await client.register_agent(EXAMPLE_AGENT_MANIFEST)
        print(f"Agent registered: {result}")
        
        # Send task
        task = await client.send_task("email_draft", {
            "recipient_email": "test@example.com",
            "subject": "Test",
            "body": "Hello!"
        })
        print(f"Task sent: {task}")

asyncio.run(test_acp())
```

## 🔍 Agent Management

### **Agent Registration**
```json
{
  "name": "email_agent",
  "version": "1.0.0",
  "description": "Professional email composition agent",
  "capabilities": ["email_draft", "template_suggestion"],
  "endpoint": "http://localhost:5000",
  "metadata": {
    "author": "MESH Team",
    "contact": "support@mesh.ai"
  }
}
```

### **Agent Discovery**
- Automatic capability detection
- Health monitoring
- Performance metrics
- Load balancing support

## 📋 Task Management

### **Supported Task Types**
- **`email_draft`** - Create professional emails
- **`contact_search`** - Search contact database
- **`template_suggestion`** - Suggest email templates
- **`custom_task`** - Extensible for any capability

### **Task Lifecycle**
1. **Pending** - Task received and queued
2. **Running** - Task execution in progress
3. **Completed** - Task finished successfully
4. **Failed** - Task execution failed
5. **Cancelled** - Task cancelled by user

### **Task Parameters**
```json
{
  "task_type": "email_draft",
  "priority": "high",
  "timeout": 300,
  "parameters": {
    "recipient_email": "user@example.com",
    "subject": "Meeting Follow-up",
    "tone": "professional"
  }
}
```

## 🔄 Message Routing

### **Message Types**
- **Task Messages** - Execute specific tasks
- **Response Messages** - Task results and updates
- **Error Messages** - Error reporting and debugging
- **Status Messages** - Progress updates and monitoring

### **Routing Logic**
- Capability-based routing
- Load balancing
- Failover handling
- Priority queuing

## 📊 Monitoring & Analytics

### **Health Metrics**
```bash
# Server health
curl http://127.0.0.1:8081/health

# Agent status
curl http://127.0.0.1:8081/agents/status

# Task statistics
curl http://127.0.0.1:8081/tasks/stats
```

### **Performance Tracking**
- Response time monitoring
- Throughput metrics
- Error rate tracking
- Resource utilization

## 🔒 Security

### **Authentication & Authorization**
- Agent identity verification
- Capability-based access control
- Rate limiting and throttling
- Input validation and sanitization

### **Data Protection**
- Message encryption
- Secure agent communication
- Audit logging
- Privacy compliance

## 🔗 Integration

### **With MCP Protocol**
- MCP tools can trigger ACP tasks
- Shared resource access
- Unified agent management

### **With A2A Protocol**
- Agent registration and discovery
- Workflow coordination
- Message routing

### **With External Systems**
- RESTful API for integration
- Webhook support
- Standardized message formats
- Enterprise system compatibility

## 🚨 Troubleshooting

### **Common Issues**
- **Port conflicts**: Change port with `export ACP_PORT=8082`
- **Agent registration fails**: Check agent manifest format
- **Task execution errors**: Verify agent capabilities and endpoints

### **Debug Commands**
```bash
# Check server process
ps aux | grep acp_server

# Test connectivity
telnet 127.0.0.1 8081

# View server logs
tail -f acp_server.log
```

### **Error Codes**
- **400** - Bad Request (invalid parameters)
- **404** - Agent or task not found
- **500** - Internal server error
- **503** - Service unavailable

## 📈 Performance & Scalability

### **Optimizations**
- Async request processing
- Connection pooling
- Response caching
- Efficient task queuing

### **Scaling Strategies**
- Horizontal scaling
- Load balancing
- Database optimization
- CDN integration

---

**For more information, see the [main README](../README.md) or [shared components](../shared/README.md).**
