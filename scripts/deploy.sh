#!/bin/bash
set -e

# Kid Agent Deployment Script
# Usage: ./scripts/deploy.sh [command]
# Commands: install, start, stop, restart, status, health, rollback

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_DIR/deploy"
SERVICE_NAME="kid-agent"
INSTALL_DIR="/opt/kid-agent"
BACKUP_DIR="/opt/kid-agent-backup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Install Kid Agent as a system service
install_service() {
    log_info "Installing Kid Agent service..."

    check_root

    # Check if service already exists
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_warning "Service is already running. Stop it first? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            systemctl stop "$SERVICE_NAME"
        else
            log_info "Installation cancelled"
            return 1
        fi
    fi

    # Create user
    if ! id "$SERVICE_NAME" &>/dev/null; then
        log_info "Creating user '$SERVICE_NAME'..."
        useradd -r -s /bin/bash -d "$INSTALL_DIR" "$SERVICE_NAME"
    fi

    # Create directories
    log_info "Creating directories..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/config"

    # Copy project files
    log_info "Copying project files..."
    rsync -av --progress \
        --exclude='.venv' \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.pytest_cache' \
        --exclude='data' \
        --exclude='*.db' \
        --exclude='*.log' \
        "$PROJECT_DIR/" "$INSTALL_DIR/"

    # Set ownership
    log_info "Setting ownership..."
    chown -R "$SERVICE_NAME:$SERVICE_NAME" "$INSTALL_DIR"

    # Create virtual environment
    log_info "Creating virtual environment..."
    sudo -u "$SERVICE_NAME" python3 -m venv "$INSTALL_DIR/.venv"

    # Install dependencies
    log_info "Installing dependencies..."
    sudo -u "$SERVICE_NAME" "$INSTALL_DIR/.venv/bin/pip" install --upgrade pip
    sudo -u "$SERVICE_NAME" "$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

    # Check for .env file
    if [ ! -f "$INSTALL_DIR/config/.env" ]; then
        log_warning "Configuration file not found at $INSTALL_DIR/config/.env"
        log_info "Please create the configuration file before starting the service"
    fi

    # Install systemd service
    log_info "Installing systemd service..."
    cp "$DEPLOY_DIR/kid-agent.service" "/etc/systemd/system/$SERVICE_NAME.service"
    systemctl daemon-reload

    log_success "Kid Agent service installed successfully"
    log_info "Next steps:"
    log_info "  1. Create/Edit config file: $INSTALL_DIR/config/.env"
    log_info "  2. Start the service: sudo systemctl start $SERVICE_NAME"
    log_info "  3. Enable on boot: sudo systemctl enable $SERVICE_NAME"
    log_info "  4. Check status: sudo systemctl status $SERVICE_NAME"
}

# Start the service
start_service() {
    log_info "Starting Kid Agent service..."

    check_root

    systemctl start "$SERVICE_NAME"
    sleep 2

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Kid Agent service started successfully"
    else
        log_error "Failed to start Kid Agent service"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Stop the service
stop_service() {
    log_info "Stopping Kid Agent service..."

    check_root

    systemctl stop "$SERVICE_NAME"

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_error "Failed to stop Kid Agent service"
        exit 1
    else
        log_success "Kid Agent service stopped successfully"
    fi
}

# Restart the service
restart_service() {
    log_info "Restarting Kid Agent service..."

    check_root

    systemctl restart "$SERVICE_NAME"
    sleep 2

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Kid Agent service restarted successfully"
    else
        log_error "Failed to restart Kid Agent service"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Check service status
status_service() {
    log_info "Kid Agent service status:"
    systemctl status "$SERVICE_NAME"
}

# Health check
health_check() {
    log_info "Performing health check..."

    # Check if service is running
    if ! systemctl is-active --quiet "$SERVICE_NAME"; then
        log_error "Service is not running"
        exit 1
    fi

    # Check HTTP endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health" || echo "000")

    if [ "$response" -eq 200 ]; then
        log_success "Health check passed (HTTP $response)"

        # Show detailed health if available
        detailed_response=$(curl -s "http://localhost:8000/health/detailed" 2>/dev/null || echo "")
        if [ -n "$detailed_response" ]; then
            echo -e "\n${BLUE}Detailed Health: ${NC}"
            echo "$detailed_response" | python3 -m json.tool 2>/dev/null || echo "$detailed_response"
        fi
    else
        log_error "Health check failed (HTTP $response)"
        exit 1
    fi
}

# Rollback to previous version
rollback_service() {
    log_warning "This will rollback to the previous backup. Continue? (y/n)"
    read -r response

    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Rollback cancelled"
        return 0
    fi

    check_root

    stop_service

    if [ -d "$BACKUP_DIR" ]; then
        log_info "Restoring from backup..."

        # Create backup of current version
        cp -r "$INSTALL_DIR" "$INSTALL_DIR-rollback-$(date +%Y%m%d-%H%M%S)"

        # Restore from backup
        rm -rf "$INSTALL_DIR"
        cp -r "$BACKUP_DIR" "$INSTALL_DIR"

        log_success "Rollback completed"
        log_info "Starting service with restored version..."
        start_service
    else
        log_error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi
}

# Create backup before update
create_backup() {
    log_info "Creating backup..."

    check_root

    if [ -d "$INSTALL_DIR" ]; then
        BACKUP_NAME="$BACKUP_DIR-$(date +%Y%m%d-%H%M%S)"
        cp -r "$INSTALL_DIR" "$BACKUP_NAME"
        ln -sf "$BACKUP_NAME" "$BACKUP_DIR"

        log_success "Backup created at: $BACKUP_NAME"
    else
        log_warning "Nothing to backup (install directory not found)"
    fi
}

# Show usage
show_usage() {
    echo "Kid Agent Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install   - Install Kid Agent as a systemd service"
    echo "  start     - Start the service"
    echo "  stop      - Stop the service"
    echo "  restart   - Restart the service"
    echo "  status    - Show service status"
    echo "  health    - Perform health check"
    echo "  backup    - Create a backup of the current installation"
    echo "  rollback  - Rollback to previous backup"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  sudo $0 install"
    echo "  sudo $0 start"
    echo "  sudo $0 health"
}

# Main command handler
case "${1:-help}" in
    install)
        install_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    health)
        health_check
        ;;
    backup)
        create_backup
        ;;
    rollback)
        rollback_service
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
