#!/bin/bash

# MESH Protocol Showcase - Streamlit App Launcher
# This script launches the Streamlit app to showcase MCP, A2A, and ACP protocols

echo "🚀 Launching MESH Protocol Showcase..."
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install Streamlit requirements
echo "📥 Installing Streamlit requirements..."
pip install -r streamlit_requirements.txt

# Check if run.sh exists and make it executable
if [ -f "run.sh" ]; then
    chmod +x run.sh
    echo "✅ Made run.sh executable"
fi

# Launch Streamlit app
echo "🌐 Starting Streamlit app..."
echo "📱 The app will open in your browser at: http://localhost:8501"
echo "🔌 You can start the protocol servers from the app interface"
echo ""
echo "Press Ctrl+C to stop the Streamlit app"
echo ""

streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
