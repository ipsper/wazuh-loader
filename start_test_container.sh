#!/bin/bash

# Wazuh Load Generator - Test Container Starter
# ============================================
# Bygger och startar test-containern på port 9090

set -e  # Stoppa vid fel

# Färger för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktioner för output
print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Kontrollera att vi är i rätt katalog
if [[ ! -f "wazuh_loader.py" ]]; then
    print_error "Kör detta script från wazuh-loader projektets rotkatalog"
    exit 1
fi

# Kontrollera att Docker är installerat
if ! command -v docker &> /dev/null; then
    print_error "Docker är inte installerat. Installera Docker först."
    exit 1
fi

# Kontrollera att Docker Compose är installerat
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose är inte installerat. Installera Docker Compose först."
    exit 1
fi

print_header "Wazuh Load Generator - Test Container"
print_info "Port: 9090"
print_info "Health endpoint: http://localhost:9090/health"
echo ""

# Stoppa eventuella existerande containrar
print_info "Stoppar eventuella existerande test-containrar..."
docker-compose -f docker-compose.test.yml down --remove-orphans 2>/dev/null || true

# Bygg och starta containern
print_header "Bygger test-container..."
docker-compose -f docker-compose.test.yml build --no-cache

print_header "Startar test-container..."
docker-compose -f docker-compose.test.yml up -d

# Vänta på att containern startar
print_info "Väntar på att containern startar..."
sleep 5

# Kontrollera container status
print_header "Container Status"
docker-compose -f docker-compose.test.yml ps

# Vänta på health check
print_info "Väntar på health check..."
for i in {1..30}; do
    if curl -f http://localhost:9090/health >/dev/null 2>&1; then
        print_success "Health check lyckades!"
        break
    fi
    if [[ $i -eq 30 ]]; then
        print_error "Health check misslyckades efter 30 försök"
        print_info "Container logs:"
        docker-compose -f docker-compose.test.yml logs
        exit 1
    fi
    echo -n "."
    sleep 2
done

# Visa container information
print_header "Container Information"
print_info "Container ID: $(docker-compose -f docker-compose.test.yml ps -q)"
print_info "API URL: http://localhost:9090"
print_info "Health URL: http://localhost:9090/health"
print_info "Root URL: http://localhost:9090/"

# Testa API
print_header "Testar API-endpoints..."
echo ""

# Testa health endpoint
print_info "Testing health endpoint..."
if curl -s http://localhost:9090/health | grep -q "healthy"; then
    print_success "Health endpoint fungerar"
else
    print_error "Health endpoint fungerar inte"
fi

# Testa root endpoint
print_info "Testing root endpoint..."
if curl -s http://localhost:9090/ | grep -q "Wazuh"; then
    print_success "Root endpoint fungerar"
else
    print_error "Root endpoint fungerar inte"
fi

echo ""
print_success "Test-container är nu tillgänglig på port 9090!"
print_info "För att stoppa containern: docker-compose -f docker-compose.test.yml down"
print_info "För att se logs: docker-compose -f docker-compose.test.yml logs -f"
print_info "För att köra tester i containern: docker exec wazuh-loader-test python -m pytest tests/"

# Visa hur man kör tester
echo ""
print_header "Exempel på API-anrop"
echo "curl http://localhost:9090/health"
echo "curl http://localhost:9090/"
echo "curl -X POST http://localhost:9090/api/v1/test/start -H 'Content-Type: application/json' -d '{\"target\":\"local\",\"duration\":10}'"
