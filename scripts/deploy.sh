#!/bin/bash
# Deployment script for MechGAIA Green Agent on AgentBeats platform.
# This script handles the deployment and configuration of the MechGAIA green agent
# for the AgentBeats platform.

set -e  # Exit on any error

# Configuration
AGENT_NAME="MechGAIA-Green-Agent"
AGENT_VERSION="0.1.0"
PYTHON_VERSION="3.13"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if virtual environment exists
check_venv() {
    if [ ! -d ".venv" ]; then
        log_error "Virtual environment not found. Please run 'uv venv' first."
        exit 1
    fi
    log_info "Virtual environment found"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    source .venv/bin/activate
    uv sync --extra dev
    log_info "Dependencies installed successfully"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    source .venv/bin/activate
    python -m pytest tests/ -v
    if [ $? -eq 0 ]; then
        log_info "All tests passed"
    else
        log_error "Tests failed"
        exit 1
    fi
}

# Create deployment package
create_package() {
    log_info "Creating deployment package..."
    
    # Create deployment directory
    DEPLOY_DIR="deploy"
    rm -rf $DEPLOY_DIR
    mkdir -p $DEPLOY_DIR
    
    # Copy necessary files
    cp agentbeats_main.py $DEPLOY_DIR/
    cp agent_card.toml $DEPLOY_DIR/
    cp agentbeats_config.py $DEPLOY_DIR/
    cp -r agents $DEPLOY_DIR/
    cp -r utils $DEPLOY_DIR/
    cp -r tasks $DEPLOY_DIR/
    cp pyproject.toml $DEPLOY_DIR/
    
    # Create requirements.txt for deployment
    source .venv/bin/activate
    pip freeze > $DEPLOY_DIR/requirements.txt
    
    # Create deployment script
    cat > $DEPLOY_DIR/deploy.sh << 'EOF'
#!/bin/bash
# Deployment script for AgentBeats platform

# Install dependencies
pip install -r requirements.txt

# Set permissions
chmod +x agentbeats_main.py

# Run the agent
python agentbeats_main.py
EOF
    
    chmod +x $DEPLOY_DIR/deploy.sh
    
    log_info "Deployment package created in $DEPLOY_DIR/"
}

# Validate agent configuration
validate_config() {
    log_info "Validating agent configuration..."
    
    # Check if agent_card.toml exists
    if [ ! -f "agent_card.toml" ]; then
        log_error "agent_card.toml not found"
        exit 1
    fi
    
    # Check if main entry point exists
    if [ ! -f "agentbeats_main.py" ]; then
        log_error "agentbeats_main.py not found"
        exit 1
    fi
    
    # Test agent info command
    source .venv/bin/activate
    python agentbeats_main.py info > /dev/null
    if [ $? -eq 0 ]; then
        log_info "Agent configuration is valid"
    else
        log_error "Agent configuration validation failed"
        exit 1
    fi
}

# Deploy to AgentBeats platform
deploy_to_agentbeats() {
    log_info "Deploying to AgentBeats platform..."
    
    # Check if AgentBeats CLI is available
    if ! command -v agentbeats &> /dev/null; then
        log_error "AgentBeats CLI not found. Please install it first."
        log_info "Install with: pip install agentbeats"
        exit 1
    fi
    
    # Deploy using AgentBeats CLI
    agentbeats deploy \
        --agent-card agent_card.toml \
        --entry-point agentbeats_main.py \
        --name "$AGENT_NAME" \
        --version "$AGENT_VERSION"
    
    if [ $? -eq 0 ]; then
        log_info "Successfully deployed to AgentBeats platform"
    else
        log_error "Deployment to AgentBeats platform failed"
        exit 1
    fi
}

# Main deployment function
main() {
    log_info "Starting deployment of $AGENT_NAME v$AGENT_VERSION"
    
    # Parse command line arguments
    case "${1:-all}" in
        "check")
            check_venv
            validate_config
            ;;
        "install")
            check_venv
            install_dependencies
            ;;
        "test")
            check_venv
            run_tests
            ;;
        "package")
            create_package
            ;;
        "deploy")
            check_venv
            validate_config
            deploy_to_agentbeats
            ;;
        "all")
            check_venv
            install_dependencies
            run_tests
            validate_config
            create_package
            log_info "Deployment preparation complete"
            log_info "To deploy to AgentBeats platform, run: $0 deploy"
            ;;
        *)
            echo "Usage: $0 {check|install|test|package|deploy|all}"
            echo ""
            echo "Commands:"
            echo "  check   - Check environment and validate configuration"
            echo "  install - Install dependencies"
            echo "  test    - Run tests"
            echo "  package - Create deployment package"
            echo "  deploy  - Deploy to AgentBeats platform"
            echo "  all     - Run all steps except deployment"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
