#!/bin/bash
"""
Wazuh Load Generator - Deployment Script
========================================
Skript för att distribuera Wazuh Load Generator till andra hosts
"""

set -e

# Färger för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfiguration
IMAGE_NAME="wazuh-loader"
TAG="latest"
REGISTRY=""
CONTAINER_NAME="wazuh-loader-api"

# Funktioner
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Hjälpfunktion
show_help() {
    echo "Wazuh Load Generator - Deployment Script"
    echo ""
    echo "Användning:"
    echo "  $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build          Bygg Docker image"
    echo "  export         Exportera image till tar-fil"
    echo "  import         Importera image från tar-fil"
    echo "  push           Pusha image till registry"
    echo "  pull           Hämta image från registry"
    echo "  run            Kör container lokalt"
    echo "  deploy         Fullständig deployment"
    echo "  remote-deploy  Deploya till remote host"
    echo ""
    echo "Options:"
    echo "  --registry REGISTRY    Docker registry (t.ex. docker.io/dittnamn)"
    echo "  --tag TAG             Image tag (default: latest)"
    echo "  --host HOST           Remote host för deployment"
    echo "  --port PORT           API port (default: 8000)"
    echo "  --help               Visa denna hjälp"
    echo ""
    echo "Exempel:"
    echo "  $0 build"
    echo "  $0 export"
    echo "  $0 deploy --registry docker.io/dittnamn"
    echo "  $0 remote-deploy --host user@remote-server"
}

# Bygg image
build_image() {
    print_info "Bygger Docker image..."
    
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile hittades inte!"
        exit 1
    fi
    
    docker build -t "${IMAGE_NAME}:${TAG}" .
    
    if [ $? -eq 0 ]; then
        print_success "Image byggd: ${IMAGE_NAME}:${TAG}"
    else
        print_error "Fel vid byggning av image"
        exit 1
    fi
}

# Exportera image
export_image() {
    print_info "Exporterar image till tar-fil..."
    
    local tar_file="${IMAGE_NAME}-${TAG}.tar"
    docker save "${IMAGE_NAME}:${TAG}" > "${tar_file}"
    
    if [ $? -eq 0 ]; then
        print_success "Image exporterad: ${tar_file}"
        print_info "Filstorlek: $(du -h "${tar_file}" | cut -f1)"
    else
        print_error "Fel vid export av image"
        exit 1
    fi
}

# Importera image
import_image() {
    print_info "Importerar image från tar-fil..."
    
    local tar_file="${IMAGE_NAME}-${TAG}.tar"
    
    if [ ! -f "${tar_file}" ]; then
        print_error "Tar-fil hittades inte: ${tar_file}"
        exit 1
    fi
    
    docker load < "${tar_file}"
    
    if [ $? -eq 0 ]; then
        print_success "Image importerad: ${IMAGE_NAME}:${TAG}"
    else
        print_error "Fel vid import av image"
        exit 1
    fi
}

# Pusha till registry
push_image() {
    if [ -z "$REGISTRY" ]; then
        print_error "Registry måste anges med --registry"
        exit 1
    fi
    
    print_info "Taggar image för registry..."
    docker tag "${IMAGE_NAME}:${TAG}" "${REGISTRY}/${IMAGE_NAME}:${TAG}"
    
    print_info "Pushear image till registry..."
    docker push "${REGISTRY}/${IMAGE_NAME}:${TAG}"
    
    if [ $? -eq 0 ]; then
        print_success "Image pushead: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
    else
        print_error "Fel vid push av image"
        exit 1
    fi
}

# Hämta från registry
pull_image() {
    if [ -z "$REGISTRY" ]; then
        print_error "Registry måste anges med --registry"
        exit 1
    fi
    
    print_info "Hämtar image från registry..."
    docker pull "${REGISTRY}/${IMAGE_NAME}:${TAG}"
    
    if [ $? -eq 0 ]; then
        print_success "Image hämtad: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
    else
        print_error "Fel vid hämtning av image"
        exit 1
    fi
}

