#!/usr/bin/env python3
"""
Wazuh Load Generator - API Client
=================================
Python-klient för att anropa Wazuh Load Generator API från andra hosts
"""

import requests
import json
import time
import argparse
from typing import Dict, List, Optional, Any
from datetime import datetime

class WazuhLoadGeneratorClient:
    """Klient för Wazuh Load Generator API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initierar API-klienten
        
        Args:
            base_url (str): Base URL för API-servern
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Gör HTTP-request till API:et"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Ogiltig HTTP-metod: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API-fel: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"   Detaljer: {error_detail}")
                except:
                    print(f"   Status: {e.response.status_code}")
            raise
    
    def health_check(self) -> Dict:
        """Kontrollera API-serverns hälsa"""
        return self._make_request("GET", "/health")
    
    def get_scenarios(self) -> Dict:
        """Hämta tillgängliga testscenarier"""
        return self._make_request("GET", "/api/v1/scenarios")
    
    def get_targets(self) -> Dict:
        """Hämta tillgängliga mål"""
        return self._make_request("GET", "/api/v1/targets")
    
    def start_test(self, 
                   target_host: str = "localhost",
                   target_port: int = 514,
                   protocol: str = "udp",
                   log_type: str = "all",
                   count: int = 100,
                   delay: float = 0.1,
                   duration: Optional[int] = None,
                   scenario: Optional[str] = None) -> Dict:
        """
        Starta ett nytt load test
        
        Args:
            target_host (str): Målvärd för loggar
            target_port (int): Målport för loggar
            protocol (str): Protokoll (udp/tcp)
            log_type (str): Loggtyp (all/ssh/web/firewall/system/malware)
            count (int): Antal loggar per typ
            delay (float): Fördröjning mellan loggar i sekunder
            duration (Optional[int]): Testlängd i sekunder
            scenario (Optional[str]): Fördefinierat scenario
            
        Returns:
            Dict: Test information med test_id
        """
        data = {
            "target_host": target_host,
            "target_port": target_port,
            "protocol": protocol,
            "log_type": log_type,
            "count": count,
            "delay": delay
        }
        
        if duration is not None:
            data["duration"] = duration
        
        if scenario is not None:
            data["scenario"] = scenario
        
        return self._make_request("POST", "/api/v1/test/start", data)
    
    def get_test_status(self, test_id: str) -> Dict:
        """Hämta status för ett specifikt test"""
        return self._make_request("GET", f"/api/v1/test/{test_id}")
    
    def get_test_result(self, test_id: str) -> Dict:
        """Hämta resultat för ett slutfört test"""
        return self._make_request("GET", f"/api/v1/test/{test_id}/result")
    
    def stop_test(self, test_id: str) -> Dict:
        """Stoppa ett pågående test"""
        return self._make_request("POST", f"/api/v1/test/{test_id}/stop")
    
    def delete_test(self, test_id: str) -> Dict:
        """Ta bort ett test från historiken"""
        return self._make_request("DELETE", f"/api/v1/test/{test_id}")
    
    def list_tests(self) -> Dict:
        """Lista alla tester"""
        return self._make_request("GET", "/api/v1/test")
    
    def wait_for_completion(self, test_id: str, poll_interval: float = 2.0, timeout: Optional[float] = None) -> Dict:
        """
        Vänta på att ett test ska slutföras
        
        Args:
            test_id (str): Test ID att vänta på
            poll_interval (float): Intervall mellan status-kontroller
            timeout (Optional[float]): Timeout i sekunder (None = oändligt)
            
        Returns:
            Dict: Slutgiltigt testresultat
        """
        start_time = time.time()
        
        while True:
            try:
                status = self.get_test_status(test_id)
                
                if status["status"] in ["completed", "failed", "stopped"]:
                    return self.get_test_result(test_id)
                
                # Kontrollera timeout
                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError(f"Test {test_id} tog för lång tid att slutföra")
                
                # Visa progress
                if status.get("progress") is not None:
                    print(f"📊 Progress: {status['progress']:.1f}%")
                if status.get("logs_sent"):
                    print(f"📤 Loggar skickade: {status['logs_sent']}")
                if status.get("logs_per_second"):
                    print(f"⚡ Loggar/sekund: {status['logs_per_second']:.2f}")
                
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"❌ Fel vid status-kontroll: {e}")
                raise
    
    def run_and_monitor(self, 
                        target_host: str = "localhost",
                        target_port: int = 514,
                        protocol: str = "udp",
                        log_type: str = "all",
                        count: int = 100,
                        delay: float = 0.1,
                        duration: Optional[int] = None,
                        scenario: Optional[str] = None,
                        poll_interval: float = 2.0) -> Dict:
        """
        Starta ett test och övervaka det till slutförande
        
        Args:
            Samma parametrar som start_test plus:
            poll_interval (float): Intervall för status-kontroller
            
        Returns:
            Dict: Slutgiltigt testresultat
        """
        print("🚀 Startar load test...")
        
        # Starta testet
        response = self.start_test(
            target_host=target_host,
            target_port=target_port,
            protocol=protocol,
            log_type=log_type,
            count=count,
            delay=delay,
            duration=duration,
            scenario=scenario
        )
        
        test_id = response["test_id"]
        print(f"✅ Test startat med ID: {test_id}")
        
        # Vänta på slutförande
        print("⏳ Väntar på slutförande...")
        result = self.wait_for_completion(test_id, poll_interval)
        
        print("✅ Test slutfört!")
        return result

def print_test_result(result: Dict):
    """Skriv ut testresultat på ett snyggt sätt"""
    print("\n" + "="*50)
    print("📊 TESTRESULTAT")
    print("="*50)
    print(f"Test ID: {result['test_id']}")
    print(f"Status: {result['status']}")
    print(f"Starttid: {result['start_time']}")
    print(f"Sluttid: {result['end_time']}")
    print(f"Totalt antal loggar: {result['total_logs_sent']:,}")
    print(f"Total tid: {result['total_time']:.2f}s")
    print(f"Loggar per sekund: {result['logs_per_second']:.2f}")
    print("\nKonfiguration:")
    for key, value in result['configuration'].items():
        print(f"  {key}: {value}")
    print("="*50)

def main():
    """Huvudfunktion för kommandoradsanvändning"""
    parser = argparse.ArgumentParser(description="Wazuh Load Generator API Client")
    parser.add_argument("--server", default="http://localhost:8000", help="API server URL")
    parser.add_argument("--action", required=True, 
                       choices=["health", "scenarios", "targets", "start", "status", "result", "stop", "delete", "list", "run"],
                       help="Åtgärd att utföra")
    parser.add_argument("--test-id", help="Test ID (för status, result, stop, delete)")
    parser.add_argument("--target-host", default="localhost", help="Målvärd")
    parser.add_argument("--target-port", type=int, default=514, help="Målport")
    parser.add_argument("--protocol", choices=["udp", "tcp"], default="udp", help="Protokoll")
    parser.add_argument("--log-type", choices=["all", "ssh", "web", "firewall", "system", "malware"], 
                       default="all", help="Loggtyp")
    parser.add_argument("--count", type=int, default=100, help="Antal loggar per typ")
    parser.add_argument("--delay", type=float, default=0.1, help="Fördröjning mellan loggar")
    parser.add_argument("--duration", type=int, help="Testlängd i sekunder")
    parser.add_argument("--scenario", help="Fördefinierat scenario")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Poll-intervall för övervakning")
    
    args = parser.parse_args()
    
    # Skapa klient
    client = WazuhLoadGeneratorClient(args.server)
    
    try:
        if args.action == "health":
            result = client.health_check()
            print("🏥 API Health Check:")
            print(json.dumps(result, indent=2))
            
        elif args.action == "scenarios":
            result = client.get_scenarios()
            print("📋 Tillgängliga scenarier:")
            print(json.dumps(result, indent=2))
            
        elif args.action == "targets":
            result = client.get_targets()
            print("🎯 Tillgängliga mål:")
            print(json.dumps(result, indent=2))
            
        elif args.action == "start":
            result = client.start_test(
                target_host=args.target_host,
                target_port=args.target_port,
                protocol=args.protocol,
                log_type=args.log_type,
                count=args.count,
                delay=args.delay,
                duration=args.duration,
                scenario=args.scenario
            )
            print("✅ Test startat:")
            print(json.dumps(result, indent=2))
            
        elif args.action == "status":
            if not args.test_id:
                print("❌ --test-id krävs för status-åtgärd")
                return
            result = client.get_test_status(args.test_id)
            print("📊 Test Status:")
            print(json.dumps(result, indent=2))
            
        elif args.action == "result":
            if not args.test_id:
                print("❌ --test-id krävs för result-åtgärd")
                return
            result = client.get_test_result(args.test_id)
            print_test_result(result)
            
        elif args.action == "stop":
            if not args.test_id:
                print("❌ --test-id krävs för stop-åtgärd")
                return
            result = client.stop_test(args.test_id)
            print("⏹️ Test stoppat:")
            print(json.dumps(result, indent=2))
            
        elif args.action == "delete":
            if not args.test_id:
                print("❌ --test-id krävs för delete-åtgärd")
                return
            result = client.delete_test(args.test_id)
            print("🗑️ Test borttaget:")
            print(json.dumps(result, indent=2))
            
        elif args.action == "list":
            result = client.list_tests()
            print("📋 Alla tester:")
            print(json.dumps(result, indent=2))
            
        elif args.action == "run":
            result = client.run_and_monitor(
                target_host=args.target_host,
                target_port=args.target_port,
                protocol=args.protocol,
                log_type=args.log_type,
                count=args.count,
                delay=args.delay,
                duration=args.duration,
                scenario=args.scenario,
                poll_interval=args.poll_interval
            )
            print_test_result(result)
            
    except Exception as e:
        print(f"❌ Fel: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
