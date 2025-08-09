#!/usr/bin/env python3
"""
Wazuh Load Generator - Container Test Utilities
==============================================
Utility-funktioner för container-tester utan assertions
"""

import httpx
import time
from typing import Dict, Any, Tuple
from test_support.config import get_test_config


def get_container_base_url() -> str:
    """Hämta container API base URL"""
    config = get_test_config()
    api_config = config.get_api_config()
    return f"http://{api_config['host']}:{api_config['port']}"


def get_container_timeout() -> httpx.Timeout:
    """Hämta timeout för container-tester"""
    return httpx.Timeout(30.0)


def get_container_health_endpoint() -> Tuple[int, Dict[str, Any]]:
    """Hämta health endpoint data och returnera status och data"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{base_url}/health")
        return response.status_code, response.json()


def get_container_root_endpoint() -> Tuple[int, Dict[str, Any]]:
    """Hämta root endpoint data och returnera status och data"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{base_url}/")
        return response.status_code, response.json()


def get_container_api_documentation() -> Tuple[int, str]:
    """Hämta API-dokumentation och returnera status och content-type"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{base_url}/docs")
        return response.status_code, response.headers.get("content-type", "")


def get_container_scenarios_endpoint() -> Tuple[int, Dict[str, Any]]:
    """Hämta scenarios endpoint data och returnera status och data"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{base_url}/api/v1/scenarios")
        return response.status_code, response.json()


def get_container_targets_endpoint() -> Tuple[int, Dict[str, Any]]:
    """Hämta targets endpoint data och returnera status och data"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{base_url}/api/v1/targets")
        return response.status_code, response.json()


def start_container_load_test(test_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Starta load test och returnera status och data"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            f"{base_url}/api/v1/test/start",
            json=test_data
        )
        return response.status_code, response.json()


def get_container_list_tests() -> Tuple[int, Dict[str, Any]]:
    """Lista tester och returnera status och data"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{base_url}/api/v1/test")
        return response.status_code, response.json()


def send_container_invalid_test_request(invalid_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Skicka ogiltig request och returnera status och data"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            f"{base_url}/api/v1/test/start",
            json=invalid_data
        )
        return response.status_code, response.json()


def check_container_network_connectivity() -> Tuple[int, Dict[str, Any]]:
    """Kontrollera nätverksanslutning och returnera status och data"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{base_url}/health")
        return response.status_code, response.json()


def measure_container_api_response_time() -> Tuple[int, float]:
    """Mäta API-svarstid och returnera status och tid"""
    base_url = get_container_base_url()
    timeout = get_container_timeout()
    
    with httpx.Client(timeout=timeout) as client:
        start_time = time.time()
        response = client.get(f"{base_url}/health")
        end_time = time.time()
        
        return response.status_code, end_time - start_time


def run_container_ssh_log_generation() -> Tuple[int, Dict[str, Any]]:
    """Kör SSH log generation och returnera status och data"""
    test_data = {
        "target": "local",
        "duration": 1,
        "log_types": ["ssh"],
        "logs_per_cycle": 2,
        "cycle_delay": 0.1
    }
    
    status_code, data = start_container_load_test(test_data)
    
    if status_code == 200 and "test_id" in data:
        # Vänta på att testet slutförs
        time.sleep(2)
        
        # Kontrollera test-status
        base_url = get_container_base_url()
        timeout = get_container_timeout()
        
        with httpx.Client(timeout=timeout) as client:
            status_response = client.get(f"{base_url}/api/v1/test/{data['test_id']}")
            return status_response.status_code, status_response.json()
    
    return status_code, data


def run_container_web_log_generation() -> Tuple[int, Dict[str, Any]]:
    """Kör web log generation och returnera status och data"""
    test_data = {
        "target": "local",
        "duration": 1,
        "log_types": ["web"],
        "logs_per_cycle": 2,
        "cycle_delay": 0.1
    }
    
    status_code, data = start_container_load_test(test_data)
    
    if status_code == 200 and "test_id" in data:
        # Vänta på att testet slutförs
        time.sleep(2)
        
        # Kontrollera test-status
        base_url = get_container_base_url()
        timeout = get_container_timeout()
        
        with httpx.Client(timeout=timeout) as client:
            status_response = client.get(f"{base_url}/api/v1/test/{data['test_id']}")
            return status_response.status_code, status_response.json()
    
    return status_code, data


def run_container_multiple_log_types() -> Tuple[int, Dict[str, Any]]:
    """Kör flera log-typer och returnera status och data"""
    test_data = {
        "target": "local",
        "duration": 1,
        "log_types": ["ssh", "web", "firewall"],
        "logs_per_cycle": 1,
        "cycle_delay": 0.1
    }
    
    status_code, data = start_container_load_test(test_data)
    
    if status_code == 200 and "test_id" in data:
        # Vänta på att testet slutförs
        time.sleep(2)
        
        # Kontrollera test-status
        base_url = get_container_base_url()
        timeout = get_container_timeout()
        
        with httpx.Client(timeout=timeout) as client:
            status_response = client.get(f"{base_url}/api/v1/test/{data['test_id']}")
            return status_response.status_code, status_response.json()
    
    return status_code, data


def check_container_environment_variables() -> Tuple[int, Dict[str, Any]]:
    """Kontrollera miljövariabler och returnera status och data"""
    config = get_test_config()
    api_config = config.get_api_config()
    timeout = httpx.Timeout(10.0)
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"http://{api_config['host']}:{api_config['port']}/health")
        return response.status_code, response.json()


def check_container_port_accessibility() -> Tuple[int, Dict[str, Any]]:
    """Kontrollera port-tillgänglighet och returnera status och data"""
    config = get_test_config()
    api_config = config.get_api_config()
    timeout = httpx.Timeout(10.0)
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"http://{api_config['host']}:{api_config['port']}/")
        return response.status_code, response.json()


def get_container_api_version() -> Tuple[int, Dict[str, Any]]:
    """Hämta API-version och returnera status och data"""
    config = get_test_config()
    api_config = config.get_api_config()
    timeout = httpx.Timeout(10.0)
    
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"http://{api_config['host']}:{api_config['port']}/")
        return response.status_code, response.json()
