#!/usr/bin/env python3
"""
Wazuh Load Generator - Container Setup Utilities
==============================================
Utility-funktioner för container setup och pre-test hantering
"""

import subprocess
import time
import httpx
from typing import Tuple, Dict, Any, Optional
from test_support.config import get_test_config


def check_container_exists() -> bool:
    """Kontrollera om test-containern finns"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=wazuh-loader-test", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        return "wazuh-loader-test" in result.stdout.strip()
    except subprocess.CalledProcessError:
        return False


def stop_and_remove_container() -> Tuple[bool, str]:
    """Stoppa och ta bort test-containern"""
    try:
        # Stoppa containern
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "down", "--remove-orphans"],
            capture_output=True,
            check=True
        )
        
        # Ta bort containern helt
        subprocess.run(
            ["docker", "rm", "-f", "wazuh-loader-test"],
            capture_output=True,
            check=False  # Ignorera fel om containern inte finns
        )
        
        return True, "Container stoppad och borttagen"
    except subprocess.CalledProcessError as e:
        return False, f"Fel vid stopp/ta bort container: {e}"


def force_stop_and_remove_container() -> Tuple[bool, str]:
    """Tvinga stopp och ta bort test-containern om den körs"""
    try:
        # Kontrollera om containern körs
        container_running = check_container_exists()
        
        if container_running:
            print("🛑 Stoppar och tar bort körande container...")
            
            # Stoppa containern med force
            subprocess.run(
                ["docker", "stop", "wazuh-loader-test"],
                capture_output=True,
                check=False
            )
            
            # Ta bort containern
            subprocess.run(
                ["docker", "rm", "-f", "wazuh-loader-test"],
                capture_output=True,
                check=False
            )
            
            # Stoppa docker-compose
            subprocess.run(
                ["docker-compose", "-f", "docker-compose.test.yml", "down", "--remove-orphans"],
                capture_output=True,
                check=False
            )
            
            return True, "Container tvingad stoppad och borttagen"
        else:
            return True, "Ingen container att stoppa"
            
    except Exception as e:
        return False, f"Fel vid tvingad stopp/ta bort container: {e}"


def build_container() -> Tuple[bool, str]:
    """Bygg test-containern på nytt"""
    try:
        # Bygg utan cache för att säkerställa färsk build
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "build", "--no-cache"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, "Container byggd framgångsrikt"
    except subprocess.CalledProcessError as e:
        return False, f"Fel vid bygg av container: {e.stderr}"


def start_container() -> Tuple[bool, str]:
    """Starta test-containern"""
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, "Container startad framgångsrikt"
    except subprocess.CalledProcessError as e:
        return False, f"Fel vid start av container: {e.stderr}"


def wait_for_container_ready(max_wait: int = 60) -> Tuple[bool, str]:
    """Vänta på att containern är redo"""
    # Använd localhost istället för 0.0.0.0 för container-tester
    health_url = "http://localhost:9090/health"
    
    for i in range(max_wait):
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(health_url)
                if response.status_code == 200:
                    return True, f"Container redo efter {i+1} sekunder"
        except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError):
            pass
        
        time.sleep(1)
    
    return False, f"Container inte redo efter {max_wait} sekunder"


def check_health_endpoint_exists() -> Tuple[bool, str]:
    """Kontrollera om health endpoint finns"""
    # Använd localhost istället för 0.0.0.0 för container-tester
    health_url = "http://localhost:9090/health"
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(health_url)
            if response.status_code == 200:
                return True, "Health endpoint finns och svarar"
            else:
                return False, f"Health endpoint svarar med status {response.status_code}"
    except (httpx.ConnectError, httpx.TimeoutException, httpx.ReadError):
        return False, "Health endpoint inte tillgänglig"


def check_health_endpoint_not_exists() -> Tuple[bool, str]:
    """Kontrollera att health endpoint INTE finns (för pre-test)"""
    # Använd localhost istället för 0.0.0.0 för container-tester
    health_url = "http://localhost:9090/health"
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(health_url)
            return False, f"Health endpoint finns trots allt (status {response.status_code})"
    except (httpx.ConnectError, httpx.TimeoutException):
        return True, "Health endpoint finns inte (som förväntat)"


def get_container_logs() -> str:
    """Hämta container logs för debugging"""
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "logs"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Kunde inte hämta logs: {e}"


def get_container_status() -> Dict[str, Any]:
    """Hämta container status information"""
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "docker-compose.test.yml", "ps"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Kontrollera om containern körs
        running_result = subprocess.run(
            ["docker", "ps", "--filter", "name=wazuh-loader-test", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "compose_status": result.stdout,
            "container_running": "Up" in running_result.stdout,
            "container_status": running_result.stdout.strip()
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": str(e),
            "compose_status": "Fel vid hämtning av status",
            "container_running": False
        }


def execute_in_container(command: str) -> Tuple[bool, str]:
    """Kör kommando i containern"""
    try:
        result = subprocess.run(
            ["docker", "exec", "wazuh-loader-test", "sh", "-c", command],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Fel vid körning av kommando: {e.stderr}"


def install_and_run_in_container() -> Tuple[bool, str]:
    """Installera och kör tester i containern"""
    commands = [
        "echo 'Installerar dependencies...'",
        "pip install -r requirements.txt",
        "pip install -r requirements_test.txt",
        "echo 'Kör health check...'",
        "python -c \"import httpx; print('HTTP client fungerar')\"",
        "echo 'Container setup slutförd'"
    ]
    
    for command in commands:
        success, output = execute_in_container(command)
        if not success:
            return False, f"Fel vid körning av '{command}': {output}"
    
    return True, "Installation och setup slutförd"


def setup_container_for_testing() -> Tuple[bool, str]:
    """Komplett setup av container för testing"""
    steps = [
        ("Kontrollerar om container finns", lambda: (True, "Container check slutförd") if check_container_exists() else (True, "Ingen container hittad")),
        ("Stoppar och tar bort container", lambda: stop_and_remove_container()),
        ("Bygger container på nytt", build_container),
        ("Startar container", start_container),
        ("Väntar på att container är redo", lambda: wait_for_container_ready()),
        ("Installerar i container", install_and_run_in_container)
    ]
    
    for step_name, step_func in steps:
        success, message = step_func()
        if not success:
            return False, f"Fel i steg '{step_name}': {message}"
    
    return True, "Container setup slutförd framgångsrikt"
