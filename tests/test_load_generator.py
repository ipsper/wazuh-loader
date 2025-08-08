#!/usr/bin/env python3
"""
Wazuh Load Generator - Load Generator Tests
==========================================
Unit-tester för WazuhLoadGenerator-klassen
"""

import pytest
from unittest.mock import Mock, patch

from test_support.load_generator_utils import (
    setup_generator_for_testing,
    setup_generator_for_tcp_testing,
    setup_mock_socket_for_udp_testing,
    setup_mock_socket_for_tcp_testing,
    generate_ssh_logs_for_testing,
    generate_web_logs_for_testing,
    generate_firewall_logs_for_testing,
    generate_system_logs_for_testing,
    generate_malware_logs_for_testing,
    send_logs_for_testing,
    setup_error_socket_for_testing,
    setup_send_error_socket_for_testing,
    measure_log_generation_performance,
    measure_send_logs_performance,
    run_full_load_test_cycle,
    test_generator_with_different_targets,
    validate_log_format_for_testing,
    validate_log_format,
    validate_log_content
)


def test_generator_initialization():
    """Testa generator-initiering"""
    generator = setup_generator_for_testing("localhost", 514, "udp")
    
    assert generator.target_host == "localhost"
    assert generator.target_port == 514
    assert generator.protocol == "udp"
    assert generator.fake is not None


def test_generator_initialization_tcp():
    """Testa generator-initiering med TCP"""
    generator = setup_generator_for_tcp_testing()
    
    assert generator.target_host == "localhost"
    assert generator.target_port == 601
    assert generator.protocol == "tcp"


def test_setup_socket_udp():
    """Testa socket-setup för UDP"""
    mock_socket_class, mock_socket = setup_mock_socket_for_udp_testing()
    generator = setup_generator_for_testing("localhost", 514, "udp")
    
    mock_socket_class.assert_called_once()
    args, kwargs = mock_socket_class.call_args
    assert args[0] == 2  # AF_INET
    assert args[1] == 2  # SOCK_DGRAM


def test_setup_socket_tcp():
    """Testa socket-setup för TCP"""
    mock_socket_class, mock_socket = setup_mock_socket_for_tcp_testing()
    generator = setup_generator_for_tcp_testing()
    
    mock_socket_class.assert_called_once()
    args, kwargs = mock_socket_class.call_args
    assert args[0] == 2  # AF_INET
    assert args[1] == 1  # SOCK_STREAM


def test_generate_ssh_logs():
    """Testa SSH-loggenerering"""
    generator = setup_generator_for_testing()
    logs = generate_ssh_logs_for_testing(generator, 5)
    
    assert len(logs) == 5
    assert validate_log_format(logs, "ssh")
    assert validate_log_content(logs, "ssh")


def test_generate_web_logs():
    """Testa web-loggenerering"""
    generator = setup_generator_for_testing()
    logs = generate_web_logs_for_testing(generator, 5)
    
    assert len(logs) == 5
    assert validate_log_format(logs, "web")
    assert validate_log_content(logs, "web")


def test_generate_firewall_logs():
    """Testa brandväggs-loggenerering"""
    generator = setup_generator_for_testing()
    logs = generate_firewall_logs_for_testing(generator, 5)
    
    assert len(logs) == 5
    assert validate_log_format(logs, "firewall")
    assert validate_log_content(logs, "firewall")


def test_generate_system_logs():
    """Testa system-loggenerering"""
    generator = setup_generator_for_testing()
    logs = generate_system_logs_for_testing(generator, 5)
    
    assert len(logs) == 5
    assert validate_log_format(logs, "system")


def test_generate_malware_logs():
    """Testa malware-loggenerering"""
    generator = setup_generator_for_testing()
    logs = generate_malware_logs_for_testing(generator, 5)
    
    assert len(logs) == 5
    assert validate_log_format(logs, "malware")


def test_send_logs_udp():
    """Testa UDP loggskickning"""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        generator = setup_generator_for_testing("localhost", 514, "udp")
        logs = generate_ssh_logs_for_testing(generator, 3)
        
        sent_count = send_logs_for_testing(generator, logs, 0.01)
        assert sent_count == 3
        assert mock_socket.sendto.call_count == 3


def test_send_logs_tcp():
    """Testa TCP loggskickning"""
    with patch('socket.socket') as mock_socket_class:
        mock_socket = Mock()
        mock_socket_class.return_value = mock_socket
        
        generator = setup_generator_for_tcp_testing()
        logs = generate_ssh_logs_for_testing(generator, 3)
        
        sent_count = send_logs_for_testing(generator, logs, 0.01)
        assert sent_count == 3
        assert mock_socket.send.call_count == 3


def test_socket_connection_error():
    """Testa socket-anslutningsfel"""
    mock_socket_class, mock_socket = setup_error_socket_for_testing()
    
    with pytest.raises(Exception):
        setup_generator_for_testing("invalid-host", 601, "tcp")


def test_send_logs_error():
    """Testa loggskickningsfel"""
    mock_socket_class, mock_socket = setup_send_error_socket_for_testing()
    
    generator = setup_generator_for_testing()
    logs = generate_ssh_logs_for_testing(generator, 3)
    
    sent_count = send_logs_for_testing(generator, logs, 0.01)
    assert sent_count == 0  # Inga loggar skickades på grund av fel


def test_invalid_log_type():
    """Testa ogiltig loggtyp"""
    generator = setup_generator_for_testing()
    
    # Testa med ogiltig loggtyp
    with pytest.raises(AttributeError):
        generator.generate_invalid_logs(5)


def test_log_generation_performance():
    """Testa loggenereringsprestanda"""
    generator = setup_generator_for_testing()
    
    execution_time = measure_log_generation_performance(generator, 100)
    assert execution_time < 1.0  # Bör ta mindre än 1 sekund


def test_send_logs_performance():
    """Testa loggskickningsprestanda"""
    generator = setup_generator_for_testing()
    logs = generate_ssh_logs_for_testing(generator, 50)
    
    execution_time = measure_send_logs_performance(generator, logs, 0.01)
    assert execution_time < 2.0  # Bör ta mindre än 2 sekunder


def test_full_load_test_cycle():
    """Testa fullständig load test-cykel"""
    generator = setup_generator_for_testing()
    
    total_sent = run_full_load_test_cycle(generator)
    assert total_sent == 25  # 5 loggar per typ * 5 typer


def test_generator_with_different_targets():
    """Testa generator med olika targets"""
    generators = test_generator_with_different_targets()
    
    for generator, host, port, protocol in generators:
        assert generator.target_host == host
        assert generator.target_port == port
        assert generator.protocol == protocol


def test_log_format_validation():
    """Testa loggformat-validering"""
    generator = setup_generator_for_testing()
    validation_data = validate_log_format_for_testing(generator)
    
    assert len(validation_data["ssh_logs"]) == 1
    ssh_log = validation_data["ssh_log"]
    assert "sshd[" in ssh_log
    assert any(keyword in ssh_log for keyword in ["Failed password", "Accepted password", "Invalid user"])
    
    assert len(validation_data["web_logs"]) == 1
    web_log = validation_data["web_log"]
    assert "HTTP/1.1" in web_log
    assert any(keyword in web_log for keyword in ["GET", "POST", "PUT", "DELETE"])
