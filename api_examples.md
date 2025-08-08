# Wazuh Load Generator API - Exempel

Detta dokument visar hur man använder Wazuh Load Generator API från olika klienter.

## Snabba exempel

### 1. Starta API-servern

```bash
# Lokalt
python api_server.py

# Med Docker
docker-compose up -d

# Med specifika inställningar
python api_server.py --host 0.0.0.0 --port 8000
```

### 2. Använd Python-klienten

```python
from api_client import WazuhLoadGeneratorClient

# Skapa klient
client = WazuhLoadGeneratorClient("http://localhost:8000")

# Kontrollera hälsa
health = client.health_check()
print(health)

# Starta test
result = client.run_and_monitor(
    target_host="192.168.1.100",
    target_port=514,
    log_type="ssh",
    count=1000,
    delay=0.1
)
print(result)
```

### 3. Använd kommandorads-klienten

```bash
# Kontrollera API-hälsa
python api_client.py --action health

# Lista tillgängliga scenarier
python api_client.py --action scenarios

# Starta test
python api_client.py --action run --target-host 192.168.1.100 --log-type ssh --count 1000

# Övervaka test
python api_client.py --action status --test-id test_1_1234567890
```

## REST API-exempel

### 1. Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

**Svar:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "active_tests": 2
}
```

### 2. Hämta scenarier

```bash
curl -X GET "http://localhost:8000/api/v1/scenarios"
```

**Svar:**
```json
{
  "scenarios": {
    "light_load": {
      "description": "Lätt last för utveckling och testning",
      "count": 50,
      "delay": 0.5,
      "duration": 300
    },
    "medium_load": {
      "description": "Medium last för prestandatestning",
      "count": 200,
      "delay": 0.2,
      "duration": 600
    }
  },
  "count": 2
}
```

### 3. Starta test

```bash
curl -X POST "http://localhost:8000/api/v1/test/start" \
  -H "Content-Type: application/json" \
  -d '{
    "target_host": "192.168.1.100",
    "target_port": 514,
    "protocol": "udp",
    "log_type": "ssh",
    "count": 1000,
    "delay": 0.1,
    "duration": 300
  }'
```

**Svar:**
```json
{
  "test_id": "test_1_1234567890",
  "status": "started",
  "message": "Load test startat med ID: test_1_1234567890",
  "start_time": "2024-01-15T10:30:00",
  "estimated_duration": 300
}
```

### 4. Övervaka test

```bash
curl -X GET "http://localhost:8000/api/v1/test/test_1_1234567890"
```

**Svar:**
```json
{
  "test_id": "test_1_1234567890",
  "status": "running",
  "progress": 45.2,
  "logs_sent": 452,
  "elapsed_time": 135.6,
  "logs_per_second": 3.33,
  "error_message": null
}
```

### 5. Hämta resultat

```bash
curl -X GET "http://localhost:8000/api/v1/test/test_1_1234567890/result"
```

**Svar:**
```json
{
  "test_id": "test_1_1234567890",
  "status": "completed",
  "total_logs_sent": 1000,
  "total_time": 300.5,
  "logs_per_second": 3.33,
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T10:35:00",
  "configuration": {
    "target_host": "192.168.1.100",
    "target_port": 514,
    "protocol": "udp",
    "log_type": "ssh",
    "count": 1000,
    "delay": 0.1,
    "duration": 300
  }
}
```

## JavaScript/Node.js exempel

### 1. Grundläggande klient

```javascript
const axios = require('axios');

class WazuhLoadGeneratorClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async healthCheck() {
        const response = await this.client.get('/health');
        return response.data;
    }

    async startTest(config) {
        const response = await this.client.post('/api/v1/test/start', config);
        return response.data;
    }

    async getTestStatus(testId) {
        const response = await this.client.get(`/api/v1/test/${testId}`);
        return response.data;
    }

    async waitForCompletion(testId, pollInterval = 2000) {
        while (true) {
            const status = await this.getTestStatus(testId);
            
            if (status.status === 'completed' || status.status === 'failed') {
                return status;
            }
            
            console.log(`Progress: ${status.progress || 0}%`);
            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }
    }
}

// Användning
async function runTest() {
    const client = new WazuhLoadGeneratorClient();
    
    // Starta test
    const result = await client.startTest({
        target_host: '192.168.1.100',
        target_port: 514,
        log_type: 'ssh',
        count: 1000,
        delay: 0.1
    });
    
    console.log(`Test startat: ${result.test_id}`);
    
    // Vänta på slutförande
    const finalResult = await client.waitForCompletion(result.test_id);
    console.log('Test slutfört:', finalResult);
}

runTest().catch(console.error);
```

## PowerShell exempel

### 1. PowerShell-klient

```powershell
class WazuhLoadGeneratorClient {
    [string]$BaseUrl
    
    WazuhLoadGeneratorClient([string]$baseUrl = "http://localhost:8000") {
        $this.BaseUrl = $baseUrl
    }
    
    [object] HealthCheck() {
        $response = Invoke-RestMethod -Uri "$($this.BaseUrl)/health" -Method Get
        return $response
    }
    
    [object] StartTest([hashtable]$config) {
        $body = $config | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$($this.BaseUrl)/api/v1/test/start" -Method Post -Body $body -ContentType "application/json"
        return $response
    }
    
