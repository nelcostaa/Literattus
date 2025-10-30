#!/bin/bash
# Common functions for Literattus management scripts

# Detect which docker compose command to use
detect_docker_compose() {
    if command -v docker &> /dev/null; then
        if docker compose version &> /dev/null 2>&1; then
            echo "docker compose"
            return 0
        elif command -v docker-compose &> /dev/null; then
            echo "docker-compose"
            return 0
        fi
    fi
    echo ""
    return 1
}

# Get Docker Compose command or exit with error
get_docker_compose_cmd() {
    local cmd=$(detect_docker_compose)
    if [ -z "$cmd" ]; then
        echo "❌ Error: Docker Compose not found!"
        echo "Please install Docker and Docker Compose."
        exit 1
    fi
    echo "$cmd"
}

# Navigate to project root
goto_project_root() {
    cd "$(dirname "$0")/.." || exit 1
}

# Check if services are running
check_services_running() {
    local cmd=$(get_docker_compose_cmd)
    local running=$(sudo $cmd ps -q 2>/dev/null | wc -l)
    [ "$running" -gt 0 ]
}

