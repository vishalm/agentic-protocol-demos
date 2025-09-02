#!/bin/bash

# MESH Hybrid Server (MCP + A2A) Setup and Run Script
# This script sets up the environment, updates dependencies, and runs the hybrid server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        REQUIRED_VERSION="3.10"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python version $PYTHON_VERSION meets requirement ($REQUIRED_VERSION+)"
            PYTHON_CMD="python3"
        else
            print_error "Python version $PYTHON_VERSION is below required version $REQUIRED_VERSION"
            exit 1
        fi
    elif command_exists python; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        REQUIRED_VERSION="3.10"
        
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            print_success "Python version $PYTHON_VERSION meets requirement ($REQUIRED_VERSION+)"
            PYTHON_CMD="python"
        else
            print_error "Python version $PYTHON_VERSION is below required version $REQUIRED_VERSION"
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3.10 or higher."
        exit 1
    fi
}

# Function to check and install uv
check_and_install_uv() {
    if command_exists uv; then
        UV_VERSION=$(uv --version)
        print_success "uv package manager found: $UV_VERSION"
    else
        print_warning "uv package manager not found. Installing..."
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            curl -LsSf https://astral.sh/uv/install.sh | sh
            source ~/.zshrc 2>/dev/null || source ~/.bash_profile 2>/dev/null
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            curl -LsSf https://astral.sh/uv/install.sh | sh
            source ~/.bashrc 2>/dev/null
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
            # Windows
            print_error "Please install uv manually on Windows: https://github.com/astral-sh/uv"
            exit 1
        else
            print_error "Unsupported operating system: $OSTYPE"
            exit 1
        fi
        
        # Verify installation
        if command_exists uv; then
            print_success "uv installed successfully"
        else
            print_error "Failed to install uv. Please install manually."
            exit 1
        fi
    fi
}

