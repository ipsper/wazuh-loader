#!/usr/bin/env python3
"""
Wazuh Load Generator - Config Flexibility Tests
==============================================
Tester som demonstrerar flexibel konfiguration med IP-adresser och portar
"""

import pytest
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from api_server import app
from test_support.utils import APITestUtils
from test_support.config import TestConfig, get_test_config, set_test_config


class TestConfigFlexibility:
    """Tester för flexibel konfiguration"""
    
    def test_default_config(self):
        """Testa standardkonfiguration"""
        config = TestConfig()
        
        # Kontrollera standardvärden
        local_target = config.get_target("local")
        assert local_target["host"] == "0.0.0.0"
        assert local_target["port"] == 514
        assert local_target["protocol"] == "udp"
        
        api_config = config.get_api_config()
        assert api_config["host"] == "0.0.0.0"
        assert api_config["port"] == 8090
    
    def test_environment_variables(self):
        """Testa miljövariabler"""
        # Sätt miljövariabler
        os.environ["TEST_TARGET_HOST"] = "192.168.1.50"
        os.environ["TEST_TARGET_PORT"] = "515"
        os.environ["TEST_API_HOST"] = "0.0.0.0"
        os.environ["TEST_API_PORT"] = "8080"
        
        config = TestConfig()
        
        # Kontrollera att miljövariabler används
        local_target = config.get_target("local")
        assert local_target["host"] == "192.168.1.50"
        assert local_target["port"] == 515
        
        api_config = config.get_api_config()
        assert api_config["host"] == "0.0.0.0"
        assert api_config["port"] == 8080
        
        # Rensa upp
        del os.environ["TEST_TARGET_HOST"]
        del os.environ["TEST_TARGET_PORT"]
        del os.environ["TEST_API_HOST"]
        del os.environ["TEST_API_PORT"]
    
    def test_target_management(self):
        """Testa target-hantering"""
        config = TestConfig()
        
        # Skapa ny target
        config.update_target("custom", host="10.0.0.1", port=9999, protocol="tcp")
        
        custom_target = config.get_target("custom")
        assert custom_target["host"] == "10.0.0.1"
        assert custom_target["port"] == 9999
        assert custom_target["protocol"] == "tcp"
    
    def test_url_generation(self):
        """Testa URL-generering"""
        config = TestConfig()
        
        # Testa target URL
        target_url = config.get_target_url("local")
        assert target_url == "udp://localhost:514"
        
        # Testa API URL
        api_url = config.get_api_url()
        assert api_url == "http://localhost:8000"
    
    def test_all_targets(self):
        """Testa alla targets"""
        config = TestConfig()
        
        targets = config.get_all_targets()
        assert "local" in targets
        assert "remote" in targets
        assert "tcp_local" in targets
        assert "tcp_remote" in targets


class TestAPITestUtilsWithConfig:
    """Tester för APITestUtils med konfiguration"""
    
    def test_create_test_request_data_with_config(self):
        """Testa skapa test request data med konfiguration"""
        config = TestConfig()
        utils = APITestUtils(config)
        
        # Testa med standard target
        request_data = utils.create_test_request_data()
        assert request_data["target_host"] == "localhost"
        assert request_data["target_port"] == 514
        assert request_data["protocol"] == "udp"
        
        # Testa med anpassad target
        config.update_target("custom", host="192.168.1.100", port=9999)
        request_data = utils.create_test_request_data("custom")
        assert request_data["target_host"] == "192.168.1.100"
        assert request_data["target_port"] == 9999
    
    def test_create_test_request_data_with_overrides(self):
        """Testa skapa test request data med överstyrningar"""
        config = TestConfig()
        utils = APITestUtils(config)
        
        request_data = utils.create_test_request_data(
            target_name="local",
            log_type="web",
            count=50,
            delay=0.05
        )
        
        assert request_data["target_host"] == "localhost"
        assert request_data["target_port"] == 514
        assert request_data["protocol"] == "udp"
        assert request_data["log_type"] == "web"
        assert request_data["count"] == 50
        assert request_data["delay"] == 0.05
    
    def test_get_target_config(self):
        """Testa hämta target-konfiguration"""
        config = TestConfig()
        utils = APITestUtils(config)
        
        target_config = utils.get_target_config("local")
        assert target_config["host"] == "localhost"
        assert target_config["port"] == 514
        
        target_config = utils.get_target_config("remote")
        assert target_config["host"] == "192.168.1.100"
        assert target_config["port"] == 514
    
    def test_get_api_config(self):
        """Testa hämta API-konfiguration"""
        config = TestConfig()
        utils = APITestUtils(config)
        
        api_config = utils.get_api_config()
        assert api_config["host"] == "localhost"
        assert api_config["port"] == 8000


