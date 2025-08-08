#!/usr/bin/env python3
"""
Wazuh Load Generator - Test Configuration
========================================
Konfiguration för testvariabler som IP-adresser och portar
"""

import os
from typing import Dict, Any


class TestConfig:
    """Test-konfiguration med flexibla variabler"""
    
    # Standardvärden
    DEFAULT_CONFIG = {
        "targets": {
            "local": {
                "host": "0.0.0.0",
                "port": 514,
                "protocol": "udp"
            },
            "remote": {
                "host": "192.168.1.100",
                "port": 514,
                "protocol": "udp"
            },
            "tcp_local": {
                "host": "0.0.0.0",
                "port": 601,
                "protocol": "tcp"
            },
            "tcp_remote": {
                "host": "192.168.1.100",
                "port": 601,
                "protocol": "tcp"
            }
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8090,
            "base_url": "http://0.0.0.0:8090"
        },
        "test": {
            "timeout": 30,
            "delay": 0.1,
            "count": 10,
            "max_retries": 3
        }
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initiera test-konfiguration"""
        self.config = config or self.DEFAULT_CONFIG.copy()
        self._load_environment_variables()
    
    def _load_environment_variables(self):
        """Ladda konfiguration från miljövariabler"""
        # Target-konfiguration
        if os.getenv("TEST_TARGET_HOST"):
            self.config["targets"]["local"]["host"] = os.getenv("TEST_TARGET_HOST")
            self.config["targets"]["remote"]["host"] = os.getenv("TEST_TARGET_HOST")
        
        if os.getenv("TEST_TARGET_PORT"):
            port = int(os.getenv("TEST_TARGET_PORT"))
            self.config["targets"]["local"]["port"] = port
            self.config["targets"]["remote"]["port"] = port
        
        if os.getenv("TEST_TARGET_PROTOCOL"):
            protocol = os.getenv("TEST_TARGET_PROTOCOL")
            self.config["targets"]["local"]["protocol"] = protocol
            self.config["targets"]["remote"]["protocol"] = protocol
        
        # API-konfiguration
        if os.getenv("TEST_API_HOST"):
            self.config["api"]["host"] = os.getenv("TEST_API_HOST")
            self.config["api"]["base_url"] = f"http://{os.getenv('TEST_API_HOST')}:{self.config['api']['port']}"
        
        if os.getenv("TEST_API_PORT"):
            port = int(os.getenv("TEST_API_PORT"))
            self.config["api"]["port"] = port
            self.config["api"]["base_url"] = f"http://{self.config['api']['host']}:{port}"
        
        # Test-konfiguration
        if os.getenv("TEST_TIMEOUT"):
            self.config["test"]["timeout"] = int(os.getenv("TEST_TIMEOUT"))
        
        if os.getenv("TEST_DELAY"):
            self.config["test"]["delay"] = float(os.getenv("TEST_DELAY"))
        
        if os.getenv("TEST_COUNT"):
            self.config["test"]["count"] = int(os.getenv("TEST_COUNT"))
    
    def get_target(self, name: str = "local") -> Dict[str, Any]:
        """Hämta target-konfiguration"""
        return self.config["targets"].get(name, self.config["targets"]["local"])
    
    def get_api_config(self) -> Dict[str, Any]:
        """Hämta API-konfiguration"""
        return self.config["api"]
    
    def get_test_config(self) -> Dict[str, Any]:
        """Hämta test-konfiguration"""
        return self.config["test"]
    
    def get_all_targets(self) -> Dict[str, Dict[str, Any]]:
        """Hämta alla targets"""
        return self.config["targets"]
    
    def update_target(self, name: str, host: str = None, port: int = None, protocol: str = None):
        """Uppdatera target-konfiguration"""
        if name not in self.config["targets"]:
            self.config["targets"][name] = self.config["targets"]["local"].copy()
        
        if host:
            self.config["targets"][name]["host"] = host
        if port:
            self.config["targets"][name]["port"] = port
        if protocol:
            self.config["targets"][name]["protocol"] = protocol
    
    def get_target_url(self, name: str = "local") -> str:
        """Hämta target URL"""
        target = self.get_target(name)
        return f"{target['protocol']}://{target['host']}:{target['port']}"
    
    def get_api_url(self) -> str:
        """Hämta API URL"""
        api = self.get_api_config()
        return f"http://{api['host']}:{api['port']}"


# Global test-konfiguration
test_config = TestConfig()


def get_test_config() -> TestConfig:
    """Hämta global test-konfiguration"""
    return test_config


def set_test_config(config: TestConfig):
    """Sätt global test-konfiguration"""
    global test_config
    test_config = config
