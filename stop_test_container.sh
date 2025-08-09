#!/bin/bash

# Wazuh Load Generator - Stop Test Container
# =========================================
# Stoppar och tar bort test-containern

set -e  # Stoppa vid fel

# Färger för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
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

show_help() {
    echo "Användning: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  -f, --force          Tvinga stopp även om containern inte körs"
    echo "  -s, --silent         Silent mode on output"
    echo "  --help               Visa denna hjälp"
    echo ""
    echo "EXEMPEL:"
    echo "  $0                   # Stoppa container om den körs"
    echo "  $0 -f                # Tvinga stopp"
    echo "  $0 -s                # Silent output"
}

# Parse argument
FORCE=""
SILENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force)
            FORCE="true"
            shift
            ;;
        -s|--silent)
            SILENT="true"
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Okänd flagga: $1"
            show_help
            exit 1
            ;;
    esac
done

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

print_header "Wazuh Load Generator - Stop Test Container"
print_info "Stoppar och tar bort test-containern"
echo ""

# Kontrollera om containern körs
if docker ps | grep -q "wazuh-loader-test"; then
    print_info "Container körs - stoppar..."
    
    if [[ -z "$SILENT" ]]; then
        print_info "Container status:"
        docker ps | grep "wazuh-loader-test"
    fi
    
    # Stoppa containern
    if docker-compose -f docker-compose.test.yml down --remove-orphans; then
        print_success "Container stoppad"
    else
        print_error "Kunde inte stoppa container med docker-compose"
        exit 1
    fi
    
    # Ta bort containern helt
    if docker rm -f wazuh-loader-test 2>/dev/null; then
        print_success "Container borttagen"
    else
        print_warning "Container var redan borttagen"
    fi
    
elif [[ -n "$FORCE" ]]; then
    print_warning "Container körs inte men tvingar stopp..."
    
    # Tvinga stopp och ta bort
    docker-compose -f docker-compose.test.yml down --remove-orphans 2>/dev/null || true
    docker rm -f wazuh-loader-test 2>/dev/null || true
    
    print_success "Tvingad stopp slutförd"
    
else
    print_info "Container körs inte"
fi

# Verifiera att containern är borta
if ! docker ps -a | grep -q "wazuh-loader-test"; then
    print_success "Container är helt borttagen"
else
    print_warning "Container finns fortfarande (kanske i stopped state)"
    
    if [[ -z "$SILENT" ]]; then
        print_info "Återstående containers:"
        docker ps -a | grep "wazuh-loader-test"
    fi
fi

# Visa sammanfattning
print_header "Stop Container Sammanfattning"
print_info "Container: wazuh-loader-test"
print_info "Status: Stoppad och borttagen"
print_success "Stopp slutförd!"

# Visa hur man startar igen
echo ""
print_info "För att starta containern igen:"
echo "  ./start_test_container.sh"
echo "  ./run_container_setup_tests.sh"
