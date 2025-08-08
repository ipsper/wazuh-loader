#!/bin/bash
"""
Wazuh Load Generator - Virtual Environment Setup
==============================================
Script för att sätta upp separata virtuella miljöer för produkt och tester
"""

set -e

# Färger för output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Konfiguration
PROD_VENV_DIR="venv"
TEST_VENV_DIR="test_venv"
PYTHON_VERSION="3.11"

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

print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                Virtual Environment Setup                      ║"
    echo "║                    Wazuh Load Generator                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Kontrollera Python-version
check_python() {
    print_info "Kontrollerar Python-version..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION_ACTUAL=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        print_success "Python $PYTHON_VERSION_ACTUAL hittad"

        if [[ "$PYTHON_VERSION_ACTUAL" == "$PYTHON_VERSION" ]]; then
            print_success "Python-version matchar krav ($PYTHON_VERSION)"
        else
            print_warning "Python-version $PYTHON_VERSION_ACTUAL (rekommenderat: $PYTHON_VERSION)"
        fi
    else
        print_error "Python3 är inte installerat"
        print_info "Installera Python 3.11 eller senare"
        exit 1
    fi
}

# Skapa produkt virtuell miljö
create_prod_venv() {
    print_info "Skapar produkt virtuell miljö..."

    if [[ -d "$PROD_VENV_DIR" ]]; then
        print_warning "Produkt virtuell miljö finns redan: $PROD_VENV_DIR"
        read -p "Vill du skapa en ny? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Tar bort befintlig produkt virtuell miljö..."
            rm -rf "$PROD_VENV_DIR"
        else
            print_info "Använder befintlig produkt virtuell miljö"
            return
        fi
    fi

    python3 -m venv "$PROD_VENV_DIR"

    if [[ $? -eq 0 ]]; then
        print_success "Produkt virtuell miljö skapad: $PROD_VENV_DIR"
    else
        print_error "Fel vid skapande av produkt virtuell miljö"
        exit 1
    fi
}

# Skapa test virtuell miljö
create_test_venv() {
    print_info "Skapar test virtuell miljö..."

    if [[ -d "$TEST_VENV_DIR" ]]; then
        print_warning "Test virtuell miljö finns redan: $TEST_VENV_DIR"
        read -p "Vill du skapa en ny? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Tar bort befintlig test virtuell miljö..."
            rm -rf "$TEST_VENV_DIR"
        else
            print_info "Använder befintlig test virtuell miljö"
            return
        fi
    fi

    python3 -m venv "$TEST_VENV_DIR"

    if [[ $? -eq 0 ]]; then
        print_success "Test virtuell miljö skapad: $TEST_VENV_DIR"
    else
        print_error "Fel vid skapande av test virtuell miljö"
        exit 1
    fi
}

# Installera produkt-beroenden
install_prod_dependencies() {
    print_info "Installerar produkt-beroenden..."

    if [[ ! -f "requirements.txt" ]]; then
        print_error "requirements.txt hittades inte"
        exit 1
    fi

    source "$PROD_VENV_DIR/bin/activate"
    pip install -r requirements.txt

    if [[ $? -eq 0 ]]; then
        print_success "Produkt-beroenden installerade"
    else
        print_error "Fel vid installation av produkt-beroenden"
        exit 1
    fi
}

# Installera test-beroenden
install_test_dependencies() {
    print_info "Installerar test-beroenden..."

    if [[ ! -f "requirements.txt" ]]; then
        print_error "requirements.txt hittades inte"
        exit 1
    fi

    if [[ ! -f "requirements_test.txt" ]]; then
        print_error "requirements_test.txt hittades inte"
        exit 1
    fi

    source "$TEST_VENV_DIR/bin/activate"
    
    # Installera produktberoenden först
    pip install -r requirements.txt
    
    # Installera testberoenden sedan
    pip install -r requirements_test.txt

    if [[ $? -eq 0 ]]; then
        print_success "Test-beroenden installerade"
    else
        print_error "Fel vid installation av test-beroenden"
        exit 1
    fi
}

# Skapa aktiveringsscript för produkt
create_prod_activation_script() {
    print_info "Skapar produkt aktiveringsscript..."

    cat > activate_prod_venv.sh << 'EOF'
#!/bin/bash
# Wazuh Load Generator - Product Virtual Environment Activator
# Kör detta script för att aktivera produktens virtuella miljö

if [[ -d "venv" ]]; then
    source venv/bin/activate
    echo "✅ Produkt virtuell miljö aktiverad"
    echo "🐍 Python: $(which python)"
    echo "📦 Pip: $(which pip)"
    echo ""
    echo "För att avaktivera, kör: deactivate"
else
    echo "❌ Produkt virtuell miljö hittades inte"
    echo "Kör ./setup_venv.sh först"
fi
EOF

    chmod +x activate_prod_venv.sh
    print_success "Produkt aktiveringsscript skapat: ./activate_prod_venv.sh"
}

