# Wazuh Load Generator - Exempel

Detta dokument innehåller praktiska exempel på hur man använder Wazuh Load Generator för olika testscenarier.

## Snabba exempel

### 1. Grundläggande test
```bash
# Kör med standardinställningar
python wazuh_loader.py
```

### 2. Testa endast SSH-loggar
```bash
python wazuh_loader.py --type ssh --count 100 --delay 0.5
```

### 3. Hög belastningstest
```bash
python wazuh_loader.py --count 1000 --delay 0.01 --duration 300
```

### 4. Testa mot specifik server
```bash
python wazuh_loader.py --host 192.168.1.100 --port 514 --protocol udp
```

## Avancerade scenarier

### 1. Simulera attack
```bash
# Generera många misslyckade SSH-försök
python wazuh_loader.py --type ssh --count 5000 --delay 0.01 --duration 600
```

### 2. Web server stress test
```bash
# Simulera hög trafik mot webbservern
python wazuh_loader.py --type web --count 2000 --delay 0.05 --duration 1800
```

### 3. Brandväggstest
```bash
# Testa brandväggsloggar
python wazuh_loader.py --type firewall --count 1000 --delay 0.1
```

### 4. Komplett systemtest
```bash
# Testa alla loggtyper med hög belastning
python wazuh_loader.py --type all --count 500 --delay 0.02 --duration 3600
```

## Test Runner exempel

### 1. Lista tillgängliga scenarier
```bash
python run_tests.py --list
```

### 2. Kör lätt last
```bash
python run_tests.py --scenario light_load --target local
```

### 3. Kör medium last med SSH-loggar
```bash
python run_tests.py --scenario medium_load --target local --type ssh
```

### 4. Kör burst test
```bash
python run_tests.py --scenario burst_load --target local --type all
```

### 5. Interaktivt läge
```bash
python run_tests.py --interactive
```

## Produktionsscenarier

### 1. Daglig övervakningstest
```bash
# Kör lätt test varje dag för att verifiera systemet
python run_tests.py --scenario light_load --target production --type all
```

### 2. Veckovis prestandatest
```bash
# Kör medium last varje vecka
python run_tests.py --scenario medium_load --target production --type all
```

### 3. Månadsvis stress-test
```bash
# Kör tung last en gång i månaden
python run_tests.py --scenario heavy_load --target production --type all
```

## Felsökningsexempel

### 1. Testa anslutning
```bash
# Testa med få loggar och lång fördröjning
python wazuh_loader.py --count 10 --delay 2.0
```

### 2. Debug-läge
```bash
# Kör med detaljerad output
python wazuh_loader.py --count 5 --delay 1.0 --type ssh
```

### 3. Testa TCP-anslutning
```bash
# Testa TCP istället för UDP
python wazuh_loader.py --protocol tcp --port 601 --count 10
```

## Automatisering

### 1. Cron-jobb för daglig testning
```bash
# Lägg till i crontab
0 2 * * * cd /path/to/wazuh-loader && python run_tests.py --scenario light_load --target local --type all
```

### 2. Skript för automatisk testning
```bash
#!/bin/bash
# test_wazuh.sh

echo "Starting Wazuh load test..."
python run_tests.py --scenario medium_load --target local --type all

if [ $? -eq 0 ]; then
    echo "Test completed successfully"
else
    echo "Test failed"
    exit 1
fi
```

### 3. CI/CD integration
```yaml
# .github/workflows/wazuh-test.yml
name: Wazuh Load Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run load test
      run: python run_tests.py --scenario light_load --target local --type ssh
```

## Prestandaoptimering

### 1. Hög genomströmning
```bash
# Minska fördröjning för hög genomströmning
python wazuh_loader.py --count 10000 --delay 0.001 --duration 300
```

### 2. Jämn belastning
```bash
# Jämn belastning över tid
python wazuh_loader.py --count 1000 --delay 0.1 --duration 3600
```

### 3. Burst-belastning
```bash
# Kort men intensiv belastning
python wazuh_loader.py --count 5000 --delay 0.01 --duration 60
```

## Övervakning och loggning

### 1. Spara testresultat
```bash
# Spara output till fil
python wazuh_loader.py --count 1000 --delay 0.1 2>&1 | tee test_results.log
```

### 2. Mät prestanda
```bash
# Mät tid och loggar per sekund
time python wazuh_loader.py --count 10000 --delay 0.01
```

### 3. Kontinuerlig övervakning
```bash
# Kör test och övervaka resultat
while true; do
    echo "$(date): Starting load test..."
    python run_tests.py --scenario light_load --target local --type all
    sleep 3600  # Vänta 1 timme
done
```

## Säkerhetsexempel

### 1. Testa säkerhetsregler
```bash
# Simulera olika säkerhetshändelser
python wazuh_loader.py --type malware --count 500 --delay 0.2
```

### 2. Testa brandväggsregler
```bash
# Testa brandväggsloggar
python wazuh_loader.py --type firewall --count 1000 --delay 0.1
```

### 3. Testa SSH-säkerhet
```bash
# Simulera SSH-attacker
python wazuh_loader.py --type ssh --count 2000 --delay 0.05
```

## Tips och tricks

1. **Börja alltid med lätt last** för att verifiera att systemet fungerar
2. **Övervaka Wazuh-dashboard** under testerna
3. **Justera fördröjning** baserat på systemets kapacitet
4. **Använd fördefinierade scenarier** för konsistenta tester
5. **Logga resultaten** för att spåra prestanda över tid
6. **Testa olika loggtyper** för att säkerställa komplett täckning
7. **Använd interaktivt läge** för enkla tester
8. **Kontrollera nätverksanslutning** innan du kör tester
