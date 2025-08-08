#!/usr/bin/env python3
"""
Wazuh Load Generator - FastAPI Server
=====================================
RESTful API för Wazuh load generator som kan anropas från andra hosts
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from wazuh_loader import WazuhLoadGenerator

# Konfigurera logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Skapa FastAPI-app
app = FastAPI(
    title="Wazuh Load Generator API",
    description="RESTful API för att generera last mot Wazuh-system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Lägg till CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globala variabler för att hålla koll på pågående tester
active_tests: Dict[str, Dict] = {}
test_counter = 0

# Thread pool för att köra tester i bakgrunden
executor = ThreadPoolExecutor(max_workers=10)

# Pydantic modeller för API
class LoadTestRequest(BaseModel):
    """Modell för load test requests"""
    target_host: str = Field(default="localhost", description="Målvärd för loggar")
    target_port: int = Field(default=514, description="Målport för loggar")
    protocol: str = Field(default="udp", description="Protokoll (udp/tcp)")
    log_type: str = Field(default="all", description="Loggtyp (all/ssh/web/firewall/system/malware)")
    count: int = Field(default=100, description="Antal loggar per typ")
    delay: float = Field(default=0.1, description="Fördröjning mellan loggar i sekunder")
    duration: Optional[int] = Field(default=None, description="Testlängd i sekunder (None = oändligt)")
    scenario: Optional[str] = Field(default=None, description="Fördefinierat scenario att använda")

class LoadTestResponse(BaseModel):
    """Modell för load test responses"""
    test_id: str
    status: str
    message: str
    start_time: Optional[str] = None
    estimated_duration: Optional[int] = None

class TestStatus(BaseModel):
    """Modell för test status"""
    test_id: str
    status: str
    progress: Optional[float] = None
    logs_sent: Optional[int] = None
    elapsed_time: Optional[float] = None
    logs_per_second: Optional[float] = None
    error_message: Optional[str] = None

class TestResult(BaseModel):
    """Modell för test resultat"""
    test_id: str
    status: str
    total_logs_sent: int
    total_time: float
    logs_per_second: float
    start_time: str
    end_time: str
    configuration: Dict[str, Any]

def load_config():
    """Laddar konfiguration från config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("config.json hittades inte, använder standardkonfiguration")
        return {
            "test_scenarios": {},
            "targets": {
                "local": {"host": "localhost", "port": 514, "protocol": "udp"}
            }
        }
    except json.JSONDecodeError as e:
        logger.error(f"Fel vid läsning av config.json: {e}")
        raise HTTPException(status_code=500, detail="Konfigurationsfel")

