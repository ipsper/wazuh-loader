#!/bin/bash

# Wazuh Load Generator - Test Runner Script
# ========================================
# Kör alla tester med konfigurerbara hostname och port argument

set -e  # Stoppa vid fel

# Färger för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default värden
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8090"
DEFAULT_API_HOST="0.0.0.0"
DEFAULT_API_PORT="8090"

# Funktioner
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
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

# Visa hjälp
show_help() {
    echo "Wazuh Load Generator - Test Runner"
    echo ""
    echo "Användning: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --host HOST        Host för load generator (default: $DEFAULT_HOST)"
    echo "  -p, --port PORT        Port för load generator (default: $DEFAULT_PORT)"
    echo "  -a, --api-host HOST    Host för API server (default: $DEFAULT_API_HOST)"
    echo "  -P, --api-port PORT    Port för API server (default: $DEFAULT_API_PORT)"
    echo "  -t, --test-type TYPE   Kör bara specifik test typ (unit, api, integration, status, all)"
    echo "  -s, --silent           Silent mode on output"
    echo "  --help                 Visa denna hjälp"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                                    # Kör alla tester med defaults"
    echo "  $0 -h localhost -p 514               # Kör med specifik host/port"
    echo "  $0 -t status                         # Kör bara status code tester"
    echo "  $0 -t unit -s                        # Kör unit tester silent"
    echo ""
}

# Parse argument
HOST="$DEFAULT_HOST"
PORT="$DEFAULT_PORT"
API_HOST="$DEFAULT_API_HOST"
API_PORT="$DEFAULT_API_PORT"
TEST_TYPE="all"
SILENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -a|--api-host)
            API_HOST="$2"
            shift 2
            ;;
        -P|--api-port)
            API_PORT="$2"
            shift 2
            ;;
        -t|--test-type)
            TEST_TYPE="$2"
            shift 2
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

# Kontrollera att virtual environment finns
if [[ ! -d "test_venv" ]]; then
    print_error "test_venv hittades inte. Kör setup_venv.sh först."
    exit 1
fi

# Aktivera virtual environment
print_info "Aktiverar test virtual environment..."
source test_venv/bin/activate

# Sätt miljövariabler för tester
export WAZUH_TEST_HOST="$HOST"
export WAZUH_TEST_PORT="$PORT"
export WAZUH_API_HOST="$API_HOST"
export WAZUH_API_PORT="$API_PORT"

print_header "Wazuh Load Generator - Test Runner"
print_info "Host: $HOST"
print_info "Port: $PORT"
print_info "API Host: $API_HOST"
print_info "API Port: $API_PORT"
print_info "Test Type: $TEST_TYPE"
echo ""

# Funktion för att köra tester
run_tests() {
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

# Kör tester baserat på typ
case "$TEST_TYPE" in
    "unit")
        run_tests "tests/test_load_generator.py" "Unit Tester"
        ;;
    "api")
        run_tests "tests/test_api_basic.py" "API Basic Tester"
        run_tests "tests/test_api_integration.py" "API Integration Tester"
        ;;
    "status")
        run_tests "tests/test_api_status_codes.py" "API Status Code Tester"
        ;;
    "integration")
        run_tests "tests/test_api_integration.py" "API Integration Tester"
        ;;
    "config")
        run_tests "tests/test_config_flexibility.py" "Config Flexibility Tester"
        ;;
    "all")
        print_header "Kör alla tester"
        
        # Kör tester i logisk ordning
        run_tests "tests/test_load_generator.py" "Unit Tester" || exit 1
        run_tests "tests/test_api_status_codes.py" "API Status Code Tester" || exit 1
        run_tests "tests/test_api_basic.py" "API Basic Tester" || exit 1
        run_tests "tests/test_config_flexibility.py" "Config Flexibility Tester" || exit 1
        run_tests "tests/test_api_integration.py" "API Integration Tester" || exit 1
        
        print_success "Alla tester slutförda framgångsrikt!"
        ;;
    *)
        print_error "Okänd test typ: $TEST_TYPE"
        echo "Tillgängliga typer: unit, api, status, integration, config, all"
        exit 1
        ;;
esac

# Sammanfattning
print_header "Test Sammanfattning"
print_info "Host: $HOST:$PORT"
print_info "API: $API_HOST:$API_PORT"
print_info "Test Type: $TEST_TYPE"
print_success "Tester slutförda!"

# Visa hur man kör specifika tester
echo ""
print_info "För att köra specifika tester:"
echo "  $0 -t unit                    # Bara unit tester"
echo "  $0 -t status                  # Bara status code tester"
echo "  $0 -t api                     # Bara API tester"
echo "  $0 -h localhost -p 514       # Med specifik host/port"
echo "  $0 -v                         # Verbose output"
