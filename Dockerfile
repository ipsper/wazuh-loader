FROM python:3.11-slim

# Sätt arbetskatalog
WORKDIR /app

# Installera systemberoenden
RUN apt-get update && apt-get install -y \
    gcc \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Skapa virtuell miljö
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Kopiera requirements först för bättre caching
COPY requirements.txt .

# Installera Python-beroenden i venv
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Kopiera applikationskod
COPY wazuh_loader.py .
COPY api_server.py .
COPY config.json .

# Skapa logs-katalog
RUN mkdir -p logs

# Exponera port
EXPOSE 8000

# Sätt miljövariabler
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD . /opt/venv/bin/activate && python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Starta API-servern med venv aktiverad
CMD [".", "/opt/venv/bin/activate", "&&", "python", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]
