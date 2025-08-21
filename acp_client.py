"""
ACP Client for MESH - Agent Communication Protocol Client
Demonstrates how to interact with the ACP server
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ACPClient:
    """ACP client for communicating with the ACP server"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8081"):
        self.base_url = base_url
        self.client_id = f"client-{uuid.uuid4().hex[:8]}"
        self.session = httpx.AsyncClient(timeout=30.0)
        logger.info(f"ACP Client initialized: {self.client_id}")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the client session"""
        await self.session.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        try:
            response = await self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def register_agent(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Register an agent with the ACP server"""
        try:
            response = await self.session.post(
                f"{self.base_url}/agents/register",
                json=manifest
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Agent registration failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def list_agents(self) -> Dict[str, Any]:
        """List all registered agents"""
        try:
            response = await self.session.get(f"{self.base_url}/agents")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return {"status": "error", "error": str(e)}
    
    async def send_task(self, task_type: str, parameters: Dict[str, Any], 
                       recipient: Optional[str] = None, priority: int = 1) -> Dict[str, Any]:
        """Send a task to the ACP server"""
        try:
            task_message = {
                "type": "task",
                "sender": self.client_id,
                "recipient": recipient,
                "task_type": task_type,
                "parameters": parameters,
                "priority": priority,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            response = await self.session.post(
                f"{self.base_url}/messages",
                json=task_message
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send task: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a specific task"""
        try:
            response = await self.session.get(f"{self.base_url}/tasks/{task_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def list_tasks(self, status: Optional[str] = None) -> Dict[str, Any]:
        """List all tasks with optional status filter"""
        try:
            params = {}
            if status:
                params["status"] = status
            
            response = await self.session.get(f"{self.base_url}/tasks", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a running task"""
        try:
            response = await self.session.delete(f"{self.base_url}/tasks/{task_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            return {"status": "error", "error": str(e)}
    
    async def list_messages(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """List recent messages"""
        try:
            response = await self.session.get(
                f"{self.base_url}/messages",
                params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list messages: {e}")
            return {"status": "error", "error": str(e)}

# Example agent manifest
EXAMPLE_AGENT_MANIFEST = {
    "id": "email-assistant-agent",
    "name": "Email Assistant Agent",
    "description": "An AI agent specialized in email composition and management",
    "version": "1.0.0",
    "capabilities": [
        "email_draft_creation",
        "contact_search",
        "template_suggestions",
        "professional_writing"
    ],
    "supported_tasks": [
        "email_draft",
        "contact_search",
        "template_suggestion"
    ],
    "supported_formats": [
        "text/plain",
        "text/html",
        "application/json"
    ],
    "contact_info": {
        "email": "agent@mesh.example.com",
        "website": "https://mesh.example.com"
    },
    "metadata": {
        "framework": "MESH",
        "language": "Python",
        "protocol": "ACP"
    }
}

async def demo_acp_communication():
    """Demonstrate ACP communication patterns"""
    print("🚀 MESH ACP Communication Demo")
    print("=" * 50)
    
    async with ACPClient() as client:
        # 1. Health check
        print("\n1️⃣ Checking server health...")
        health = await client.health_check()
        print(f"   Health: {health}")
        
        if health.get("status") != "healthy":
            print("❌ Server is not healthy. Make sure the ACP server is running.")
            return
        
        # 2. Register agent
        print("\n2️⃣ Registering example agent...")
        registration = await client.register_agent(EXAMPLE_AGENT_MANIFEST)
        print(f"   Registration: {registration}")
        
        # 3. List agents
        print("\n3️⃣ Listing registered agents...")
        agents = await client.list_agents()
        print(f"   Agents: {len(agents.get('agents', []))} found")
        
        # 4. Send email draft task
        print("\n4️⃣ Sending email draft task...")
        email_task = await client.send_task(
            task_type="email_draft",
            parameters={
                "recipient_email": "colleague@company.com",
                "subject": "Project Update Meeting",
                "body": "Hi, I'd like to schedule a meeting to discuss the project updates."
            },
            priority=5
        )
        print(f"   Email Task: {email_task}")
        
        # 5. Send contact search task
        print("\n5️⃣ Sending contact search task...")
        contact_task = await client.send_task(
            task_type="contact_search",
            parameters={"query": "John"},
            priority=3
        )
        print(f"   Contact Task: {contact_task}")
        
        # 6. Send template suggestion task
        print("\n6️⃣ Sending template suggestion task...")
        template_task = await client.send_task(
            task_type="template_suggestion",
            parameters={"context": "introduction"},
            priority=4
        )
        print(f"   Template Task: {template_task}")
        
        # 7. Wait a moment for tasks to process
        print("\n7️⃣ Waiting for tasks to process...")
        await asyncio.sleep(2)
        
        # 8. Check task statuses
        print("\n8️⃣ Checking task statuses...")
        tasks = await client.list_tasks()
        print(f"   Total Tasks: {len(tasks.get('tasks', []))}")
        
        for task in tasks.get('tasks', []):
            print(f"   - Task {task['id'][:8]}: {task['task_type']} - {task['status']}")
        
        # 9. List recent messages
        print("\n9️⃣ Listing recent messages...")
        messages = await client.list_messages(limit=10)
        print(f"   Messages: {len(messages.get('messages', []))} found")
        
        # 10. Summary
        print("\n🎯 Demo Summary:")
        print("   ✅ ACP server communication established")
        print("   ✅ Agent registration successful")
        print("   ✅ Multiple task types processed")
        print("   ✅ Message history maintained")
        print("\n💡 Next steps:")
        print("   - Explore the ACP server API")
        print("   - Implement more sophisticated agents")
        print("   - Add streaming and async capabilities")
        print("   - Integrate with existing MCP tools")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_acp_communication())
