#!/bin/bash

# Wazuh Load Generator - Container Setup Test Runner
# ================================================
# Kör container setup tester utanför containern

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
    echo "EXEMPEL:"
    echo "  $0                     # Kör setup tester (verbose default)"
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

# Kontrollera att virtual environment finns
if [[ ! -d "test_venv" ]]; then
    print_error "test_venv hittades inte. Kör setup_venv.sh först."
    exit 1
fi

print_header "Wazuh Load Generator - Container FULL SETUP"
print_info "STOPPAR, TAR BORT, BYGGER och INSTALLERAR container från scratch"
echo ""

# Aktivera virtual environment
print_info "Aktiverar test virtual environment..."
source test_venv/bin/activate

# Sätt miljövariabler för tester
export WAZUH_TEST_HOST="0.0.0.0"
export WAZUH_TEST_PORT="514"
export WAZUH_API_HOST="0.0.0.0"
export WAZUH_API_PORT="9090"

print_header "Container Setup Tests"
print_info "Host: $WAZUH_TEST_HOST"
print_info "Port: $WAZUH_TEST_PORT"
print_info "API Host: $WAZUH_API_HOST"
print_info "API Port: $WAZUH_API_PORT"
echo ""

# Funktion för att köra setup tester
run_setup_tests() {
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

# Kör setup tester
run_setup_tests "tests/test_container_full_setup.py" "Container Full Setup Tester"

# Sammanfattning
print_header "Setup Test Sammanfattning"
print_info "Host: $WAZUH_TEST_HOST:$WAZUH_TEST_PORT"
print_info "API: $WAZUH_API_HOST:$WAZUH_API_PORT"
print_success "Setup tester slutförda!"

# Visa hur man kör specifika tester
echo ""
print_info "För att köra specifika tester:"
echo "  $0                    # Kör setup tester"
echo "  $0 -v                 # Verbose output"
