#!/usr/bin/env python3
"""
Wazuh Load Generator - Test Runner
==================================
Script för att köra alla tester
"""

import subprocess
import sys
import os
from pathlib import Path


def run_pytest_tests():
    """Kör pytest-tester"""
    print("🧪 Kör pytest-tester...")
    
    # Kontrollera att vi är i rätt katalog
    if not Path("tests").exists():
        print("❌ tests-katalog hittades inte")
        return False
    
    # Kör testerna
    try:
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=.",
            "--cov-report=term-missing"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Fel vid körning av tester: {e}")
        return False


def run_unit_tests():
    """Kör endast unit-tester"""
    print("🧪 Kör unit-tester...")
    
    try:
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/",
            "-m", "unit",
            "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Fel vid körning av unit-tester: {e}")
        return False


def run_api_tests():
    """Kör endast API-tester"""
    print("🧪 Kör API-tester...")
    
    try:
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/",
            "-m", "api",
            "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Fel vid körning av API-tester: {e}")
        return False


def run_integration_tests():
    """Kör endast integration-tester"""
    print("🧪 Kör integration-tester...")
    
    try:
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/",
            "-m", "integration",
            "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Fel vid körning av integration-tester: {e}")
        return False


def run_coverage_report():
    """Kör coverage-rapport"""
    print("📊 Genererar coverage-rapport...")
    
    try:
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/",
            "--cov=.",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing"
        ], capture_output=True, text=True)
        
        print("✅ Coverage-rapport genererad i htmlcov/")
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Fel vid generering av coverage-rapport: {e}")
        return False


def install_test_dependencies():
    """Installera test-beroenden"""
    print("📦 Installerar test-beroenden...")
    
    try:
        result = subprocess.run([
            "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test-beroenden installerade")
            return True
        else:
            print(f"❌ Fel vid installation: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Fel vid installation av beroenden: {e}")
        return False


def main():
    """Huvudfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Wazuh Load Generator Test Runner")
    parser.add_argument("--type", choices=["all", "unit", "api", "integration"], 
                       default="all", help="Typ av tester att köra")
    parser.add_argument("--coverage", action="store_true", help="Generera coverage-rapport")
    parser.add_argument("--install-deps", action="store_true", help="Installera test-beroenden")
    
    args = parser.parse_args()
    
    # Installera beroenden om begärt
    if args.install_deps:
        if not install_test_dependencies():
            sys.exit(1)
    
    # Kör tester baserat på typ
    success = False
    
    if args.type == "all":
        success = run_pytest_tests()
    elif args.type == "unit":
        success = run_unit_tests()
    elif args.type == "api":
        success = run_api_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    
    # Kör coverage om begärt
    if args.coverage and success:
        run_coverage_report()
    
    if success:
        print("✅ Alla tester slutförda framgångsrikt!")
        sys.exit(0)
    else:
        print("❌ Några tester misslyckades")
        sys.exit(1)


if __name__ == "__main__":
    main()
