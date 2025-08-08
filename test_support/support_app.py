#!/usr/bin/env python3
"""
Wazuh Load Generator - Test Support App
=======================================
Support-kod för FastAPI-tester inklusive test fixtures och utilities
"""

import asyncio
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import uvicorn

from api_server import app


class TestSupportApp:
    """Support-klass för FastAPI-tester"""
    
    def __init__(self):
        self.test_client = TestClient(app)
        self.test_data = {}
        self.mock_targets = {}
    
    def create_test_config(self, scenarios: Dict = None, targets: Dict = None) -> Dict:
        """Skapa test-konfiguration"""
        default_scenarios = {
            "test_light": {
                "description": "Test lätt last",
                "count": 10,
                "delay": 0.1,
                "duration": 60
            },
            "test_medium": {
                "description": "Test medium last",
                "count": 50,
                "delay": 0.05,
                "duration": 120
            }
        }
        
        default_targets = {
            "test_local": {
                "host": "localhost",
                "port": 514,
                "protocol": "udp"
            },
            "test_remote": {
                "host": "192.168.1.100",
                "port": 514,
                "protocol": "udp"
            }
        }
        
        return {
            "test_scenarios": scenarios or default_scenarios,
            "targets": targets or default_targets
        }
    
    def create_test_logs(self, log_type: str = "ssh", count: int = 10) -> List[str]:
        """Skapa test-loggar"""
        from faker import Faker
        fake = Faker('sv_SE')
        
        logs = []
        for i in range(count):
            timestamp = datetime.now()
            ip = fake.ipv4()
            user = fake.user_name()
            
            if log_type == "ssh":
                event = f"sshd[{i+1000}]: Failed password for {user} from {ip} port {fake.random_int(1024, 65535)} ssh2"
            elif log_type == "web":
                event = f'{ip} - - [{timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /test HTTP/1.1" 200 1234'
            elif log_type == "firewall":
                event = f"kernel: iptables: DROP IN=eth0 OUT= SRC={ip} DST={fake.ipv4()} LEN=60"
            else:
                event = f"test[{i+1000}]: Test log entry {i+1}"
            
            log_entry = f"{timestamp.strftime('%b %d %H:%M:%S')} {fake.hostname()} {event}"
            logs.append(log_entry)
        
        return logs
    
    def mock_socket_send(self, target_host: str = "localhost", target_port: int = 514):
        """Mock socket send-funktion för tester"""
        mock_socket = Mock()
        mock_socket.sendto = Mock()
        mock_socket.send = Mock()
        mock_socket.close = Mock()
        
        return mock_socket
    
    def create_test_request_data(self, **kwargs) -> Dict:
        """Skapa test request data"""
        default_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": "ssh",
            "count": 10,
            "delay": 0.1
        }
        default_data.update(kwargs)
        return default_data


class TestFixtures:
    """Pytest fixtures för FastAPI-tester"""
    
    @pytest.fixture
    def test_client(self) -> TestClient:
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    def async_client(self) -> AsyncClient:
        """Async HTTP client för tester"""
        return AsyncClient(app=app, base_url="http://test")
    
    @pytest.fixture
    def test_support(self) -> TestSupportApp:
        """Test support app"""
        return TestSupportApp()
    
    @pytest.fixture
    def test_config(self) -> Dict:
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
    def mock_socket(self):
        """Mock socket för tester"""
        with patch('socket.socket') as mock_socket_class:
            mock_socket = Mock()
            mock_socket.sendto = Mock()
            mock_socket.send = Mock()
            mock_socket.close = Mock()
            mock_socket_class.return_value = mock_socket
            yield mock_socket
    
    @pytest.fixture
    def temp_config_file(self):
        """Temporär config-fil för tester"""
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


class TestUtilities:
    """Utility-funktioner för tester"""
    
    @staticmethod
    def wait_for_api_ready(client: TestClient, timeout: int = 30) -> bool:
        """Vänta på att API ska vara redo"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = client.get("/health")
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(1)
        return False
    
    @staticmethod
    def create_test_log_entry(log_type: str = "ssh", index: int = 0) -> str:
        """Skapa en test log-entry"""
        from faker import Faker
        fake = Faker('sv_SE')
        
        timestamp = datetime.now()
        ip = fake.ipv4()
        user = fake.user_name()
        
        if log_type == "ssh":
            event = f"sshd[{1000+index}]: Failed password for {user} from {ip} port {fake.random_int(1024, 65535)} ssh2"
        elif log_type == "web":
            event = f'{ip} - - [{timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /test{index} HTTP/1.1" 200 1234'
        elif log_type == "firewall":
            event = f"kernel: iptables: DROP IN=eth0 OUT= SRC={ip} DST={fake.ipv4()} LEN=60"
        else:
            event = f"test[{1000+index}]: Test log entry {index+1}"
        
        return f"{timestamp.strftime('%b %d %H:%M:%S')} {fake.hostname()} {event}"
    
    @staticmethod
    def validate_api_response(response, expected_status: int = 200):
        """Validera API-svar"""
        assert response.status_code == expected_status
        if expected_status == 200:
            assert response.json() is not None
    
    @staticmethod
    def check_test_completion(client: TestClient, test_id: str, timeout: int = 60) -> Dict:
        """Kontrollera test-slutförande"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = client.get(f"/api/v1/test/{test_id}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["completed", "failed", "stopped"]:
                    return data
            time.sleep(2)
        
        raise TimeoutError(f"Test {test_id} tog för lång tid att slutföra")


# Export för pytest
test_fixtures = TestFixtures()
test_utilities = TestUtilities()
