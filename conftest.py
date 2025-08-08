#!/usr/bin/env python3
"""
Wazuh Load Generator - Pytest Configuration
==========================================
Pytest-konfiguration och fixtures för Wazuh Load Generator
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from api_server import app
from test_support.support_app import TestSupportApp, TestFixtures, TestUtilities


# Importera fixtures från support_app
@pytest.fixture
def test_client() -> TestClient:
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def async_client() -> AsyncClient:
    """Async HTTP client för tester"""
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def test_support() -> TestSupportApp:
    """Test support app"""
    return TestSupportApp()


@pytest.fixture
def test_config() -> dict:
    """Test-konfiguration"""
    return {
        "test_scenarios": {
            "test_light": {"count": 10, "delay": 0.1, "duration": 60},
            "test_medium": {"count": 50, "delay": 0.05, "duration": 120}
        },
        "targets": {
            "test_local": {"host": "localhost", "port": 514, "protocol": "udp"},
            "test_remote": {"host": "192.168.1.100", "port": 514, "protocol": "udp"}
        }
    }


@pytest.fixture
def mock_socket():
    """Mock socket för tester"""
    from unittest.mock import Mock, patch
    
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket.sendto = Mock()
        mock_socket.send = Mock()
        mock_socket.close = Mock()
        mock_socket_class.return_value = mock_socket
        yield mock_socket


@pytest.fixture
def temp_config_file():
    """Temporär config-fil för tester"""
    import json
    import tempfile
    from pathlib import Path
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "test_scenarios": {
                "test_light": {"count": 10, "delay": 0.1, "duration": 60}
            },
            "targets": {
                "test_local": {"host": "localhost", "port": 514, "protocol": "udp"}
            }
        }
        json.dump(config, f)
        temp_file = f.name
    
    yield temp_file
    
    # Rensa upp
    Path(temp_file).unlink(missing_ok=True)


# Export utilities för enkel åtkomst
test_utilities = TestUtilities()
