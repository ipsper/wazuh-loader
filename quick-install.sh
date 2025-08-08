#!/bin/bash
# Wazuh Load Generator - Quick Install
# Kör med: curl -fsSL https://raw.githubusercontent.com/dittnamn/wazuh-loader/main/quick-install.sh | sh

set -e

echo "🚀 Installerar Wazuh Load Generator..."

# Kontrollera Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Installerar Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "⚠️  Logga ut och in igen för att aktivera Docker"
fi

# Skapa projekt katalog
PROJECT_DIR="/opt/wazuh-loader"
sudo mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

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

COPY . .

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
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
EOF

# Skapa config.json
cat > config.json << 'EOF'
{
  "test_scenarios": {
    "light_load": {"count": 50, "delay": 0.5, "duration": 300},
    "medium_load": {"count": 200, "delay": 0.2, "duration": 600},
    "heavy_load": {"count": 500, "delay": 0.05, "duration": 1800}
  },
  "targets": {
    "local": {"host": "localhost", "port": 514, "protocol": "udp"}
  }
}
EOF

# Skapa docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  wazuh-loader:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
    volumes:
      - ./config.json:/app/config.json:ro
EOF

# Skapa enkel API server med venv-stöd
cat > api_server.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import json
import random
import socket
import time
import sys
from datetime import datetime
from faker import Faker
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Aktivera virtuell miljö om den finns
try:
    import os
    venv_path = "/opt/venv/bin/activate_this.py"
    if os.path.exists(venv_path):
        exec(open(venv_path).read(), {'__file__': venv_path})
except ImportError:
    pass

app = FastAPI(title="Wazuh Load Generator API")
fake = Faker('sv_SE')

class LoadTestRequest(BaseModel):
    target_host: str = "localhost"
    target_port: int = 514
    protocol: str = "udp"
    log_type: str = "all"
    count: int = 100
    delay: float = 0.1

def generate_ssh_logs(count=10):
    events = []
    for i in range(count):
        timestamp = datetime.now()
        ip = fake.ipv4()
        user = fake.user_name()
        event = f"sshd[{random.randint(1000, 9999)}]: Failed password for {user} from {ip} port {random.randint(1024, 65535)} ssh2"
        log_entry = f"{timestamp.strftime('%b %d %H:%M:%S')} {fake.hostname()} {event}"
        events.append(log_entry)
    return events

def send_logs(logs, target_host="localhost", target_port=514, protocol="udp", delay=0.1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM if protocol == "udp" else socket.SOCK_STREAM)
    if protocol == "tcp":
        sock.connect((target_host, target_port))
    
    sent_count = 0
    for log in logs:
        try:
            if protocol == "udp":
                sock.sendto(log.encode('utf-8'), (target_host, target_port))
            else:
                sock.send(log.encode('utf-8') + b'\n')
            sent_count += 1
            time.sleep(delay)
        except Exception as e:
            print(f"Fel vid skickning: {e}")
            break
    
    sock.close()
    return sent_count

@app.get("/")
async def root():
    return {
        "message": "Wazuh Load Generator API", 
        "version": "1.0.0",
        "python_path": sys.executable,
        "venv_active": "VIRTUAL_ENV" in os.environ
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/test/start")
async def start_test(request: LoadTestRequest):
    test_id = f"test_{int(time.time())}"
    
    # Generera och skicka loggar
    logs = generate_ssh_logs(request.count)
    sent_count = send_logs(logs, request.target_host, request.target_port, request.protocol, request.delay)
    
    return {
        "test_id": test_id,
        "status": "completed",
        "logs_sent": sent_count,
        "message": f"Skickade {sent_count} loggar till {request.target_host}:{request.target_port}"
    }

@app.get("/api/v1/scenarios")
async def get_scenarios():
    with open('config.json') as f:
        config = json.load(f)
    return {"scenarios": config.get("test_scenarios", {})}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Bygg och starta
echo "🔨 Bygger Docker image med virtuell miljö..."
docker build -t wazuh-loader .

echo "🚀 Startar Wazuh Load Generator..."
docker-compose up -d

echo "⏳ Väntar på att API ska starta..."
sleep 10

# Testa API
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Installation slutförd!"
    echo ""
    echo "🌐 API Endpoints:"
    echo "   Health: http://localhost:8000/health"
    echo "   Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 Exempel:"
    echo "   curl http://localhost:8000/health"
    echo "   curl -X POST http://localhost:8000/api/v1/test/start \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"target_host\":\"localhost\",\"count\":100}'"
    echo ""
    echo "🔧 Hantering:"
    echo "   cd $PROJECT_DIR"
    echo "   docker-compose up -d    # Starta"
    echo "   docker-compose down     # Stoppa"
    echo "   docker-compose logs -f  # Loggar"
    echo ""
    echo "🐍 Virtuell miljö: Aktiverad i containern"
else
    echo "❌ Installation misslyckades. Kontrollera loggar:"
    docker-compose logs
fi
