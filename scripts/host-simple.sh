#!/bin/bash
# Simple hosting script without Docker
# For users who prefer direct Python deployment

set -e

echo "🌐 RCA Agent Simple Hosting (No Docker)"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check Python installation
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    print_success "Python $python_version detected"
    
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_error "pip is not installed. Please install pip first."
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    print_success "Virtual environment activated"
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
}

# Start the server
start_server() {
    print_status "Starting RCA Agent web server..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Start server in background
    python serve.py &
    SERVER_PID=$!
    
    print_status "Waiting for server to start..."
    sleep 5
    
    # Health check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "RCA Agent is running!"
        echo ""
        echo "🌐 Access your RCA Agent at:"
        echo "   Dashboard: http://localhost:8000/web/index.html"
        echo "   API: http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "📊 Server PID: $SERVER_PID"
        echo "   To stop: kill $SERVER_PID"
        echo "   Or use: ./scripts/host-simple.sh stop"
        echo ""
        echo "Press Ctrl+C to stop the server"
        
        # Save PID for later stopping
        echo $SERVER_PID > .server.pid
        
        # Wait for server (keep script running)
        wait $SERVER_PID
    else
        print_error "Server health check failed"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
}

# Stop the server
stop_server() {
    if [ -f ".server.pid" ]; then
        SERVER_PID=$(cat .server.pid)
        print_status "Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null || true
        rm -f .server.pid
        print_success "Server stopped"
    else
        print_warning "No server PID file found. Trying to find and stop any running servers..."
        pkill -f "python serve.py" || print_warning "No running servers found"
    fi
}

# Show server status
show_status() {
    if [ -f ".server.pid" ]; then
        SERVER_PID=$(cat .server.pid)
        if ps -p $SERVER_PID > /dev/null 2>&1; then
            print_success "Server is running (PID: $SERVER_PID)"
            echo "Access at: http://localhost:8000/web/index.html"
        else
            print_error "Server PID file exists but process is not running"
            rm -f .server.pid
        fi
    else
        print_warning "Server is not running (no PID file found)"
    fi
}

# Install system dependencies (optional)
install_deps() {
    print_status "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv curl git
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y python3 python3-pip curl git
    elif command -v brew &> /dev/null; then
        # macOS
        brew install python curl git
    else
        print_warning "Could not detect package manager. Please install Python 3, pip, curl, and git manually."
    fi
    
    print_success "System dependencies installed"
}

# Main script logic
case "${1:-start}" in
    "start")
        check_python
        setup_venv
        start_server
        ;;
    "stop")
        stop_server
        ;;
    "status")
        show_status
        ;;
    "setup")
        check_python
        setup_venv
        print_success "Setup complete! Run './scripts/host-simple.sh start' to start the server."
        ;;
    "install-deps")
        install_deps
        ;;
    "help"|"-h"|"--help")
        echo "RCA Agent Simple Hosting Script (No Docker)"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start        Setup and start the server (default)"
        echo "  stop         Stop the running server"
        echo "  status       Show server status"
        echo "  setup        Setup virtual environment and dependencies only"
        echo "  install-deps Install system dependencies (requires sudo)"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                    # Setup and start server"
        echo "  $0 setup              # Just setup, don't start"
        echo "  $0 start              # Start server"
        echo "  $0 stop               # Stop server"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