def run_load_test_sync(test_id: str, request: LoadTestRequest):
    """Kör load test synkront (anropas från thread pool)"""
    try:
        active_tests[test_id]["status"] = "running"
        active_tests[test_id]["start_time"] = datetime.now().isoformat()
        
        # Skapa generator
        generator = WazuhLoadGenerator(
            request.target_host,
            request.target_port,
            request.protocol
        )
        
        # Spara konfiguration
        active_tests[test_id]["configuration"] = request.dict()
        
        # Kör testet
        start_time = time.time()
        total_sent = 0
        
        # Anpassad send_logs metod för att uppdatera progress
        def send_logs_with_progress(logs, delay=0.1):
            nonlocal total_sent
            sent_count = 0
            total_count = len(logs)
            
            for i, log in enumerate(logs, 1):
                try:
                    if request.protocol == "udp":
                        generator.socket.sendto(log.encode('utf-8'), (request.target_host, request.target_port))
                    else:
                        generator.socket.send(log.encode('utf-8') + b'\n')
                    
                    sent_count += 1
                    total_sent += 1
                    
                    # Uppdatera progress var 10:e logg
                    if i % 10 == 0 or i == total_count:
                        active_tests[test_id]["logs_sent"] = total_sent
                        active_tests[test_id]["elapsed_time"] = time.time() - start_time
                        if active_tests[test_id]["elapsed_time"] > 0:
                            active_tests[test_id]["logs_per_second"] = total_sent / active_tests[test_id]["elapsed_time"]
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Fel vid skickning av log {i}: {e}")
                    active_tests[test_id]["error_message"] = str(e)
                    break
            
            return sent_count
        
        # Ersätt send_logs metod temporärt
        original_send_logs = generator.send_logs
        generator.send_logs = send_logs_with_progress
        
        # Kör testet baserat på scenario eller direkt parametrar
        if request.scenario:
            config = load_config()
            if request.scenario in config.get("test_scenarios", {}):
                scenario = config["test_scenarios"][request.scenario]
                generator.run_load_test(
                    log_type=request.log_type,
                    count=scenario["count"],
                    delay=scenario["delay"],
                    duration=scenario["duration"]
                )
            else:
                raise ValueError(f"Scenario '{request.scenario}' finns inte")
        else:
            generator.run_load_test(
                log_type=request.log_type,
                count=request.count,
                delay=request.delay,
                duration=request.duration
            )
        
        # Återställ original metod
        generator.send_logs = original_send_logs
        
        # Uppdatera final status
        end_time = time.time()
        total_time = end_time - start_time
        
        active_tests[test_id].update({
            "status": "completed",
            "total_logs_sent": total_sent,
            "total_time": total_time,
            "logs_per_second": total_sent / total_time if total_time > 0 else 0,
            "end_time": datetime.now().isoformat()
        })
        
        if generator.socket:
            generator.socket.close()
            
    except Exception as e:
        logger.error(f"Fel vid körning av test {test_id}: {e}")
        active_tests[test_id].update({
            "status": "failed",
            "error_message": str(e),
            "end_time": datetime.now().isoformat()
        })

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Wazuh Load Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "start_test": "POST /api/v1/test/start",
            "get_status": "GET /api/v1/test/{test_id}",
            "list_tests": "GET /api/v1/test",
            "stop_test": "POST /api/v1/test/{test_id}/stop",
            "get_scenarios": "GET /api/v1/scenarios",
            "get_targets": "GET /api/v1/targets"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_tests": len([t for t in active_tests.values() if t["status"] == "running"])
    }

@app.get("/api/v1/scenarios")
async def get_scenarios():
    """Hämta tillgängliga testscenarier"""
    config = load_config()
    return {
        "scenarios": config.get("test_scenarios", {}),
        "count": len(config.get("test_scenarios", {}))
    }

@app.get("/api/v1/targets")
async def get_targets():
    """Hämta tillgängliga mål"""
    config = load_config()
    return {
        "targets": config.get("targets", {}),
        "count": len(config.get("targets", {}))
    }

@app.post("/api/v1/test/start", response_model=LoadTestResponse)
async def start_load_test(request: LoadTestRequest, background_tasks: BackgroundTasks):
    """Starta ett nytt load test"""
    global test_counter
    test_counter += 1
    test_id = f"test_{test_counter}_{int(time.time())}"
    
    # Validera request
    if request.scenario:
        config = load_config()
        if request.scenario not in config.get("test_scenarios", {}):
            raise HTTPException(status_code=400, detail=f"Scenario '{request.scenario}' finns inte")
    
    if request.log_type not in ["all", "ssh", "web", "firewall", "system", "malware"]:
        raise HTTPException(status_code=400, detail=f"Ogiltig loggtyp: {request.log_type}")
    
    if request.protocol not in ["udp", "tcp"]:
        raise HTTPException(status_code=400, detail=f"Ogiltigt protokoll: {request.protocol}")
    
    # Initiera test status
    active_tests[test_id] = {
        "status": "starting",
        "start_time": None,
        "logs_sent": 0,
        "elapsed_time": 0,
        "logs_per_second": 0,
        "configuration": request.dict()
    }
    
    # Starta testet i bakgrunden
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, run_load_test_sync, test_id, request)
    
    return LoadTestResponse(
        test_id=test_id,
        status="started",
        message=f"Load test startat med ID: {test_id}",
        start_time=datetime.now().isoformat(),
        estimated_duration=request.duration
    )