# Function to check project structure
check_project_structure() {
    print_status "Checking project structure..."
    
    REQUIRED_FILES=(
        "hybrid_server.py"
        "a2a_server.py"
        "agent_manager.py"
        "task_orchestrator.py"
        "a2a_config.py"
        "agent_capabilities.py"
        "acp_server.py"
        "acp_client.py"
        "test-acp-functions.py"
        "prompts/mesh.md"
        "email-examples/3-way-intro.md"
        "email-examples/call-follow-up.md"
        "directory.csv"
        "pyproject.toml"
        "requirements.txt"
    )
    
    MISSING_FILES=()
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ] && [ ! -d "$file" ]; then
            MISSING_FILES+=("$file")
        fi
    done
    
    if [ ${#MISSING_FILES[@]} -eq 0 ]; then
        print_success "All required files and directories found"
    else
        print_warning "Missing files/directories:"
        for file in "${MISSING_FILES[@]}"; do
            echo "  - $file"
        done
        print_error "Please ensure all required files are present"
        exit 1
    fi
}

# Function to setup virtual environment
setup_virtual_environment() {
    print_status "Setting up virtual environment..."
    
    if [ -d ".venv" ]; then
        print_status "Virtual environment already exists, removing old one..."
        rm -rf .venv
    fi
    
    print_status "Creating new virtual environment..."
    uv venv
    
    print_success "Virtual environment created"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Sync dependencies using uv
    print_status "Running uv sync..."
    uv sync
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Function to validate configuration
validate_configuration() {
    print_status "Validating configuration..."
    
    # Test A2A configuration
    print_status "Testing A2A configuration..."
    uv run python a2a_config.py
    
    if [ $? -eq 0 ]; then
        print_success "A2A configuration validation passed"
    else
        print_warning "A2A configuration validation failed, but continuing..."
    fi
}

# Function to run tests
run_tests() {
    print_status "Running integration tests..."
    
    # Run ACP function tests
    print_status "Running ACP function tests..."
    if uv run python test-acp-functions.py; then
        print_success "ACP function tests passed"
    else
        print_warning "Some ACP function tests failed, but continuing..."
    fi
    
    # Run MCP function tests
    print_status "Running MCP function tests..."
    if uv run python test-mcp-functions.py; then
        print_success "MCP function tests passed"
    else
        print_warning "Some MCP function tests failed, but continuing..."
    fi
    
    print_status "Server is ready for use!"
}

# Function to stop running servers
stop_servers() {
    print_status "Stopping any running servers..."
    
    local stopped_count=0
    
    # Stop hybrid server
    if pgrep -f "hybrid_server.py" > /dev/null; then
        print_status "Stopping hybrid server..."
        pkill -f "hybrid_server.py"
        sleep 2
        if ! pgrep -f "hybrid_server.py" > /dev/null; then
            print_success "Hybrid server stopped"
            ((stopped_count++))
        else
            print_warning "Force killing hybrid server..."
            pkill -9 -f "hybrid_server.py"
            ((stopped_count++))
        fi
    fi
    
    # Stop A2A server
    if pgrep -f "a2a_server.py" > /dev/null; then
        print_status "Stopping A2A server..."
        pkill -f "a2a_server.py"
        sleep 2
        if ! pgrep -f "a2a_server.py" > /dev/null; then
            print_success "A2A server stopped"
            ((stopped_count++))
        else
            print_warning "Force killing A2A server..."
            pkill -9 -f "a2a_server.py"
            ((stopped_count++))
        fi
    fi
    
    # Stop ACP server
    if pgrep -f "acp_server.py" > /dev/null; then
        print_status "Stopping ACP server..."
        pkill -f "acp_server.py"
        sleep 2
        if ! pgrep -f "acp_server.py" > /dev/null; then
            print_success "ACP server stopped"
            ((stopped_count++))
        else
            print_warning "Force killing ACP server..."
            pkill -9 -f "acp_server.py"
            ((stopped_count++))
        fi
    fi
    
    if [ $stopped_count -gt 0 ]; then
        print_success "Stopped $stopped_count server(s)"
        sleep 1
    else
        print_status "No servers were running"
    fi
}

# Function to start the hybrid server
start_hybrid_server() {
    print_header "Starting MESH Hybrid Server (MCP + A2A)"
    
    # Stop any existing servers first
    stop_servers
    
    print_status "Server will be available on:"
    echo "  - MCP: STDIO transport (for AI applications)"
    echo "  - A2A: http://127.0.0.1:8080"
    echo "  - A2A WebSocket: ws://127.0.0.1:8080/ws"
    echo ""
    print_status "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the hybrid server
    print_status "Starting hybrid server..."
    uv run python hybrid_server.py
}

# Function to start the enhanced MCP server
start_enhanced_mcp_server() {
    print_header "Starting MESH Enhanced MCP Server"
    
    # Stop any existing servers first
    stop_servers
    
    print_status "Enhanced MCP Server features:"
    echo "  - ✅ Ping: Health monitoring and connection verification"
    echo "  - ✅ Sampling: AI-powered text and image generation"
    echo "  - ✅ Elicitation: Interactive information gathering"
    echo "  - ✅ Roots: File system access control"
    echo "  - ✅ Auth: Secure user management"
    echo "  - ✅ Logging: Comprehensive activity tracking"
    echo "  - ✅ Enhanced Tools: Advanced email and contact management"
    echo ""
    print_status "Server will be available via STDIO transport"
    print_status "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the enhanced MCP server
    print_status "Starting enhanced MCP server..."
    uv run python mcp-server-enhanced.py
}

# Function to start the ACP server
start_acp_server() {
    print_header "Starting MESH ACP Server"
    
    # Stop any existing servers first
    stop_servers
    
    print_status "Server will be available on:"
    echo "  - ACP: http://127.0.0.1:8081"
    echo "  - API Docs: http://127.0.0.1:8081/docs"
    echo "  - Health Check: http://127.0.0.1:8081/health"
    echo ""
    print_status "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the ACP server
    print_status "Starting ACP server..."
    uv run python acp_server.py
}

# Function to start all servers (Hybrid + ACP)
start_all_servers() {
    print_header "Starting MESH All Servers (MCP + A2A + ACP)"
    
    # Stop any existing servers first
    stop_servers
    
    print_status "Servers will be available on:"
    echo "  - MCP: STDIO transport (for AI applications)"
    echo "  - A2A: http://127.0.0.1:8080"
    echo "  - A2A WebSocket: ws://127.0.0.1:8080/ws"
    echo "  - ACP: http://127.0.0.1:8081"
    echo "  - ACP API Docs: http://127.0.0.1:8081/docs"
    echo ""
    print_status "Press Ctrl+C to stop all servers"
    echo ""
    
    # Start hybrid server in background
    print_status "Starting hybrid server in background..."
    uv run python hybrid_server.py &
    HYBRID_PID=$!
    
    # Wait a moment for hybrid server to start
    sleep 3
    
    # Start ACP server in background
    print_status "Starting ACP server in background..."
    uv run python acp_server.py &
    ACP_PID=$!
    
    # Wait a moment for ACP server to start
    sleep 3
    
    print_status "All servers started. PIDs:"
    echo "  - Hybrid Server: $HYBRID_PID"
    echo "  - ACP Server: $ACP_PID"
    echo ""
    print_status "Monitoring servers... (Press Ctrl+C to stop all)"
    
    # Wait for either server to stop
    wait $HYBRID_PID $ACP_PID
    
    # Cleanup if we get here
    stop_servers
}

# Function to show server status
show_server_status() {
    print_status "Checking server status..."
    
    # Check if A2A server is responding
    if command_exists curl; then
        print_status "Testing A2A server health..."
        if curl -s http://127.0.0.1:8080/health > /dev/null 2>&1; then
            print_success "A2A server is responding"
            
            # Get server info
            server_info=$(curl -s http://127.0.0.1:8080/ 2>/dev/null)
            if [ $? -eq 0 ]; then
                print_status "Server info: $server_info"
            fi
        else
            print_warning "A2A server is not responding"
        fi
    fi
    
    # Check if ACP server is responding
    if command_exists curl; then
        print_status "Testing ACP server health..."
        if curl -s http://127.0.0.1:8081/health > /dev/null 2>&1; then
            print_success "ACP server is responding"
            
            # Get server info
            server_info=$(curl -s http://127.0.0.1:8081/ 2>/dev/null)
            if [ $? -eq 0 ]; then
                print_status "Server info: $server_info"
            fi
        else
            print_warning "ACP server is not responding"
        fi
    fi
    
    # Check if MCP server is running
    if pgrep -f "hybrid_server.py" > /dev/null; then
        print_success "MCP server is running"
        
        # Get process info
        mcp_pid=$(pgrep -f "hybrid_server.py")
        print_status "MCP server PID: $mcp_pid"
    else
        print_warning "MCP server is not running"
    fi
    
    # Check if A2A server process is running
    if pgrep -f "a2a_server.py" > /dev/null; then
        print_success "A2A server process is running"
        
        # Get process info
        a2a_pid=$(pgrep -f "a2a_server.py")
        print_status "A2A server PID: $a2a_pid"
    else
        print_warning "A2A server process is not running"
    fi
    
    # Check if ACP server process is running
    if pgrep -f "acp_server.py" > /dev/null; then
        print_success "ACP server process is running"
        
        # Get process info
        acp_pid=$(pgrep -f "acp_server.py")
        print_status "ACP server PID: $acp_pid"
    else
        print_warning "ACP server process is not running"
    fi
}

# Function to show usage information
show_usage() {
    print_header "MESH Server Usage"
    
    echo "This script sets up and runs MESH servers with MCP, A2A, and ACP protocols."
    echo ""
    echo "Usage:"
    echo "  ./run.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup         - Setup environment and install dependencies"
    echo "  test          - Run tests only"
    echo "  start         - Start the hybrid server (MCP + A2A)"
    echo "  start-enhanced- Start the enhanced MCP server (all MCP features)"
    echo "  start-acp     - Start the ACP server only"
    echo "  start-all     - Start all servers (MCP + A2A + ACP)"
    echo "  stop          - Stop running servers"
    echo "  restart       - Restart servers (stop + start)"
    echo "  status        - Check server status"
    echo "  help          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh setup          # Setup everything"
    echo "  ./run.sh test           # Run tests only"
    echo "  ./run.sh start          # Start hybrid server only"
    echo "  ./run.sh start-enhanced # Start enhanced MCP server (all features)"
    echo "  ./run.sh start-acp      # Start ACP server only"
    echo "  ./run.sh start-all      # Start all servers"
    echo "  ./run.sh stop           # Stop running servers"
    echo "  ./run.sh restart        # Restart servers"
    echo "  ./run.sh                # Full setup and start hybrid server"
    echo ""
    echo "For more information, see README.md"
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    
    # Kill any running server processes
    if pgrep -f "hybrid_server.py" > /dev/null; then
        print_status "Stopping hybrid server..."
        pkill -f "hybrid_server.py"
    fi
    
    if pgrep -f "a2a_server.py" > /dev/null; then
        print_status "Stopping A2A server..."
        pkill -f "a2a_server.py"
    fi
    
    if pgrep -f "acp_server.py" > /dev/null; then
        print_status "Stopping ACP server..."
        pkill -f "acp_server.py"
    fi
    
    print_success "Cleanup completed"
}

# Set trap for cleanup (only for non-status commands)
if [ "${1:-}" != "status" ]; then
    trap cleanup EXIT INT TERM
fi

# Main execution
main() {
    print_header "MESH Server Setup"
    
    # Parse command line arguments
    case "${1:-}" in
        "setup")
            print_status "Running setup only..."
            check_python_version
            check_and_install_uv
            check_project_structure
            setup_virtual_environment
            install_dependencies
            validate_configuration
            print_success "Setup completed successfully!"
            exit 0
            ;;
        "test")
            print_status "Running tests only..."
            check_python_version
            check_and_install_uv
            check_project_structure
            run_tests
            print_success "Tests completed!"
            exit 0
            ;;
        "start")
            print_status "Starting hybrid server only..."
            check_python_version
            check_and_install_uv
            check_project_structure
            start_hybrid_server
            ;;
        "start-enhanced")
            print_status "Starting enhanced MCP server only..."
            check_python_version
            check_and_install_uv
            check_project_structure
            start_enhanced_mcp_server
            ;;
        "start-acp")
            print_status "Starting ACP server only..."
            check_python_version
            check_and_install_uv
            check_project_structure
            start_acp_server
            ;;
        "start-all")
            print_status "Starting all servers..."
            check_python_version
            check_and_install_uv
            check_project_structure
            start_all_servers
            ;;
        "stop")
            print_status "Stopping servers only..."
            stop_servers
            exit 0
            ;;
        "restart")
            print_status "Restarting servers..."
            check_python_version
            check_and_install_uv
            check_project_structure
            stop_servers
            start_hybrid_server
            ;;
        "status")
            show_server_status
            exit 0
            ;;
        "help"|"-h"|"--help")
            show_usage
            exit 0
            ;;
        "")
            # No arguments - run full setup and start
            print_status "Running full setup and start hybrid server..."
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    # Full setup and start (default behavior) - only for non-status commands
    if [ "${1:-}" != "status" ]; then
        check_python_version
        check_and_install_uv
        check_project_structure
        setup_virtual_environment
        install_dependencies
        validate_configuration
        run_tests
        start_hybrid_server
    fi
}

# Run main function with all arguments
main "$@"
