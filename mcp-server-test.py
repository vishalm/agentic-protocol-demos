from mcp.server.fastmcp import FastMCP
import csv
import os
import signal
import sys

# Create an MCP server
mcp = FastMCP("MESH")

# Global flag to control server shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    print("Shutdown signal received, stopping MESH server...", file=sys.stderr)
    shutdown_requested = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Define prompts
@mcp.prompt()
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

# Define resources
@mcp.resource("email-examples://3-way-intro")
def write_3way_intro() -> str:
    """Example of a 3-way intro email"""
    try:
        with open("email-examples/3-way-intro.md", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "# 3-Way Introduction Template\n\nTemplate file not available. Please check file path."
    except Exception as e:
        return f"Error reading template: {str(e)}"

@mcp.resource("email-examples://call-follow-up")
def write_call_followup() -> str:
    """Example of a call follow-up email"""
    try:
        with open("email-examples/call-follow-up.md", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "# Call Follow-up Template\n\nTemplate file not available. Please check file path."
    except Exception as e:
        return f"Error reading template: {str(e)}"

@mcp.resource("directory://all")
def get_directory() -> str:
    """Get the entire directory of contacts"""
    try:
        with open("directory.csv", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Name,Email,Url,Bio\nError,error@example.com,https://example.com,Directory file not available"
    except Exception as e:
        return f"Error reading directory: {str(e)}"

# Define tools
@mcp.tool()
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

@mcp.tool()
def get_contact_info(name: str = None) -> dict:
    """Get contact information from the directory.
    
    Args:
        name (str, optional): Name to search for. If None, returns all contacts.
    
    Returns:
        dict: Contact information.
    """
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

@mcp.tool()
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

if __name__ == "__main__":
    print("Starting MESH MCP Server...", file=sys.stderr)
    try:
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print("MESH server stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Error running MESH server: {e}", file=sys.stderr)
        sys.exit(1) 