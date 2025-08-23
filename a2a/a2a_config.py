"""
A2A Protocol Configuration for MESH Server
"""

from typing import Dict, List, Any
from pydantic import BaseModel

class A2AServerConfig(BaseModel):
    """Configuration for the A2A server"""
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = True
    log_level: str = "info"
    
    # A2A Protocol settings
    protocol_version: str = "2024-11-05"
    agent_name: str = "MESH"
    agent_version: str = "1.0.0"
    agent_description: str = "Model Exchange Server Handler with A2A Integration"
    
    # Agent capabilities
    supported_methods: List[str] = [
        "initialize",
        "capabilities", 
        "methods",
        "discover_agents",
        "delegate_task",
        "collaborate",
        "get_contact_info",
        "suggest_email_template",
        "write_email_draft"
    ]
    
    # Communication settings
    max_message_size: int = 1024 * 1024  # 1MB
    timeout_seconds: int = 30
    retry_attempts: int = 3
    
    # Discovery settings
    discovery_enabled: bool = True
    registry_url: str = "https://registry.a2aprotocol.ai"
    heartbeat_interval: int = 60  # seconds
    
    # Security settings
    enable_auth: bool = False
    api_key_required: bool = False
    allowed_origins: List[str] = ["*"]

class AgentCapabilities(BaseModel):
    """MESH agent capabilities definition"""
    name: str = "MESH"
    version: str = "1.0.0"
    description: str = "Professional email management and networking assistant"
    
    capabilities: Dict[str, Any] = {
        "email_management": {
            "description": "Create, edit, and manage professional emails",
            "methods": ["write_email_draft", "suggest_email_template"],
            "supported_formats": ["text", "html"],
            "templates_available": ["introduction", "follow-up", "networking"]
        },
        "contact_management": {
            "description": "Access and search professional contact directory",
            "methods": ["get_contact_info", "search_contacts"],
            "data_sources": ["directory.csv", "external_crm"],
            "search_capabilities": ["name", "email", "company", "expertise"]
        },
        "professional_networking": {
            "description": "Facilitate strategic introductions and connections",
            "methods": ["create_introduction", "suggest_connections"],
            "network_analysis": True,
            "opportunity_matching": True
        },
        "collaboration": {
            "description": "Work with other A2A agents for enhanced capabilities",
            "methods": ["delegate_task", "collaborate", "coordinate_workflow"],
            "agent_discovery": True,
            "task_orchestration": True
        }
    }
    
    communication_protocols: List[str] = ["A2A", "MCP"]
    supported_transports: List[str] = ["HTTP", "WebSocket", "STDIO"]
    
    performance_metrics: Dict[str, Any] = {
        "response_time_ms": 500,
        "throughput_requests_per_second": 100,
        "concurrent_connections": 50,
        "memory_usage_mb": 128
    }

class A2AMessageConfig(BaseModel):
    """A2A message configuration"""
    max_message_length: int = 10000
    supported_content_types: List[str] = ["text/plain", "application/json", "text/markdown"]
    compression_enabled: bool = True
    encryption_enabled: bool = False
    
    # Message routing
    routing_strategy: str = "direct"  # direct, broadcast, multicast
    priority_levels: List[str] = ["low", "normal", "high", "urgent"]
    
    # Error handling
    retry_on_failure: bool = True
    max_retry_attempts: int = 3
    backoff_strategy: str = "exponential"  # linear, exponential, fixed

# Default configuration instances
default_server_config = A2AServerConfig()
default_agent_capabilities = AgentCapabilities()
default_message_config = A2AMessageConfig()

# Configuration validation
def validate_config() -> bool:
    """Validate the A2A configuration"""
    try:
        # Validate server config
        server_config = A2AServerConfig()
        
        # Validate agent capabilities
        agent_caps = AgentCapabilities()
        
        # Validate message config
        msg_config = A2AMessageConfig()
        
        print("✅ A2A configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ A2A configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    print("A2A Configuration Module")
    print("=" * 30)
    
    # Validate configuration
    if validate_config():
        print("\nConfiguration Summary:")
        print(f"Server: {default_server_config.host}:{default_server_config.port}")
        print(f"Agent: {default_agent_capabilities.name} v{default_agent_capabilities.version}")
        print(f"Methods: {len(default_server_config.supported_methods)} supported")
        print(f"Capabilities: {len(default_agent_capabilities.capabilities)} areas")
    else:
        print("Configuration validation failed!")
