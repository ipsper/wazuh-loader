#!/usr/bin/env python3
"""
Wazuh Load Generator - Basic API Tests
======================================
Grundläggande API-tester för FastAPI-endpoints
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from test_support.api_utils import (
    get_root_endpoint_response,
    get_health_endpoint_response,
    get_scenarios_endpoint_response,
    get_targets_endpoint_response,
    get_list_tests_endpoint_response,
    get_nonexistent_endpoint_response,
    get_invalid_method_response,
    get_async_root_endpoint_response,
    get_async_health_endpoint_response,
    get_start_test_invalid_data_response,
    get_test_status_invalid_id_response,
    get_stop_test_invalid_id_response,
    get_delete_test_invalid_id_response,
    get_api_ready_response,
    get_api_response_structure_data,
    get_cors_headers_response
)


def test_root_endpoint(test_client: TestClient):
    """Testa root endpoint"""
    response, data = get_root_endpoint_response(test_client)
    
    assert response.status_code == 200
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Wazuh Load Generator API"


def test_health_endpoint(test_client: TestClient):
    """Testa health endpoint"""
    response, data = get_health_endpoint_response(test_client)
    
    assert response.status_code == 200
    assert "status" in data
    assert "timestamp" in data
    assert data["status"] == "healthy"


def test_scenarios_endpoint(test_client: TestClient):
    """Testa scenarios endpoint"""
    response, data = get_scenarios_endpoint_response(test_client)
    
    assert response.status_code == 200
    assert "scenarios" in data
    assert "count" in data
    assert isinstance(data["scenarios"], dict)
    assert isinstance(data["count"], int)


def test_targets_endpoint(test_client: TestClient):
    """Testa targets endpoint"""
    response, data = get_targets_endpoint_response(test_client)
    
    assert response.status_code == 200
    assert "targets" in data
    assert "count" in data
    assert isinstance(data["targets"], dict)
    assert isinstance(data["count"], int)


def test_list_tests_endpoint(test_client: TestClient):
    """Testa list tests endpoint"""
    response, data = get_list_tests_endpoint_response(test_client)
    
    assert response.status_code == 200
    assert "tests" in data
    assert "total" in data
    assert "running" in data
    assert "completed" in data
    assert "failed" in data
    assert isinstance(data["tests"], list)


def test_nonexistent_endpoint(test_client: TestClient):
    """Testa icke-existerande endpoint"""
    response = get_nonexistent_endpoint_response(test_client)
    assert response.status_code == 404


def test_invalid_method(test_client: TestClient):
    """Testa ogiltig HTTP-metod"""
    response = get_invalid_method_response(test_client)
    assert response.status_code == 405  # Method Not Allowed


async def test_async_root_endpoint(async_client: AsyncClient):
    """Testa root endpoint async"""
    response, data = await get_async_root_endpoint_response(async_client)
    
    assert response.status_code == 200
    assert "message" in data
    assert data["message"] == "Wazuh Load Generator API"


async def test_async_health_endpoint(async_client: AsyncClient):
    """Testa health endpoint async"""
    response, data = await get_async_health_endpoint_response(async_client)
    
    assert response.status_code == 200
    assert "status" in data
    assert data["status"] == "healthy"


def test_start_test_invalid_data(test_client: TestClient):
    """Testa start test med ogiltig data"""
    response = get_start_test_invalid_data_response(test_client)
    assert response.status_code == 422  # Validation Error


def test_get_test_status_invalid_id(test_client: TestClient):
    """Testa hämta test status med ogiltigt ID"""
    response = get_test_status_invalid_id_response(test_client)
    assert response.status_code == 404


def test_stop_test_invalid_id(test_client: TestClient):
    """Testa stoppa test med ogiltigt ID"""
    response = get_stop_test_invalid_id_response(test_client)
    assert response.status_code == 404


def test_delete_test_invalid_id(test_client: TestClient):
    """Testa ta bort test med ogiltigt ID"""
    response = get_delete_test_invalid_id_response(test_client)
    assert response.status_code == 404


def test_api_ready(test_client: TestClient):
    """Testa att API är redo"""
    response, data = get_api_ready_response(test_client)
    
    assert response.status_code == 200
    assert data["status"] == "healthy"


def test_api_response_structure(test_client: TestClient):
    """Testa API response-struktur"""
    response, data = get_api_response_structure_data(test_client)
    
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert isinstance(data, dict)
    assert "message" in data


def test_cors_headers(test_client: TestClient):
    """Testa CORS-headers"""
    response = get_cors_headers_response(test_client)
    
    assert response.status_code == 200
    
    # Kontrollera CORS-headers
    headers = response.headers
    assert "access-control-allow-origin" in headers
    assert "access-control-allow-methods" in headers
    assert "access-control-allow-headers" in headers
