#!/usr/bin/env python3
"""
Wazuh Load Generator - Test Utilities
=====================================
Utility-funktioner för tester
"""

import time
from datetime import datetime
from typing import Dict, List, Any
from fastapi.testclient import TestClient

from faker import Faker


class TestLogGenerator:
    """Generator för test-loggar"""
    
    def __init__(self, locale: str = 'sv_SE'):
        self.fake = Faker(locale)
    
    def generate_ssh_log(self, index: int = 0) -> str:
        """Generera SSH-log"""
        timestamp = datetime.now()
        ip = self.fake.ipv4()
        user = self.fake.user_name()
        
        event = f"sshd[{1000+index}]: Failed password for {user} from {ip} port {self.fake.random_int(1024, 65535)} ssh2"
        return f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
    
    def generate_web_log(self, index: int = 0) -> str:
        """Generera web-log"""
        timestamp = datetime.now()
        ip = self.fake.ipv4()
        
        event = f'{ip} - - [{timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET /test{index} HTTP/1.1" 200 1234'
        return f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
    
    def generate_firewall_log(self, index: int = 0) -> str:
        """Generera brandväggs-log"""
        timestamp = datetime.now()
        ip = self.fake.ipv4()
        
        event = f"kernel: iptables: DROP IN=eth0 OUT= SRC={ip} DST={self.fake.ipv4()} LEN=60"
        return f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
    
    def generate_system_log(self, index: int = 0) -> str:
        """Generera system-log"""
        timestamp = datetime.now()
        
        events = [
            f"systemd[{1000+index}]: Started user service for user {self.fake.user_name()}",
            f"kernel: CPU temperature above threshold, cpu clock throttled",
            f"cron[{1000+index}]: (root) CMD (/usr/bin/updatedb)",
            f"sudo: {self.fake.user_name()} : TTY=pts/0 ; PWD=/home/{self.fake.user_name()} ; USER=root ; COMMAND=/bin/ls"
        ]
        
        event = events[index % len(events)]
        return f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
    
    def generate_malware_log(self, index: int = 0) -> str:
        """Generera malware-log"""
        timestamp = datetime.now()
        ip = self.fake.ipv4()
        
        events = [
            f"clamav[{1000+index}]: Found virus 'Trojan.Generic' in file /tmp/test{index}.exe",
            f"malware_detector[{1000+index}]: Suspicious activity detected from {ip}",
            f"antivirus[{1000+index}]: Quarantined file /var/tmp/suspicious{index}.dat"
        ]
        
        event = events[index % len(events)]
        return f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
    
    def generate_logs(self, log_type: str = "ssh", count: int = 10) -> List[str]:
        """Generera flera loggar av given typ"""
        logs = []
        for i in range(count):
            if log_type == "ssh":
                logs.append(self.generate_ssh_log(i))
            elif log_type == "web":
                logs.append(self.generate_web_log(i))
            elif log_type == "firewall":
                logs.append(self.generate_firewall_log(i))
            elif log_type == "system":
                logs.append(self.generate_system_log(i))
            elif log_type == "malware":
                logs.append(self.generate_malware_log(i))
            else:
                logs.append(f"test[{1000+i}]: Test log entry {i+1}")
        
        return logs


class APITestUtils:
    """Utility-funktioner för API-tester"""
    
    def __init__(self, config=None):
        """Initiera med konfiguration"""
        from .config import get_test_config
        self.config = config or get_test_config()
    
    def wait_for_api_ready(self, client: TestClient, timeout: int = None) -> bool:
        """Vänta på att API ska vara redo"""
        if timeout is None:
            timeout = self.config.get_test_config()["timeout"]
        
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
    
    def validate_api_response(self, response, expected_status: int = 200):
        """Validera API-svar"""
        assert response.status_code == expected_status
        if expected_status == 200:
            assert response.json() is not None
    
    def check_test_completion(self, client: TestClient, test_id: str, timeout: int = None) -> Dict:
        """Kontrollera test-slutförande"""
        if timeout is None:
            timeout = self.config.get_test_config()["timeout"]
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = client.get(f"/api/v1/test/{test_id}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["completed", "failed", "stopped"]:
                    return data
            time.sleep(2)
        
        raise TimeoutError(f"Test {test_id} tog för lång tid att slutföra")
    
    def create_test_request_data(self, target_name: str = "local", **kwargs) -> Dict:
        """Skapa test request data med konfigurerbar target"""
        target = self.config.get_target(target_name)
        test_config = self.config.get_test_config()
        
        default_data = {
            "target_host": target["host"],
            "target_port": target["port"],
            "protocol": target["protocol"],
            "log_type": "ssh",
            "count": test_config["count"],
            "delay": test_config["delay"]
        }
        default_data.update(kwargs)
        return default_data
    
    def get_target_config(self, target_name: str = "local") -> Dict[str, Any]:
        """Hämta target-konfiguration"""
        return self.config.get_target(target_name)
    
    def get_api_config(self) -> Dict[str, Any]:
        """Hämta API-konfiguration"""
        return self.config.get_api_config()


class MockUtils:
    """Utility-funktioner för mocking"""
    
    @staticmethod
    def create_mock_socket():
        """Skapa mock socket"""
        from unittest.mock import Mock
        
        mock_socket = Mock()
        mock_socket.sendto = Mock()
        mock_socket.send = Mock()
        mock_socket.close = Mock()
        mock_socket.connect = Mock()
        
        return mock_socket
    
    @staticmethod
    def create_mock_generator():
        """Skapa mock generator"""
        from unittest.mock import Mock
        
        mock_generator = Mock()
        mock_generator.generate_ssh_logs = Mock(return_value=["test ssh log"])
        mock_generator.generate_web_logs = Mock(return_value=["test web log"])
        mock_generator.generate_firewall_logs = Mock(return_value=["test firewall log"])
        mock_generator.generate_system_logs = Mock(return_value=["test system log"])
        mock_generator.generate_malware_logs = Mock(return_value=["test malware log"])
        mock_generator.send_logs = Mock(return_value=1)
        
        return mock_generator


class PerformanceUtils:
    """Utility-funktioner för prestandatester"""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Mäta exekveringstid för funktion"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        return result, end_time - start_time
    
    @staticmethod
    def assert_performance_threshold(execution_time: float, max_time: float, description: str = ""):
        """Assert att prestanda är inom tröskelvärde"""
        assert execution_time < max_time, f"{description} tog {execution_time:.2f}s (max: {max_time:.2f}s)"


# Export huvudklasser
__all__ = ["TestLogGenerator", "APITestUtils", "MockUtils", "PerformanceUtils"]
