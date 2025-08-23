#!/bin/bash

# MESH Protocol Chat App Launcher
# This script launches the Streamlit chat app from the chat-app folder

echo "🚀 Launching MESH Protocol Chat App..."
echo "======================================"

# Check if chat-app folder exists
if [ ! -d "chat-app" ]; then
    echo "❌ chat-app folder not found!"
    echo "Please ensure you're in the project root directory"
    exit 1
fi

# Change to chat-app directory
cd chat-app

# Check if launcher script exists
if [ ! -f "launch_streamlit.sh" ]; then
    echo "❌ launch_streamlit.sh not found in chat-app folder!"
    exit 1
fi

# Launch the chat app
echo "🌐 Starting Streamlit chat app..."
echo "📱 The app will open in your browser at: http://localhost:8501"
echo "🔌 You can start the protocol servers from the app interface"
echo ""

./launch_streamlit.sh
