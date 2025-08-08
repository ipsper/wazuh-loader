# Wazuh Load Generator

En Python-baserad last generator för Wazuh som skapar olika typer av säkerhetsloggar för att testa och belasta Wazuh-systemet. Nu med RESTful API-stöd för enkel integration från andra hosts och virtuell miljö (venv) för bättre isolering.

## Funktioner

- **Flera loggtyper**: SSH, web server, brandvägg, system och malware-loggar
- **Konfigurerbar last**: Justerbara parametrar för antal loggar, fördröjning och testlängd
- **Fördefinierade scenarier**: Förkonfigurerade testscenarier för olika belastningsnivåer
- **Interaktivt läge**: Enkelt att använda interaktivt gränssnitt
- **Färgad output**: Tydlig visuell feedback med färgkodning
- **Flexibla mål**: Stöd för både UDP och TCP-protokoll
- **🆕 RESTful API**: Fullständig API för fjärranrop från andra hosts
- **🆕 Docker-stöd**: Enkel containerisering och deployment
- **🆕 Python-klient**: Komplett klientbibliotek för API-anrop
- **🆕 Enkel installation**: Installation scripts för snabb distribution
- **🆕 Virtuell miljö**: Automatisk venv-hantering för bättre isolering

## Installation

### 🐍 Virtuella miljöer (rekommenderat)

Projektet använder separata virtuella miljöer för produkt och tester:

```bash
# Sätt upp båda miljöerna
./setup_venv.sh

# Aktivera produktmiljö (endast produktberoenden)
source venv/bin/activate
# eller
./activate_prod_venv.sh

# Aktivera testmiljö (produkt- + testberoenden)
source test_venv/bin/activate
# eller
./activate_test_venv.sh
```

**Requirements-filer:**
- `requirements.txt` - Produktberoenden
- `requirements_test.txt` - Testberoenden

### 🚀 Snabb installation

```bash
# En-kommando installation
curl -fsSL https://github.com/ipsper/wazuh-loader/main/quick-install.sh | sh

# Eller med fullständig installation
curl -fsSL https://github.com/ipsper/wazuh-loader/main/install.sh | sh
```

### Lokal installation med venv

1. Klona repository:
```bash
git clone <repository-url>
cd wazuh-loader
```

2. Sätt upp virtuell miljö:
```bash
# Automatisk setup med venv
./setup_venv.sh

# Eller manuellt
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Aktivera virtuell miljö:
```bash
# Aktivera
source venv/bin/activate
# eller
./activate_venv.sh

# Avaktivera
deactivate
# eller
./deactivate_venv.sh
```

### Docker-installation

```bash
# Bygg och starta med Docker Compose
docker-compose up -d

# Eller bygg manuellt
docker build -t wazuh-loader .
docker run -p 8000:8000 wazuh-loader
```

## Användning

### Kommandoradsanvändning

```bash
# Aktivera virtuell miljö först
source venv/bin/activate

# Kör med standardinställningar (localhost:514 via UDP)
python wazuh_loader.py

# Ange specifikt mål
python wazuh_loader.py --host wazuh-server.example.com --port 514

# Kör endast SSH-loggar
python wazuh_loader.py --type ssh --count 1000

# Kör med TCP istället för UDP
python wazuh_loader.py --protocol tcp --port 601
```

### Test Runner (rekommenderat)

```bash
# Aktivera virtuell miljö
source venv/bin/activate

# Lista tillgängliga scenarier och mål
python run_tests.py --list

# Kör interaktivt läge
python run_tests.py --interactive

# Kör specifikt scenario
python run_tests.py --scenario medium_load --target local --type all
```

### 🆕 RESTful API

#### Starta API-servern

```bash
# Aktivera virtuell miljö
source venv/bin/activate

# Lokalt
python api_server.py

# Med Docker
docker-compose up -d

# Med specifika inställningar
python api_server.py --host 0.0.0.0 --port 8000
```

#### Använd Python-klienten

```python
# Aktivera virtuell miljö först
# source venv/bin/activate

from api_client import WazuhLoadGeneratorClient

# Skapa klient
client = WazuhLoadGeneratorClient("http://localhost:8000")

# Kontrollera hälsa
health = client.health_check()
print(health)

# Starta test
result = client.run_and_monitor(
    target_host="192.168.1.100",
    target_port=514,
    log_type="ssh",
    count=1000,
    delay=0.1
)
print(result)
```

#### Använd kommandorads-klienten

```bash
# Aktivera virtuell miljö
source venv/bin/activate

# Kontrollera API-hälsa
python api_client.py --action health

# Lista tillgängliga scenarier
python api_client.py --action scenarios

# Starta test
python api_client.py --action run --target-host 192.168.1.100 --log-type ssh --count 1000

# Övervaka test
python api_client.py --action status --test-id test_1_1234567890
```

#### REST API-exempel

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Starta test
curl -X POST "http://localhost:8000/api/v1/test/start" \
  -H "Content-Type: application/json" \
  -d '{
    "target_host": "192.168.1.100",
    "target_port": 514,
    "protocol": "udp",
    "log_type": "ssh",
    "count": 1000,
    "delay": 0.1
  }'

# Övervaka test
curl -X GET "http://localhost:8000/api/v1/test/test_1_1234567890"
```

### Kommandoradsalternativ

#### wazuh_loader.py
- `--host`: Målvärd (default: localhost)
- `--port`: Målport (default: 514)
- `--protocol`: Protokoll (udp/tcp, default: udp)
- `--type`: Loggtyp (all/ssh/web/firewall/system/malware, default: all)
- `--count`: Antal loggar per typ (default: 100)
- `--delay`: Fördröjning mellan loggar i sekunder (default: 0.1)
- `--duration`: Testlängd i sekunder (default: oändligt)

#### run_tests.py
- `--scenario`: Testscenario att köra
- `--target`: Mål att skicka loggar till
- `--type`: Loggtyp (default: all)
- `--list`: Lista tillgängliga scenarier och mål
- `--interactive` eller `-i`: Kör i interaktivt läge

#### 🆕 api_server.py
- `--host`: Server host (default: 0.0.0.0)
- `--port`: Server port (default: 8000)
- `--reload`: Aktivera auto-reload för utveckling

