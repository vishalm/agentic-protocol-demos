"""
ACP Server for MESH - Agent Communication Protocol Implementation
Implements the Agent Communication Protocol for agent interoperability
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ACP Message Types
class MessageType(str, Enum):
    TASK = "task"
    RESPONSE = "response"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"

# ACP Message Status
class MessageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# ACP Message Models
class ACPMessage(BaseModel):
    """Base ACP message structure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sender: str
    recipient: Optional[str] = None
    content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: MessageStatus = MessageStatus.PENDING
    error: Optional[str] = None

class TaskMessage(ACPMessage):
    """Task message for requesting agent actions"""
    type: MessageType = MessageType.TASK
    task_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=10)
    timeout: Optional[int] = None  # seconds

class ResponseMessage(ACPMessage):
    """Response message for task results"""
    type: MessageType = MessageType.RESPONSE
    task_id: str
    result: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)

class ErrorMessage(ACPMessage):
    """Error message for task failures"""
    type: MessageType = MessageType.ERROR
    task_id: str
    error_code: str
    error_details: str

# ACP Agent Manifest
class AgentManifest(BaseModel):
    """Agent manifest for discovery and capabilities"""
    id: str
    name: str
    description: str
    version: str
    capabilities: List[str] = Field(default_factory=list)
    supported_tasks: List[str] = Field(default_factory=list)
    supported_formats: List[str] = Field(default_factory=list)
    contact_info: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ACP Server
