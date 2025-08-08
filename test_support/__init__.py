#!/usr/bin/env python3
"""
Wazuh Load Generator - Test Support Library
==========================================
Support-bibliotek för tester
"""

# Importera alla utility-funktioner
from .load_generator_utils import *
from .api_utils import *

# Exportera huvudklasser och moduler
__all__ = [
    # Test Support App
    "TestSupportApp",
    
    # Test Fixtures
    "TestFixtures",
    
    # Test Utilities
    "TestUtilities",
    
    # Load Generator Utils
    "setup_generator_for_testing",
    "setup_generator_for_tcp_testing",
    "setup_mock_socket_for_udp_testing",
    "setup_mock_socket_for_tcp_testing",
    "generate_ssh_logs_for_testing",
    "generate_web_logs_for_testing",
    "generate_firewall_logs_for_testing",
    "generate_system_logs_for_testing",
    "generate_malware_logs_for_testing",
    "send_logs_for_testing",
    "setup_error_socket_for_testing",
    "setup_send_error_socket_for_testing",
    "measure_log_generation_performance",
    "measure_send_logs_performance",
    "run_full_load_test_cycle",
    "test_generator_with_different_targets",
    "validate_log_format_for_testing",
    "validate_log_format",
    "validate_log_content",
    
    # API Utils
    "get_root_endpoint_response",
    "get_health_endpoint_response",
    "get_scenarios_endpoint_response",
    "get_targets_endpoint_response",
    "get_list_tests_endpoint_response",
    "get_nonexistent_endpoint_response",
    "get_invalid_method_response",
    "get_async_root_endpoint_response",
    "get_async_health_endpoint_response",
    "get_start_test_invalid_data_response",
    "get_test_status_invalid_id_response",
    "get_stop_test_invalid_id_response",
    "get_delete_test_invalid_id_response",
    "get_api_ready_response",
    "get_api_response_structure_data",
    "get_cors_headers_response",
    "get_start_test_basic_response",
    "get_start_test_with_scenario_response",
    "get_start_test_all_log_types_responses",
    "get_start_test_different_protocols_responses",
    "get_test_status_response",
    "get_stop_test_response",
    "get_delete_test_response",
    "get_test_result_response",
    "get_test_result_invalid_id_response",
    "get_scenarios_response",
    "get_targets_response",
    "get_full_test_lifecycle_responses",
    "get_multiple_concurrent_tests_responses",
    "get_invalid_scenario_response",
    "get_invalid_target_response",
    "get_network_error_handling_response"
]
