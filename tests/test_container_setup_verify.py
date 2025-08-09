#!/usr/bin/env python3
"""
Wazuh Load Generator - Container Verification Tests
=================================================
Enklare version som bara verifierar containern utan att starta om den

Denna test suite fokuserar på:
✅ Verifiera att container körs
✅ Health endpoint verifiering
✅ Container status och logs
✅ API endpoints fungerar

Alla tester körs utan att starta om containern.
"""

import pytest
import time
from test_support.container_setup_utils import *


def test_container_running():
    """Verifiera att containern körs"""
    container_exists = check_container_exists()
    assert container_exists, "Container körs inte"


def test_health_endpoint_working():
    """Verifiera att health endpoint fungerar"""
    health_exists, health_message = check_health_endpoint_exists()
    assert health_exists, f"Health endpoint fungerar inte: {health_message}"


def test_container_status_ok():
    """Verifiera container status"""
    status = get_container_status()
    
    assert "error" not in status, f"Fel vid hämtning av status: {status.get('error')}"
    assert status["container_running"], "Container körs inte"
    assert "Up" in status["container_status"], f"Container status felaktig: {status['container_status']}"


def test_container_logs_exist():
    """Verifiera att container logs finns"""
    logs = get_container_logs()
    
    assert len(logs) > 0, "Container logs är tomma"
    assert "wazuh-loader-test" in logs or "Wazuh" in logs, "Container logs innehåller inte förväntad information"


def test_container_execution_works():
    """Testa att vi kan köra kommandon i containern"""
    success, output = execute_in_container("echo 'Test kommando'")
    assert success, f"Kunde inte köra kommando i container: {output}"
    assert "Test kommando" in output, f"Felaktig output från container: {output}"


def test_container_python_environment():
    """Testa Python-miljön i containern"""
    success, output = execute_in_container("python --version")
    assert success, f"Python fungerar inte i container: {output}"
    
    success, output = execute_in_container("pip list | grep httpx")
    assert success, f"httpx är inte installerat i container: {output}"
    assert "httpx" in output, f"httpx saknas i container: {output}"


def test_container_api_endpoints():
    """Testa att API-endpoints fungerar"""
    # Testa root endpoint
    success, output = execute_in_container("curl -s http://localhost:9090/")
    assert success, f"Root endpoint fungerar inte: {output}"
    assert "Wazuh" in output, f"Root endpoint returnerar fel data: {output}"
    
    # Testa health endpoint från containern
    success, output = execute_in_container("curl -s http://localhost:9090/health")
    assert success, f"Health endpoint fungerar inte från container: {output}"
    assert "healthy" in output, f"Health endpoint returnerar fel data: {output}"


def test_container_network_connectivity():
    """Testa nätverksanslutning från containern"""
    # Testa att container kan nå sig själv
    success, output = execute_in_container("curl -s http://localhost:9090/health")
    assert success, f"Container kan inte nå sig själv: {output}"
    assert "healthy" in output, f"Health check returnerar fel data: {output}"


def test_container_api_scenarios():
    """Testa API scenarios endpoint"""
    success, output = execute_in_container("curl -s http://localhost:9090/api/v1/scenarios")
    assert success, f"Scenarios endpoint fungerar inte: {output}"
    assert "scenarios" in output, f"Scenarios endpoint returnerar fel data: {output}"


def test_container_api_targets():
    """Testa API targets endpoint"""
    success, output = execute_in_container("curl -s http://localhost:9090/api/v1/targets")
    assert success, f"Targets endpoint fungerar inte: {output}"
    assert "targets" in output, f"Targets endpoint returnerar fel data: {output}"
