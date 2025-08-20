"""
A2A Protocol Server for MESH Integration
Implements A2A protocol alongside existing MCP functionality
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from a2a_config import default_server_config
from agent_capabilities import mesh_capabilities
from agent_manager import agent_manager
from task_orchestrator import task_orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# A2A Protocol Models
class A2ARequest(BaseModel):
    """A2A protocol request model"""
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: Optional[Dict[str, Any]] = None

class A2AResponse(BaseModel):
    """A2A protocol response model"""
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class A2AError(BaseModel):
    """A2A protocol error model"""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

class A2AServer:
    """A2A Protocol Server Implementation"""
    
    def __init__(self):
        self.app = FastAPI(
            title="MESH A2A Server",
            description="A2A Protocol Server for MESH Integration",
            version="1.0.0"
        )
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins for development
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
        
        # Server state
        self.connected_clients: List[WebSocket] = []
        self.server_start_time = datetime.now()
        
        logger.info("A2A Server initialized")
    
    def _register_routes(self):
        """Register A2A protocol routes"""
        
        @self.app.get("/")
        async def root():
            """Server root endpoint"""
            return {
                "name": "MESH A2A Server",
                "version": "1.0.0",
                "protocol": "A2A",
                "status": "running",
                "uptime": (datetime.now() - self.server_start_time).total_seconds()
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "agent_manager": "running",
                "task_orchestrator": "running"
            }
        
        @self.app.post("/a2a")
        async def a2a_endpoint(request: A2ARequest):
            """Main A2A protocol endpoint"""
            try:
                logger.info(f"Handling A2A request: {request.method}")
                result = await self._handle_a2a_request(request)
                return result
            except Exception as e:
                logger.error(f"Error handling A2A request: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                }
               
        @self.app.post("/")
        async def a2a_protocol_root(request: dict):
            """A2A protocol root endpoint for compatibility"""
            try:
                # Log incoming request for debugging
                logger.info(f"🔍 Incoming request to root endpoint: {request.get('method', 'NO_METHOD')}")
                logger.info(f"🔍 Request ID: {request.get('id', 'NO_ID')}")
                logger.info(f"🔍 Request params: {request.get('params', {})}")
                
                # Handle both A2A protocol and direct method calls
                if "method" in request:
                    # Use the new direct method handler for A2A Inspector compatibility
                    logger.info(f"🔍 Calling _handle_direct_method for method: {request['method']}")
                    result = await self._handle_direct_method(request)
                    logger.info(f"🔍 _handle_direct_method returned: {result}")
                    # Return raw response to bypass FastAPI validation
                    from fastapi.responses import JSONResponse
                    return JSONResponse(content=result)
                else:
                    # Direct method call
                    logger.info(f"🔍 No method found, calling _handle_direct_method anyway")
                    result = await self._handle_direct_method(request)
                    logger.info(f"🔍 _handle_direct_method returned: {result}")
                    # Return raw response to bypass FastAPI validation
                    from fastapi.responses import JSONResponse
                    return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"❌ Error handling A2A protocol request: {e}")
                logger.error(f"❌ Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", "unknown"),
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                }
                from fastapi.responses import JSONResponse
                return JSONResponse(content=error_response)
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time A2A communication"""
            await websocket.accept()
            self.connected_clients.append(websocket)
            
            try:
                while True:
                    # Receive message
                    data = await websocket.receive_text()
                    request_data = json.loads(data)
                    request = A2ARequest(**request_data)
                    
                    # Handle request
                    result = await self._handle_a2a_request(request)
                    
                    # Send response
                    response = A2AResponse(
                        id=request.id,
                        result=result
                    )
                    await websocket.send_text(response.json())
                    
            except WebSocketDisconnect:
                self.connected_clients.remove(websocket)
                logger.info("WebSocket client disconnected")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                if websocket in self.connected_clients:
                    self.connected_clients.remove(websocket)
        
        @self.app.get("/agents")
        async def list_agents():
            """List discovered agents"""
            try:
                agents = await agent_manager.discover_agents()
                return agents
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents/{agent_name}")
        async def get_agent_status(agent_name: str):
            """Get status of a specific agent"""
            try:
                status = await agent_manager.get_agent_status(agent_name)
                if not status:
                    raise HTTPException(status_code=404, detail="Agent not found")
                return status
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/delegate")
        async def delegate_task(request: Dict[str, Any]):
            """Delegate a task to an agent"""
            try:
                result = await agent_manager.delegate_task(
                    task_type=request.get("task_type"),
                    target_agent=request.get("target_agent"),
                    task_data=request.get("task_data", {}),
                    priority=request.get("priority", "normal")
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/collaborate")
        async def collaborate(request: Dict[str, Any]):
            """Initiate collaboration with an agent"""
            try:
                result = await agent_manager.collaborate(
                    collaboration_type=request.get("collaboration_type"),
                    partner_agent=request.get("partner_agent"),
                    shared_context=request.get("shared_context", {}),
                    collaboration_goals=request.get("collaboration_goals", [])
                )
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/workflows")
        async def list_workflows():
            """List available workflow templates"""
            try:
                templates = task_orchestrator.get_templates()
                return {"templates": templates}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/workflows")
        async def create_workflow(request: Dict[str, Any]):
            """Create a new workflow"""
            try:
                workflow_id = await task_orchestrator.create_workflow(
                    template_name=request.get("template_name"),
                    input_data=request.get("input_data", {})
                )
                return {"workflow_id": workflow_id}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/workflows/{workflow_id}/execute")
        async def execute_workflow(workflow_id: str):
            """Execute a workflow"""
            try:
                result = await task_orchestrator.execute_workflow(workflow_id)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/workflows/{workflow_id}")
        async def get_workflow_status(workflow_id: str):
            """Get workflow status"""
            try:
                status = task_orchestrator.get_workflow_status(workflow_id)
                if not status:
                    raise HTTPException(status_code=404, detail="Workflow not found")
                return status
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/.well-known/agent-card.json")
        async def get_agent_card():
            """Get agent card for A2A Inspector discovery"""
            try:
                from agent_capabilities import mesh_capabilities
                
                agent_card = {
                    "name": "mesh_agent",
                    "version": "1.0.0",
                    "description": "Professional email management and networking assistant with multi-agent collaboration capabilities.",
                    "url": f"http://{default_server_config.host}:{default_server_config.port}/",
                    "protocolVersion": "0.3.0",
                    "preferredTransport": "JSONRPC",
                    "capabilities": {
                        "streaming": False,
                        "collaboration": True,
                        "workflow": True
                    },
                    "defaultInputModes": [
                        "text",
                        "text/plain",
                        "application/json"
                    ],
                    "defaultOutputModes": [
                        "text",
                        "text/plain",
                        "application/json"
                    ],
                    "skills": [
                        {
                            "id": "email_management",
                            "name": "Email Composition & Management",
                            "description": "Create professional emails and manage email templates",
                            "examples": [
                                "Write a professional follow-up email",
                                "Generate an email template for networking"
                            ],
                            "tags": [
                                "email",
                                "composition",
                                "templates",
                                "professional"
                            ]
                        },
                        {
                            "id": "contact_management",
                            "name": "Contact Database Operations",
                            "description": "Search and retrieve contact information from database",
                            "examples": [
                                "Find contact information for John Smith",
                                "Search for contacts in the tech industry"
                            ],
                            "tags": [
                                "contacts",
                                "database",
                                "search",
                                "relationships"
                            ]
                        },
                        {
                            "id": "professional_networking",
                            "name": "Strategic Networking",
                            "description": "Build professional relationships and networking strategies",
                            "examples": [
                                "Create a 3-way introduction strategy",
                                "Develop networking follow-up plan"
                            ],
                            "tags": [
                                "networking",
                                "relationships",
                                "strategy",
                                "professional"
                            ]
                        },
                        {
                            "id": "agent_collaboration",
                            "name": "Multi-Agent Collaboration",
                            "description": "Coordinate with other AI agents for complex workflows",
                            "examples": [
                                "Delegate email writing to specialized agent",
                                "Collaborate with multiple agents for project"
                            ],
                            "tags": [
                                "collaboration",
                                "workflow",
                                "orchestration",
                                "multi-agent"
                            ]
                        }
                    ]
                }
                
                return agent_card
                
            except Exception as e:
                logger.error(f"Error generating agent card: {e}")
                raise HTTPException(status_code=500, detail=str(e))
               
        @self.app.get("/.well-known/ai-plugin.json")
        async def get_ai_plugin():
            """Get AI plugin manifest for compatibility"""
            try:
                from agent_capabilities import mesh_capabilities
                
                ai_plugin = {
                    "schema_version": "v1",
                    "name_for_model": "MESH A2A Agent",
                    "name_for_human": "MESH - Professional Email & Networking Assistant",
                    "description_for_model": "MESH is a professional email management and networking assistant that can collaborate with other AI agents to provide enhanced capabilities.",
                    "description_for_human": "Professional email management, contact management, and networking with multi-agent collaboration capabilities.",
                    "auth": {
                        "type": "none"
                    },
                    "api": {
                        "type": "openapi",
                        "url": f"http://{default_server_config.host}:{default_server_config.port}/openapi.json"
                    },
                    "logo_url": "https://github.com/vishalm/agentic-protocol-demos/raw/main/resources/MESH-I-1.png",
                    "contact_email": "vishal.mishra@example.com",
                    "legal_info_url": "https://github.com/vishalm/agentic-protocol-demos/blob/main/LICENSE"
                }
                
                return ai_plugin
                
            except Exception as e:
                logger.error(f"Error generating AI plugin manifest: {e}")
                raise HTTPException(status_code=500, detail=str(e))
               
        @self.app.get("/openapi.json")
        async def get_openapi_schema():
            """Get OpenAPI schema for the A2A server"""
            try:
                # Return a simplified OpenAPI schema for A2A Inspector
                openapi_schema = {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "MESH A2A Server",
                        "version": "1.0.0",
                        "description": "A2A Protocol Server for MESH Integration"
                    },
                    "servers": [
                        {
                            "url": f"http://{default_server_config.host}:{default_server_config.port}",
                            "description": "MESH A2A Server"
                        }
                    ],
                    "paths": {
                        "/a2a": {
                            "post": {
                                "summary": "A2A Protocol Endpoint",
                                "description": "Main A2A protocol endpoint for all methods",
                                "requestBody": {
                                    "required": True,
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "type": "object",
                                                "properties": {
                                                    "jsonrpc": {"type": "string"},
                                                    "id": {"type": "string"},
                                                    "method": {"type": "string"},
                                                    "params": {"type": "object"}
                                                }
                                            }
                                        }
                                    }
                                },
                                "responses": {
                                    "200": {
                                        "description": "Successful A2A response"
                                    }
                                }
                            }
                        },
                        "/agents": {
                            "get": {
                                "summary": "List Discovered Agents",
                                "description": "Get list of discovered A2A agents"
                            }
                        },
                        "/workflows": {
                            "get": {
                                "summary": "List Workflow Templates",
                                "description": "Get available workflow templates"
                            },
                            "post": {
                                "summary": "Create Workflow",
                                "description": "Create a new workflow from template"
                            }
                        }
                    }
                }
                
                return openapi_schema
                
            except Exception as e:
                logger.error(f"Error generating OpenAPI schema: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _handle_a2a_request(self, request: A2ARequest) -> Dict[str, Any]:
        """Handle A2A protocol requests"""
        method = request.method
        params = request.params or {}
        
        logger.info(f"Handling A2A request: {method}")
        
        try:
            if method == "initialize":
                return await self._handle_initialize(params)
            elif method == "capabilities":
                return await self._handle_capabilities(params)
            elif method == "methods":
                return await self._handle_methods(params)
            elif method == "discover_agents":
                return await self._handle_discover_agents(params)
            elif method == "delegate_task":
                return await self._handle_delegate_task(params)
            elif method == "collaborate":
                return await self._handle_collaborate(params)
            elif method == "get_contact_info":
                return await self._handle_get_contact_info(params)
            elif method == "suggest_email_template":
                return await self._handle_suggest_email_template(params)
            elif method == "write_email_draft":
                return await self._handle_write_email_draft(params)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Error handling method {method}: {e}")
            raise
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize method"""
        client_info = params.get("client_info", {})
        client_capabilities = params.get("capabilities", {})
        
        logger.info(f"Initializing connection with client: {client_info.get('name', 'Unknown')}")
        
        return {
            "agent_info": {
                "name": mesh_capabilities.agent_info["name"],
                "version": mesh_capabilities.agent_info["version"],
                "description": mesh_capabilities.agent_info["description"],
                "protocols": mesh_capabilities.agent_info["protocols"],
                "transports": mesh_capabilities.agent_info["transports"]
            },
            "capabilities": {
                "email_management": True,
                "contact_management": True,
                "professional_networking": True,
                "collaboration": True
            },
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capabilities method"""
        return {
            "capabilities": mesh_capabilities.capabilities,
            "methods": mesh_capabilities.list_methods(),
            "data_sources": ["directory.csv", "email-examples/", "prompts/"],
            "performance_metrics": list(mesh_capabilities.capabilities.values())[0].performance_metrics if mesh_capabilities.capabilities else {}
        }
    
    async def _handle_methods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle methods method"""
        methods_info = {}
        for method_name in mesh_capabilities.list_methods():
            method = mesh_capabilities.get_method_info(method_name)
            if method:
                methods_info[method_name] = {
                    "description": method.description,
                    "parameters": method.parameters,
                    "returns": method.returns,
                    "examples": method.examples
                }
        
        return {"methods": methods_info}
    
    async def _handle_discover_agents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle discover_agents method"""
        capability_filter = params.get("capability_filter")
        protocol_version = params.get("protocol_version")
        max_results = params.get("max_results", 50)
        
        return await agent_manager.discover_agents(
            capability_filter=capability_filter,
            protocol_version=protocol_version,
            max_results=max_results
        )
    
    async def _handle_delegate_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delegate_task method"""
        task_type = params.get("task_type")
        target_agent = params.get("target_agent")
        task_data = params.get("task_data", {})
        priority = params.get("priority", "normal")
        timeout = params.get("timeout", 30)
        
        if not all([task_type, target_agent]):
            raise ValueError("task_type and target_agent are required")
        
        return await agent_manager.delegate_task(
            task_type=task_type,
            target_agent=target_agent,
            task_data=task_data,
            priority=priority,
            timeout=timeout
        )
    
    async def _handle_collaborate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaborate method"""
        collaboration_type = params.get("collaboration_type")
        partner_agent = params.get("partner_agent")
        shared_context = params.get("shared_context", {})
        collaboration_goals = params.get("collaboration_goals", [])
        
        if not all([collaboration_type, partner_agent]):
            raise ValueError("collaboration_type and partner_agent are required")
        
        return await agent_manager.collaborate(
            collaboration_type=collaboration_type,
            partner_agent=partner_agent,
            shared_context=shared_context,
            collaboration_goals=collaboration_goals
        )
    
    async def _handle_get_contact_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_contact_info method using MESH capabilities"""
        # This would integrate with the existing MESH contact functionality
        # For now, return mock data
        
        name = params.get("name")
        email = params.get("email")
        company = params.get("company")
        expertise = params.get("expertise")
        
        # Simulate contact lookup
        await asyncio.sleep(0.2)
        
        if name:
            return {
                "contacts": [
                    {
                        "name": name,
                        "email": f"{name.lower().replace(' ', '.')}@example.com",
                        "company": "Example Corp",
                        "expertise": "AI/ML"
                    }
                ],
                "count": 1,
                "search_criteria": {"name": name}
            }
        else:
            return {
                "contacts": [
                    {
                        "name": "Sarah Chen",
                        "email": "sarah@innovateai.tech",
                        "company": "InnovateAI",
                        "expertise": "AI Solutions"
                    }
                ],
                "count": 1,
                "search_criteria": {}
            }
    
    async def _handle_suggest_email_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle suggest_email_template method using MESH capabilities"""
        context = params.get("context", "general")
        recipient_type = params.get("recipient_type", "colleague")
        urgency = params.get("urgency", "normal")
        
        # Simulate template suggestion
        await asyncio.sleep(0.1)
        
        templates = {
            "introduction": {
                "template": "email-examples://3-way-intro",
                "description": "Professional 3-way introduction template",
                "best_for": "Connecting two people who could benefit from knowing each other"
            },
            "follow-up": {
                "template": "email-examples://call-follow-up",
                "description": "Call follow-up template with action items",
                "best_for": "Following up after meetings or calls"
            }
        }
        
        context_lower = context.lower()
        suggested_template = None
        
        for key, template_info in templates.items():
            if key in context_lower:
                suggested_template = template_info
                break
        
        return {
            "suggested_template": suggested_template,
            "context": context,
            "available_templates": list(templates.keys()),
            "message": "Template suggestion based on context"
        }
    
    async def _handle_write_email_draft(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle write_email_draft method using MESH capabilities"""
        recipient_email = params.get("recipient_email")
        subject = params.get("subject")
        body = params.get("body")
        template_type = params.get("template_type")
        priority = params.get("priority", "normal")
        
        if not all([recipient_email, subject, body]):
            raise ValueError("recipient_email, subject, and body are required")
        
        # Simulate email draft creation
        await asyncio.sleep(0.5)
        
        draft_id = f"draft_{int(time.time())}_{hash(recipient_email) % 1000}"
        
        return {
            "status": "success",
            "draft_id": draft_id,
            "recipient": recipient_email,
            "subject": subject,
            "body": body,
            "template_type": template_type,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "message": "Email draft created successfully"
        }
    
    async def _handle_direct_method(self, request: dict):
        """Handle direct method calls"""
        try:
            method = request.get("method", "")
            params = request.get("params", {})
            
            logger.info(f"🔍 _handle_direct_method called with method: '{method}'")
            logger.info(f"🔍 Request params: {params}")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id", "unknown"),
                    "result": {
                        "status": "success",
                        "agent_info": {
                            "name": "mesh_agent",
                            "version": "1.0.0",
                            "capabilities": ["email_management", "contact_management", "professional_networking", "collaboration"]
                        }
                    }
                }
            elif method == "capabilities":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id", "unknown"),
                    "result": {
                        "capabilities": {
                            "streaming": False,
                            "collaboration": True,
                            "workflow": True
                        },
                        "skills": [
                            "email_management",
                            "contact_management", 
                            "professional_networking",
                            "agent_collaboration"
                        ]
                    }
                }
            elif method == "methods":
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id", "unknown"),
                    "result": {
                        "methods": [
                            "initialize",
                            "capabilities", 
                            "methods",
                            "write_email_draft",
                            "get_contact_info",
                            "suggest_email_template",
                            "discover_agents",
                            "delegate_task",
                            "collaborate"
                        ]
                    }
                }
            elif method == "write_email_draft":
                recipient = params.get("recipient", "unknown")
                subject = params.get("subject", "No Subject")
                context = params.get("context", "")
                
                # Generate email content based on context
                if "follow-up" in context.lower():
                    email_body = f"Hi {recipient},\n\nThank you for our recent conversation. I wanted to follow up on the points we discussed.\n\nBest regards,\nMESH Assistant"
                elif "networking" in context.lower():
                    email_body = f"Hi {recipient},\n\nI hope this email finds you well. I'm reaching out to connect and explore potential collaboration opportunities.\n\nBest regards,\nMESH Assistant"
                else:
                    email_body = f"Hi {recipient},\n\n{context}\n\nBest regards,\nMESH Assistant"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id", "unknown"),
                    "result": {
                        "email_draft": {
                            "to": recipient,
                            "subject": subject,
                            "body": email_body,
                            "status": "draft_created"
                        }
                    }
                }
            elif method == "get_contact_info":
                query = params.get("query", "")
                # Mock contact search
                contacts = [
                    {"name": "John Smith", "email": "john@example.com", "company": "Tech Corp"},
                    {"name": "Sarah Johnson", "email": "sarah@example.com", "company": "Innovation Inc"}
                ]
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id", "unknown"),
                    "result": {
                        "contacts": contacts,
                        "query": query,
                        "count": len(contacts)
                    }
                }
            elif method == "message/send":
                # Handle message/send method for A2A Inspector conversation
                logger.info(f"🔍 Processing message/send method")
                message = params.get("message", {})
                message_text = ""
                
                logger.info(f"🔍 Message object: {message}")
                
                # Extract text from message parts
                if "parts" in message:
                    for part in message["parts"]:
                        if part.get("kind") == "text" or part.get("type") == "text":
                            message_text += part.get("text", "")
                
                logger.info(f"🔍 Extracted message text: '{message_text}'")
                
                # Process the message and generate response
                response_text = self._process_message(message_text)
                logger.info(f"🔍 Generated response text: '{response_text[:100]}...'")
                
                # Generate unique IDs
                import uuid
                from datetime import datetime
                
                message_id = f"msg-{int(datetime.now().timestamp())}-{str(uuid.uuid4())[:8]}"
                task_id = f"task-{int(datetime.now().timestamp())}-{str(uuid.uuid4())[:8]}"
                context_id = f"ctx-{int(datetime.now().timestamp())}-{str(uuid.uuid4())[:8]}"
                
                logger.info(f"🔍 Generated IDs - Message: {message_id}, Task: {task_id}, Context: {context_id}")
                
                # Return the CORRECT format with ALL required fields
                # A2A Inspector expects flattened structure with specific field values
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", message_id),
                    "result": {
                        # Task fields - flattened as A2A Inspector expects
                        "id": task_id,
                        "contextId": context_id,
                        "status": "completed",  # Simple string as expected
                        # Message fields - flattened as A2A Inspector expects
                        "messageId": message_id,
                        "parts": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ],
                        "role": "agent"  # Must be 'agent' not 'assistant'
                    }
                }
                
                logger.info(f"🔍 Returning response: {response}")
                return response
            else:
                # Handle unknown methods
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id", "unknown"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                        "data": None
                    }
                }
                    
        except Exception as e:
            logger.error(f"Error handling direct method: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", "unknown"),
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
    
    def _process_message(self, message_text: str) -> str:
        """Process incoming messages and generate intelligent responses"""
        message_lower = message_text.lower()
        
        # Email-related queries
        if any(word in message_lower for word in ["email", "draft", "compose", "write"]):
            if "template" in message_lower:
                return "I can help you with email templates! I offer several professional templates:\n\n1. **Follow-up Template** - For post-meeting follow-ups\n2. **Networking Template** - For building professional connections\n3. **Introduction Template** - For 3-way introductions\n4. **Thank You Template** - For post-interview follow-ups\n\nWould you like me to generate a specific template for you?"
            elif "professional" in message_lower:
                return "I specialize in creating professional emails! I can help you with:\n\n• Business follow-ups\n• Networking outreach\n• Professional introductions\n• Thank you notes\n• Meeting confirmations\n\nJust let me know what type of email you need and I'll craft it for you."
            else:
                return "I'm your email composition assistant! I can help you create professional emails, suggest templates, and manage your email communications. What type of email would you like help with?"
        
        # Contact-related queries
        elif any(word in message_lower for word in ["contact", "database", "search", "find"]):
            return "I can help you search and manage your contact database! I can:\n\n• Search for contacts by name, company, or industry\n• Provide contact details and relationship history\n• Suggest networking opportunities\n• Help organize your professional network\n\nWhat contact information are you looking for?"
        
        # Networking-related queries
        elif any(word in message_lower for word in ["network", "introduction", "connect", "relationship"]):
            if "3-way" in message_lower or "introduction" in message_lower:
                return "I'm excellent at 3-way introductions! This involves connecting two people through a mutual contact. I can help you:\n\n• Identify potential connections\n• Craft introduction messages\n• Follow up on introductions\n• Build your professional network strategically\n\nWould you like me to help you set up a 3-way introduction?"
            else:
                return "I can help you build and manage your professional network! I offer:\n\n• Strategic networking strategies\n• Introduction management\n• Follow-up planning\n• Relationship tracking\n• Networking opportunity identification\n\nWhat networking goal would you like to work on?"
        
        # Collaboration-related queries
        elif any(word in message_lower for word in ["collaborate", "workflow", "agent", "coordinate"]):
            return "I'm designed for multi-agent collaboration! I can:\n\n• Coordinate with other AI agents\n• Execute complex workflows\n• Delegate tasks to specialized agents\n• Manage multi-step processes\n• Orchestrate team efforts\n\nWhat kind of collaboration or workflow would you like to explore?"
        
        # General queries
        elif any(word in message_lower for word in ["help", "what can you do", "capabilities", "skills"]):
            return "I'm MESH, your professional email management and networking assistant! Here's what I can do:\n\n📧 **Email Management**\n• Compose professional emails\n• Generate email templates\n• Manage follow-ups\n\n👥 **Contact Management**\n• Search contact database\n• Track relationships\n• Organize network\n\n🤝 **Professional Networking**\n• Strategic networking\n• 3-way introductions\n• Relationship building\n\n🔄 **Multi-Agent Collaboration**\n• Workflow orchestration\n• Task delegation\n• Team coordination\n\nHow can I help you today?"
        
        # Default response
        else:
            return f"I understand you're asking about: '{message_text}'\n\nAs your professional email and networking assistant, I can help you with:\n\n• Creating professional emails and templates\n• Managing your contact database\n• Building strategic professional relationships\n• Coordinating multi-agent workflows\n\nCould you please rephrase your question or let me know what specific help you need?"
    
    async def start(self):
        """Start the A2A server"""
        logger.info("Starting A2A server...")
        
        # Start agent manager
        await agent_manager.start()
        
        logger.info(f"A2A server ready on {default_server_config.host}:{default_server_config.port}")
    
    async def stop(self):
        """Stop the A2A server"""
        logger.info("Stopping A2A server...")
        
        # Stop agent manager
        await agent_manager.stop()
        
        logger.info("A2A server stopped")

# Global instance
a2a_server = A2AServer()

if __name__ == "__main__":
    print("A2A Server Module")
    print("=" * 30)
    
    import uvicorn
    import os
    
    # Get port from environment variable or use default
    port = int(os.environ.get('A2A_PORT', default_server_config.port))
    
    async def main():
        """Main function to run the A2A server"""
        await a2a_server.start()
        
        # Run the FastAPI app
        config = uvicorn.Config(
            app=a2a_server.app,
            host=default_server_config.host,
            port=port,
            log_level=default_server_config.log_level
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    # Run the server
    asyncio.run(main())