class TestConfigIntegration:
    """Integration-tester för konfiguration"""
    
    def test_config_with_api_tests(self, test_client: TestClient):
        """Testa konfiguration med API-tester"""
        # Skapa anpassad konfiguration
        custom_config = TestConfig()
        custom_config.update_target("test_target", host="127.0.0.1", port=9999)
        
        utils = APITestUtils(custom_config)
        
        # Skapa test request med anpassad target
        request_data = utils.create_test_request_data("test_target")
        assert request_data["target_host"] == "127.0.0.1"
        assert request_data["target_port"] == 9999
        
        # Testa API-anrop (mock)
        response = test_client.get("/health")
        utils.validate_api_response(response)
    
    def test_global_config_management(self):
        """Testa global konfigurationshantering"""
        # Spara ursprunglig konfiguration
        original_config = get_test_config()
        
        # Skapa ny konfiguration
        new_config = TestConfig()
        new_config.update_target("global_test", host="10.0.0.1", port=8888)
        
        # Sätt global konfiguration
        set_test_config(new_config)
        
        # Kontrollera att global konfiguration används
        utils = APITestUtils()
        request_data = utils.create_test_request_data("global_test")
        assert request_data["target_host"] == "10.0.0.1"
        assert request_data["target_port"] == 8888
        
        # Återställ ursprunglig konfiguration
        set_test_config(original_config)


class TestEnvironmentVariableIntegration:
    """Integration-tester för miljövariabler"""
    
    def test_environment_variable_override(self):
        """Testa att miljövariabler överskrider standardvärden"""
        # Sätt miljövariabler
        os.environ["TEST_TARGET_HOST"] = "192.168.1.200"
        os.environ["TEST_TARGET_PORT"] = "1234"
        os.environ["TEST_API_HOST"] = "0.0.0.0"
        os.environ["TEST_API_PORT"] = "9000"
        
        try:
            config = TestConfig()
            
            # Kontrollera att miljövariabler används
            local_target = config.get_target("local")
            assert local_target["host"] == "192.168.1.200"
            assert local_target["port"] == 1234
            
            api_config = config.get_api_config()
            assert api_config["host"] == "0.0.0.0"
            assert api_config["port"] == 9000
            
        finally:
            # Rensa upp
            for var in ["TEST_TARGET_HOST", "TEST_TARGET_PORT", "TEST_API_HOST", "TEST_API_PORT"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_test_config_environment_variables(self):
        """Testa test-konfiguration med miljövariabler"""
        # Sätt test-miljövariabler
        os.environ["TEST_TIMEOUT"] = "60"
        os.environ["TEST_DELAY"] = "0.5"
        os.environ["TEST_COUNT"] = "25"
        
        try:
            config = TestConfig()
            test_config = config.get_test_config()
            
            assert test_config["timeout"] == 60
            assert test_config["delay"] == 0.5
            assert test_config["count"] == 25
            
        finally:
            # Rensa upp
            for var in ["TEST_TIMEOUT", "TEST_DELAY", "TEST_COUNT"]:
                if var in os.environ:
                    del os.environ[var]
