#!/usr/bin/env python3
"""
Wazuh Load Generator - API Test Utilities
========================================
Utility-funktioner för API-tester
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from typing import Dict, Any

from api_server import app
from .utils import APITestUtils


def get_root_endpoint_response(test_client: TestClient):
    """Hämta root endpoint response"""
    response = test_client.get("/")
    return response, response.json()


def get_health_endpoint_response(test_client: TestClient):
    """Hämta health endpoint response"""
    response = test_client.get("/health")
    return response, response.json()


def get_scenarios_endpoint_response(test_client: TestClient):
    """Hämta scenarios endpoint response"""
    response = test_client.get("/api/v1/scenarios")
    return response, response.json()


def get_targets_endpoint_response(test_client: TestClient):
    """Hämta targets endpoint response"""
    response = test_client.get("/api/v1/targets")
    return response, response.json()


def get_list_tests_endpoint_response(test_client: TestClient):
    """Hämta list tests endpoint response"""
    response = test_client.get("/api/v1/test")
    return response, response.json()


def get_nonexistent_endpoint_response(test_client: TestClient):
    """Hämta icke-existerande endpoint response"""
    response = test_client.get("/api/v1/nonexistent")
    return response


def get_invalid_method_response(test_client: TestClient):
    """Hämta ogiltig HTTP-metod response"""
    response = test_client.post("/health")
    return response


async def get_async_root_endpoint_response(async_client: AsyncClient):
    """Hämta async root endpoint response"""
    response = await async_client.get("/")
    return response, response.json()


async def get_async_health_endpoint_response(async_client: AsyncClient):
    """Hämta async health endpoint response"""
    response = await async_client.get("/health")
    return response, response.json()


def get_start_test_invalid_data_response(test_client: TestClient):
    """Hämta start test invalid data response"""
    invalid_data = {
        "target_host": "",  # Ogiltig host
        "target_port": -1,  # Ogiltig port
        "protocol": "invalid",  # Ogiltigt protokoll
        "log_type": "invalid",  # Ogiltig loggtyp
        "count": -1,  # Ogiltigt antal
        "delay": -0.1  # Ogiltig fördröjning
    }
    
    response = test_client.post("/api/v1/test/start", json=invalid_data)
    return response


def get_test_status_invalid_id_response(test_client: TestClient):
    """Hämta test status invalid ID response"""
    response = test_client.get("/api/v1/test/invalid-id")
    return response


def get_stop_test_invalid_id_response(test_client: TestClient):
    """Hämta stop test invalid ID response"""
    response = test_client.post("/api/v1/test/invalid-id/stop")
    return response


def get_delete_test_invalid_id_response(test_client: TestClient):
    """Hämta delete test invalid ID response"""
    response = test_client.delete("/api/v1/test/invalid-id")
    return response


def get_api_ready_response(test_client: TestClient):
    """Hämta API ready response"""
    response = test_client.get("/health")
    return response, response.json()


def get_api_response_structure_data(test_client: TestClient):
    """Hämta API response structure data"""
    response = test_client.get("/")
    return response, response.json()


def get_cors_headers_response(test_client: TestClient):
    """Hämta CORS headers response"""
    response = test_client.options("/")
    return response


def get_start_test_basic_response(test_client: TestClient):
    """Hämta start test basic response"""
    test_data = {
        "target_host": "localhost",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "count": 5,
        "delay": 0.1
    }
    
    response = test_client.post("/api/v1/test/start", json=test_data)
    return response, response.json()


def get_start_test_with_scenario_response(test_client: TestClient):
    """Hämta start test with scenario response"""
    test_data = {
        "target_host": "localhost",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "scenario": "light_load"
    }
    
    response = test_client.post("/api/v1/test/start", json=test_data)
    return response, response.json()


def get_start_test_all_log_types_responses(test_client: TestClient):
    """Hämta start test all log types responses"""
    log_types = ["ssh", "web", "firewall", "system", "malware"]
    responses = []
    
    for log_type in log_types:
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": log_type,
            "count": 3,
            "delay": 0.1
        }
        
        response = test_client.post("/api/v1/test/start", json=test_data)
        responses.append((response, response.json()))
    
    return responses


def get_start_test_different_protocols_responses(test_client: TestClient):
    """Hämta start test different protocols responses"""
    protocols = ["udp", "tcp"]
    responses = []
    
    for protocol in protocols:
        test_data = {
            "target_host": "localhost",
            "target_port": 514 if protocol == "udp" else 601,
            "protocol": protocol,
            "log_type": "ssh",
            "count": 3,
            "delay": 0.1
        }
        
        response = test_client.post("/api/v1/test/start", json=test_data)
        responses.append((response, response.json()))
    
    return responses


def get_test_status_response(test_client: TestClient):
    """Hämta test status response"""
    # Starta ett test först
    test_data = {
        "target_host": "localhost",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "count": 3,
        "delay": 0.1
    }
    
    start_response = test_client.post("/api/v1/test/start", json=test_data)
    test_id = start_response.json()["test_id"]
    
    # Hämta status
    response = test_client.get(f"/api/v1/test/{test_id}")
    return response, response.json(), test_id


def get_stop_test_response(test_client: TestClient):
    """Hämta stop test response"""
    # Starta ett test först
    test_data = {
        "target_host": "localhost",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "count": 3,
        "delay": 0.1
    }
    
    start_response = test_client.post("/api/v1/test/start", json=test_data)
    test_id = start_response.json()["test_id"]
    
    # Stoppa testet
    response = test_client.post(f"/api/v1/test/{test_id}/stop")
    return response, response.json(), test_id


def get_delete_test_response(test_client: TestClient):
    """Hämta delete test response"""
    # Starta ett test först
    test_data = {
        "target_host": "localhost",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "count": 3,
        "delay": 0.1
    }
    
    start_response = test_client.post("/api/v1/test/start", json=test_data)
    test_id = start_response.json()["test_id"]
    
    # Ta bort testet
    response = test_client.delete(f"/api/v1/test/{test_id}")
    return response, response.json(), test_id


def get_test_result_response(test_client: TestClient):
    """Hämta test result response"""
    # Starta ett test först
    test_data = {
        "target_host": "localhost",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "count": 3,
        "delay": 0.1
    }
    
    start_response = test_client.post("/api/v1/test/start", json=test_data)
    test_id = start_response.json()["test_id"]
    
    # Vänta lite för att testet ska slutföras
    import time
    time.sleep(0.5)
    
    # Hämta resultat
    response = test_client.get(f"/api/v1/test/{test_id}/result")
    return response, response.json(), test_id


def get_test_result_invalid_id_response(test_client: TestClient):
    """Hämta test result invalid ID response"""
    response = test_client.get("/api/v1/test/invalid-id/result")
    return response


def get_scenarios_response(test_client: TestClient):
    """Hämta scenarios response"""
    response = test_client.get("/api/v1/scenarios")
    return response, response.json()


def get_targets_response(test_client: TestClient):
    """Hämta targets response"""
    response = test_client.get("/api/v1/targets")
    return response, response.json()


def get_full_test_lifecycle_responses(test_client: TestClient):
    """Hämta full test lifecycle responses"""
    # 1. Starta test
    test_data = {
        "target_host": "localhost",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "count": 5,
        "delay": 0.1
    }
    
    start_response = test_client.post("/api/v1/test/start", json=test_data)
    test_id = start_response.json()["test_id"]
    
    # 2. Kontrollera status
    status_response = test_client.get(f"/api/v1/test/{test_id}")
    
    # 3. Vänta lite för att testet ska slutföras
    import time
    time.sleep(0.5)
    
    # 4. Hämta resultat
    result_response = test_client.get(f"/api/v1/test/{test_id}/result")
    
    # 5. Ta bort testet
    delete_response = test_client.delete(f"/api/v1/test/{test_id}")
    
    return {
        "start": start_response.json(),
        "status": status_response.json(),
        "result": result_response.json(),
        "delete": delete_response.json(),
        "test_id": test_id
    }


def get_multiple_concurrent_tests_responses(test_client: TestClient):
    """Hämta multiple concurrent tests responses"""
    test_ids = []
    responses = []
    
    # Starta flera tester
    for i in range(3):
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": "ssh",
            "count": 2,
            "delay": 0.1
        }
        
        response = test_client.post("/api/v1/test/start", json=test_data)
        test_id = response.json()["test_id"]
        test_ids.append(test_id)
        responses.append((response, response.json()))
    
    # Kontrollera att alla tester finns
    status_responses = []
    for test_id in test_ids:
        response = test_client.get(f"/api/v1/test/{test_id}")
        status_responses.append((response, response.json()))
    
    # Rensa upp
    delete_responses = []
    for test_id in test_ids:
        response = test_client.delete(f"/api/v1/test/{test_id}")
        delete_responses.append((response, response.json()))
    
    return {
        "start_responses": responses,
        "status_responses": status_responses,
        "delete_responses": delete_responses,
        "test_ids": test_ids
    }


def get_invalid_scenario_response(test_client: TestClient):
    """Hämta invalid scenario response"""
    test_data = {
        "target_host": "localhost",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "scenario": "nonexistent_scenario"
    }
    
    response = test_client.post("/api/v1/test/start", json=test_data)
    return response


def get_invalid_target_response(test_client: TestClient):
    """Hämta invalid target response"""
    test_data = {
        "target_host": "invalid-host",
        "target_port": 99999,
        "protocol": "invalid",
        "log_type": "ssh",
        "count": 5
    }
    
    response = test_client.post("/api/v1/test/start", json=test_data)
    return response


def get_network_error_handling_response(test_client: TestClient):
    """Hämta network error handling response"""
    test_data = {
        "target_host": "unreachable-host",
        "target_port": 514,
        "protocol": "udp",
        "log_type": "ssh",
        "count": 5
    }
    
    response = test_client.post("/api/v1/test/start", json=test_data)
    return response, response.json()
