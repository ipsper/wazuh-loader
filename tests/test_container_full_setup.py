#!/usr/bin/env python3
"""
Wazuh Load Generator - Full Container Setup Tests
===============================================
Komplett test suite som stoppar, tar bort och installerar containern

Denna test suite fokuserar på:
✅ Pre-test: Stoppa och ta bort eventuell container
✅ Container build och installation
✅ Health endpoint verifiering
✅ Container installation och setup
✅ Post-setup verifiering

Alla tester körs i logisk ordning för komplett container lifecycle.
"""

import pytest
import time
from test_support.container_setup_utils import *


def test_01_pre_cleanup():
    """Step 1: Ta bort eventuell körande container"""
    print("\n🧹 Steg 1: Rensa eventuell körande container...")
    
    # Tvinga stopp och ta bort container om den finns
    success, message = force_stop_and_remove_container()
    assert success, f"Kunde inte ta bort körande container: {message}"
    
    # Verifiera att health endpoint inte finns
    health_exists, health_message = check_health_endpoint_not_exists()
    assert health_exists, f"Health endpoint finns fortfarande: {health_message}"
    
    print("✅ Pre-cleanup slutförd")


def test_02_build_container():
    """Step 2: Bygg container på nytt"""
    print("\n🔨 Steg 2: Bygger container...")
    
    success, message = build_container()
    assert success, f"Kunde inte bygga container: {message}"
    
    print("✅ Container byggd")


def test_03_start_container():
    """Step 3: Starta container"""
    print("\n🚀 Steg 3: Startar container...")
    
    success, message = start_container()
    assert success, f"Kunde inte starta container: {message}"
    
    print("✅ Container startad")


def test_04_wait_container_ready():
    """Step 4: Vänta på att container är redo"""
    print("\n⏳ Steg 4: Väntar på att container blir redo...")
    
    success, message = wait_for_container_ready(max_wait=90)
    assert success, f"Container blev inte redo: {message}"
    
    print("✅ Container är redo")


def test_05_verify_container_exists():
    """Step 5: Verifiera att containern finns"""
    print("\n🔍 Steg 5: Verifierar att container finns...")
    
    container_exists = check_container_exists()
    assert container_exists, "Container finns inte efter start"
    
    print("✅ Container verifierad")


def test_06_verify_health_endpoint():
    """Step 6: Verifiera health endpoint"""
    print("\n🏥 Steg 6: Verifierar health endpoint...")
    
    health_exists, health_message = check_health_endpoint_exists()
    assert health_exists, f"Health endpoint fungerar inte: {health_message}"
    
    print("✅ Health endpoint fungerar")


def test_07_verify_container_status():
    """Step 7: Verifiera container status"""
    print("\n📊 Steg 7: Verifierar container status...")
    
    status = get_container_status()
    
    assert "error" not in status, f"Fel vid hämtning av status: {status.get('error')}"
    assert status["container_running"], "Container körs inte"
    assert "Up" in status["container_status"], f"Container status felaktig: {status['container_status']}"
    
    print("✅ Container status OK")


def test_08_install_in_container():
    """Step 8: Installera dependencies i containern"""
    print("\n📦 Steg 8: Installerar dependencies i container...")
    
    success, message = install_and_run_in_container()
    assert success, f"Kunde inte installera i container: {message}"
    
    print("✅ Installation slutförd")


def test_09_verify_python_environment():
    """Step 9: Verifiera Python-miljön"""
    print("\n🐍 Steg 9: Verifierar Python-miljö...")
    
    success, output = execute_in_container("python --version")
    assert success, f"Python fungerar inte i container: {output}"
    
    success, output = execute_in_container("pip list | grep httpx")
    assert success, f"httpx är inte installerat i container: {output}"
    assert "httpx" in output, f"httpx saknas i container: {output}"
    
    print("✅ Python-miljö verifierad")


def test_10_verify_api_endpoints():
    """Step 10: Verifiera API endpoints"""
    print("\n🌐 Steg 10: Verifierar API endpoints...")
    
    # Testa root endpoint
    success, output = execute_in_container("curl -s http://localhost:9090/")
    assert success, f"Root endpoint fungerar inte: {output}"
    assert "Wazuh" in output, f"Root endpoint returnerar fel data: {output}"
    
    # Testa health endpoint från containern
    success, output = execute_in_container("curl -s http://localhost:9090/health")
    assert success, f"Health endpoint fungerar inte från container: {output}"
    assert "healthy" in output, f"Health endpoint returnerar fel data: {output}"
    
    # Testa scenarios endpoint
    success, output = execute_in_container("curl -s http://localhost:9090/api/v1/scenarios")
    assert success, f"Scenarios endpoint fungerar inte: {output}"
    assert "scenarios" in output, f"Scenarios endpoint returnerar fel data: {output}"
    
    # Testa targets endpoint
    success, output = execute_in_container("curl -s http://localhost:9090/api/v1/targets")
    assert success, f"Targets endpoint fungerar inte: {output}"
    assert "targets" in output, f"Targets endpoint returnerar fel data: {output}"
    
    print("✅ API endpoints verifierade")


def test_11_verify_network_connectivity():
    """Step 11: Verifiera nätverksanslutning"""
    print("\n🔗 Steg 11: Verifierar nätverksanslutning...")
    
    # Testa att container kan nå sig själv
    success, output = execute_in_container("curl -s http://localhost:9090/health")
    assert success, f"Container kan inte nå sig själv: {output}"
    assert "healthy" in output, f"Health check returnerar fel data: {output}"
    
    print("✅ Nätverksanslutning verifierad")


def test_12_verify_container_logs():
    """Step 12: Verifiera container logs"""
    print("\n📋 Steg 12: Verifierar container logs...")
    
    logs = get_container_logs()
    
    assert len(logs) > 0, "Container logs är tomma"
    assert "wazuh-loader-test" in logs or "Wazuh" in logs, "Container logs innehåller inte förväntad information"
    
    print("✅ Container logs verifierade")


def test_13_final_health_check():
    """Step 13: Slutlig health check"""
    print("\n🏁 Steg 13: Slutlig health check...")
    
    # Vänta lite extra för att säkerställa stabilitet
    time.sleep(3)
    
    health_exists, health_message = check_health_endpoint_exists()
    assert health_exists, f"Slutlig health check misslyckades: {health_message}"
    
    # Kör en sista test från utsidan
    success, output = execute_in_container("curl -s http://localhost:9090/health")
    assert success, f"Slutlig health test misslyckades: {output}"
    assert "healthy" in output, f"Slutlig health test returnerar fel data: {output}"
    
    print("✅ Slutlig health check OK")
    print("\n🎉 Komplett container setup och verifiering slutförd!")


def test_14_setup_summary():
    """Step 14: Setup sammanfattning"""
    print("\n📊 Setup Sammanfattning:")
    print("✅ Container stoppad och borttagen")
    print("✅ Container byggd på nytt") 
    print("✅ Container startad")
    print("✅ Health endpoint fungerar")
    print("✅ Dependencies installerade")
    print("✅ API endpoints verifierade")
    print("✅ Nätverksanslutning OK")
    print("✅ Container logs OK")
    print("✅ Slutlig verifiering OK")
    print("\n🚀 Container är nu redo för användning!")
    
    # En sista verifiering att allt fungerar
    container_exists = check_container_exists()
    assert container_exists, "Container finns inte vid slutlig kontroll"
    
    health_exists, _ = check_health_endpoint_exists()
    assert health_exists, "Health endpoint fungerar inte vid slutlig kontroll"