@app.get("/api/v1/test/{test_id}", response_model=TestStatus)
async def get_test_status(test_id: str):
    """Hämta status för ett specifikt test"""
    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail=f"Test {test_id} hittades inte")
    
    test_info = active_tests[test_id]
    
    # Beräkna progress för pågående tester
    progress = None
    if test_info["status"] == "running" and test_info["elapsed_time"] > 0:
        if test_info["configuration"].get("duration"):
            progress = min(100.0, (test_info["elapsed_time"] / test_info["configuration"]["duration"]) * 100)
    
    return TestStatus(
        test_id=test_id,
        status=test_info["status"],
        progress=progress,
        logs_sent=test_info.get("logs_sent", 0),
        elapsed_time=test_info.get("elapsed_time", 0),
        logs_per_second=test_info.get("logs_per_second", 0),
        error_message=test_info.get("error_message")
    )

@app.get("/api/v1/test")
async def list_tests():
    """Lista alla tester"""
    tests = []
    for test_id, test_info in active_tests.items():
        tests.append({
            "test_id": test_id,
            "status": test_info["status"],
            "start_time": test_info.get("start_time"),
            "logs_sent": test_info.get("logs_sent", 0),
            "elapsed_time": test_info.get("elapsed_time", 0),
            "configuration": test_info.get("configuration", {})
        })
    
    return {
        "tests": tests,
        "total": len(tests),
        "running": len([t for t in tests if t["status"] == "running"]),
        "completed": len([t for t in tests if t["status"] == "completed"]),
        "failed": len([t for t in tests if t["status"] == "failed"])
    }

@app.post("/api/v1/test/{test_id}/stop")
async def stop_test(test_id: str):
    """Stoppa ett pågående test"""
    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail=f"Test {test_id} hittades inte")
    
    test_info = active_tests[test_id]
    if test_info["status"] not in ["running", "starting"]:
        raise HTTPException(status_code=400, detail=f"Test {test_id} är inte aktivt")
    
    # Markera testet som stoppat
    test_info["status"] = "stopped"
    test_info["end_time"] = datetime.now().isoformat()
    
    return {
        "test_id": test_id,
        "status": "stopped",
        "message": f"Test {test_id} har stoppats"
    }

@app.delete("/api/v1/test/{test_id}")
async def delete_test(test_id: str):
    """Ta bort ett test från historiken"""
    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail=f"Test {test_id} hittades inte")
    
    del active_tests[test_id]
    
    return {
        "test_id": test_id,
        "status": "deleted",
        "message": f"Test {test_id} har tagits bort"
    }

@app.get("/api/v1/test/{test_id}/result", response_model=TestResult)
async def get_test_result(test_id: str):
    """Hämta resultat för ett slutfört test"""
    if test_id not in active_tests:
        raise HTTPException(status_code=404, detail=f"Test {test_id} hittades inte")
    
    test_info = active_tests[test_id]
    if test_info["status"] not in ["completed", "failed", "stopped"]:
        raise HTTPException(status_code=400, detail=f"Test {test_id} är inte slutfört")
    
    return TestResult(
        test_id=test_id,
        status=test_info["status"],
        total_logs_sent=test_info.get("total_logs_sent", 0),
        total_time=test_info.get("total_time", 0),
        logs_per_second=test_info.get("logs_per_second", 0),
        start_time=test_info.get("start_time", ""),
        end_time=test_info.get("end_time", ""),
        configuration=test_info.get("configuration", {})
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Wazuh Load Generator API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Aktivera auto-reload för utveckling")
    
    args = parser.parse_args()
    
    print(f"🚀 Startar Wazuh Load Generator API på {args.host}:{args.port}")
    print(f"📖 API dokumentation: http://{args.host}:{args.port}/docs")
    print(f"🔍 Health check: http://{args.host}:{args.port}/health")
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )
