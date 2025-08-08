# Testing Guide

Denna guide beskriver hur man kör testerna för Wazuh Load Generator med separata virtuella miljöer.

## Virtuella Miljöer

Projektet använder två separata virtuella miljöer:

- **`venv/`** - Produktmiljö för att köra Wazuh Load Generator
- **`test_venv/`** - Testmiljö för att köra alla tester

## Installation

### 1. Sätt upp virtuella miljöer

```bash
# Kör setup-scriptet
./setup_venv.sh
```

Detta skapar:
- `venv/` med endast produktberoenden (`requirements.txt`)
- `test_venv/` med produkt- och testberoenden (`requirements.txt` + `requirements_test.txt`)
- Aktiveringsscript: `activate_prod_venv.sh`, `activate_test_venv.sh`
- Deaktiveringsscript: `deactivate_venv.sh`

### 2. Aktivera rätt miljö

**För produkt:**
```bash
source venv/bin/activate
# eller
./activate_prod_venv.sh
```

**För tester:**
```bash
source test_venv/bin/activate
# eller
./activate_test_venv.sh
```

## Köra Tester

### Grundläggande tester

```bash
# Aktivera testmiljö
source test_venv/bin/activate

# Kör alla tester
python -m pytest tests/

# Kör specifika tester
python -m pytest tests/test_api_basic.py
python -m pytest tests/test_load_generator.py
python -m pytest tests/test_api_integration.py

# Kör med coverage
python -m pytest tests/ --cov=. --cov-report=html
```

### Använd test runner-scriptet

```bash
# Aktivera testmiljö
source test_venv/bin/activate

# Kör alla tester
python run_tests.py

# Kör specifika testtyper
python run_tests.py --type unit
python run_tests.py --type api
python run_tests.py --type integration

# Kör med coverage
python run_tests.py --coverage
```

### Testa specifika komponenter

```bash
# API-tester
python -m pytest tests/test_api_basic.py -v

# Load generator-tester
python -m pytest tests/test_load_generator.py -v

# Integration-tester
python -m pytest tests/test_api_integration.py -v

# Konfigurationsflexibilitet-tester
python -m pytest tests/test_config_flexibility.py -v

# Prestandatester
python -m pytest tests/ -m "not slow" -v
```

## Teststruktur

```
tests/
├── __init__.py
├── test_api_basic.py          # Grundläggande API-tester
├── test_load_generator.py     # Load generator-tester
├── test_api_integration.py   # Integration-tester
└── test_config_flexibility.py # Konfigurationsflexibilitet-tester

test_support/
├── __init__.py
├── conftest.py               # Pytest fixtures
├── support_app.py            # Test support-klasser
├── utils.py                  # Utility-funktioner
├── config.py                 # Flexibel konfiguration
└── README.md
```

## Test-typer

### Unit-tester
- Testar enskilda funktioner och klasser
- Använder mocks för externa beroenden
- Snabba att köra

### API-tester
- Testar FastAPI endpoints
- Validerar request/response-format
- Testar felhantering

### Integration-tester
- Testar hela arbetsflöden
- Testar interaktion mellan komponenter
- Kan ta längre tid att köra

### Konfigurationsflexibilitet-tester
- Testar flexibel konfiguration med IP-adresser och portar
- Testar miljövariabler för dynamisk konfiguration
- Testar target-hantering och URL-generering

## Flexibel Konfiguration

Testerna stöder nu flexibel konfiguration med miljövariabler:

### Miljövariabler

```bash
# Target-konfiguration
export TEST_TARGET_HOST="192.168.1.100"
export TEST_TARGET_PORT="515"
export TEST_TARGET_PROTOCOL="tcp"

# API-konfiguration
export TEST_API_HOST="0.0.0.0"
export TEST_API_PORT="8080"

# Test-konfiguration
export TEST_TIMEOUT="60"
export TEST_DELAY="0.5"
export TEST_COUNT="25"
```

