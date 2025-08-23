"""
Agent Manager for MESH A2A Integration
Handles agent discovery, registration, and communication
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
import websockets

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from a2a.a2a_config import default_server_config
from shared.agent_capabilities import mesh_capabilities

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(str, Enum):
    """Agent connection status"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"

class AgentConnectionType(str, Enum):
    """Type of agent connection"""
    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"

@dataclass
class AgentInfo:
    """Information about a discovered agent"""
    name: str
    version: str
    description: str
    endpoint: str
    connection_type: AgentConnectionType
    capabilities: List[str]
    protocols: List[str]
    status: AgentStatus
    last_seen: datetime
    response_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TaskDelegation:
    """Task delegation information"""
    delegation_id: str
    task_type: str
    target_agent: str
    task_data: Dict[str, Any]
    priority: str
    status: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AgentManager:
    """Manages agent discovery, registration, and communication"""
    
    def __init__(self):
        self.discovered_agents: Dict[str, AgentInfo] = {}
        self.registered_agents: Set[str] = set()
        self.task_delegations: Dict[str, TaskDelegation] = {}
        self.agent_registry_url = default_server_config.registry_url
        self.heartbeat_interval = default_server_config.heartbeat_interval
        self.discovery_enabled = default_server_config.discovery_enabled
        
        # Performance tracking
        self.agent_response_times: Dict[str, List[int]] = {}
        self.failed_connections: Dict[str, int] = {}
        
        # Async tasks
        self.discovery_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        logger.info("Agent Manager initialized")
    
    async def start(self):
        """Start the agent manager services"""
        if self.discovery_enabled:
            self.discovery_task = asyncio.create_task(self._discovery_loop())
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("Agent Manager services started")
    
    async def stop(self):
        """Stop the agent manager services"""
        if self.discovery_task:
            self.discovery_task.cancel()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        logger.info("Agent Manager services stopped")
    
    async def discover_agents(self, capability_filter: Optional[str] = None, 
                            protocol_version: Optional[str] = None,
                            max_results: int = 50) -> Dict[str, Any]:
        """Discover agents in the A2A network"""
        try:
            logger.info(f"Discovering agents with filter: {capability_filter}")
            
            # Simulate agent discovery (in real implementation, this would query the registry)
            discovered_agents = await self._query_agent_registry(capability_filter, protocol_version)
            
            # Filter results
            if capability_filter:
                discovered_agents = [
                    agent for agent in discovered_agents 
                    if capability_filter.lower() in [cap.lower() for cap in agent.get('capabilities', [])]
                ]
            
            # Limit results
            if max_results:
                discovered_agents = discovered_agents[:max_results]
            
            # Update local cache
            for agent_data in discovered_agents:
                agent_info = self._create_agent_info(agent_data)
                self.discovered_agents[agent_info.name] = agent_info
            
            return {
                "agents": [asdict(agent) for agent in discovered_agents],
                "count": len(discovered_agents),
                "discovery_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "filter_applied": capability_filter,
                    "protocol_version": protocol_version,
                    "total_discovered": len(self.discovered_agents)
                }
            }
            
        except Exception as e:
            logger.error(f"Error discovering agents: {e}")
            return {
                "agents": [],
                "count": 0,
                "error": str(e),
                "discovery_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "error": True
                }
            }
    
    async def delegate_task(self, task_type: str, target_agent: str, 
                          task_data: Dict[str, Any], priority: str = "normal",
                          timeout: int = 30) -> Dict[str, Any]:
        """Delegate a task to another agent"""
        try:
            logger.info(f"Delegating task '{task_type}' to agent '{target_agent}'")
            
            # Check if target agent is available
            if target_agent not in self.discovered_agents:
                return {
                    "delegation_id": None,
                    "status": "failed",
                    "error": f"Target agent '{target_agent}' not found"
                }
            
            agent_info = self.discovered_agents[target_agent]
            if agent_info.status != AgentStatus.ONLINE:
                return {
                    "delegation_id": None,
                    "status": "failed",
                    "error": f"Target agent '{target_agent}' is {agent_info.status}"
                }
            
            # Create delegation record
            delegation_id = f"deleg_{int(time.time())}_{hash(target_agent) % 1000}"
            delegation = TaskDelegation(
                delegation_id=delegation_id,
                task_type=task_type,
                target_agent=target_agent,
                task_data=task_data,
                priority=priority,
                status="pending",
                created_at=datetime.now(),
                estimated_completion=datetime.now() + timedelta(seconds=timeout)
            )
            
            self.task_delegations[delegation_id] = delegation
            
            # Execute task delegation
            result = await self._execute_task_delegation(delegation, agent_info)
            
            return {
                "delegation_id": delegation_id,
                "status": delegation.status,
                "estimated_completion": delegation.estimated_completion.isoformat() if delegation.estimated_completion else None,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error delegating task: {e}")
            return {
                "delegation_id": None,
                "status": "failed",
                "error": str(e)
            }
    
    async def collaborate(self, collaboration_type: str, partner_agent: str,
                         shared_context: Dict[str, Any], 
                         collaboration_goals: List[str]) -> Dict[str, Any]:
        """Initiate collaboration with another agent"""
        try:
            logger.info(f"Initiating collaboration '{collaboration_type}' with agent '{partner_agent}'")
            
            # Check if partner agent is available
            if partner_agent not in self.discovered_agents:
                return {
                    "collaboration_id": None,
                    "status": "failed",
                    "error": f"Partner agent '{partner_agent}' not found"
                }
            
            agent_info = self.discovered_agents[partner_agent]
            if agent_info.status != AgentStatus.ONLINE:
                return {
                    "collaboration_id": None,
                    "status": "failed",
                    "error": f"Partner agent '{partner_agent}' is {agent_info.status}"
                }
            
            # Create collaboration session
            collaboration_id = f"collab_{int(time.time())}_{hash(partner_agent) % 1000}"
            shared_workspace = f"workspace_{collaboration_id}"
            
            # Initialize collaboration
            collaboration_result = await self._initialize_collaboration(
                collaboration_id, collaboration_type, partner_agent, 
                shared_context, collaboration_goals, agent_info
            )
            
            return {
                "collaboration_id": collaboration_id,
                "status": "active" if collaboration_result else "failed",
                "shared_workspace": shared_workspace,
                "partner_agent": partner_agent,
                "collaboration_type": collaboration_type
            }
            
        except Exception as e:
            logger.error(f"Error initiating collaboration: {e}")
            return {
                "collaboration_id": None,
                "status": "failed",
                "error": str(e)
            }
    
    async def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a specific agent"""
        if agent_name not in self.discovered_agents:
            return None
        
        agent_info = self.discovered_agents[agent_name]
        return {
            "name": agent_info.name,
            "status": agent_info.status,
            "last_seen": agent_info.last_seen.isoformat(),
            "response_time_ms": agent_info.response_time_ms,
            "capabilities": agent_info.capabilities,
            "endpoint": agent_info.endpoint
        }
    
    def get_available_agents(self, capability: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available agents, optionally filtered by capability"""
        available_agents = []
        
        for agent_info in self.discovered_agents.values():
            if agent_info.status == AgentStatus.ONLINE:
                if capability is None or capability.lower() in [cap.lower() for cap in agent_info.capabilities]:
                    available_agents.append(asdict(agent_info))
        
        return available_agents
    
    async def _discovery_loop(self):
        """Continuous agent discovery loop"""
        while True:
            try:
                await self.discover_agents()
                await asyncio.sleep(300)  # Discover every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _heartbeat_loop(self):
        """Continuous heartbeat loop to check agent status"""
        while True:
            try:
                await self._check_agent_health()
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
    
    async def _query_agent_registry(self, capability_filter: Optional[str], 
                                  protocol_version: Optional[str]) -> List[Dict[str, Any]]:
        """Query the agent registry for available agents"""
        # Simulate registry query - in real implementation, this would make HTTP calls
        # For now, return mock data
        
        mock_agents = [
            {
                "name": "EmailBot",
                "version": "1.0.0",
                "description": "AI-powered email writing and editing assistant",
                "endpoint": "https://emailbot.a2a.example.com",
                "connection_type": "http",
                "capabilities": ["email_management", "writing_assistance"],
                "protocols": ["A2A"],
                "status": "online"
            },
            {
                "name": "GrammarBot",
                "version": "1.2.0",
                "description": "Grammar and style checking for professional communication",
                "endpoint": "https://grammarbot.a2a.example.com",
                "connection_type": "http",
                "capabilities": ["grammar_check", "style_analysis"],
                "protocols": ["A2A"],
                "status": "online"
            },
            {
                "name": "CRMConnector",
                "version": "1.1.0",
                "description": "CRM integration and contact enrichment",
                "endpoint": "https://crm.a2a.example.com",
                "connection_type": "http",
                "capabilities": ["contact_management", "crm_integration"],
                "protocols": ["A2A"],
                "status": "online"
            },
            {
                "name": "NetworkAnalyzer",
                "version": "1.0.0",
                "description": "Professional network analysis and opportunity identification",
                "endpoint": "https://network.a2a.example.com",
                "connection_type": "http",
                "capabilities": ["network_analysis", "opportunity_matching"],
                "protocols": ["A2A"],
                "status": "online"
            }
        ]
        
        # Filter by capability if specified
        if capability_filter:
            mock_agents = [
                agent for agent in mock_agents
                if capability_filter.lower() in [cap.lower() for cap in agent.get('capabilities', [])]
            ]
        
        return mock_agents
    
    def _create_agent_info(self, agent_data: Dict[str, Any]) -> AgentInfo:
        """Create AgentInfo object from registry data"""
        return AgentInfo(
            name=agent_data.get('name', 'Unknown'),
            version=agent_data.get('version', '1.0.0'),
            description=agent_data.get('description', ''),
            endpoint=agent_data.get('endpoint', ''),
            connection_type=AgentConnectionType(agent_data.get('connection_type', 'http')),
            capabilities=agent_data.get('capabilities', []),
            protocols=agent_data.get('protocols', []),
            status=AgentStatus(agent_data.get('status', 'offline')),
            last_seen=datetime.now(),
            metadata=agent_data.get('metadata', {})
        )
    
    async def _execute_task_delegation(self, delegation: TaskDelegation, 
                                     agent_info: AgentInfo) -> Optional[Dict[str, Any]]:
        """Execute a task delegation to a target agent"""
        try:
            # Simulate task execution
            logger.info(f"Executing task delegation {delegation.delegation_id}")
            
            # Update status
            delegation.status = "in_progress"
            
            # Simulate task processing time
            await asyncio.sleep(1)
            
            # Simulate successful completion
            delegation.status = "completed"
            delegation.result = {
                "task_type": delegation.task_type,
                "executed_by": agent_info.name,
                "completion_time": datetime.now().isoformat(),
                "result_data": f"Task '{delegation.task_type}' completed successfully"
            }
            
            return delegation.result
            
        except Exception as e:
            logger.error(f"Error executing task delegation: {e}")
            delegation.status = "failed"
            delegation.error = str(e)
            return None
    
    async def _initialize_collaboration(self, collaboration_id: str, 
                                      collaboration_type: str, partner_agent: str,
                                      shared_context: Dict[str, Any], 
                                      collaboration_goals: List[str],
                                      agent_info: AgentInfo) -> bool:
        """Initialize a collaboration session with a partner agent"""
        try:
            logger.info(f"Initializing collaboration {collaboration_id}")
            
            # Simulate collaboration initialization
            await asyncio.sleep(0.5)
            
            # In real implementation, this would establish a shared workspace
            # and coordinate with the partner agent
            
            logger.info(f"Collaboration {collaboration_id} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing collaboration: {e}")
            return False
    
    async def _check_agent_health(self):
        """Check the health of discovered agents"""
        for agent_name, agent_info in list(self.discovered_agents.items()):
            try:
                # Simulate health check
                if agent_info.connection_type == AgentConnectionType.HTTP:
                    # In real implementation, make HTTP health check
                    await asyncio.sleep(0.1)  # Simulate network delay
                    
                    # Simulate random status changes for demo
                    import random
                    if random.random() < 0.1:  # 10% chance of status change
                        new_status = random.choice(list(AgentStatus))
                        agent_info.status = new_status
                        logger.info(f"Agent {agent_name} status changed to {new_status}")
                
                agent_info.last_seen = datetime.now()
                
            except Exception as e:
                logger.error(f"Health check failed for agent {agent_name}: {e}")
                agent_info.status = AgentStatus.ERROR
                self.failed_connections[agent_name] = self.failed_connections.get(agent_name, 0) + 1

# Global instance
agent_manager = AgentManager()

if __name__ == "__main__":
    print("Agent Manager Module")
    print("=" * 30)
    
    async def test_agent_manager():
        """Test the agent manager functionality"""
        print("Testing Agent Manager...")
        
        # Start the manager
        await agent_manager.start()
        
        # Discover agents
        print("\n1. Discovering agents...")
        discovery_result = await agent_manager.discover_agents()
        print(f"Discovered {discovery_result['count']} agents")
        
        # Get available agents
        print("\n2. Available agents:")
        available = agent_manager.get_available_agents()
        for agent in available:
            print(f"  - {agent['name']}: {agent['description']}")
        
        # Test task delegation
        if available:
            print("\n3. Testing task delegation...")
            target_agent = available[0]['name']
            delegation_result = await agent_manager.delegate_task(
                "test_task", target_agent, {"data": "test"}, "normal"
            )
            print(f"Delegation result: {delegation_result}")
        
        # Test collaboration
        if available:
            print("\n4. Testing collaboration...")
            partner_agent = available[0]['name']
            collaboration_result = await agent_manager.collaborate(
                "test_collaboration", partner_agent, 
                {"context": "test"}, ["goal1", "goal2"]
            )
            print(f"Collaboration result: {collaboration_result}")
        
        # Stop the manager
        await agent_manager.stop()
        print("\n✅ Agent Manager test completed!")
    
    # Run the test
    asyncio.run(test_agent_manager())
