#!/bin/bash
# RCA Agent Deployment Script

set -e

echo "🚀 RCA Agent Deployment Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running!"
        echo ""
        echo "Please start Docker:"
        echo "  macOS: Open Docker Desktop application"
        echo "  Linux: sudo systemctl start docker"
        echo "  Windows: Start Docker Desktop"
        echo ""
        echo "Then try again: $0"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed and running"
}

# Build and deploy
deploy() {
    print_status "Building RCA Agent Docker image..."
    docker-compose build
    
    print_status "Starting RCA Agent services..."
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    # Health check with retry
    for i in {1..5}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "RCA Agent API is running!"
            break
        else
            if [ $i -eq 5 ]; then
                print_error "RCA Agent API health check failed after 5 attempts"
                print_status "Container logs:"
                docker-compose logs rca-agent
                print_warning "Server might still be starting. Try accessing http://localhost:8000/web/index.html directly"
                break
            else
                print_status "Health check attempt $i/5 failed, retrying in 3 seconds..."
                sleep 3
            fi
        fi
    done
    
    print_success "Deployment complete!"
    echo ""
    echo "🌐 Access your RCA Agent at:"
    echo "   Dashboard: http://localhost/web/index.html"
    echo "   API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 Monitor with:"
    echo "   docker-compose logs -f"
    echo "   docker-compose ps"
}

# Production deployment with Nginx
deploy_production() {
    print_status "Deploying RCA Agent with Nginx reverse proxy..."
    docker-compose --profile production up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    # Health check through Nginx
    if curl -f http://localhost/api/health > /dev/null 2>&1; then
        print_success "RCA Agent is running behind Nginx!"
    else
        print_error "Production deployment health check failed"
        docker-compose --profile production logs
        exit 1
    fi
    
    print_success "Production deployment complete!"
    echo ""
    echo "🌐 Access your RCA Agent at:"
    echo "   Dashboard: http://localhost/"
    echo "   API: http://localhost/api/"
    echo "   API Docs: http://localhost/api/docs"
}

# Stop services
stop() {
    print_status "Stopping RCA Agent services..."
    docker-compose down
    print_success "Services stopped"
}

# Show logs
logs() {
    docker-compose logs -f
}

# Show status
status() {
    echo "🔍 RCA Agent Status:"
    echo "==================="
    docker-compose ps
    echo ""
    echo "📊 Resource Usage:"
    docker stats --no-stream $(docker-compose ps -q) 2>/dev/null || echo "No containers running"
}

# Update deployment
update() {
    print_status "Updating RCA Agent deployment..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    print_success "Update complete!"
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        check_docker
        deploy
        ;;
    "production")
        check_docker
        deploy_production
        ;;
    "stop")
        stop
        ;;
    "logs")
        logs
        ;;
    "status")
        status
        ;;
    "update")
        check_docker
        update
        ;;
    "help"|"-h"|"--help")
        echo "RCA Agent Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  deploy      Deploy RCA Agent (default)"
        echo "  production  Deploy with Nginx reverse proxy"
        echo "  stop        Stop all services"
        echo "  logs        Show service logs"
        echo "  status      Show service status"
        echo "  update      Update and redeploy"
        echo "  help        Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
