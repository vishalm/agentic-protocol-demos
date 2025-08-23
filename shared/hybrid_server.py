"""
Hybrid Server for MESH - MCP + A2A Integration
Runs both MCP and A2A protocols concurrently
"""

import asyncio
import logging
import signal
import sys
import threading
import time
from typing import Optional
import socket
import os

from mcp.server.fastmcp import FastMCP
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from a2a.a2a_config import default_server_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridServer:
    """Hybrid server that runs both MCP and A2A protocols"""
    
    def __init__(self):
        # MCP Server
        self.mcp_server = FastMCP("MESH")
        self.mcp_running = False
        
        # A2A Server thread
        self.a2a_thread = None
        self.a2a_running = False
        self.a2a_stop_event = threading.Event()
        self.a2a_uvicorn_server = None
        
        # Server state
        self.shutdown_requested = False
        
        # Register MCP tools and resources
        self._register_mcp_functionality()
        
        logger.info("Hybrid Server initialized")
    
    def _register_mcp_functionality(self):
        """Register MCP tools and resources"""
        
        # Prompts
        @self.mcp_server.prompt()
        def mesh(user_name: str, user_title: str) -> str:
            """Global instructions for MESH (Model Exchange Server Handler)"""
            try:
                with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "mesh.md"), "r", encoding="utf-8") as file:
                    template = file.read()
                return template.format(user_name=user_name, user_title=user_title)
            except FileNotFoundError:
                return f"""# MESH (Model Exchange Server Handler)

You are MESH, a virtual assistant to {user_name} ({user_title}). You support them with administrative tasks, particularly email management and professional networking.

Note: Main prompt file not found - using fallback template."""
            except Exception as e:
                return f"Error loading prompt template: {str(e)}"
        
        # Resources
        @self.mcp_server.resource("email-examples://3-way-intro")
        def write_3way_intro() -> str:
            """Example of a 3-way intro email"""
            try:
                with open(os.path.join(os.path.dirname(__file__), "..", "email-examples", "3-way-intro.md"), "r", encoding="utf-8") as file:
                    return file.read()
            except FileNotFoundError:
                return "# 3-Way Introduction Template\n\nTemplate file not available. Please check file path."
            except Exception as e:
                return f"Error reading template: {str(e)}"
        
        @self.mcp_server.resource("email-examples://call-follow-up")
        def write_call_followup() -> str:
            """Example of a call follow-up email"""
            try:
                with open(os.path.join(os.path.dirname(__file__), "..", "email-examples", "call-follow-up.md"), "r", encoding="utf-8") as file:
                    return file.read()
            except FileNotFoundError:
                return "# Call Follow-up Template\n\nTemplate file not available. Please check file path."
            except Exception as e:
                return f"Error reading template: {str(e)}"
        
        @self.mcp_server.resource("directory://all")
        def get_directory() -> str:
            """Get the entire directory of contacts"""
            try:
                with open(os.path.join(os.path.dirname(__file__), "..", "directory.csv"), "r", encoding="utf-8") as file:
                    return file.read()
            except FileNotFoundError:
                return "Name,Email,Url,Bio\nError,error@example.com,https://example.com,Directory file not available"
            except Exception as e:
                return f"Error reading directory: {str(e)}"
        
        # Tools
        @self.mcp_server.tool()
        def write_email_draft(recipient_email: str, subject: str, body: str) -> dict:
            """Create a draft email (test version - prints to console instead of Gmail).
            
            Args:
                recipient_email: Email address of the recipient
                subject: Subject line of the email
                body: Body content of the email
                
            Returns:
                Dictionary with email draft details
            """
            try:
                # In a real implementation, this would create a Gmail draft
                # For now, we'll just print to console and return the details
                print(f"\n📧 Email Draft Created:")
                print(f"To: {recipient_email}")
                print(f"Subject: {subject}")
                print(f"Body: {body}")
                print("-" * 50)
                
                return {
                    "status": "success",
                    "message": "Email draft created successfully (test mode)",
                    "draft": {
                        "to": recipient_email,
                        "subject": subject,
                        "body": body,
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to create email draft: {str(e)}"
                }
        
        @self.mcp_server.tool()
        def suggest_email_template(context: str) -> dict:
            """Suggest an email template based on the context.
            
            Args:
                context: The context for the email (e.g., "follow-up", "networking", "introduction")
                
            Returns:
                Dictionary with template suggestions
            """
            try:
                context_lower = context.lower()
                
                if "intro" in context_lower or "introduction" in context_lower:
                    template = """Subject: Introduction - [Your Name] from [Company/Organization]

Hi [Name],

I hope this email finds you well. I'm [Your Name], [Your Title] at [Company/Organization].

[Brief introduction about your role and company]

I'm reaching out because [specific reason for connecting - mutual connection, shared interest, etc.].

[What you admire about their work or company]

[Specific way you could potentially collaborate or help each other]

Would you be open to a brief conversation to explore potential synergies?

Best regards,
[Your Name]
[Your Contact Information]"""
                    
                    return {
                        "status": "success",
                        "context": context,
                        "template": template,
                        "tips": [
                            "Be genuine about your interest in connecting",
                            "Offer value before asking for anything",
                            "Keep it concise and professional"
                        ]
                    }
                    
                elif "follow" in context_lower or "follow-up" in context_lower:
                    template = """Subject: Follow-up on [Previous Discussion/Topic]

Hi [Name],

I hope you're doing well. I wanted to follow up on our [conversation/meeting] from [date/time].

[Brief recap of what was discussed]

[Next steps or action items that were agreed upon]

[Any additional questions or clarifications needed]

[Proposed timeline or next meeting]

Looking forward to hearing from you.

Best regards,
[Your Name]"""
                    
                    return {
                        "status": "success",
                        "context": context,
                        "template": template,
                        "tips": [
                            "Reference specific points from your previous interaction",
                            "Include clear next steps",
                            "Set expectations for response timeline"
                        ]
                    }
                    
                elif "network" in context_lower or "networking" in context_lower:
                    template = """Subject: Connecting - [Your Name] from [Company/Organization]

Hi [Name],

I hope this email finds you well. I'm [Your Name], [Your Title] at [Company/Organization].

[Brief introduction about your role and company]

I'm reaching out because [specific reason for connecting - mutual connection, shared interest, etc.].

[What you admire about their work or company]

[Specific way you could potentially collaborate or help each other]

Would you be open to a brief conversation to explore potential synergies?

Best regards,
[Your Name]
[Your Contact Information]"""
                    
                    return {
                        "status": "success",
                        "context": context,
                        "template": template,
                        "tips": [
                            "Be genuine about your interest in connecting",
                            "Offer value before asking for anything",
                            "Keep it concise and professional"
                        ]
                    }
                    
                else:
                    return {
                        "status": "success",
                        "context": context,
                        "message": "Here's a general professional email template:",
                        "template": """Subject: [Clear, Professional Subject Line]

Hi [Name],

I hope this email finds you well.

[Professional greeting and introduction]

[Clear, concise message with your main point]

[Professional closing]

Best regards,
[Your Name]""",
                        "tips": [
                            "Keep subject lines clear and professional",
                            "Use a professional but friendly tone",
                            "Be concise and get to the point quickly",
                            "Always proofread before sending"
                        ]
                    }
                    
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error generating template: {str(e)}"
                }
    
    def start_a2a_server(self):
        """Start the A2A server in a separate thread"""
        try:
            logger.info("Starting A2A server in separate thread...")
            
            # Find available port
            port = default_server_config.port
            max_port_attempts = 10
            
            for attempt in range(max_port_attempts):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('127.0.0.1', port))
                        break
                except OSError:
                    logger.warning(f"Port {port} is busy, trying {port + 1}")
                    port += 1
                    if attempt == max_port_attempts - 1:
                        logger.error(f"Could not find available port after {max_port_attempts} attempts")
                        return False
            
            logger.info(f"Using port {port} for A2A server")
            
            # Set port in environment
            os.environ['A2A_PORT'] = str(port)
            
            # Start A2A server in a separate thread
            def run_a2a_server():
                try:
                    import uvicorn
                    from a2a.a2a_server import a2a_server
                    
                    # Create config and server
                    config = uvicorn.Config(
                        a2a_server.app,
                        host=default_server_config.host,
                        port=port,
                        log_level=default_server_config.log_level,
                        access_log=False
                    )
                    server = uvicorn.Server(config)
                    
                    # Store reference to server for graceful shutdown
                    hybrid_server.a2a_uvicorn_server = server
                    
                    # Run the A2A server
                    server.run()
                except Exception as e:
                    logger.error(f"A2A server thread error: {e}")
            
            self.a2a_thread = threading.Thread(target=run_a2a_server, daemon=False)
            self.a2a_thread.start()
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if server is responding
            try:
                import httpx
                with httpx.Client(timeout=5.0) as client:
                    response = client.get(f"http://127.0.0.1:{port}/health")
                    if response.status_code == 200:
                        self.a2a_running = True
                        logger.info(f"A2A server started successfully in thread on port {port}")
                        return True
                    else:
                        logger.error(f"A2A server health check failed with status {response.status_code}")
                        return False
            except ImportError:
                # httpx not available, assume success
                self.a2a_running = True
                logger.info(f"A2A server started successfully in thread on port {port}")
                return True
            except Exception as e:
                logger.error(f"A2A server health check failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start A2A server: {e}")
            return False
    
    def start_mcp_server(self):
        """Start the MCP server in the main thread"""
        try:
            logger.info("Starting MCP server...")
            self.mcp_server.run(transport='stdio')
            self.mcp_running = True
            logger.info("MCP server started successfully")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            self.mcp_running = False
    
    def stop_a2a_server(self):
        """Stop the A2A server thread"""
        if self.a2a_uvicorn_server:
            logger.info("Stopping A2A uvicorn server...")
            try:
                self.a2a_uvicorn_server.should_exit = True
                # Give it a moment to shutdown gracefully
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error stopping uvicorn server: {e}")
        
        if self.a2a_thread and self.a2a_thread.is_alive():
            logger.info("Stopping A2A server thread...")
            self.a2a_stop_event.set()
            # The thread will exit when the process ends
            self.a2a_running = False
            logger.info("A2A server stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        if self.shutdown_requested:
            # Already shutting down, exit immediately
            sys.exit(0)
            
        try:
            logger.info(f"Shutdown signal {signum} received, stopping servers...")
            self.shutdown_requested = True
            
            # Stop A2A server
            self.stop_a2a_server()
            
            # Exit gracefully
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error in signal handler: {e}")
            sys.exit(1)

def main():
    """Main function to run the hybrid server"""
    print("MESH Hybrid Server (MCP + A2A)")
    print("=" * 40)
    print("Starting both MCP and A2A protocols...")
    
    # Create hybrid server
    hybrid_server = HybridServer()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, hybrid_server.signal_handler)
    signal.signal(signal.SIGTERM, hybrid_server.signal_handler)
    
    try:
        # Start A2A server in separate thread
        if hybrid_server.start_a2a_server():
            print("✅ A2A server started successfully")
            print(f"   Available at: http://{default_server_config.host}:{default_server_config.port}")
        else:
            print("⚠️ A2A server failed to start, continuing with MCP only")
        
        print("\n🚀 Starting MCP server...")
        print("   MCP server will be available via STDIO transport")
        print("   Press Ctrl+C to stop both servers")
        print()
        
        # Start MCP server (this will block)
        hybrid_server.start_mcp_server()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            hybrid_server.stop_a2a_server()
            print("✅ Cleanup completed")
        except (Exception, OSError) as e:
            # Don't fail if cleanup has issues, especially I/O errors
            pass

if __name__ == "__main__":
    main()