    [object] GetTestStatus([string]$testId) {
        $response = Invoke-RestMethod -Uri "$($this.BaseUrl)/api/v1/test/$testId" -Method Get
        return $response
    }
    
    [object] WaitForCompletion([string]$testId, [int]$pollInterval = 2000) {
        while ($true) {
            $status = $this.GetTestStatus($testId)
            
            if ($status.status -eq "completed" -or $status.status -eq "failed") {
                return $status
            }
            
            Write-Host "Progress: $($status.progress)%"
            Start-Sleep -Milliseconds $pollInterval
        }
    }
}

# Användning
$client = [WazuhLoadGeneratorClient]::new()

# Starta test
$result = $client.StartTest(@{
    target_host = "192.168.1.100"
    target_port = 514
    log_type = "ssh"
    count = 1000
    delay = 0.1
})

Write-Host "Test startat: $($result.test_id)"

# Vänta på slutförande
$finalResult = $client.WaitForCompletion($result.test_id)
Write-Host "Test slutfört: $($finalResult | ConvertTo-Json)"
```

## Bash/Shell exempel

### 1. Bash-klient

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# Health check
health_check() {
    curl -s "$BASE_URL/health" | jq .
}

# Starta test
start_test() {
    local config="$1"
    curl -s -X POST "$BASE_URL/api/v1/test/start" \
        -H "Content-Type: application/json" \
        -d "$config" | jq .
}

# Hämta test status
get_test_status() {
    local test_id="$1"
    curl -s "$BASE_URL/api/v1/test/$test_id" | jq .
}

# Vänta på slutförande
wait_for_completion() {
    local test_id="$1"
    local poll_interval="${2:-2}"
    
    while true; do
        local status=$(get_test_status "$test_id")
        local test_status=$(echo "$status" | jq -r '.status')
        
        if [[ "$test_status" == "completed" || "$test_status" == "failed" ]]; then
            echo "$status"
            return 0
        fi
        
        local progress=$(echo "$status" | jq -r '.progress // 0')
        echo "Progress: ${progress}%" >&2
        
        sleep "$poll_interval"
    done
}

# Exempel användning
echo "Kontrollerar API-hälsa..."
health_check

echo "Startar test..."
config='{
    "target_host": "192.168.1.100",
    "target_port": 514,
    "log_type": "ssh",
    "count": 1000,
    "delay": 0.1
}'

result=$(start_test "$config")
test_id=$(echo "$result" | jq -r '.test_id')
echo "Test startat: $test_id"

echo "Väntar på slutförande..."
final_result=$(wait_for_completion "$test_id")
echo "Test slutfört:"
echo "$final_result" | jq .
```

## Docker-exempel

### 1. Kör med Docker

```bash
# Bygg och starta
docker-compose up -d

# Kontrollera status
docker-compose ps

# Visa loggar
docker-compose logs -f wazuh-loader-api

# Stoppa
docker-compose down
```

### 2. Anropa från annan container

```yaml
# docker-compose.yml
version: '3.8'

services:
  wazuh-loader-api:
    build: .
    ports:
      - "8000:8000"
    networks:
      - test-network

  test-client:
    image: python:3.11-slim
    volumes:
      - ./api_client.py:/app/api_client.py
    working_dir: /app
    command: >
      sh -c "pip install requests &&
              python api_client.py --action run --target-host wazuh-server --log-type ssh --count 100"
    depends_on:
      - wazuh-loader-api
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
```

## CI/CD exempel

### 1. GitHub Actions

```yaml
name: Wazuh Load Test
on: [push, pull_request]

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Start API server
      run: |
        python api_server.py --host 0.0.0.0 --port 8000 &
        sleep 5
    
    - name: Run load test
      run: |
        python api_client.py --action run --target-host localhost --log-type ssh --count 100
    
    - name: Check results
      run: |
        python api_client.py --action list
```

### 2. Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Start API') {
            steps {
                sh 'python api_server.py --host 0.0.0.0 --port 8000 &'
                sh 'sleep 5'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'python api_client.py --action run --target-host localhost --log-type ssh --count 1000'
            }
        }
        
        stage('Cleanup') {
            steps {
                sh 'pkill -f api_server.py'
            }
        }
    }
}
```

## Felsökning

### 1. Vanliga problem

```bash
# Kontrollera att API-servern körs
curl http://localhost:8000/health

# Kontrollera loggar
docker-compose logs wazuh-loader-api

# Testa anslutning
python api_client.py --action health
```

### 2. Debug-läge

```bash
# Starta API med debug
python api_server.py --reload

# Testa med curl
curl -v http://localhost:8000/api/v1/scenarios
```

### 3. Prestanda-optimering

```bash
# Öka antal workers
docker-compose up --scale wazuh-loader-api=3

# Använd load balancer
# Se nginx.conf för exempel
```

## Säkerhet

### 1. Autentisering (framtida funktion)

```python
# Exempel på framtida autentisering
headers = {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
}

response = requests.post(
    'http://localhost:8000/api/v1/test/start',
    json=config,
    headers=headers
)
```

### 2. HTTPS

```bash
# Med SSL-certifikat
python api_server.py --ssl-cert cert.pem --ssl-key key.pem
```