class ACPServer:
    """ACP-compliant server for agent communication"""
    
    def __init__(self):
        self.app = FastAPI(title="MESH ACP Server", version="1.0.0")
        self.agents: Dict[str, AgentManifest] = {}
        self.tasks: Dict[str, TaskMessage] = {}
        self.message_history: List[ACPMessage] = []
        
        # Register routes
        self._register_routes()
        
        logger.info("ACP Server initialized")
    
    def _register_routes(self):
        """Register ACP API routes"""
        
        @self.app.get("/")
        async def root():
            return {"message": "MESH ACP Server", "version": "1.0.0"}
        
        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        @self.app.post("/agents/register")
        async def register_agent(manifest: AgentManifest):
            """Register a new agent"""
            try:
                self.agents[manifest.id] = manifest
                logger.info(f"Agent registered: {manifest.name} ({manifest.id})")
                return {"status": "success", "agent_id": manifest.id}
            except Exception as e:
                logger.error(f"Failed to register agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents")
        async def list_agents():
            """List all registered agents"""
            return {"agents": [asdict(agent) for agent in self.agents.values()]}
        
        @self.app.get("/agents/{agent_id}")
        async def get_agent(agent_id: str):
            """Get agent details"""
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            return {"agent": asdict(self.agents[agent_id])}
        
        @self.app.post("/messages")
        async def send_message(message: ACPMessage):
            """Send a message to an agent"""
            try:
                # Store message
                self.message_history.append(message)
                
                # Handle different message types
                if message.type == MessageType.TASK:
                    return await self._handle_task(message)
                elif message.type == MessageType.RESPONSE:
                    return await self._handle_response(message)
                elif message.type == MessageType.ERROR:
                    return await self._handle_error(message)
                else:
                    return {"status": "received", "message_id": message.id}
                    
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/messages")
        async def list_messages(limit: int = 100, offset: int = 0):
            """List recent messages"""
            messages = self.message_history[offset:offset + limit]
            return {"messages": [asdict(msg) for msg in messages]}
        
        @self.app.get("/messages/{message_id}")
        async def get_message(message_id: str):
            """Get message details"""
            for msg in self.message_history:
                if msg.id == message_id:
                    return {"message": asdict(msg)}
            raise HTTPException(status_code=404, detail="Message not found")
        
        @self.app.get("/tasks")
        async def list_tasks(status: Optional[MessageStatus] = None):
            """List tasks with optional status filter"""
            tasks = self.tasks.values()
            if status:
                tasks = [t for t in tasks if t.status == status]
            return {"tasks": [asdict(task) for task in tasks]}
        
        @self.app.get("/tasks/{task_id}")
        async def get_task(task_id: str):
            """Get task details"""
            if task_id not in self.tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            return {"task": asdict(self.tasks[task_id])}
        
        @self.app.delete("/tasks/{task_id}")
        async def cancel_task(task_id: str):
            """Cancel a running task"""
            if task_id not in self.tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            
            task = self.tasks[task_id]
            if task.status in [MessageStatus.COMPLETED, MessageStatus.FAILED]:
                raise HTTPException(status_code=400, detail="Cannot cancel completed/failed task")
            
            task.status = MessageStatus.CANCELLED
            logger.info(f"Task cancelled: {task_id}")
            return {"status": "cancelled", "task_id": task_id}
    
    async def _handle_task(self, message: TaskMessage) -> Dict[str, Any]:
        """Handle incoming task messages"""
        try:
            # Store task
            self.tasks[message.id] = message
            
            # Update status
            message.status = MessageStatus.RUNNING
            
            # Process task based on type
            result = await self._process_task(message)
            
            # Create response
            response = ResponseMessage(
                sender="mesh-acp-server",
                recipient=message.sender,
                task_id=message.id,
                result=result
            )
            
            # Update task status
            message.status = MessageStatus.COMPLETED
            
            # Store response
            self.message_history.append(response)
            
            logger.info(f"Task completed: {message.id}")
            return {"status": "task_processed", "task_id": message.id, "response_id": response.id}
            
        except Exception as e:
            # Create error message
            error_msg = ErrorMessage(
                sender="mesh-acp-server",
                recipient=message.sender,
                task_id=message.id,
                error_code="TASK_FAILED",
                error_details=str(e)
            )
            
            # Update task status
            message.status = MessageStatus.FAILED
            message.error = str(e)
            
            # Store error message
            self.message_history.append(error_msg)
            
            logger.error(f"Task failed: {message.id} - {e}")
            return {"status": "task_failed", "task_id": message.id, "error_id": error_msg.id}
    
    async def _process_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Process a task based on its type"""
        task_type = task.task_type.lower()
        
        if task_type == "email_draft":
            return await self._handle_email_draft_task(task)
        elif task_type == "contact_search":
            return await self._handle_contact_search_task(task)
        elif task_type == "template_suggestion":
            return await self._handle_template_suggestion_task(task)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    async def _handle_email_draft_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Handle email draft creation task"""
        params = task.parameters
        recipient = params.get("recipient_email", "")
        subject = params.get("subject", "")
        body = params.get("body", "")
        
        # In a real implementation, this would create an actual email draft
        # For now, we'll simulate the process
        draft = {
            "to": recipient,
            "subject": subject,
            "body": body,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "draft"
        }
        
        return {
            "task_type": "email_draft",
            "result": "Email draft created successfully",
            "draft": draft
        }
    
    async def _handle_contact_search_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Handle contact search task"""
        params = task.parameters
        query = params.get("query", "")
        
        # Simulate contact search
        # In a real implementation, this would search the actual contact database
        contacts = [
            {"name": "John Doe", "email": "john@example.com", "role": "Developer"},
            {"name": "Jane Smith", "email": "jane@example.com", "role": "Designer"}
        ]
        
        if query:
            contacts = [c for c in contacts if query.lower() in c["name"].lower()]
        
        return {
            "task_type": "contact_search",
            "query": query,
            "results": contacts,
            "count": len(contacts)
        }
    
    async def _handle_template_suggestion_task(self, task: TaskMessage) -> Dict[str, Any]:
        """Handle email template suggestion task"""
        params = task.parameters
        context = params.get("context", "general")
        
        # Simulate template suggestions
        templates = {
            "introduction": "Hi [Name], I hope this email finds you well...",
            "follow_up": "Thank you for our conversation yesterday...",
            "networking": "I came across your work and was impressed...",
            "general": "Hello [Name], I'm reaching out because..."
        }
        
        template = templates.get(context.lower(), templates["general"])
        
        return {
            "task_type": "template_suggestion",
            "context": context,
            "template": template,
            "suggestions": list(templates.keys())
        }
    
    async def _handle_response(self, message: ResponseMessage) -> Dict[str, Any]:
        """Handle response messages"""
        logger.info(f"Response received for task: {message.task_id}")
        return {"status": "response_processed", "message_id": message.id}
    
    async def _handle_error(self, message: ErrorMessage) -> Dict[str, Any]:
        """Handle error messages"""
        logger.error(f"Error message received: {message.error_code} - {message.error_details}")
        return {"status": "error_processed", "message_id": message.id}
    
    def run(self, host: str = "127.0.0.1", port: int = 8081):
        """Run the ACP server"""
        logger.info(f"Starting ACP server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

# Create and configure the ACP server
acp_server = ACPServer()

if __name__ == "__main__":
    # Run the ACP server
    acp_server.run()
