"""
Hybrid Server for MESH - MCP + A2A Integration
Runs both MCP and A2A protocols concurrently
"""

import asyncio
import logging
import signal
import sys
import subprocess
import time
from typing import Optional
import socket
import os

from mcp.server.fastmcp import FastMCP
from a2a_config import default_server_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridServer:
    """Hybrid server that runs both MCP and A2A protocols"""
    
    def __init__(self):
        # MCP Server
        self.mcp_server = FastMCP("MESH")
        self.mcp_running = False
        
        # A2A Server process
        self.a2a_process = None
        self.a2a_running = False
        
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
                with open("prompts/mesh.md", "r", encoding="utf-8") as file:
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
                with open("email-examples/3-way-intro.md", "r", encoding="utf-8") as file:
                    return file.read()
            except FileNotFoundError:
                return "# 3-Way Introduction Template\n\nTemplate file not available. Please check file path."
            except Exception as e:
                return f"Error reading template: {str(e)}"
        
        @self.mcp_server.resource("email-examples://call-follow-up")
        def write_call_followup() -> str:
            """Example of a call follow-up email"""
            try:
                with open("email-examples/call-follow-up.md", "r", encoding="utf-8") as file:
                    return file.read()
            except FileNotFoundError:
                return "# Call Follow-up Template\n\nTemplate file not available. Please check file path."
            except Exception as e:
                return f"Error reading template: {str(e)}"
        
        @self.mcp_server.resource("directory://all")
        def get_directory() -> str:
            """Get the entire directory of contacts"""
            try:
                with open("directory.csv", "r", encoding="utf-8") as file:
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
                recipient_email (str): The email address of the recipient.
                subject (str): The subject line of the email.
                body (str): The main content/body of the email.
            
            Returns:
                dict: A dictionary containing the draft information.
            """
            print("=" * 50, file=sys.stderr)
            print("EMAIL DRAFT CREATED (Test Mode)", file=sys.stderr)
            print("=" * 50, file=sys.stderr)
            print(f"To: {recipient_email}", file=sys.stderr)
            print(f"Subject: {subject}", file=sys.stderr)
            print(f"Body: {body}", file=sys.stderr)
            print("=" * 50, file=sys.stderr)
            print("Note: This is a test version. In production, this would create a Gmail draft.", file=sys.stderr)
            print("=" * 50, file=sys.stderr)
            
            return {
                "status": "success",
                "message": "Email draft created (test mode)",
                "recipient": recipient_email,
                "subject": subject,
                "body": body
            }
        
        @self.mcp_server.tool()
        def get_contact_info(name: str = None) -> dict:
            """Get contact information from the directory.
            
            Args:
                name (str, optional): Name to search for. If None, returns all contacts.
            
            Returns:
                dict: Contact information.
            """
            import csv
            contacts = []
            try:
                with open("directory.csv", "r", encoding="utf-8") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if name is None or (name and name.lower() in row.get('Name', '').lower()):
                            contacts.append(row)
            except FileNotFoundError:
                return {
                    "error": "Directory file not found",
                    "contacts": [],
                    "count": 0,
                    "search_term": name
                }
            except Exception as e:
                return {
                    "error": f"Error reading directory: {str(e)}",
                    "contacts": [],
                    "count": 0,
                    "search_term": name
                }
            
            return {
                "contacts": contacts,
                "count": len(contacts),
                "search_term": name
            }
        
        @self.mcp_server.tool()
        def suggest_email_template(context: str) -> dict:
            """Suggest an email template based on context.
            
            Args:
                context (str): The context for the email (e.g., "introduction", "follow-up", "networking")
            
            Returns:
                dict: Suggested template and guidance.
            """
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
                },
                "networking": {
                    "template": "email-examples://3-way-intro",
                    "description": "Professional networking introduction",
                    "best_for": "Expanding your professional network"
                }
            }
            
            context_lower = context.lower() if context else ""
            for key, template_info in templates.items():
                if key in context_lower:
                    return {
                        "suggested_template": template_info,
                        "context": context,
                        "available_templates": list(templates.keys())
                    }
            
            return {
                "suggested_template": None,
                "context": context,
                "available_templates": list(templates.keys()),
                "message": "No specific template found. Consider using a general professional email format."
            }
        
        # New A2A-related tools
        @self.mcp_server.tool()
        def discover_a2a_agents(capability_filter: str = None) -> dict:
            """Discover A2A agents in the network.
            
            Args:
                capability_filter (str, optional): Filter agents by specific capability.
            
            Returns:
                dict: Information about discovered agents.
            """
            try:
                # This would call the A2A agent manager
                # For now, return mock data
                return {
                    "agents": [
                        {
                            "name": "EmailBot",
                            "description": "AI-powered email writing assistant",
                            "capabilities": ["email_management", "writing_assistance"]
                        },
                        {
                            "name": "GrammarBot", 
                            "description": "Grammar and style checking",
                            "capabilities": ["grammar_check", "style_analysis"]
                        }
                    ],
                    "count": 2,
                    "message": "A2A agent discovery (mock data)"
                }
            except Exception as e:
                return {
                    "error": f"Error discovering agents: {str(e)}",
                    "agents": [],
                    "count": 0
                }
        
        @self.mcp_server.tool()
        def execute_a2a_workflow(workflow_type: str, input_data: str = "{}") -> dict:
            """Execute an A2A workflow.
            
            Args:
                workflow_type (str): Type of workflow to execute (e.g., "email_composition").
                input_data (str): JSON string containing input data for the workflow.
            
            Returns:
                dict: Workflow execution results.
            """
            try:
                import json
                parsed_input = json.loads(input_data) if input_data else {}
                
                # This would call the A2A task orchestrator
                # For now, return mock data
                return {
                    "workflow_type": workflow_type,
                    "status": "completed",
                    "result": f"Workflow '{workflow_type}' executed successfully with A2A integration",
                    "input_data": parsed_input,
                    "message": "A2A workflow execution (mock data)"
                }
            except Exception as e:
                return {
                    "error": f"Error executing workflow: {str(e)}",
                    "workflow_type": workflow_type,
                    "status": "failed"
                }
    
    def start_a2a_server(self):
        """Start the A2A server in a subprocess"""
        try:
            logger.info("Starting A2A server in subprocess...")
            
            # Check if port is available, try alternative ports if needed
            port = default_server_config.port
            max_port_attempts = 5
            
            for attempt in range(max_port_attempts):
                try:
                    # Test if port is available
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind((default_server_config.host, port))
                        s.close()
                    break
                except OSError:
                    logger.warning(f"Port {port} is busy, trying {port + 1}")
                    port += 1
                    if attempt == max_port_attempts - 1:
                        logger.error(f"Could not find available port after {max_port_attempts} attempts")
                        return False
            
            logger.info(f"Using port {port} for A2A server")
            
            # Start A2A server as a subprocess using the a2a_server.py directly
            # Pass the port as an environment variable
            env = os.environ.copy()
            env['A2A_PORT'] = str(port)
            
            self.a2a_process = subprocess.Popen([
                sys.executable, "a2a_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            
            # Wait a moment for server to start
            time.sleep(3)
            
            # Check if process is still running
            if self.a2a_process.poll() is None:
                self.a2a_running = True
                logger.info(f"A2A server started successfully in subprocess on port {port}")
                return True
            else:
                # Check for errors
                stdout, stderr = self.a2a_process.communicate()
                logger.error(f"A2A server process failed. stdout: {stdout.decode()}, stderr: {stderr.decode()}")
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
        """Stop the A2A server subprocess"""
        if self.a2a_process and self.a2a_process.poll() is None:
            logger.info("Stopping A2A server subprocess...")
            self.a2a_process.terminate()
            try:
                self.a2a_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.a2a_process.kill()
            self.a2a_running = False
            logger.info("A2A server stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Shutdown signal {signum} received, stopping servers...")
        self.shutdown_requested = True
        
        # Stop A2A server
        self.stop_a2a_server()
        
        # Exit gracefully
        sys.exit(0)

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
        # Start A2A server in subprocess
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
        hybrid_server.stop_a2a_server()
        print("✅ Cleanup completed")

if __name__ == "__main__":
    main()
