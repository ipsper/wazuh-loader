# Test Support Library

Detta bibliotek innehåller support-kod för tester av Wazuh Load Generator.

## Struktur

```
test_support/
├── __init__.py          # Paket-initiering och exports
├── conftest.py          # Pytest-konfiguration och fixtures
├── support_app.py       # Huvudklasser för test support
├── utils.py             # Utility-funktioner för tester
└── README.md           # Denna dokumentation
```

## Huvudkomponenter

### TestSupportApp
Huvudklass för test support med metoder för:
- Skapa test-konfigurationer
- Generera test-loggar
- Mock socket-funktionalitet
- Skapa test request data

### TestFixtures
Pytest fixtures för:
- `test_client`: FastAPI test client
- `async_client`: Async HTTP client
- `test_support`: TestSupportApp-instans
- `test_config`: Test-konfiguration
- `mock_socket`: Mock socket för tester
- `temp_config_file`: Temporär config-fil

### TestUtilities
Statiska utility-funktioner för:
- `wait_for_api_ready()`: Vänta på API-beredskap
- `validate_api_response()`: Validera API-svar
- `check_test_completion()`: Kontrollera test-slutförande
- `create_test_log_entry()`: Skapa test log-entry

## Användning

### I test-filer

```python
from test_support.utils import APITestUtils, TestLogGenerator

# Använd utilities
test_utilities = APITestUtils()
test_utilities.validate_api_response(response)

# Använd log generator
log_gen = TestLogGenerator()
logs = log_gen.generate_logs("ssh", 10)
```

### Med fixtures

```python
def test_example(test_client, test_support, mock_socket):
    # Använd fixtures direkt
    response = test_client.get("/health")
    assert response.status_code == 200
```

### Med utilities

```python
from test_support.utils import MockUtils, PerformanceUtils

# Skapa mocks
mock_socket = MockUtils.create_mock_socket()

# Mät prestanda
result, execution_time = PerformanceUtils.measure_execution_time(
    some_function, arg1, arg2
)
PerformanceUtils.assert_performance_threshold(execution_time, 1.0)
```

## Loggtyper

TestLogGenerator stöder följande loggtyper:
- `ssh`: SSH-anslutningsloggar
- `web`: Web-serverloggar
- `firewall`: Brandväggsloggar
- `system`: Systemloggar
- `malware`: Malware-detektionsloggar

## Mocking

MockUtils tillhandahåller:
- `create_mock_socket()`: Mock socket för nätverkstester
- `create_mock_generator()`: Mock generator för load generator-tester

## Prestandatester

PerformanceUtils tillhandahåller:
- `measure_execution_time()`: Mät exekveringstid
- `assert_performance_threshold()`: Assert prestandakrav

## Exempel

Se `tests/`-katalogen för kompletta exempel på hur biblioteket används.