#### 🆕 api_client.py
- `--server`: API server URL (default: http://localhost:8000)
- `--action`: Åtgärd att utföra (health/scenarios/targets/start/status/result/stop/delete/list/run)
- `--test-id`: Test ID (för status, result, stop, delete)
- Samma parametrar som wazuh_loader.py för test-konfiguration

## API Endpoints

### Grundläggande
- `GET /` - API-information
- `GET /health` - Health check
- `GET /docs` - Interaktiv API-dokumentation (Swagger UI)

### Test Management
- `GET /api/v1/scenarios` - Hämta tillgängliga testscenarier
- `GET /api/v1/targets` - Hämta tillgängliga mål
- `POST /api/v1/test/start` - Starta nytt test
- `GET /api/v1/test/{test_id}` - Hämta test status
- `GET /api/v1/test/{test_id}/result` - Hämta test resultat
- `POST /api/v1/test/{test_id}/stop` - Stoppa test
- `DELETE /api/v1/test/{test_id}` - Ta bort test
- `GET /api/v1/test` - Lista alla tester

## Testscenarier

### Lätt last (light_load)
- **Antal loggar**: 50 per typ
- **Fördröjning**: 0.5s
- **Längd**: 5 minuter
- **Användning**: Utveckling och grundläggande testning

### Medium last (medium_load)
- **Antal loggar**: 200 per typ
- **Fördröjning**: 0.2s
- **Längd**: 10 minuter
- **Användning**: Prestandatestning

### Hög last (heavy_load)
- **Antal loggar**: 500 per typ
- **Fördröjning**: 0.05s
- **Längd**: 30 minuter
- **Användning**: Stress-testning

### Burst last (burst_load)
- **Antal loggar**: 1000 per typ
- **Fördröjning**: 0.01s
- **Längd**: 5 minuter
- **Användning**: Kapacitetstestning

## Loggtyper

### SSH-loggar
- Misslyckade inloggningsförsök
- Lyckade inloggningar
- Ogiltiga användare
- Anslutningsavbrott
- PAM-autentiseringsfel

### Web server loggar
- HTTP-requests (GET, POST, PUT, DELETE)
- Olika statuskoder (200, 404, 403, 500, etc.)
- User-Agent strängar
- Olika URL:er inklusive säkerhetsrelevanta

### Brandväggsloggar
- iptables-händelser
- DROP/ACCEPT/LOG-regler
- TCP/UDP-protokoll
- MAC-adresser och IP-adresser

### Systemloggar
- systemd-tjänster
- Kernel-händelser
- Cron-jobb
- sudo-kommandon
- Användarsessioner

### Malware-loggar
- ClamAV-detekteringar
- Antivirus-händelser
- Säkerhetsskanningar
- Misstänkt aktivitet

## Konfiguration

Redigera `config.json` för att anpassa:
- Testscenarier
- Målservrar
- Loggtyper och vikter

## Exempel

### Snabbt test
```bash
# Aktivera venv
source venv/bin/activate

python wazuh_loader.py --count 50 --delay 0.5 --duration 60
```

### Stress-test
```bash
source venv/bin/activate
python run_tests.py --scenario heavy_load --target local
```

### Specifikt mål
```bash
source venv/bin/activate
python wazuh_loader.py --host 192.168.1.100 --port 514 --type firewall --count 1000
```

### 🆕 API-test
```bash
# Starta API
source venv/bin/activate
python api_server.py

# I annan terminal
source venv/bin/activate
python api_client.py --action run --target-host 192.168.1.100 --log-type ssh --count 1000
```

### 🆕 Docker-test
```bash
# Starta med Docker
docker-compose up -d

# Testa API
curl http://localhost:8000/health

# Kör test via API
python api_client.py --action run --target-host localhost --log-type ssh --count 100
```

### 🆕 Snabb installation
```bash
# En-kommando installation
curl -fsSL https://raw.githubusercontent.com/dittnamn/wazuh-loader/main/quick-install.sh | sh

# Testa efter installation
curl http://localhost:8000/health
```

### 🆕 Venv-hantering
```bash
# Sätt upp venv
./setup_venv.sh

# Aktivera venv
./activate_venv.sh

# Kör programmet
python wazuh_loader.py

# Avaktivera venv
./deactivate_venv.sh
```

## 🧪 Tester

Se [TESTING.md](TESTING.md) för detaljerad information om hur man kör testerna.

### Snabb test-körning

```bash
# Aktivera testmiljö
source test_venv/bin/activate

# Kör alla tester
python -m pytest tests/

# Kör med coverage
python -m pytest tests/ --cov=. --cov-report=html

# Använd test runner
python run_tests.py --type all --coverage
```

### Teststruktur

```
tests/
├── test_api_basic.py          # Grundläggande API-tester
├── test_load_generator.py     # Load generator-tester
└── test_api_integration.py   # Integration-tester

test_support/
├── conftest.py               # Pytest fixtures
├── support_app.py            # Test support-klasser
└── utils.py                  # Utility-funktioner
```

## Felsökning

### Vanliga problem

1. **Anslutningsfel**: Kontrollera att Wazuh-servern lyssnar på rätt port
2. **Inga loggar visas**: Verifiera att Wazuh är konfigurerat att ta emot syslog
3. **Prestanda**: Justera `--delay` parametern för att kontrollera belastningen
4. **🆕 API-fel**: Kontrollera att API-servern körs på rätt port
5. **🆕 Venv-fel**: Kontrollera att virtuell miljö är aktiverad

### Debug-läge
```bash
source venv/bin/activate
python wazuh_loader.py --count 10 --delay 1.0
```

### 🆕 API Debug
```bash
# Starta API med debug
source venv/bin/activate
python api_server.py --reload

# Testa anslutning
python api_client.py --action health
```

### 🆕 Venv Debug
```bash
# Kontrollera venv-status
echo $VIRTUAL_ENV
which python
which pip

# Återinstallera venv
rm -rf venv
./setup_venv.sh
```

## Säkerhet

⚠️ **Viktigt**: Denna verktyg är endast avsett för testning i kontrollerade miljöer. Använd aldrig mot produktionssystem utan tillstånd.

### 🆕 API-säkerhet
- API:et är konfigurerat för utveckling och testning
- För produktion, överväg att lägga till autentisering och HTTPS
- Använd brandvägg för att begränsa åtkomst till API:et

### 🆕 Venv-säkerhet
- Virtuell miljö isolerar beroenden från systemet
- Inga konflikter med andra Python-projekt
- Enkel att ta bort: `rm -rf venv`

## Bidrag

Förslag och buggrapporter är välkomna! Skapa en issue eller pull request.

## Licens

MIT License 
