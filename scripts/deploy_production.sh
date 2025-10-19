#!/bin/bash
# Production Deployment Script for MechGAIA Green Agent
# This script handles production deployment with metrics and leaderboard

set -e  # Exit on any error

# Configuration
PROJECT_NAME="mechgaia-green-agent"
VERSION="0.1.0"
ENVIRONMENT="${1:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log_step "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p ssl
    
    log_info "Directories created"
}

# Build Docker images
build_images() {
    log_step "Building Docker images..."
    
    # Build the main application image
    docker build -t ${PROJECT_NAME}:${VERSION} .
    docker tag ${PROJECT_NAME}:${VERSION} ${PROJECT_NAME}:latest
    
    log_info "Docker images built successfully"
}

# Deploy with Docker Compose
deploy_services() {
    log_step "Deploying services with Docker Compose..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.prod.yml up -d
    else
        docker-compose up -d
    fi
    
    log_info "Services deployed successfully"
}

# Wait for services to be healthy
wait_for_services() {
    log_step "Waiting for services to be healthy..."
    
    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    timeout 60 bash -c 'until docker exec mechgaia-postgres pg_isready -U mechgaia; do sleep 2; done'
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    timeout 30 bash -c 'until docker exec mechgaia-redis redis-cli ping; do sleep 2; done'
    
    # Wait for Leaderboard API
    log_info "Waiting for Leaderboard API..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
    
    # Wait for MechGAIA Agent
    log_info "Waiting for MechGAIA Agent..."
    timeout 60 bash -c 'until curl -f http://localhost:8080/health; do sleep 2; done'
    
    log_info "All services are healthy"
}

# Run health checks
run_health_checks() {
    log_step "Running health checks..."
    
    # Check Leaderboard API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ Leaderboard API is healthy"
    else
        log_error "❌ Leaderboard API health check failed"
        return 1
    fi
    
    # Check MechGAIA Agent
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        log_info "✅ MechGAIA Agent is healthy"
    else
        log_error "❌ MechGAIA Agent health check failed"
        return 1
    fi
    
    # Check database connection
    if docker exec mechgaia-postgres pg_isready -U mechgaia > /dev/null 2>&1; then
        log_info "✅ PostgreSQL is healthy"
    else
        log_error "❌ PostgreSQL health check failed"
        return 1
    fi
    
    # Check Redis
    if docker exec mechgaia-redis redis-cli ping > /dev/null 2>&1; then
        log_info "✅ Redis is healthy"
    else
        log_error "❌ Redis health check failed"
        return 1
    fi
    
    log_info "All health checks passed"
}

# Test the system
test_system() {
    log_step "Testing the system..."
    
    # Test leaderboard API
    log_info "Testing leaderboard API..."
    if curl -f http://localhost:8000/leaderboard > /dev/null 2>&1; then
        log_info "✅ Leaderboard API test passed"
    else
        log_warn "⚠️ Leaderboard API test failed (may be empty)"
    fi
    
    # Test agent info endpoint
    log_info "Testing agent info endpoint..."
    if curl -f http://localhost:8080/info > /dev/null 2>&1; then
        log_info "✅ Agent info endpoint test passed"
    else
        log_warn "⚠️ Agent info endpoint test failed"
    fi
    
    log_info "System tests completed"
}

# Show deployment information
show_deployment_info() {
    log_step "Deployment Information"
    
    echo ""
    echo "🎉 MechGAIA Green Agent deployed successfully!"
    echo ""
    echo "📊 Services:"
    echo "  • MechGAIA Agent:     http://localhost:8080"
    echo "  • Leaderboard API:    http://localhost:8000"
    echo "  • Dashboard:          http://localhost:8000/dashboard"
    echo "  • PostgreSQL:        localhost:5432"
    echo "  • Redis:              localhost:6379"
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs:          docker-compose logs -f"
    echo "  • Stop services:      docker-compose down"
    echo "  • Restart services:   docker-compose restart"
    echo "  • View containers:    docker ps"
    echo ""
    echo "📈 API Endpoints:"
    echo "  • GET  /leaderboard           - Get leaderboard"
    echo "  • GET  /agent/{id}/stats      - Get agent statistics"
    echo "  • GET  /task/{level}/stats   - Get task statistics"
    echo "  • POST /evaluation            - Record evaluation"
    echo "  • GET  /dashboard             - Web dashboard"
    echo ""
    echo "🚀 Ready for AgentBeats integration!"
}

# Cleanup function
cleanup() {
    log_warn "Cleaning up..."
    docker-compose down
}

# Main deployment function
main() {
    log_info "Starting production deployment of ${PROJECT_NAME} v${VERSION}"
    log_info "Environment: ${ENVIRONMENT}"
    
    # Parse command line arguments
    case "${2:-deploy}" in
        "check")
            check_prerequisites
            ;;
        "build")
            check_prerequisites
            build_images
            ;;
        "deploy")
            check_prerequisites
            create_directories
            build_images
            deploy_services
            wait_for_services
            run_health_checks
            test_system
            show_deployment_info
            ;;
        "stop")
            cleanup
            ;;
        "restart")
            cleanup
            deploy_services
            wait_for_services
            run_health_checks
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "status")
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            ;;
        *)
            echo "Usage: $0 {production|development} {check|build|deploy|stop|restart|logs|status}"
            echo ""
            echo "Commands:"
            echo "  check   - Check prerequisites"
            echo "  build   - Build Docker images"
            echo "  deploy  - Full deployment (default)"
            echo "  stop    - Stop all services"
            echo "  restart - Restart all services"
            echo "  logs    - View service logs"
            echo "  status  - Show service status"
            exit 1
            ;;
    esac
}

# Trap cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"