# Skapa aktiveringsscript för tester
create_test_activation_script() {
    print_info "Skapar test aktiveringsscript..."

    cat > activate_test_venv.sh << 'EOF'
#!/bin/bash
# Wazuh Load Generator - Test Virtual Environment Activator
# Kör detta script för att aktivera testens virtuella miljö

if [[ -d "test_venv" ]]; then
    source test_venv/bin/activate
    echo "✅ Test virtuell miljö aktiverad"
    echo "🐍 Python: $(which python)"
    echo "📦 Pip: $(which pip)"
    echo ""
    echo "För att avaktivera, kör: deactivate"
else
    echo "❌ Test virtuell miljö hittades inte"
    echo "Kör ./setup_venv.sh först"
fi
EOF

    chmod +x activate_test_venv.sh
    print_success "Test aktiveringsscript skapat: ./activate_test_venv.sh"
}

# Skapa deaktiveringsscript
create_deactivation_script() {
    print_info "Skapar deaktiveringsscript..."

    cat > deactivate_venv.sh << 'EOF'
#!/bin/bash
# Wazuh Load Generator - Virtual Environment Deactivator

if [[ -n "$VIRTUAL_ENV" ]]; then
    deactivate
    echo "✅ Virtuell miljö avaktiverad"
else
    echo "ℹ️  Ingen virtuell miljö är aktiv"
fi
EOF

    chmod +x deactivate_venv.sh
    print_success "Deaktiveringsscript skapat: ./deactivate_venv.sh"
}

# Testa produktinstallationen
test_prod_installation() {
    print_info "Testar produktinstallationen..."

    source "$PROD_VENV_DIR/bin/activate"
    
    # Testa att Python kan importera viktiga moduler
    python -c "
import sys
print(f'Python-version: {sys.version}')
import requests
print('✅ Requests installerat')
import faker
print('✅ Faker installerat')
import fastapi
print('✅ FastAPI installerat')
import uvicorn
print('✅ Uvicorn installerat')
print('✅ Alla produktberoenden fungerar!')
"

    if [[ $? -eq 0 ]]; then
        print_success "Produktinstallationstest lyckades"
    else
        print_error "Produktinstallationstest misslyckades"
        exit 1
    fi
}

# Testa testinstallationen
test_test_installation() {
    print_info "Testar testinstallationen..."

    source "$TEST_VENV_DIR/bin/activate"
    
    # Testa att Python kan importera test-moduler
    python -c "
import sys
print(f'Python-version: {sys.version}')
import pytest
print('✅ Pytest installerat')
import httpx
print('✅ Httpx installerat')
import pytest_asyncio
print('✅ Pytest-asyncio installerat')
import pytest_cov
print('✅ Pytest-cov installerat')
print('✅ Alla testberoenden fungerar!')
"

    if [[ $? -eq 0 ]]; then
        print_success "Testinstallationstest lyckades"
    else
        print_error "Testinstallationstest misslyckades"
        exit 1
    fi
}

# Visa användningsinformation
show_usage() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Setup Slutförd!                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    echo "🐍 Produkt virtuell miljö: $PROD_VENV_DIR"
    echo "🧪 Test virtuell miljö: $TEST_VENV_DIR"

    echo ""
    echo "📝 Användning:"
    echo ""
    echo "   # Aktivera produkt virtuell miljö"
    echo "   source venv/bin/activate"
    echo "   # eller"
    echo "   ./activate_prod_venv.sh"
    echo ""
    echo "   # Aktivera test virtuell miljö"
    echo "   source test_venv/bin/activate"
    echo "   # eller"
    echo "   ./activate_test_venv.sh"
    echo ""
    echo "   # Avaktivera virtuell miljö"
    echo "   deactivate"
    echo "   # eller"
    echo "   ./deactivate_venv.sh"
    echo ""
    echo "   # Kör Wazuh Load Generator (produkt)"
    echo "   source venv/bin/activate"
    echo "   python wazuh_loader.py"
    echo "   python api_server.py"
    echo ""
    echo "   # Kör tester"
    echo "   source test_venv/bin/activate"
    echo "   python -m pytest tests/"
    echo "   python run_tests.py"

    echo ""
    echo "🔧 Hantering:"
    echo "   # Ta bort virtuella miljöer"
    echo "   rm -rf venv test_venv"
    echo ""
    echo "   # Återinstallera produktberoenden"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "   # Återinstallera testberoenden"
    echo "   source test_venv/bin/activate"
    echo "   pip install -r requirements.txt"

    echo ""
    print_success "Virtuella miljöer är redo att användas!"
}

# Huvudfunktion
main() {
    print_header

    # Kontrollera om scriptet körs interaktivt
    if [[ -t 0 ]]; then
        print_info "Interaktiv installation"
    else
        print_info "Non-interaktiv installation (curl | sh)"
    fi

    check_python
    create_prod_venv
    create_test_venv
    install_prod_dependencies
    install_test_dependencies
    create_prod_activation_script
    create_test_activation_script
    create_deactivation_script
    test_prod_installation
    test_test_installation
    show_usage
}

# Kör huvudfunktion
main "$@"
