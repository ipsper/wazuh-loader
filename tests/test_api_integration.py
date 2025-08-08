#!/usr/bin/env python3
"""
Wazuh Load Generator - API Integration Tests
===========================================
Integrationstester för FastAPI-endpoints (mockade för att undvika riktiga load generator-tester)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from test_support.api_utils import (
    get_start_test_basic_response,
    get_start_test_with_scenario_response,
    get_start_test_all_log_types_responses,
    get_start_test_different_protocols_responses,
    get_test_status_response,
    get_stop_test_response,
    get_delete_test_response,
    get_test_result_response,
    get_test_result_invalid_id_response,
    get_scenarios_response,
    get_targets_response,
    get_full_test_lifecycle_responses,
    get_multiple_concurrent_tests_responses,
    get_invalid_scenario_response,
    get_invalid_target_response,
    get_network_error_handling_response
)


@pytest.fixture(autouse=True)
def mock_load_generator():
    """Mocka WazuhLoadGenerator för att undvika riktiga nätverksanrop"""
    with patch('api_server.WazuhLoadGenerator') as mock:
        # Mocka generator-instansen
        mock_instance = MagicMock()
        mock_instance.send_logs.return_value = 5  # Returnera 5 skickade loggar
        mock_instance.generate_ssh_logs.return_value = ["ssh log 1", "ssh log 2"]
        mock_instance.generate_web_logs.return_value = ["web log 1", "web log 2"]
        mock_instance.generate_firewall_logs.return_value = ["firewall log 1", "firewall log 2"]
        mock_instance.generate_system_logs.return_value = ["system log 1", "system log 2"]
        mock_instance.generate_malware_logs.return_value = ["malware log 1", "malware log 2"]
        mock.return_value = mock_instance
        yield mock


def test_start_test_basic(test_client: TestClient, mock_load_generator):
    """Testa grundläggande test-start (mockad)"""
    response, data = get_start_test_basic_response(test_client)
    
    assert response.status_code == 200
    assert "test_id" in data
    assert "status" in data
    assert "message" in data
    assert data["status"] == "started"
    assert "test_" in data["test_id"]


def test_start_test_with_scenario(test_client: TestClient, mock_load_generator):
    """Testa test-start med scenario (mockad)"""
    response, data = get_start_test_with_scenario_response(test_client)
    
    assert response.status_code == 200
    assert "test_id" in data
    assert data["status"] == "started"


def test_start_test_all_log_types(test_client: TestClient, mock_load_generator):
    """Testa test-start med alla loggtyper (mockad)"""
    responses = get_start_test_all_log_types_responses(test_client)
    
    for response, data in responses:
        assert response.status_code == 200
        assert data["status"] == "started"


def test_start_test_different_protocols(test_client: TestClient, mock_load_generator):
    """Testa test-start med olika protokoll (mockad)"""
    responses = get_start_test_different_protocols_responses(test_client)
    
    for response, data in responses:
        assert response.status_code == 200
        assert data["status"] == "started"


def test_get_test_status(test_client: TestClient, mock_load_generator):
    """Testa hämta test status (mockad)"""
    response, data, test_id = get_test_status_response(test_client)
    
    assert response.status_code == 200
    assert "test_id" in data
    assert "status" in data
    assert data["test_id"] == test_id


def test_stop_test(test_client: TestClient, mock_load_generator):
    """Testa stoppa test (mockad)"""
    response, data, test_id = get_stop_test_response(test_client)
    
    assert response.status_code == 200
    assert "test_id" in data
    assert "status" in data
    assert data["status"] == "stopped"


def test_delete_test(test_client: TestClient, mock_load_generator):
    """Testa ta bort test (mockad)"""
    response, data, test_id = get_delete_test_response(test_client)
    
    assert response.status_code == 200
    assert "test_id" in data
    assert "status" in data
    assert data["status"] == "deleted"


def test_get_test_result(test_client: TestClient, mock_load_generator):
    """Testa hämta test resultat (mockad)"""
    response, data, test_id = get_test_result_response(test_client)
    
    assert response.status_code == 200
    assert "test_id" in data
    assert "status" in data
    assert "total_logs_sent" in data
    assert "total_time" in data
    assert "logs_per_second" in data


def test_get_test_result_invalid_id(test_client: TestClient, mock_load_generator):
    """Testa hämta test resultat med ogiltigt ID (mockad)"""
    response = get_test_result_invalid_id_response(test_client)
    assert response.status_code == 404


def test_get_scenarios(test_client: TestClient, mock_load_generator):
    """Testa hämta scenarier (mockad)"""
    response, data = get_scenarios_response(test_client)
    
    assert response.status_code == 200
    assert "scenarios" in data
    assert "count" in data
    
    scenarios = data["scenarios"]
    assert isinstance(scenarios, dict)
    assert len(scenarios) > 0
    
    # Validera scenario-struktur
    for scenario_name, scenario_data in scenarios.items():
        assert "description" in scenario_data
        assert "count" in scenario_data
        assert "delay" in scenario_data
        assert "duration" in scenario_data


def test_get_targets(test_client: TestClient, mock_load_generator):
    """Testa hämta targets (mockad)"""
    response, data = get_targets_response(test_client)
    
    assert response.status_code == 200
    assert "targets" in data
    assert "count" in data
    
    targets = data["targets"]
    assert isinstance(targets, dict)
    assert len(targets) > 0
    
    # Validera target-struktur
    for target_name, target_data in targets.items():
        assert "host" in target_data
        assert "port" in target_data
        assert "protocol" in target_data


def test_full_test_lifecycle(test_client: TestClient, mock_load_generator):
    """Testa fullständig test-cykel (mockad)"""
    lifecycle_data = get_full_test_lifecycle_responses(test_client)
    
    # Validera start
    assert lifecycle_data["start"]["status"] == "started"
    assert "test_id" in lifecycle_data["start"]
    
    # Validera status
    assert "test_id" in lifecycle_data["status"]
    assert "status" in lifecycle_data["status"]
    
    # Validera resultat
    assert "test_id" in lifecycle_data["result"]
    assert "total_logs_sent" in lifecycle_data["result"]
    
    # Validera delete
    assert lifecycle_data["delete"]["status"] == "deleted"
    assert lifecycle_data["delete"]["test_id"] == lifecycle_data["test_id"]


def test_multiple_concurrent_tests(test_client: TestClient, mock_load_generator):
    """Testa flera samtidiga tester (mockad)"""
    concurrent_data = get_multiple_concurrent_tests_responses(test_client)
    
    # Validera att alla tester startades
    for response, data in concurrent_data["start_responses"]:
        assert response.status_code == 200
        assert data["status"] == "started"
    
    # Validera att alla tester finns
    for response, data in concurrent_data["status_responses"]:
        assert response.status_code == 200
        assert "test_id" in data
    
    # Validera att alla tester togs bort
    for response, data in concurrent_data["delete_responses"]:
        assert response.status_code == 200
        assert data["status"] == "deleted"
    
    # Validera att vi fick 3 test-ID:n
    assert len(concurrent_data["test_ids"]) == 3


def test_invalid_scenario(test_client: TestClient, mock_load_generator):
    """Testa ogiltigt scenario (mockad)"""
    response = get_invalid_scenario_response(test_client)
    assert response.status_code == 400


def test_invalid_target(test_client: TestClient, mock_load_generator):
    """Testa ogiltigt target (mockad)"""
    response = get_invalid_target_response(test_client)
    # Bör ge 422 (Validation Error) eller 400 (Bad Request)
    assert response.status_code in [400, 422]


def test_network_error_handling(test_client: TestClient, mock_load_generator):
    """Testa nätverksfelhantering (mockad)"""
    response, data = get_network_error_handling_response(test_client)
    
    # API:et ska hantera detta gracefully
    assert response.status_code == 200