### Användning i tester

```python
from test_support.config import TestConfig, get_test_config
from test_support.utils import APITestUtils

# Skapa anpassad konfiguration
config = TestConfig()
config.update_target("custom", host="10.0.0.1", port=9999)

# Använd i tester
utils = APITestUtils(config)
request_data = utils.create_test_request_data("custom")
```

### Standardkonfiguration

```python
# Standard targets
local: localhost:514 (udp)
remote: 192.168.1.100:514 (udp)
tcp_local: localhost:601 (tcp)
tcp_remote: 192.168.1.100:601 (tcp)

# Standard API
host: localhost
port: 8000

# Standard test
timeout: 30
delay: 0.1
count: 10
```

## Coverage

Generera coverage-rapport:

```bash
# Aktivera testmiljö
source test_venv/bin/activate

# Kör med coverage
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Öppna HTML-rapport
open htmlcov/index.html
```

## Felsökning

### Vanliga problem

1. **ImportError: No module named 'pytest'**
   ```bash
   # Aktivera testmiljö
   source test_venv/bin/activate
   pip install -r requirements_test.txt
   ```

2. **ModuleNotFoundError för projektmoduler**
   ```bash
   # Säkerställ att du är i projektets rotkatalog
   cd /path/to/wazuh-loader
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

3. **ImportError: No module named 'pytest'**
   ```bash
   # Aktivera testmiljö
   source test_venv/bin/activate
   pip install -r requirements_test.txt
   ```

3. **Test failures på grund av nätverksfel**
   ```bash
   # Kör tester som inte kräver nätverk
   python -m pytest tests/ -m "not integration" -v
   ```

### Debug-tester

```bash
# Kör med debug-output
python -m pytest tests/ -v -s

# Kör endast en test
python -m pytest tests/test_api_basic.py::TestBasicAPI::test_root_endpoint -v -s

# Kör med pdb
python -m pytest tests/ --pdb
```

## CI/CD Integration

För CI/CD-pipelines:

```yaml
# Exempel för GitHub Actions
- name: Set up Python
  uses: actions/setup-python@v3
  with:
    python-version: '3.11'

- name: Install dependencies
  run: |
    python -m venv test_venv
    source test_venv/bin/activate
    pip install -r requirements_test.txt

- name: Run tests
  run: |
    source test_venv/bin/activate
    python -m pytest tests/ --cov=. --cov-report=xml
```

## Best Practices

1. **Använd rätt miljö**
   - Produkt: `source venv/bin/activate`
   - Tester: `source test_venv/bin/activate`

2. **Kör tester regelbundet**
   - Innan commits
   - Efter större ändringar
   - I CI/CD-pipeline

3. **Håll tester snabba**
   - Använd mocks för externa beroenden
   - Undvik nätverksanrop i unit-tester
   - Använd `@pytest.mark.slow` för långsamma tester

4. **Skriv testbara kod**
   - Separera logik från I/O
   - Använd dependency injection
   - Skriv små, fokuserade funktioner

## Exempel

### Skapa ny test

```python
# tests/test_new_feature.py
import pytest
from test_support.utils import APITestUtils

test_utilities = APITestUtils()

def test_new_feature(test_client):
    """Testa ny funktion"""
    response = test_client.get("/api/v1/new-endpoint")
    test_utilities.validate_api_response(response)
    
    data = response.json()
    assert "expected_field" in data
```

### Använd fixtures

```python
def test_with_fixtures(test_client, test_support, mock_socket):
    """Testa med fixtures"""
    # Använd test_client för API-anrop
    response = test_client.get("/health")
    assert response.status_code == 200
    
    # Använd test_support för hjälpfunktioner
    logs = test_support.create_test_logs("ssh", 5)
    assert len(logs) == 5
```

Detta säkerställer att testerna körs i en isolerad miljö med rätt beroenden! 🧪
