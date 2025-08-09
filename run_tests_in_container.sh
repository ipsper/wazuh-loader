#!/bin/bash

# Wazuh Load Generator - Test Runner i Container
# =============================================
# Kör tester i Docker-containern

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

# Default värden
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="514"
DEFAULT_API_HOST="0.0.0.0"
DEFAULT_API_PORT="9090"

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
            echo "Användning: $0 [OPTIONS]"
            echo ""
            echo "OPTIONS:"
            echo "  -h, --host HOST        Test host (default: $DEFAULT_HOST)"
            echo "  -p, --port PORT        Test port (default: $DEFAULT_PORT)"
            echo "  -a, --api-host HOST    API host (default: $DEFAULT_API_HOST)"
            echo "  -P, --api-port PORT    API port (default: $DEFAULT_API_PORT)"
                                echo "  -t, --test-type TYPE   Test typ: unit, api, status, integration, container, setup, config, all (default: all)"
            echo "  -s, --silent           Silent mode on output"
            echo "  --help                 Visa denna hjälp"
            echo ""
            echo "EXEMPEL:"
            echo "  $0                     # Kör alla tester"
            echo "  $0 -t status           # Kör bara status tester"
            echo "  $0 -h localhost -p 514 # Med specifik host/port"
            exit 0
            ;;
        *)
            print_error "Okänd flagga: $1"
            echo "Använd --help för hjälp"
            exit 1
            ;;
    esac
done

# Kontrollera att vi är i rätt katalog
if [[ ! -f "wazuh_loader.py" ]]; then
    print_error "Kör detta script från wazuh-loader projektets rotkatalog"
    exit 1
fi

# Kontrollera att containern körs
if ! docker ps | grep -q "wazuh-loader-test"; then
    print_error "Test-containern körs inte. Starta den först med: ./start_test_container.sh"
    exit 1
fi

print_header "Wazuh Load Generator - Test Runner i Container"
print_info "Container: wazuh-loader-test"
print_info "Host: $HOST"
print_info "Port: $PORT"
print_info "API Host: $API_HOST"
print_info "API Port: $API_PORT"
print_info "Test Type: $TEST_TYPE"
echo ""

# Sätt miljövariabler för tester
export WAZUH_TEST_HOST="$HOST"
export WAZUH_TEST_PORT="$PORT"
export WAZUH_API_HOST="$API_HOST"
export WAZUH_API_PORT="$API_PORT"

# Funktion för att köra tester i containern
run_tests_in_container() {
    local test_pattern="$1"
    local test_name="$2"
    
    print_header "Kör $test_name i container"
    
    if [[ -n "$SILENT" ]]; then
        docker exec wazuh-loader-test python -m pytest "$test_pattern" --tb=short -q
    else
        docker exec wazuh-loader-test python -m pytest "$test_pattern" -v --tb=short
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
        run_tests_in_container "tests/test_load_generator.py" "Unit Tester"
        ;;
    "api")
        run_tests_in_container "tests/test_api_basic.py" "API Basic Tester"
        run_tests_in_container "tests/test_api_integration.py" "API Integration Tester"
        ;;
    "status")
        run_tests_in_container "tests/test_api_status_codes.py" "API Status Code Tester"
        ;;
    "integration")
        run_tests_in_container "tests/test_api_integration.py" "API Integration Tester"
        ;;
                "container")
                run_tests_in_container "tests/test_container_integration.py" "Container Integration Tester"
                ;;
            "setup")
                run_tests_in_container "tests/test_container_setup.py" "Container Setup Tester"
                ;;
    "config")
        run_tests_in_container "tests/test_config_flexibility.py" "Config Flexibility Tester"
        ;;
    "all")
        print_header "Kör alla tester i container"
        
        # Kör tester i logisk ordning
        run_tests_in_container "tests/test_load_generator.py" "Unit Tester" || exit 1
        run_tests_in_container "tests/test_api_status_codes.py" "API Status Code Tester" || exit 1
        run_tests_in_container "tests/test_api_basic.py" "API Basic Tester" || exit 1
        run_tests_in_container "tests/test_config_flexibility.py" "Config Flexibility Tester" || exit 1
                        run_tests_in_container "tests/test_container_setup.py" "Container Setup Tester" || exit 1
                run_tests_in_container "tests/test_container_integration.py" "Container Integration Tester" || exit 1
        run_tests_in_container "tests/test_api_integration.py" "API Integration Tester" || exit 1
        
        print_success "Alla tester slutförda framgångsrikt!"
        ;;
    *)
        print_error "Okänd test typ: $TEST_TYPE"
                    echo "Tillgängliga typer: unit, api, status, integration, container, setup, config, all"
        exit 1
        ;;
esac

# Sammanfattning
print_header "Test Sammanfattning"
print_info "Container: wazuh-loader-test"
print_info "Host: $HOST:$PORT"
print_info "API: $API_HOST:$API_PORT"
print_info "Test Type: $TEST_TYPE"
print_success "Tester slutförda i container!"

# Visa hur man kör specifika tester
echo ""
print_info "För att köra specifika tester i containern:"
            echo "  $0 -t unit                    # Bara unit tester"
            echo "  $0 -t status                  # Bara status code tester"
            echo "  $0 -t api                     # Bara API tester"
            echo "  $0 -t setup                   # Bara container setup tester"
            echo "  $0 -t container               # Bara container integration tester"
            echo "  $0 -h localhost -p 514       # Med specifik host/port"
            echo "  $0 -v                         # Verbose output"
