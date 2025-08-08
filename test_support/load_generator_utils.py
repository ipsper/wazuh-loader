#!/usr/bin/env python3
"""
Wazuh Load Generator - Load Generator Test Utilities
==================================================
Utility-funktioner för load generator-tester
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from wazuh_loader import WazuhLoadGenerator
from .utils import MockUtils, PerformanceUtils


def create_test_generator(host: str = "localhost", port: int = 514, protocol: str = "udp") -> WazuhLoadGenerator:
    """Skapa en test-generator"""
    return WazuhLoadGenerator(host, port, protocol)


def validate_log_format(logs: List[str], expected_type: str) -> bool:
    """Validera loggformat"""
    if expected_type == "ssh":
        return all("sshd[" in log for log in logs)
    elif expected_type == "web":
        return all("HTTP/1.1" in log for log in logs)
    elif expected_type == "firewall":
        return all("iptables" in log for log in logs)
    elif expected_type == "system":
        return all(any(keyword in log for keyword in ["systemd", "kernel", "cron", "sudo"]) for log in logs)
    elif expected_type == "malware":
        return all(any(keyword in log for keyword in ["clamav", "malware_detector", "antivirus"]) for log in logs)
    return False


def validate_log_content(logs: List[str], expected_type: str) -> bool:
    """Validera logginnehåll"""
    if expected_type == "ssh":
        return all(any(keyword in log for keyword in ["Failed password", "Accepted password", "Invalid user"]) for log in logs)
    elif expected_type == "web":
        return all(any(keyword in log for keyword in ["GET", "POST", "PUT", "DELETE"]) for log in logs)
    elif expected_type == "firewall":
        return all(any(keyword in log for keyword in ["DROP", "ACCEPT", "LOG"]) for log in logs)
    return True


def setup_generator_for_testing(host: str = "localhost", port: int = 514, protocol: str = "udp") -> WazuhLoadGenerator:
    """Sätt upp generator för testning"""
    return create_test_generator(host, port, protocol)


def setup_generator_for_tcp_testing() -> WazuhLoadGenerator:
    """Sätt upp generator för TCP-testning"""
    return create_test_generator("localhost", 601, "tcp")


def setup_mock_socket_for_udp_testing():
    """Sätt upp mock socket för UDP-testning"""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        return mock_socket_class, mock_socket


def setup_mock_socket_for_tcp_testing():
    """Sätt upp mock socket för TCP-testning"""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        return mock_socket_class, mock_socket


def generate_ssh_logs_for_testing(generator: WazuhLoadGenerator, count: int = 5) -> List[str]:
    """Generera SSH-loggar för testning"""
    return generator.generate_ssh_logs(count)


def generate_web_logs_for_testing(generator: WazuhLoadGenerator, count: int = 5) -> List[str]:
    """Generera web-loggar för testning"""
    return generator.generate_web_logs(count)


def generate_firewall_logs_for_testing(generator: WazuhLoadGenerator, count: int = 5) -> List[str]:
    """Generera brandväggs-loggar för testning"""
    return generator.generate_firewall_logs(count)


def generate_system_logs_for_testing(generator: WazuhLoadGenerator, count: int = 5) -> List[str]:
    """Generera system-loggar för testning"""
    return generator.generate_system_logs(count)


def generate_malware_logs_for_testing(generator: WazuhLoadGenerator, count: int = 5) -> List[str]:
    """Generera malware-loggar för testning"""
    return generator.generate_malware_logs(count)


def send_logs_for_testing(generator: WazuhLoadGenerator, logs: List[str], delay: float = 0.01) -> int:
    """Skicka loggar för testning"""
    return generator.send_logs(logs, delay)


def setup_error_socket_for_testing():
    """Sätt upp error socket för testning"""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket.connect.side_effect = Exception("Connection failed")
        mock_socket_class.return_value = mock_socket
        return mock_socket_class, mock_socket


def setup_send_error_socket_for_testing():
    """Sätt upp send error socket för testning"""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket.sendto.side_effect = Exception("Send failed")
        mock_socket_class.return_value = mock_socket
        return mock_socket_class, mock_socket


def measure_log_generation_performance(generator: WazuhLoadGenerator, count: int = 100) -> float:
    """Mäta loggenereringsprestanda"""
    return PerformanceUtils.measure_execution_time(
        generator.generate_ssh_logs, count
    )


def measure_send_logs_performance(generator: WazuhLoadGenerator, logs: List[str], delay: float = 0.01) -> float:
    """Mäta loggskickningsprestanda"""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        return PerformanceUtils.measure_execution_time(
            generator.send_logs, logs, delay
        )


def run_full_load_test_cycle(generator: WazuhLoadGenerator) -> int:
    """Kör fullständig load test-cykel"""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        # Testa alla loggtyper
        log_types = ["ssh", "web", "firewall", "system", "malware"]
        total_sent = 0
        
        for log_type in log_types:
            if log_type == "ssh":
                logs = generator.generate_ssh_logs(5)
            elif log_type == "web":
                logs = generator.generate_web_logs(5)
            elif log_type == "firewall":
                logs = generator.generate_firewall_logs(5)
            elif log_type == "system":
                logs = generator.generate_system_logs(5)
            elif log_type == "malware":
                logs = generator.generate_malware_logs(5)
            
            sent_count = generator.send_logs(logs, delay=0.01)
            total_sent += sent_count
        
        return total_sent


def test_generator_with_different_targets():
    """Testa generator med olika targets"""
    targets = [
        ("localhost", 514, "udp"),
        ("localhost", 601, "tcp"),
        ("192.168.1.100", 514, "udp")
    ]
    
    generators = []
    for host, port, protocol in targets:
        generator = create_test_generator(host, port, protocol)
        generators.append((generator, host, port, protocol))
    
    return generators


def validate_log_format_for_testing(generator: WazuhLoadGenerator):
    """Validera loggformat för testning"""
    # Testa SSH-loggar
    ssh_logs = generator.generate_ssh_logs(1)
    web_logs = generator.generate_web_logs(1)
    
    return {
        "ssh_logs": ssh_logs,
        "web_logs": web_logs,
        "ssh_log": ssh_logs[0] if ssh_logs else None,
        "web_log": web_logs[0] if web_logs else None
    }
