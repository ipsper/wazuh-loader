#!/usr/bin/env python3
"""
Wazuh Load Generator
====================
En Python-baserad last generator för Wazuh som skapar olika typer av säkerhetsloggar
för att testa och belasta Wazuh-systemet.
"""

import argparse
import json
import random
import socket
import sys
import time
from datetime import datetime, timedelta
from faker import Faker
from colorama import init, Fore, Style

# Initiera colorama för färgad output
init()

class WazuhLoadGenerator:
    def __init__(self, target_host="localhost", target_port=514, protocol="udp"):
        """
        Initierar Wazuh load generator
        
        Args:
            target_host (str): Målvärd för loggar
            target_port (int): Port för loggar
            protocol (str): Protokoll (udp/tcp)
        """
        self.target_host = target_host
        self.target_port = target_port
        self.protocol = protocol.lower()
        self.fake = Faker('sv_SE')
        self.socket = None
        self.setup_socket()
        
    def setup_socket(self):
        """Sätter upp socket-anslutning"""
        try:
            if self.protocol == "udp":
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.target_host, self.target_port))
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} Ansluten till {self.target_host}:{self.target_port} via {self.protocol.upper()}")
        except Exception as e:
            print(f"{Fore.RED}✗{Style.RESET_ALL} Kunde inte ansluta: {e}")
            sys.exit(1)
    
    def generate_ssh_logs(self, count=10):
        """Genererar SSH-relaterade loggar"""
        events = []
        for i in range(count):
            timestamp = datetime.now() - timedelta(seconds=random.randint(0, 3600))
            ip = self.fake.ipv4()
            user = self.fake.user_name()
            
            # Olika SSH-händelser
            event_types = [
                f"sshd[{random.randint(1000, 9999)}]: Failed password for {user} from {ip} port {random.randint(1024, 65535)} ssh2",
                f"sshd[{random.randint(1000, 9999)}]: Accepted password for {user} from {ip} port {random.randint(1024, 65535)} ssh2",
                f"sshd[{random.randint(1000, 9999)}]: Invalid user {user} from {ip}",
                f"sshd[{random.randint(1000, 9999)}]: Connection closed by {ip} [preauth]",
                f"sshd[{random.randint(1000, 9999)}]: PAM 2 more authentication failures; logname= uid=0 euid=0 tty=ssh ruser= rhost={ip}"
            ]
            
            event = random.choice(event_types)
            log_entry = f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
            events.append(log_entry)
        
        return events
    
    def generate_web_logs(self, count=10):
        """Genererar web server loggar (Apache/Nginx)"""
        events = []
        for i in range(count):
            timestamp = datetime.now() - timedelta(seconds=random.randint(0, 3600))
            ip = self.fake.ipv4()
            user_agent = self.fake.user_agent()
            
            # Olika HTTP-statuskoder
            status_codes = [200, 200, 200, 404, 403, 500, 301, 302]
            status = random.choice(status_codes)
            
            # Olika HTTP-metoder
            methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
            method = random.choice(methods)
            
            # Olika URL:er
            urls = [
                "/index.html",
                "/api/users",
                "/admin/login",
                "/wp-admin/",
                "/phpmyadmin/",
                "/config.php",
                "/.env",
                "/robots.txt"
            ]
            url = random.choice(urls)
            
            log_entry = f'{ip} - - [{timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")}] "{method} {url} HTTP/1.1" {status} {random.randint(100, 5000)} "{user_agent}"'
            events.append(log_entry)
        
        return events
    
    def generate_firewall_logs(self, count=10):
        """Genererar brandväggsloggar"""
        events = []
        for i in range(count):
            timestamp = datetime.now() - timedelta(seconds=random.randint(0, 3600))
            src_ip = self.fake.ipv4()
            dst_ip = self.fake.ipv4()
            
            # Olika brandväggshändelser
            event_types = [
                f"kernel: iptables: DROP IN=eth0 OUT= MAC=00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd SRC={src_ip} DST={dst_ip} LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12345 DF PROTO=TCP SPT=12345 DPT=22 WINDOW=5840 RES=0x00 SYN URGP=0",
                f"kernel: iptables: ACCEPT IN=eth0 OUT= MAC=00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd SRC={src_ip} DST={dst_ip} LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12345 DF PROTO=TCP SPT=12345 DPT=80 WINDOW=5840 RES=0x00 SYN URGP=0",
                f"kernel: iptables: LOG IN=eth0 OUT= MAC=00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd SRC={src_ip} DST={dst_ip} LEN=60 TOS=0x00 PREC=0x00 TTL=64 ID=12345 DF PROTO=UDP SPT=12345 DPT=53 WINDOW=5840 RES=0x00 SYN URGP=0"
            ]
            
            event = random.choice(event_types)
            log_entry = f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
            events.append(log_entry)
        
        return events
    
    def generate_system_logs(self, count=10):
        """Genererar systemloggar"""
        events = []
        for i in range(count):
            timestamp = datetime.now() - timedelta(seconds=random.randint(0, 3600))
            
            # Olika systemhändelser
            event_types = [
                f"systemd[1]: Started {self.fake.word()} service",
                f"systemd[1]: Stopped {self.fake.word()} service",
                f"kernel: CPU temperature above threshold, cpu clock throttled",
                f"kernel: Out of memory: Kill process {random.randint(1000, 9999)} ({self.fake.word()}) score {random.randint(100, 999)} or sacrifice child",
                f"systemd-logind[123]: New session {random.randint(1, 100)} of user {self.fake.user_name()}",
                f"systemd-logind[123]: Removed session {random.randint(1, 100)}",
                f"cron[12345]: (root) CMD ({self.fake.word()})",
                f"sudo: {self.fake.user_name()} : TTY=pts/0 ; PWD=/home/{self.fake.user_name()} ; USER=root ; COMMAND=/bin/{self.fake.word()}"
            ]
            
            event = random.choice(event_types)
            log_entry = f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
            events.append(log_entry)
        
        return events
    
    def generate_malware_logs(self, count=10):
        """Genererar malware-relaterade loggar"""
        events = []
        for i in range(count):
            timestamp = datetime.now() - timedelta(seconds=random.randint(0, 3600))
            ip = self.fake.ipv4()
            file_path = f"/home/{self.fake.user_name()}/{self.fake.file_name()}"
            
            # Olika malware-händelser
            event_types = [
                f"clamav: {file_path}: {random.choice(['Win.Trojan', 'Linux.Malware', 'Mac.Adware'])} FOUND",
                f"malware_detector: Suspicious activity detected from {ip}",
                f"antivirus: Quarantined file {file_path}",
                f"security_scan: Potential threat detected in {file_path}",
                f"firewall: Blocked connection from {ip} due to suspicious activity"
            ]
            
            event = random.choice(event_types)
            log_entry = f"{timestamp.strftime('%b %d %H:%M:%S')} {self.fake.hostname()} {event}"
            events.append(log_entry)
        
        return events
    
    def send_logs(self, logs, delay=0.1):
        """Skickar loggar till målservern"""
        sent_count = 0
        total_count = len(logs)
        
        print(f"{Fore.CYAN}Skickar {total_count} loggar...{Style.RESET_ALL}")
        
        for i, log in enumerate(logs, 1):
            try:
                if self.protocol == "udp":
                    self.socket.sendto(log.encode('utf-8'), (self.target_host, self.target_port))
                else:
                    self.socket.send(log.encode('utf-8') + b'\n')
                
                sent_count += 1
                
                # Visa progress
                if i % 10 == 0 or i == total_count:
                    progress = (i / total_count) * 100
                    print(f"{Fore.YELLOW}Progress: {progress:.1f}% ({i}/{total_count}){Style.RESET_ALL}")
                
                time.sleep(delay)
                
            except Exception as e:
                print(f"{Fore.RED}Fel vid skickning av log {i}: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} Skickade {sent_count} av {total_count} loggar")
        return sent_count
    
    def run_load_test(self, log_type="all", count=100, delay=0.1, duration=None):
        """
        Kör last test
        
        Args:
            log_type (str): Typ av loggar att generera
            count (int): Antal loggar per typ
            delay (float): Fördröjning mellan loggar
            duration (int): Testlängd i sekunder (None = oändligt)
        """
        print(f"{Fore.BLUE}=== Wazuh Load Generator ==={Style.RESET_ALL}")
        print(f"Loggtyp: {log_type}")
        print(f"Antal per typ: {count}")
        print(f"Fördröjning: {delay}s")
        print(f"Längd: {'Oändligt' if duration is None else f'{duration}s'}")
        print()
        
        start_time = time.time()
        total_sent = 0
        
        try:
            while True:
                if log_type == "all" or log_type == "ssh":
                    logs = self.generate_ssh_logs(count)
                    total_sent += self.send_logs(logs, delay)
                
                if log_type == "all" or log_type == "web":
                    logs = self.generate_web_logs(count)
                    total_sent += self.send_logs(logs, delay)
                
                if log_type == "all" or log_type == "firewall":
                    logs = self.generate_firewall_logs(count)
                    total_sent += self.send_logs(logs, delay)
                
                if log_type == "all" or log_type == "system":
                    logs = self.generate_system_logs(count)
                    total_sent += self.send_logs(logs, delay)
                
                if log_type == "all" or log_type == "malware":
                    logs = self.generate_malware_logs(count)
                    total_sent += self.send_logs(logs, delay)
                
                # Kontrollera om vi ska stoppa
                if duration and (time.time() - start_time) >= duration:
                    break
                    
                print(f"{Fore.GREEN}--- Cykel slutförd ---{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Avbruten av användaren{Style.RESET_ALL}")
        
        elapsed_time = time.time() - start_time
        print(f"\n{Fore.BLUE}=== Testresultat ==={Style.RESET_ALL}")
        print(f"Totalt skickade loggar: {total_sent}")
        print(f"Förfluten tid: {elapsed_time:.2f}s")
        print(f"Loggar per sekund: {total_sent/elapsed_time:.2f}")
        
        if self.socket:
            self.socket.close()

def main():
    """Huvudfunktion"""
    parser = argparse.ArgumentParser(description="Wazuh Load Generator")
    parser.add_argument("--host", default="localhost", help="Målvärd (default: localhost)")
    parser.add_argument("--port", type=int, default=514, help="Målport (default: 514)")
    parser.add_argument("--protocol", choices=["udp", "tcp"], default="udp", help="Protokoll (default: udp)")
    parser.add_argument("--type", choices=["all", "ssh", "web", "firewall", "system", "malware"], 
                       default="all", help="Loggtyp (default: all)")
    parser.add_argument("--count", type=int, default=100, help="Antal loggar per typ (default: 100)")
    parser.add_argument("--delay", type=float, default=0.1, help="Fördröjning mellan loggar (default: 0.1s)")
    parser.add_argument("--duration", type=int, help="Testlängd i sekunder (default: oändligt)")
    
    args = parser.parse_args()
    
    try:
        generator = WazuhLoadGenerator(args.host, args.port, args.protocol)
        generator.run_load_test(args.type, args.count, args.delay, args.duration)
    except Exception as e:
        print(f"{Fore.RED}Fel: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
