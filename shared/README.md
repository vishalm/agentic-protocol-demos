# Shared Components

## 🔧 Overview

The shared folder contains common components used across all MESH protocols, providing unified functionality for agent management, task orchestration, and system integration.

## 📁 Files

- **`agent_manager.py`** - Agent discovery and management system
- **`task_orchestrator.py`** - Workflow orchestration and task delegation
- **`agent_capabilities.py`** - Agent skill definitions and capabilities
- **`hybrid_server.py`** - Multi-protocol server implementation

## 🚀 Quick Start

### **Initialize Shared Components**
```python
from shared.agent_manager import AgentManager
from shared.task_orchestrator import TaskOrchestrator
from shared.agent_capabilities import mesh_capabilities

# Initialize components
agent_manager = AgentManager()
task_orchestrator = TaskOrchestrator(agent_manager)
```

### **Start Hybrid Server**
```bash
# From project root
python shared/hybrid_server.py

# Or use the management script
./run.sh start
```

## 🔍 Agent Manager

### **Core Functions**
```python
# Discover agents
agents = await agent_manager.discover_agents(
    capability_filter="email_management",
    protocol_version="1.0"
)

# Register agent
await agent_manager.register_agent(agent_info)

# Get agent status
status = await agent_manager.get_agent_status("email_agent")
```

### **Agent Discovery**
- **Capability-based filtering** - Find agents by skills
- **Protocol version matching** - Ensure compatibility
- **Health monitoring** - Track agent availability
- **Performance metrics** - Response time and reliability

### **Agent Registry**
```python
# Agent information structure
agent_info = {
    "name": "email_agent",
    "version": "1.0.0",
    "capabilities": ["email_draft", "template_suggestion"],
    "endpoint": "http://localhost:5000",
    "protocols": ["MCP", "A2A", "ACP"],
    "status": "online"
}
```

## 🔄 Task Orchestrator

### **Workflow Management**
```python
# Create workflow
workflow = {
    "id": "email_composition_001",
    "type": "email_composition",
    "steps": [
        {"step": "contact_lookup", "agent": "contact_agent"},
        {"step": "template_selection", "agent": "template_agent"},
        {"step": "content_generation", "agent": "writing_agent"}
    ],
    "priority": "high",
    "timeout": 300
}

# Execute workflow
result = await task_orchestrator.execute_workflow(workflow)
```

### **Task Delegation**
- **Parallel execution** - Run independent tasks simultaneously
- **Dependency management** - Handle task prerequisites
- **Error handling** - Retry logic and fallback strategies
- **Progress tracking** - Real-time workflow status

### **Workflow Types**
- **Sequential** - Tasks executed in order
- **Parallel** - Independent tasks run simultaneously
- **Conditional** - Tasks based on conditions
- **Loop** - Repeated task execution

## 🎯 Agent Capabilities

### **Core Skills**
```python
# Email management capabilities
email_capabilities = {
    "email_draft": "Create professional email drafts",
    "template_suggestion": "Suggest appropriate email templates",
    "tone_analysis": "Analyze and adjust email tone",
    "grammar_check": "Validate email grammar and style"
}

# Contact management capabilities
contact_capabilities = {
    "contact_search": "Search contact database",
    "contact_validation": "Validate contact information",
    "relationship_analysis": "Analyze professional relationships"
}
```

### **Capability Registration**
```python
# Register new capability
mesh_capabilities.register_capability(
    name="custom_task",
    description="Custom task implementation",
    parameters=["param1", "param2"],
    return_type="string"
)
```

## 🔗 Hybrid Server

### **Multi-Protocol Support**
The hybrid server provides unified access to all three protocols:

- **MCP** - STDIO transport for AI applications
- **A2A** - HTTP/WebSocket for multi-agent communication
- **ACP** - RESTful API for enterprise integration

### **Configuration**
```python
# Server configuration
server_config = {
    "mcp": {"enabled": True, "transport": "stdio"},
    "a2a": {"enabled": True, "port": 8080},
    "acp": {"enabled": True, "port": 8081}
}
```

### **Start Hybrid Server**
```bash
# Start all protocols
python shared/hybrid_server.py

# Or start specific protocols
export MCP_ENABLED=true
export A2A_ENABLED=true
export ACP_ENABLED=false
python shared/hybrid_server.py
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Agent discovery
export AGENT_DISCOVERY_ENABLED=true
export AGENT_REGISTRY_URL=http://localhost:8081

# Task orchestration
export MAX_CONCURRENT_TASKS=10
export TASK_TIMEOUT=300

# Server settings
export MCP_ENABLED=true
export A2A_ENABLED=true
export ACP_ENABLED=true
```

### **Configuration Files**
```python
# Load configuration
from shared.config import load_config
config = load_config("config.yaml")

# Access settings
mcp_enabled = config.get("mcp.enabled", True)
a2a_port = config.get("a2a.port", 8080)
```

## 📊 Monitoring & Logging

### **Health Checks**
```python
# Check component health
health = {
    "agent_manager": agent_manager.health_check(),
    "task_orchestrator": task_orchestrator.health_check(),
    "hybrid_server": hybrid_server.health_check()
}
```

### **Logging Configuration**
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Component-specific loggers
agent_logger = logging.getLogger("agent_manager")
orchestrator_logger = logging.getLogger("task_orchestrator")
```

## 🔒 Security

### **Agent Authentication**
- **Identity verification** - Validate agent credentials
- **Capability checking** - Ensure authorized access
- **Rate limiting** - Prevent abuse and overload
- **Audit logging** - Track all operations

### **Data Protection**
- **Message encryption** - Secure communication
- **Input validation** - Prevent malicious input
- **Access control** - Role-based permissions
- **Privacy compliance** - Data protection standards

## 🚨 Troubleshooting

### **Common Issues**
- **Agent discovery fails**: Check registry connectivity
- **Task execution errors**: Verify agent capabilities
- **Protocol conflicts**: Ensure unique ports
- **Import errors**: Check Python path and dependencies

### **Debug Commands**
```bash
# Check component status
python -c "from shared.agent_manager import AgentManager; am = AgentManager(); print(am.health_check())"

# Test task orchestration
python -c "from shared.task_orchestrator import TaskOrchestrator; to = TaskOrchestrator(); print(to.health_check())"

# Verify hybrid server
python shared/hybrid_server.py --help
```

### **Performance Issues**
- **High memory usage**: Check for memory leaks in agent management
- **Slow task execution**: Monitor agent response times
- **Protocol bottlenecks**: Check network and port configurations

## 📈 Performance & Optimization

### **Caching Strategies**
- **Agent capability cache** - Reduce discovery overhead
- **Task result cache** - Avoid redundant execution
- **Connection pooling** - Reuse network connections
- **Resource pooling** - Efficient resource management

### **Scaling Considerations**
- **Horizontal scaling** - Multiple server instances
- **Load balancing** - Distribute workload
- **Database optimization** - Efficient data storage
- **Async processing** - Non-blocking operations

---

**For more information, see the [main README](../README.md) or individual protocol READMEs.**
