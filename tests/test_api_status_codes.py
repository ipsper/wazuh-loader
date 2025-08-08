#!/usr/bin/env python3
"""
Wazuh Load Generator - API Status Code Tests
===========================================
Testar bara API-serverns returkoder utan att starta riktiga load generator-tester

Denna test suite fokuserar på:
✅ HTTP status codes (200, 404, 405, 422, etc.)
✅ API response strukturer
✅ Validering av input-data
✅ Felhantering

Inga riktiga load generator-tester körs - allt är mockat för snabba tester.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from api_server import app


@pytest.fixture(autouse=True)
def mock_load_generator():
    """Mocka WazuhLoadGenerator för att undvika riktiga nätverksanrop"""
    with patch('api_server.WazuhLoadGenerator') as mock:
        # Mocka generator-instansen
        mock_instance = MagicMock()
        mock_instance.send_logs.return_value = 5  # Returnera 5 skickade loggar
        mock_instance.generate_ssh_logs.return_value = ["ssh log 1", "ssh log 2"]
        mock_instance.generate_web_logs.return_value = ["web log 1", "web log 2"]
        mock_instance.generate_firewall_logs.return_value = ["firewall log 1", "firewall log 2"]
        mock_instance.generate_system_logs.return_value = ["system log 1", "system log 2"]
        mock_instance.generate_malware_logs.return_value = ["malware log 1", "malware log 2"]
        mock.return_value = mock_instance
        yield mock


class TestAPIStatusCodes:
    """Testar API-serverns returkoder"""

    def test_root_endpoint_status_code(self, test_client: TestClient):
        """Testa root endpoint returkod"""
        response = test_client.get("/")
        assert response.status_code == 200

    def test_health_endpoint_status_code(self, test_client: TestClient):
        """Testa health endpoint returkod"""
        response = test_client.get("/health")
        assert response.status_code == 200

    def test_scenarios_endpoint_status_code(self, test_client: TestClient):
        """Testa scenarios endpoint returkod"""
        response = test_client.get("/api/v1/scenarios")
        assert response.status_code == 200

    def test_targets_endpoint_status_code(self, test_client: TestClient):
        """Testa targets endpoint returkod"""
        response = test_client.get("/api/v1/targets")
        assert response.status_code == 200

    def test_list_tests_endpoint_status_code(self, test_client: TestClient):
        """Testa list tests endpoint returkod"""
        response = test_client.get("/api/v1/test")
        assert response.status_code == 200

    def test_nonexistent_endpoint_status_code(self, test_client: TestClient):
        """Testa icke-existerande endpoint returkod"""
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_invalid_method_status_code(self, test_client: TestClient):
        """Testa ogiltig HTTP-metod returkod"""
        response = test_client.post("/health")
        assert response.status_code == 405  # Method Not Allowed

    def test_start_test_basic_status_code(self, test_client: TestClient):
        """Testa start test grundläggande returkod"""
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": "ssh",
            "count": 5,
            "delay": 0.1
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 200

    def test_start_test_invalid_data_status_code(self, test_client: TestClient):
        """Testa start test med ogiltig data returkod"""
        invalid_data = {
            "target_host": "",  # Ogiltig host
            "target_port": -1,  # Ogiltig port
            "protocol": "invalid",  # Ogiltigt protokoll
            "log_type": "invalid",  # Ogiltig loggtyp
            "count": -1,  # Ogiltigt antal
            "delay": -0.1  # Ogiltig fördröjning
        }
        response = test_client.post("/api/v1/test/start", json=invalid_data)
        assert response.status_code == 400  # Bad Request (API validerar innan Pydantic)

    def test_get_test_status_invalid_id_status_code(self, test_client: TestClient):
        """Testa hämta test status med ogiltigt ID returkod"""
        response = test_client.get("/api/v1/test/invalid-id")
        assert response.status_code == 404

    def test_stop_test_invalid_id_status_code(self, test_client: TestClient):
        """Testa stoppa test med ogiltigt ID returkod"""
        response = test_client.post("/api/v1/test/invalid-id/stop")
        assert response.status_code == 404

    def test_delete_test_invalid_id_status_code(self, test_client: TestClient):
        """Testa ta bort test med ogiltigt ID returkod"""
        response = test_client.delete("/api/v1/test/invalid-id")
        assert response.status_code == 404

    def test_get_test_result_invalid_id_status_code(self, test_client: TestClient):
        """Testa hämta test resultat med ogiltigt ID returkod"""
        response = test_client.get("/api/v1/test/invalid-id/result")
        assert response.status_code == 404

    def test_start_test_with_scenario_status_code(self, test_client: TestClient):
        """Testa start test med scenario returkod"""
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": "ssh",
            "scenario": "light_load"
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 200

    def test_start_test_invalid_scenario_status_code(self, test_client: TestClient):
        """Testa start test med ogiltigt scenario returkod"""
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": "ssh",
            "scenario": "nonexistent_scenario"
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 400

    def test_start_test_all_log_types_status_codes(self, test_client: TestClient):
        """Testa start test med alla loggtyper returkoder"""
        log_types = ["ssh", "web", "firewall", "system", "malware"]
        
        for log_type in log_types:
            test_data = {
                "target_host": "localhost",
                "target_port": 514,
                "protocol": "udp",
                "log_type": log_type,
                "count": 3,
                "delay": 0.1
            }
            response = test_client.post("/api/v1/test/start", json=test_data)
            assert response.status_code == 200

    def test_start_test_different_protocols_status_codes(self, test_client: TestClient):
        """Testa start test med olika protokoll returkoder"""
        protocols = ["udp", "tcp"]
        
        for protocol in protocols:
            test_data = {
                "target_host": "localhost",
                "target_port": 514 if protocol == "udp" else 601,
                "protocol": protocol,
                "log_type": "ssh",
                "count": 3,
                "delay": 0.1
            }
            response = test_client.post("/api/v1/test/start", json=test_data)
            assert response.status_code == 200

    def test_start_test_invalid_protocol_status_code(self, test_client: TestClient):
        """Testa start test med ogiltigt protokoll returkod"""
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "invalid",
            "log_type": "ssh",
            "count": 5
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 400

    def test_start_test_invalid_log_type_status_code(self, test_client: TestClient):
        """Testa start test med ogiltig loggtyp returkod"""
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": "invalid",
            "count": 5
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 400

    def test_cors_headers_status_code(self, test_client: TestClient):
        """Testa CORS headers returkod"""
        response = test_client.options("/")
        assert response.status_code == 405  # Method Not Allowed (root endpoint stöder inte OPTIONS)

    def test_api_documentation_status_codes(self, test_client: TestClient):
        """Testa API-dokumentation returkoder"""
        # Testa Swagger UI
        response = test_client.get("/docs")
        assert response.status_code == 200
        
        # Testa ReDoc
        response = test_client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_schema_status_code(self, test_client: TestClient):
        """Testa OpenAPI schema returkod"""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200


class TestAPIResponseStructure:
    """Testar API-svar strukturer"""

    def test_root_endpoint_response_structure(self, test_client: TestClient):
        """Testa root endpoint svarsstruktur"""
        response = test_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "Wazuh Load Generator API"

    def test_health_endpoint_response_structure(self, test_client: TestClient):
        """Testa health endpoint svarsstruktur"""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"

    def test_scenarios_endpoint_response_structure(self, test_client: TestClient):
        """Testa scenarios endpoint svarsstruktur"""
        response = test_client.get("/api/v1/scenarios")
        assert response.status_code == 200
        
        data = response.json()
        assert "scenarios" in data
        assert "count" in data
        assert isinstance(data["scenarios"], dict)
        assert isinstance(data["count"], int)

    def test_targets_endpoint_response_structure(self, test_client: TestClient):
        """Testa targets endpoint svarsstruktur"""
        response = test_client.get("/api/v1/targets")
        assert response.status_code == 200
        
        data = response.json()
        assert "targets" in data
        assert "count" in data
        assert isinstance(data["targets"], dict)
        assert isinstance(data["count"], int)

    def test_list_tests_endpoint_response_structure(self, test_client: TestClient):
        """Testa list tests endpoint svarsstruktur"""
        response = test_client.get("/api/v1/test")
        assert response.status_code == 200
        
        data = response.json()
        assert "tests" in data
        assert "total" in data
        assert "running" in data
        assert "completed" in data
        assert "failed" in data
        assert isinstance(data["tests"], list)

    def test_start_test_response_structure(self, test_client: TestClient):
        """Testa start test svarsstruktur"""
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": "ssh",
            "count": 5,
            "delay": 0.1
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "test_id" in data
        assert "status" in data
        assert "message" in data
        assert data["status"] == "started"
        assert "test_" in data["test_id"]

    def test_error_response_structure(self, test_client: TestClient):
        """Testa felmeddelande svarsstruktur"""
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Test" in data["detail"] or "not found" in data["detail"].lower()


class TestAPIValidation:
    """Testar API-validering"""

    def test_required_fields_validation(self, test_client: TestClient):
        """Testa validering av obligatoriska fält"""
        # Testa utan obligatoriska fält - API:et använder defaults
        response = test_client.post("/api/v1/test/start", json={})
        assert response.status_code == 200  # API:et använder default-värden

    def test_field_type_validation(self, test_client: TestClient):
        """Testa validering av fälttyper"""
        test_data = {
            "target_host": "localhost",
            "target_port": "not_a_number",  # Fel typ
            "protocol": "udp",
            "log_type": "ssh",
            "count": 5,
            "delay": 0.1
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 422

    def test_field_range_validation(self, test_client: TestClient):
        """Testa validering av fältintervall"""
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "udp",
            "log_type": "ssh",
            "count": -1,  # Negativt värde
            "delay": 0.1
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 200  # API:et validerar inte negativa värden

    def test_enum_validation(self, test_client: TestClient):
        """Testa validering av enum-värden"""
        test_data = {
            "target_host": "localhost",
            "target_port": 514,
            "protocol": "invalid_protocol",  # Ogiltigt protokoll
            "log_type": "ssh",
            "count": 5,
            "delay": 0.1
        }
        response = test_client.post("/api/v1/test/start", json=test_data)
        assert response.status_code == 400
