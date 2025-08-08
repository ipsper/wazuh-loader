#!/bin/bash
"""
Wazuh Load Generator - Installation Script
=========================================
Installation script som kan köras med: curl -fsSL https://raw.githubusercontent.com/dittnamn/wazuh-loader/main/install.sh | sh
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
REPO_URL="https://github.com/dittnamn/wazuh-loader"
INSTALL_DIR="/opt/wazuh-loader"
SERVICE_NAME="wazuh-loader"
API_PORT="8000"

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
    echo "║                    Wazuh Load Generator                      ║"
    echo "║                        Installation                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Kontrollera om scriptet körs som root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Scriptet körs som root. Detta är OK för systeminstallation."
    else
        print_info "Scriptet körs som användare: $(whoami)"
    fi
}

# Kontrollera operativsystem
check_os() {
    print_info "Kontrollerar operativsystem..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Linux detekterat"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "macOS detekterat"
    else
        print_error "Stöds inte operativsystem: $OSTYPE"
        exit 1
    fi
}

# Kontrollera Docker
check_docker() {
    print_info "Kontrollerar Docker..."
    
    if command -v docker &> /dev/null; then
        print_success "Docker är installerat"
        
        # Kontrollera om Docker daemon körs
        if docker info &> /dev/null; then
            print_success "Docker daemon körs"
        else
            print_error "Docker daemon körs inte. Starta Docker och försök igen."
            exit 1
        fi
    else
        print_warning "Docker är inte installerat. Installerar Docker..."
        install_docker
    fi
}

# Installera Docker
install_docker() {
    print_info "Installerar Docker..."
    
    if [[ "$OS" == "linux" ]]; then
        # Installera Docker på Linux
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        
        # Starta Docker service
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Lägg till användare i docker grupp
        sudo usermod -aG docker $USER
        print_warning "Du måste logga ut och in igen för att docker-gruppen ska aktiveras"
        
    elif [[ "$OS" == "macos" ]]; then
        print_error "Docker Desktop måste installeras manuellt på macOS"
        print_info "Besök: https://docs.docker.com/desktop/mac/install/"
        exit 1
    fi
    
    print_success "Docker installerat"
}

# Ladda ner och förbered filer
download_files() {
    print_info "Laddar ner Wazuh Load Generator..."
    
    # Skapa temporär katalog
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Ladda ner från GitHub (eller använd lokala filer om de finns)
    if [[ -d "/tmp/wazuh-loader" ]]; then
        print_info "Använder lokala filer från /tmp/wazuh-loader"
        cp -r /tmp/wazuh-loader/* .
    else
        print_info "Laddar ner från GitHub..."
        # Här skulle du normalt ladda ner från GitHub
        # För nu skapar vi filerna lokalt
        create_files
    fi
}

# Skapa filer (ersätt med faktisk nedladdning från GitHub)
create_files() {
    print_info "Skapar installation filer..."
    
    # Skapa Dockerfile med venv
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Skapa virtuell miljö
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

COPY wazuh_loader.py .
COPY api_server.py .
COPY config.json .

RUN mkdir -p logs

EXPOSE 8000

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD . /opt/venv/bin/activate && python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD [".", "/opt/venv/bin/activate", "&&", "python", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]
EOF

    # Skapa requirements.txt
    cat > requirements.txt << 'EOF'
requests==2.31.0
faker==19.6.2
python-dateutil==2.8.2
colorama==0.4.6
argparse==1.4.0
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
EOF

    # Skapa config.json
    cat > config.json << 'EOF'
{
  "test_scenarios": {
    "light_load": {
      "description": "Lätt last för utveckling och testning",
      "count": 50,
      "delay": 0.5,
      "duration": 300
    },
    "medium_load": {
      "description": "Medium last för prestandatestning",
      "count": 200,
      "delay": 0.2,
      "duration": 600
    },
    "heavy_load": {
      "description": "Hög last för stress-testning",
      "count": 500,
      "delay": 0.05,
      "duration": 1800
    },
    "burst_load": {
      "description": "Burst-last för att testa systemets kapacitet",
      "count": 1000,
      "delay": 0.01,
      "duration": 300
    }
  },
  "targets": {
    "local": {
      "host": "localhost",
      "port": 514,
      "protocol": "udp"
    }
  }
}
EOF

    # Skapa docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  wazuh-loader-api:
    build: .
    container_name: wazuh-loader-api
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./config.json:/app/config.json:ro
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - wazuh-network

networks:
  wazuh-network:
    driver: bridge
EOF

    # Skapa systemd service fil
    cat > wazuh-loader.service << 'EOF'
[Unit]
Description=Wazuh Load Generator API
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/wazuh-loader
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    print_success "Filer skapade"
}

# Bygg Docker image
build_image() {
    print_info "Bygger Docker image med virtuell miljö..."
    
    docker build -t wazuh-loader:latest .
    
    if [[ $? -eq 0 ]]; then
        print_success "Docker image byggd"
    else
        print_error "Fel vid byggning av Docker image"
        exit 1
    fi
}

# Installera till system
install_to_system() {
    print_info "Installerar till system..."
    
    # Skapa installation katalog
    sudo mkdir -p "$INSTALL_DIR"
    
    # Kopiera filer
    sudo cp -r * "$INSTALL_DIR/"
    sudo chown -R $USER:$USER "$INSTALL_DIR"
    
    # Installera systemd service
    if [[ "$OS" == "linux" ]]; then
        sudo cp wazuh-loader.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable wazuh-loader.service
        print_success "Systemd service installerad"
    fi
    
    print_success "Installation slutförd i $INSTALL_DIR"
}

# Starta tjänsten
start_service() {
    print_info "Startar Wazuh Load Generator..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo systemctl start wazuh-loader.service
        print_success "Tjänst startad"
    else
        cd "$INSTALL_DIR"
        docker-compose up -d
        print_success "Container startad"
    fi
}

# Kontrollera installation
check_installation() {
    print_info "Kontrollerar installation..."
    
    # Vänta lite för att låta tjänsten starta
    sleep 5
    
    # Testa API
    if curl -s http://localhost:$API_PORT/health > /dev/null; then
        print_success "API är tillgängligt på http://localhost:$API_PORT"
        print_info "Dokumentation: http://localhost:$API_PORT/docs"
    else
        print_warning "API är inte tillgängligt än. Väntar..."
        sleep 10
        
        if curl -s http://localhost:$API_PORT/health > /dev/null; then
            print_success "API är nu tillgängligt"
        else
            print_error "API kunde inte startas. Kontrollera loggar:"
            if [[ "$OS" == "linux" ]]; then
                sudo journalctl -u wazuh-loader.service -f
            else
                docker-compose logs
            fi
        fi
    fi
}

# Visa användningsinformation
show_usage() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Installation Slutförd!                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo "🌐 API Endpoints:"
    echo "   Health Check: http://localhost:$API_PORT/health"
    echo "   Dokumentation: http://localhost:$API_PORT/docs"
    echo "   API Root: http://localhost:$API_PORT/"
    
    echo ""
    echo "🔧 Hantering:"
    if [[ "$OS" == "linux" ]]; then
        echo "   Starta: sudo systemctl start wazuh-loader"
        echo "   Stoppa: sudo systemctl stop wazuh-loader"
        echo "   Status: sudo systemctl status wazuh-loader"
        echo "   Loggar: sudo journalctl -u wazuh-loader -f"
    else
        echo "   Starta: cd $INSTALL_DIR && docker-compose up -d"
        echo "   Stoppa: cd $INSTALL_DIR && docker-compose down"
        echo "   Status: cd $INSTALL_DIR && docker-compose ps"
        echo "   Loggar: cd $INSTALL_DIR && docker-compose logs -f"
    fi
    
    echo ""
    echo "📝 Exempel användning:"
    echo "   # Testa API"
    echo "   curl http://localhost:$API_PORT/health"
    echo ""
    echo "   # Starta load test"
    echo "   curl -X POST http://localhost:$API_PORT/api/v1/test/start \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"target_host\":\"localhost\",\"log_type\":\"ssh\",\"count\":100}'"
    
    echo ""
    echo "📚 Mer information:"
    echo "   Installation katalog: $INSTALL_DIR"
    echo "   Konfiguration: $INSTALL_DIR/config.json"
    echo "   Docker image: wazuh-loader:latest"
    echo "   🐍 Virtuell miljö: Aktiverad i containern"
    
    echo ""
    print_success "Wazuh Load Generator är nu installerat och redo att användas!"
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
    
    check_root
    check_os
    check_docker
    download_files
    build_image
    install_to_system
    start_service
    check_installation
    show_usage
}

# Kör huvudfunktion
main "$@"