# Kör container
run_container() {
    print_info "Startar container..."
    
    # Stoppa befintlig container om den körs
    if docker ps -q -f name="${CONTAINER_NAME}" | grep -q .; then
        print_warning "Stoppar befintlig container..."
        docker stop "${CONTAINER_NAME}"
        docker rm "${CONTAINER_NAME}"
    fi
    
    # Kör ny container
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${PORT}:8000" \
        --restart unless-stopped \
        "${IMAGE_NAME}:${TAG}"
    
    if [ $? -eq 0 ]; then
        print_success "Container startad: ${CONTAINER_NAME}"
        print_info "API tillgängligt på: http://localhost:${PORT}"
        print_info "Health check: http://localhost:${PORT}/health"
        print_info "Dokumentation: http://localhost:${PORT}/docs"
    else
        print_error "Fel vid start av container"
        exit 1
    fi
}

# Fullständig deployment
deploy() {
    print_info "Startar fullständig deployment..."
    
    build_image
    
    if [ -n "$REGISTRY" ]; then
        push_image
    else
        export_image
    fi
    
    run_container
    
    print_success "Deployment slutförd!"
}

# Remote deployment
remote_deploy() {
    if [ -z "$REMOTE_HOST" ]; then
        print_error "Remote host måste anges med --host"
        exit 1
    fi
    
    print_info "Deployar till remote host: ${REMOTE_HOST}"
    
    # Bygg och exportera lokalt
    build_image
    export_image
    
    local tar_file="${IMAGE_NAME}-${TAG}.tar"
    
    # Kopiera till remote host
    print_info "Kopierar image till remote host..."
    scp "${tar_file}" "${REMOTE_HOST}:/tmp/"
    
    # Kör deployment på remote host
    print_info "Kör deployment på remote host..."
    ssh "${REMOTE_HOST}" << EOF
        set -e
        
        # Importera image
        docker load < "/tmp/${tar_file}"
        
        # Stoppa befintlig container
        if docker ps -q -f name="${CONTAINER_NAME}" | grep -q .; then
            docker stop "${CONTAINER_NAME}" || true
            docker rm "${CONTAINER_NAME}" || true
        fi
        
        # Kör ny container
        docker run -d \\
            --name "${CONTAINER_NAME}" \\
            -p "${PORT}:8000" \\
            --restart unless-stopped \\
            "${IMAGE_NAME}:${TAG}"
        
        # Rensa upp
        rm -f "/tmp/${tar_file}"
        
        echo "✅ Deployment slutförd på remote host!"
        echo "🌐 API tillgängligt på: http://\$(hostname -I | awk '{print \$1}'):${PORT}"
EOF
    
    print_success "Remote deployment slutförd!"
}

# Huvudlogik
main() {
    local command=""
    local PORT="8000"
    local REMOTE_HOST=""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            build|export|import|push|pull|run|deploy|remote-deploy)
                command="$1"
                shift
                ;;
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --tag)
                TAG="$2"
                shift 2
                ;;
            --host)
                REMOTE_HOST="$2"
                shift 2
                ;;
            --port)
                PORT="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Okänd parameter: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    if [ -z "$command" ]; then
        print_error "Inget kommando angivet"
        show_help
        exit 1
    fi
    
    # Kör kommando
    case $command in
        build)
            build_image
            ;;
        export)
            build_image
            export_image
            ;;
        import)
            import_image
            ;;
        push)
            build_image
            push_image
            ;;
        pull)
            pull_image
            ;;
        run)
            run_container
            ;;
        deploy)
            deploy
            ;;
        remote-deploy)
            remote_deploy
            ;;
        *)
            print_error "Okänt kommando: $command"
            show_help
            exit 1
            ;;
    esac
}

# Kör huvudfunktion
main "$@"
