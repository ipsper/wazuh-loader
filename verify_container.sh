#!/bin/bash

# Wazuh Load Generator - Container Verification
# ============================================
# Verifierar att containern fungerar utan att starta om den

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
    echo "  -s, --silent           Silent mode on output"
    echo "  --help                 Visa denna hjälp"
    echo ""
    echo "BESKRIVNING:"
    echo "  Verifierar att containern körs och fungerar korrekt:"
    echo "  - Kontrollerar att container körs"
    echo "  - Testar health endpoint"
    echo "  - Verifierar API endpoints"
    echo "  - Testar Python-miljö"
    echo ""
    echo "EXEMPEL:"
    echo "  $0                     # Verifiera container (verbose default)"
    echo "  $0 -s                  # Silent output"
}

# Parse argument
SILENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
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

# Kontrollera att virtual environment finns
if [[ ! -d "test_venv" ]]; then
    print_error "test_venv hittades inte. Kör setup_venv.sh först."
    exit 1
fi

print_header "Wazuh Load Generator - Container Verification"
print_info "Verifierar att containern fungerar korrekt"
echo ""

# Aktivera virtual environment
print_info "Aktiverar test virtual environment..."
source test_venv/bin/activate

# Sätt miljövariabler för tester
export WAZUH_TEST_HOST="0.0.0.0"
export WAZUH_TEST_PORT="514"
export WAZUH_API_HOST="0.0.0.0"
export WAZUH_API_PORT="9090"

print_header "Container Verification"
print_info "Host: $WAZUH_TEST_HOST"
print_info "Port: $WAZUH_TEST_PORT"
print_info "API Host: $WAZUH_API_HOST"
print_info "API Port: $WAZUH_API_PORT"
echo ""

# Funktion för att köra verifierings-tester
run_verification() {
    local test_pattern="$1"
    local test_name="$2"
    
    print_header "Kör $test_name"
    
    if [[ -n "$SILENT" ]]; then
        python -m pytest "$test_pattern" --tb=short -q
    else
        python -m pytest "$test_pattern" -v --tb=short
    fi
    
    if [[ $? -eq 0 ]]; then
        print_success "$test_name slutförda"
    else
        print_error "$test_name misslyckades"
        return 1
    fi
    echo ""
}

# Kör verifierings-tester
run_verification "tests/test_container_setup_verify.py" "Container Verification"

# Sammanfattning
print_header "Verification Sammanfattning"
print_info "Host: $WAZUH_TEST_HOST:$WAZUH_TEST_PORT"
print_info "API: $WAZUH_API_HOST:$WAZUH_API_PORT"
print_success "Verifiering slutförd!"

# Visa status
echo ""
print_info "Container status:"
docker ps | grep wazuh-loader-test || print_warning "Container körs inte"

print_info "Health check:"
if curl -s http://localhost:9090/health >/dev/null 2>&1; then
    print_success "Health endpoint fungerar"
else
    print_warning "Health endpoint svarar inte"
fi

# Visa hur man använder
echo ""
print_info "För att använda containern:"
echo "  curl http://localhost:9090/health"
echo "  curl http://localhost:9090/"
echo "  ./run_tests_in_container.sh"
echo ""
print_info "För att göra full setup:"
echo "  ./run_container_setup_tests.sh"
echo ""
print_info "För att stoppa containern:"
echo "  ./stop_test_container.sh"
