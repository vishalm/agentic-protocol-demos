import streamlit as st
import asyncio
import json
import time
from datetime import datetime
import pandas as pd
import subprocess
import os
import sys
import requests

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from a2a.a2a_server import A2AServer
from acp.acp_server import ACPServer
from shared.agent_manager import AgentManager
from shared.task_orchestrator import TaskOrchestrator
# Page configuration
st.set_page_config(
    page_title="MESH Protocol Showcase",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean minimalist CSS styling
st.markdown("""
<style>
    /* Global Clean Styles */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    
    .main {
        background-color: #ffffff;
        padding: 0;
    }
    
    /* Clean Header */
    .main-header {
        background-color: #000000;
        color: #ffffff;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2rem;
        font-weight: 400;
        margin: 0;
        letter-spacing: 2px;
    }
    
    .main-header p {
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.8;
        font-weight: 300;
    }
    
    /* Clean Chat Container */
    .chat-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 1.5rem;
        height: 500px;
        overflow-y: auto;
        margin-bottom: 1rem;
    }
    
    /* Clean Messages */
    .message {
        margin: 1rem 0;
        padding: 1rem;
        max-width: 85%;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .message-user {
        background-color: #000000;
        color: #ffffff;
        margin-left: auto;
        text-align: right;
    }
    
    .message-assistant {
        background-color: #f5f5f5;
        color: #000000;
        border: 1px solid #e0e0e0;
    }
    
    .message-system {
        background-color: #f9f9f9;
        color: #666666;
        text-align: center;
        max-width: 100%;
        font-style: italic;
    }
    
    /* Clean Input */
    .chat-input-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .stTextInput > div > div > input {
        border: 1px solid #cccccc;
        padding: 0.75rem;
        font-size: 0.95rem;
        background-color: #ffffff;
        color: #000000;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #000000;
        outline: none;
        box-shadow: none;
    }
    
    /* Clean Buttons */
    .stButton > button {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #000000;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        font-weight: 400;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #333333;
        border-color: #333333;
    }
    
    /* Clean Status Cards */
    .status-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .status-card h3 {
        color: #000000;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { 
        background-color: #000000;
    }
    
    .status-offline { 
        background-color: #cccccc;
    }
    
    /* Clean Protocol Cards */
    .protocol-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .protocol-card h4 {
        color: #000000;
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Clean Scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 4px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f0f0f0;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: #cccccc;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #999999;
    }
    
    /* Clean Selectbox */
    .stSelectbox > div > div {
        background-color: #ffffff;
        border: 1px solid #cccccc;
    }
    
    /* Clean DataFrame */
    .stDataFrame {
        border: 1px solid #e0e0e0;
    }
    
    /* Remove default Streamlit styling */
    .css-1d391kg {
        background-color: #ffffff;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #000000;
        font-weight: 400;
    }
    
    p {
        color: #333333;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)



class MESHShowcase:
    def __init__(self):
        self.mcp_server = None
        self.a2a_server = None
        self.acp_server = None
        self.agent_manager = None
        self.task_orchestrator = None
        self.chat_history = []
        
    def initialize_servers(self):
        """Initialize available protocol servers"""
        try:
            # Initialize shared components
            self.agent_manager = AgentManager()
            self.task_orchestrator = TaskOrchestrator(self.agent_manager)
            
            # Initialize protocol servers (MCP runs independently)
            self.a2a_server = A2AServer()
            self.acp_server = ACPServer()
            
            return True
        except Exception as e:
            st.error(f"Failed to initialize servers: {e}")
            return False
    
    def get_server_status(self):
        """Get status of all servers"""
        status = {
            'mcp': {'status': 'offline', 'port': 'STDIO', 'name': 'Model Context Protocol'},
            'a2a': {'status': 'offline', 'port': 8080, 'name': 'Agent-to-Agent Protocol'},
            'acp': {'status': 'offline', 'port': 8081, 'name': 'Agent Communication Protocol'}
        }
        
        # Check MCP server (STDIO-based)
        try:
            if self.mcp_server:
                status['mcp']['status'] = 'online'
        except:
            pass
            
        # Check A2A server
        try:
            response = requests.get(f"http://127.0.0.1:8080/health", timeout=2)
            if response.status_code == 200:
                status['a2a']['status'] = 'online'
        except:
            pass
            
        # Check ACP server
        try:
            response = requests.get(f"http://127.0.0.1:8081/health", timeout=2)
            if response.status_code == 200:
                status['acp']['status'] = 'online'
        except:
            pass
            
        return status

def process_message(message, protocol):
    """Process message based on active protocol"""
    # Simple response logic - in a real app, this would call the actual protocol servers
    if "email" in message.lower():
        return "I can help you compose professional emails using the MESH system. What type of email would you like to create?"
    elif "contact" in message.lower():
        return "I can search through your contact database and help you find the right connections. What are you looking for?"
    elif "template" in message.lower():
        return "I have several professional email templates available: introduction, follow-up, networking, and thank you notes. Which would you like to see?"
    else:
        return f"I'm your MESH assistant, ready to help with {protocol} operations. I can assist with email composition, contact management, and professional networking. What would you like to do?"

def main():
    # Initialize session state
    if 'mesh_showcase' not in st.session_state:
        st.session_state.mesh_showcase = MESHShowcase()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'active_protocol' not in st.session_state:
        st.session_state.active_protocol = "MCP"
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>MESH Protocol Showcase</h1>
        <p>Model Exchange Server Handler - Demonstrating MCP, A2A, and ACP Protocols</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## Chat Interface")
        
        # Protocol selector
        protocol_options = ["MCP", "A2A", "ACP"]
        selected_protocol = st.selectbox(
            "Select Protocol:",
            protocol_options,
            index=protocol_options.index(st.session_state.active_protocol),
            key="protocol_selector"
        )
        st.session_state.active_protocol = selected_protocol
        
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="message message-system">
                <strong>Welcome to MESH</strong><br>
                AI assistant for MCP, A2A, and ACP protocol exploration. 
                Ask about email composition, contact management, or professional networking.
            </div>
            """, unsafe_allow_html=True)
        else:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="message message-user">
                        <strong>You:</strong> {message['content']}
                        <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                elif message['role'] == 'assistant':
                    st.markdown(f"""
                    <div class="message message-assistant">
                        <strong>Assistant:</strong> {message['content']}
                        <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                elif message['role'] == 'system':
                    st.markdown(f"""
                    <div class="message message-system">
                        <strong>System:</strong> {message['content']}
                        <br><small>{message['timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input container
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input(
            "Type your message here...",
            key="chat_input",
            placeholder="Ask about email composition, contacts, or networking..."
        )
        
        # Input buttons
        col_input1, col_input2, col_input3 = st.columns([3, 1, 1])
        with col_input1:
            if st.button("Send", type="primary", use_container_width=True):
                if user_input.strip():
                    # Add user message to chat
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': user_input,
                        'timestamp': datetime.now()
                    })
                    
                    # Process message based on active protocol
                    response = process_message(user_input, st.session_state.active_protocol)
                    
                    # Add assistant response
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response,
                        'timestamp': datetime.now()
                    })
                    
                    st.rerun()
        
        with col_input2:
            if st.button("Clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col_input3:
            if st.button("Reset", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("## Server Status")
        
        # Get server status
        status = st.session_state.mesh_showcase.get_server_status()
        
        # Display server status
        for protocol, info in status.items():
            status_class = f"status-{info['status']}"
            status_text = info['status'].title()
            
            st.markdown(f"""
            <div class="status-card">
                <h3>{info['name']}</h3>
                <p><span class="status-indicator {status_class}"></span>{status_text}</p>
                <p><strong>Port:</strong> {info['port']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Protocol information
        st.markdown("## Protocol Details")
        
        if st.session_state.active_protocol == "MCP":
            st.markdown("""
            <div class="protocol-card">
                <h4>Model Context Protocol</h4>
                <p><strong>Transport:</strong> STDIO</p>
                <p><strong>Use Case:</strong> AI application integration</p>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>Tool calling</li>
                    <li>Resource access</li>
                    <li>Prompt management</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.active_protocol == "A2A":
            st.markdown("""
            <div class="protocol-card">
                <h4>Agent-to-Agent Protocol</h4>
                <p><strong>Transport:</strong> HTTP + WebSocket</p>
                <p><strong>Use Case:</strong> Multi-agent collaboration</p>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>Agent discovery</li>
                    <li>Message routing</li>
                    <li>Workflow orchestration</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="protocol-card">
                <h4>Agent Communication Protocol</h4>
                <p><strong>Transport:</strong> RESTful HTTP API</p>
                <p><strong>Use Case:</strong> Cross-platform integration</p>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>Agent registration</li>
                    <li>Task management</li>
                    <li>Message history</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Available tools
        st.markdown("## Available Tools")
        tools = [
            "Email Composition",
            "Contact Search", 
            "Template Suggestions",
            "Network Analysis",
            "Calendar Integration"
        ]
        
        for tool in tools:
            st.markdown(f"- {tool}")
    
    # Bottom section with protocol comparison
    st.markdown("---")
    st.markdown("## Protocol Comparison")
    
    # Create comparison table
    comparison_data = {
        'Protocol': ['MCP', 'A2A', 'ACP'],
        'Transport': ['STDIO', 'HTTP + WebSocket', 'RESTful HTTP'],
        'Use Case': ['AI Integration', 'Multi-Agent', 'Cross-Platform'],
        'Complexity': ['Low', 'Medium', 'High'],
        'Real-time': ['No', 'Yes', 'Partial']
    }
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
