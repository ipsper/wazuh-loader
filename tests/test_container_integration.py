#!/usr/bin/env python3
"""
Wazuh Load Generator - Container Integration Tests
=================================================
Testar container-funktionalitet och API-integration

Denna test suite fokuserar på:
✅ Container health och tillgänglighet
✅ API-endpoints i container-miljö
✅ Load test-funktionalitet i container
✅ Nätverkskommunikation från container
✅ Test-körning i container-miljö

Alla tester körs mot container-API:et på port 9090.
"""

import pytest
from test_support.container_utils import *


def test_container_health_endpoint():
    """Testa att health endpoint fungerar i container"""
    status_code, data = get_container_health_endpoint()
    
    assert status_code == 200
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "active_tests" in data


def test_container_root_endpoint():
    """Testa att root endpoint fungerar i container"""
    status_code, data = get_container_root_endpoint()
    
    assert status_code == 200
    assert "message" in data
    assert "Wazuh" in data["message"]
    assert "endpoints" in data
    assert "start_test" in data["endpoints"]


def test_container_api_documentation():
    """Testa att API-dokumentation är tillgänglig"""
    status_code, content_type = get_container_api_documentation()
    
    assert status_code == 200
    assert "text/html" in content_type


def test_container_scenarios_endpoint():
    """Testa att scenarios endpoint fungerar"""
    status_code, data = get_container_scenarios_endpoint()
    
    assert status_code == 200
    # API returnerar ett objekt med count och scenarios
    assert isinstance(data, dict)
    assert "count" in data
    assert "scenarios" in data
    assert len(data["scenarios"]) > 0


def test_container_targets_endpoint():
    """Testa att targets endpoint fungerar"""
    status_code, data = get_container_targets_endpoint()
    
    assert status_code == 200
    # API returnerar ett objekt med count och targets
    assert isinstance(data, dict)
    assert "count" in data
    assert "targets" in data
    assert len(data["targets"]) > 0


def test_container_start_load_test():
    """Testa att starta load test i container"""
    test_data = {
        "target": "local",
        "duration": 1,  # Bara 1 sekund
        "log_types": ["ssh"],
        "logs_per_cycle": 2,
        "cycle_delay": 0.1
    }
    
    status_code, data = start_container_load_test(test_data)
    
    assert status_code == 200
    assert "test_id" in data
    assert "status" in data
    assert data["status"] == "started"
    assert "start_time" in data


def test_container_list_tests():
    """Testa att lista aktiva tester"""
    status_code, data = get_container_list_tests()
    
    assert status_code == 200
    # API returnerar ett objekt med test-statistik
    assert isinstance(data, dict)
    assert "tests" in data
    assert isinstance(data["tests"], list)


def test_container_invalid_test_request():
    """Testa felhantering för ogiltiga test-requests"""
    invalid_data = {
        "target": "invalid_target",
        "duration": 1
    }
    
    status_code, data = send_container_invalid_test_request(invalid_data)
    
    assert status_code == 400


def test_container_network_connectivity():
    """Testa nätverksanslutning från container"""
    status_code, data = check_container_network_connectivity()
    
    assert status_code == 200


def test_container_api_response_time():
    """Testa API-svarstid i container"""
    status_code, response_time = measure_container_api_response_time()
    
    assert status_code == 200
    assert response_time < 2.0  # Ska svara inom 2 sekunder


def test_container_ssh_log_generation():
    """Testa SSH log generation i container"""
    status_code, data = run_container_ssh_log_generation()
    
    assert status_code == 200


def test_container_web_log_generation():
    """Testa web log generation i container"""
    status_code, data = run_container_web_log_generation()
    
    assert status_code == 200


def test_container_multiple_log_types():
    """Testa flera log-typer samtidigt i container"""
    status_code, data = run_container_multiple_log_types()
    
    assert status_code == 200


def test_container_environment_variables():
    """Testa att miljövariabler är korrekt satta"""
    status_code, data = check_container_environment_variables()
    
    assert status_code == 200
    assert "status" in data
    assert data["status"] == "healthy"


def test_container_port_accessibility():
    """Testa att port 9090 är tillgänglig"""
    status_code, data = check_container_port_accessibility()
    
    assert status_code == 200
    assert "message" in data


def test_container_api_version():
    """Testa API-version i container"""
    status_code, data = get_container_api_version()
    
    assert status_code == 200
    assert "version" in data
    assert data["version"] == "1.0.0"
