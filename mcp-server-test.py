"""
MESH - Model Exchange Server Handler
A simple MCP server for email management and contact management
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("MESH")

# Prompts
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

# Resources
@mcp.resource("email-examples://3-way-intro")
def write_3way_intro() -> str:
    """Example of a 3-way introduction email"""
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

# Tools
@mcp.tool()
def write_email_draft(recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
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

@mcp.tool()
def get_contact_info(name: Optional[str] = None) -> Dict[str, Any]:
    """Search and retrieve contact information from the directory.
    
    Args:
        name: Optional name to search for. If None, returns all contacts.
        
    Returns:
        Dictionary with contact information
    """
    try:
        with open("directory.csv", "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        if len(lines) < 2:
            return {
                "status": "error",
                "message": "Directory file is empty or invalid"
            }
        
        # Parse CSV header
        headers = lines[0].strip().split(',')
        contacts = []
        
        # Parse contact data
        for line in lines[1:]:
            if line.strip():
                values = line.strip().split(',')
                contact = dict(zip(headers, values))
                contacts.append(contact)
        
        # Filter by name if provided
        if name:
            filtered_contacts = [
                contact for contact in contacts 
                if name.lower() in contact.get('Name', '').lower()
            ]
            contacts = filtered_contacts
        
        return {
            "status": "success",
            "count": len(contacts),
            "contacts": contacts
        }
        
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Directory file not found"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading directory: {str(e)}"
        }

@mcp.tool()
def suggest_email_template(context: str) -> Dict[str, Any]:
    """Get AI-powered email template suggestions based on context.
    
    Args:
        context: The context for the email (e.g., 'introduction', 'follow-up', 'networking')
        
    Returns:
        Dictionary with template suggestions
    """
    try:
        context = context.lower()
        
        if "intro" in context or "introduction" in context:
            template = """Subject: Introduction - [Your Name] from [Company/Organization]

Hi [Name],

I hope this email finds you well. My name is [Your Name] and I'm [Your Title] at [Company/Organization].

[Brief introduction about what you do and why you're reaching out]

I came across your work on [specific project/topic] and was impressed by [specific detail].

[State your purpose - what you'd like to discuss or how you can help each other]

Would you be available for a brief call next week to discuss this further?

Best regards,
[Your Name]
[Your Contact Information]"""
            
            return {
                "status": "success",
                "context": context,
                "template": template,
                "tips": [
                    "Personalize the introduction based on the recipient's background",
                    "Be specific about what caught your attention",
                    "Include a clear call to action"
                ]
            }
            
        elif "follow" in context or "follow-up" in context:
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
            
        elif "network" in context or "networking" in context:
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

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
