# MESH Protocol Chat App

## 🌐 Interactive Protocol Showcase

This folder contains the Streamlit-based interactive application for showcasing and testing the MCP, A2A, and ACP protocols.

## 🚀 Quick Start

### **Launch the App**
```bash
# Use the launcher script (recommended)
./launch_streamlit.sh

# Or manually
streamlit run streamlit_app.py
```

### **Access the Interface**
- Open your browser to: http://localhost:8501
- The app will automatically load with all features

## ✨ Features

### **🎛️ Server Management**
- Visual controls for starting/stopping protocol servers
- Real-time status monitoring for all servers
- One-click server management

### **💬 Interactive Chat**
- Natural language interface for testing protocols
- Protocol-specific responses and information
- Quick action buttons for common functions

### **🔌 Protocol Selection**
- Choose between MCP, A2A, and ACP protocols
- Protocol-specific information and capabilities
- Easy switching between different protocols

### **📊 Real-time Monitoring**
- Live server status indicators
- Connection information for each protocol
- Performance metrics and health checks

## 🛠️ Technical Details

### **Dependencies**
- **Streamlit**: Web application framework
- **Python 3.11+**: Modern Python with async support
- **Protocol Servers**: MCP, A2A, and ACP servers running

### **File Structure**
```
chat-app/
├── streamlit_app.py           # Main Streamlit application
├── streamlit_requirements.txt # Streamlit-specific dependencies
├── launch_streamlit.sh        # App launcher script
└── README.md                  # This file
```

### **Port Configuration**
- **Default Port**: 8501
- **Configurable**: Can be changed via command line arguments
- **Network Access**: Configured for local and network access

## 🔧 Configuration

### **Custom Port**
```bash
streamlit run streamlit_app.py --server.port 8502
```

### **Network Access**
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

### **Debug Mode**
```bash
streamlit run streamlit_app.py --logger.level debug
```

## 🧪 Testing

### **Test Functions**
The app provides several test functions:
- 📧 **Email Composition**: Test email drafting capabilities
- 👥 **Contact Search**: Test contact management functions
- 📝 **Template Suggestions**: Test template recommendation system
- 🔍 **Network Analysis**: Test networking capabilities

### **Protocol Testing**
- **MCP**: Test Model Context Protocol tools
- **A2A**: Test Agent-to-Agent communication
- **ACP**: Test Agent Communication Protocol

## 🚨 Troubleshooting

### **Common Issues**

#### **Port Already in Use**
```bash
# Change to different port
streamlit run streamlit_app.py --server.port 8502
```

#### **Import Errors**
- Ensure all dependencies are installed: `pip install -r streamlit_requirements.txt`
- Check that protocol servers are accessible
- Verify Python path includes project root

#### **Server Connection Issues**
- Use the app's server management controls
- Check server status with `./run.sh status` from project root
- Verify firewall and network settings

### **Debug Information**
```bash
# Enable verbose logging
streamlit run streamlit_app.py --logger.level debug

# Check server logs
./run.sh logs
```

## 🔗 Integration

### **With Protocol Servers**
The chat app integrates with:
- **MCP Server**: Model Context Protocol tools
- **A2A Server**: Agent-to-Agent communication
- **ACP Server**: Agent Communication Protocol

### **With Project Structure**
- **Root Level**: Protocol servers and core components
- **Chat App**: Interactive interface and testing tools
- **Shared Components**: Common functionality across protocols

## 📱 Usage Examples

### **1. Start All Servers**
1. Open the app in your browser
2. Use the sidebar "Start All" button
3. Monitor server status in real-time

### **2. Test Protocol Functions**
1. Select your preferred protocol from the dropdown
2. Use the chat interface to ask questions
3. Try quick action buttons for instant testing

### **3. Monitor System Health**
1. Check server status indicators
2. View connection information
3. Monitor performance metrics

## 🎯 Next Steps

1. **Launch the app**: `./launch_streamlit.sh`
2. **Start servers**: Use the app interface
3. **Test protocols**: Try different functions
4. **Explore capabilities**: Discover all features
5. **Customize**: Modify for your needs

---

**Ready to explore the MESH protocols? Launch the app and start testing! 🚀**
