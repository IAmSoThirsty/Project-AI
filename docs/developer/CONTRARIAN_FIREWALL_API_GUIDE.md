# Contrarian Firewall - API Integration Guide

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Ensure Project-AI is in PYTHONPATH
export PYTHONPATH=/path/to/Project-AI:$PYTHONPATH
```

### Start the Server

```bash
# From Project-AI root
cd /home/runner/work/Project-AI/Project-AI

# Start FastAPI server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The Contrarian Firewall Orchestrator will automatically start on server startup.

---

## Basic Usage

### 1. Start the Chaos Engine

```bash
curl -X POST "http://localhost:8000/api/firewall/chaos/start" \
  -H "Content-Type: application/json" \
  -d '{
    "base_decoy_count": 10,
    "swarm_multiplier": 3.0,
    "escalation_threshold": 3,
    "auto_tune_enabled": true,
    "feedback_learning": true
  }'
```

**Response:**
```json
{
  "status": "started",
  "message": "Chaos engine activated through orchestrator",
  "orchestrator_status": {
    "orchestrator": {
      "running": true,
      "mode": "adaptive",
      "stability": 0.5,
      "threat_score": 0.0,
      "active_crises": 0
    },
    "subsystems": {
      "swarm_defense": {...},
      "security_bridge": {...},
      "governance": 0,
      "agents": 6
    }
  },
  "timestamp": "2026-02-06T18:30:00Z"
}
```

### 2. Report a Security Violation

```bash
curl -X POST "http://localhost:8000/api/firewall/violation/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.100",
    "violation_type": "sql_injection",
    "details": {
      "endpoint": "/api/users",
      "payload": "admin'\''  OR '\''1'\''='\''1",
      "method": "POST"
    }
  }'
```

**Response:**
```json
{
  "attacker_ip": "192.168.1.100",
  "threat_level": "scout",
  "violation_count": 1,
  "cognitive_overload": 0.2,
  "active_decoys": 10,
  "swarm_active": false,
  "intent_id": "intent_1_1707246000",
  "governance_verdict": {
    "verdict": "deny",
    "votes": [
      {
        "pillar": "Galahad",
        "verdict": "deny",
        "reason": "Actor not ethically authorized"
      },
      {
        "pillar": "Cerberus",
        "verdict": "deny",
        "reason": "High-risk action blocked by default"
      }
    ]
  },
  "orchestration": {
    "mode": "adaptive",
    "stability": 0.5,
    "threat_score": 0.1,
    "auto_tuning_active": true
  }
}
```

### 3. Get Firewall Status

```bash
curl -X GET "http://localhost:8000/api/firewall/status"
```

**Response:**
```json
{
  "orchestrator": {
    "orchestrator": {
      "running": true,
      "mode": "adaptive",
      "stability": 0.5,
      "threat_score": 15.3,
      "active_crises": 0
    },
    "subsystems": {
      "swarm_defense": {
        "total_attackers_tracked": 5,
        "active_decoys": 30,
        "threat_distribution": {
          "scout": 2,
          "probe": 2,
          "attack": 1,
          "siege": 0,
          "swarm": 0
        },
        "swarm_active": false,
        "max_cognitive_overload": 3.5
      },
      "security_bridge": {
        "mode": "hybrid",
        "modules": {
          "threat_detection": {...},
          "code_morphing": {...},
          "defensive_compilation": {...},
          "policy_engine": {...}
        }
      }
    },
    "tracking": {
      "intents": 15,
      "telemetry_records": 120,
      "threat_intel_sources": 2,
      "agent_communications": 8
    }
  },
  "telemetry": {
    "time_window_minutes": 15,
    "records": 180,
    "avg_threat_score": 12.5,
    "avg_cognitive_overload": 2.8,
    "avg_violations": 3,
    "avg_stability": 0.52
  },
  "timestamp": "2026-02-06T18:45:00Z"
}
```

---

## Advanced Usage

### Intent Tracking

Track security intents for analysis:

```python
import requests

# Track an intent
response = requests.post("http://localhost:8000/api/firewall/intent/track", json={
    "intent_type": "file_access",
    "parameters": {
        "path": "/etc/passwd",
        "mode": "read"
    },
    "priority": 8
})

intent_id = response.json()["intent_id"]

# List all intents
intents = requests.get("http://localhost:8000/api/firewall/intent/list?limit=50")

# Get specific intent
intent_details = requests.get(f"http://localhost:8000/api/firewall/intent/{intent_id}")
```

### Decoy Management

Deploy and manage honeypot decoys:

```python
# Deploy additional decoys
requests.post("http://localhost:8000/api/firewall/decoy/deploy", json={
    "decoy_types": ["fake_admin_panel", "fake_database", "fake_ssh_server"],
    "count": 5,
    "believability_min": 0.8
})

# List active decoys
decoys = requests.get("http://localhost:8000/api/firewall/decoy/list?limit=100")

# Record decoy access (attacker took the bait)
requests.post(
    "http://localhost:8000/api/firewall/decoy/access/fake_admin_panel_abc123",
    params={"source_ip": "192.168.1.100"}
)
```

### Cognitive Overload Monitoring

Monitor cognitive warfare effectiveness:

```python
# Get aggregate overload status
overload_status = requests.get("http://localhost:8000/api/firewall/cognitive/overload")

# Get specific attacker overload
attacker_overload = requests.get(
    "http://localhost:8000/api/firewall/cognitive/overload/192.168.1.100"
)

print(f"Cognitive Overload: {attacker_overload.json()['cognitive_overload']:.2f}/10.0")
print(f"Threat Level: {attacker_overload.json()['threat_level']}")
print(f"Decoys Accessed: {attacker_overload.json()['decoys_accessed']}")
```

### Dynamic Tuning

Adjust chaos parameters during runtime:

```python
# Increase chaos for aggressive defense
requests.post("http://localhost:8000/api/firewall/chaos/tune", json={
    "base_decoy_count": 20,
    "swarm_multiplier": 5.0,
    "escalation_threshold": 2,
    "auto_tune_enabled": true,
    "feedback_learning": true
})

# Check new status
status = requests.get("http://localhost:8000/api/firewall/chaos/status")
print(f"New stability: {status.json()['orchestrator']['orchestrator']['stability']}")
```

### Adversary Profiling

Create and manage adversary profiles:

```python
# Create adversary profile
requests.post("http://localhost:8000/api/firewall/adversary/profile", json={
    "profile_id": "apt_group_1",
    "characteristics": {
        "sophistication": "high",
        "persistence": "extreme",
        "tools": ["metasploit", "cobalt_strike"],
        "tactics": ["spear_phishing", "lateral_movement"]
    },
    "rotation_schedule": "daily"
})

# List all profiles
profiles = requests.get("http://localhost:8000/api/firewall/adversary/profiles")

# Trigger rotation
requests.post("http://localhost:8000/api/firewall/adversary/rotate")
```

### Federated Threat Scoring

Get aggregated threat intelligence:

```python
# Get federated threat score
threat_score = requests.get("http://localhost:8000/api/firewall/threat/score")

print(f"Threat Score: {threat_score.json()['federated_threat_score']:.1f}/100")
print(f"Threat Level: {threat_score.json()['threat_level']}")

# Update score from external source
requests.post("http://localhost:8000/api/firewall/threat/score/update", 
    params={"source": "external_feed"},
    json=45.8
)
```

---

## Python SDK

### Installation

```python
# Add to your project
from src.app.security.contrarian_firewall_orchestrator import (
    get_orchestrator,
    OrchestratorConfig,
    FirewallMode,
)
```

### Basic SDK Usage

```python
import asyncio
from src.app.security.contrarian_firewall_orchestrator import get_orchestrator

async def main():
    # Get orchestrator instance
    orchestrator = get_orchestrator()
    
    # Start orchestrator
    await orchestrator.start()
    
    try:
        # Process violation
        result = orchestrator.process_violation(
            source_ip="192.168.1.100",
            violation_type="xss_attempt",
            details={
                "payload": "<script>alert('xss')</script>",
                "user_agent": "Mozilla/5.0..."
            }
        )
        
        print(f"Threat Level: {result['threat_level']}")
        print(f"Cognitive Overload: {result['cognitive_overload']}")
        print(f"Intent ID: {result['intent_id']}")
        
        # Get status
        status = orchestrator.get_comprehensive_status()
        print(f"Running: {status['orchestrator']['running']}")
        print(f"Stability: {status['orchestrator']['stability']:.2f}")
        
        # Get intent history
        intents = orchestrator.get_intent_history(limit=10)
        for intent in intents:
            print(f"- {intent['type']}: {intent['threat_score']:.2f}")
        
        # Get telemetry summary
        telemetry = orchestrator.get_telemetry_summary(minutes=60)
        print(f"Avg Threat: {telemetry['avg_threat_score']:.2f}")
        print(f"Avg Overload: {telemetry['avg_cognitive_overload']:.2f}")
        
    finally:
        # Stop orchestrator
        await orchestrator.stop()

# Run
asyncio.run(main())
```

### Custom Configuration

```python
from src.app.security.contrarian_firewall_orchestrator import (
    OrchestratorConfig,
    FirewallMode,
)

# Create custom config
config = OrchestratorConfig(
    mode=FirewallMode.AGGRESSIVE,
    stability_target=0.8,  # High chaos
    auto_tune_enabled=True,
    feedback_learning_rate=0.2,
    telemetry_polling_interval=2.0,  # More frequent
    threat_escalation_threshold=0.6,
    cognitive_overload_target=9.0,
    decoy_expansion_rate=5.0,
)

# Create orchestrator with config
orchestrator = get_orchestrator(config)
```

---

## Integration Examples

### Example 1: Web Application Firewall

```python
from fastapi import FastAPI, Request, HTTPException
from src.app.security.contrarian_firewall_orchestrator import get_orchestrator

app = FastAPI()
orchestrator = get_orchestrator()

@app.middleware("http")
async def firewall_middleware(request: Request, call_next):
    # Check for suspicious patterns
    suspicious = False
    violation_type = None
    
    if "' OR '" in str(request.url):
        suspicious = True
        violation_type = "sql_injection"
    elif "<script>" in str(request.url):
        suspicious = True
        violation_type = "xss_attempt"
    
    if suspicious:
        # Process through orchestrator
        result = orchestrator.process_violation(
            source_ip=request.client.host,
            violation_type=violation_type,
            details={
                "url": str(request.url),
                "method": request.method,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # Block if governance denies
        if result.get("governance_verdict", {}).get("verdict") == "deny":
            raise HTTPException(status_code=403, detail="Blocked by security policy")
    
    response = await call_next(request)
    return response
```

### Example 2: API Rate Limiting with Cognitive Overload

```python
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()
orchestrator = get_orchestrator()
request_counts = defaultdict(int)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    request_counts[client_ip] += 1
    
    # Check if exceeding rate limit
    if request_counts[client_ip] > 100:  # 100 requests
        # Report as violation
        result = orchestrator.process_violation(
            source_ip=client_ip,
            violation_type="rate_limit_exceeded",
            details={"request_count": request_counts[client_ip]}
        )
        
        # If cognitive overload high, they're confused - mission accomplished
        if result["cognitive_overload"] > 8.0:
            # Serve them random decoys
            decoys = orchestrator.swarm_defense.get_decoy_recommendations(client_ip)
            return JSONResponse({"error": "Rate limited", "try_these": decoys[:5]})
    
    response = await call_next(request)
    return response
```

### Example 3: Integration with Existing Security System

```python
class ExistingSecuritySystem:
    """Your existing security system"""
    
    def detect_threat(self, data):
        # Your existing threat detection
        return {"threat": True, "confidence": 0.85}

# Enhance with Contrarian Firewall
orchestrator = get_orchestrator()

def enhanced_threat_detection(source_ip, data):
    # Get existing system's opinion
    existing_result = existing_security.detect_threat(data)
    
    if existing_result["threat"]:
        # Feed to orchestrator for cognitive warfare
        contrarian_result = orchestrator.process_violation(
            source_ip=source_ip,
            violation_type="existing_system_detection",
            details={
                "confidence": existing_result["confidence"],
                "data": data
            }
        )
        
        # Combine results
        return {
            "block": contrarian_result["governance_verdict"]["verdict"] == "deny",
            "serve_decoys": contrarian_result["swarm_active"],
            "cognitive_overload": contrarian_result["cognitive_overload"],
            "recommended_decoys": orchestrator.swarm_defense.get_decoy_recommendations(source_ip)
        }
    
    return {"block": False}
```

---

## Testing

### Unit Tests

```python
import pytest
from src.app.security.contrarian_firewall_orchestrator import (
    ContrariaNFirewallOrchestrator,
    OrchestratorConfig,
    reset_orchestrator,
)

@pytest.fixture
def orchestrator():
    reset_orchestrator()  # Reset singleton
    config = OrchestratorConfig(
        auto_tune_enabled=False,  # Disable for predictable tests
        real_time_adaptation=False,
    )
    orch = ContrariaNFirewallOrchestrator(config)
    yield orch
    reset_orchestrator()

def test_violation_processing(orchestrator):
    result = orchestrator.process_violation(
        source_ip="test.ip.1.1",
        violation_type="test_violation",
        details={"test": True}
    )
    
    assert result["attacker_ip"] == "test.ip.1.1"
    assert result["threat_level"] == "scout"
    assert "intent_id" in result

def test_threat_escalation(orchestrator):
    # Simulate 25 violations (SWARM level)
    for i in range(25):
        result = orchestrator.process_violation(
            source_ip="aggressive.attacker",
            violation_type=f"violation_{i}",
            details={}
        )
    
    assert result["threat_level"] == "swarm"
    assert result["swarm_active"] == True
    assert result["cognitive_overload"] > 8.0
```

### Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_chaos_engine_lifecycle():
    # Start chaos engine
    response = client.post("/api/firewall/chaos/start")
    assert response.status_code == 200
    assert response.json()["status"] == "started"
    
    # Check status
    response = client.get("/api/firewall/chaos/status")
    assert response.status_code == 200
    assert response.json()["orchestrator"]["orchestrator"]["running"] == True
    
    # Stop chaos engine
    response = client.post("/api/firewall/chaos/stop")
    assert response.status_code == 200
    assert response.json()["status"] == "stopped"

def test_violation_detection():
    # Start engine
    client.post("/api/firewall/chaos/start")
    
    # Report violation
    response = client.post("/api/firewall/violation/detect", json={
        "source_ip": "test.ip",
        "violation_type": "test",
        "details": {}
    })
    
    assert response.status_code == 200
    assert "intent_id" in response.json()
    assert "governance_verdict" in response.json()
```

---

## Troubleshooting

### Issue: "Orchestrator not active"

**Solution**: Start the chaos engine first:
```bash
curl -X POST "http://localhost:8000/api/firewall/chaos/start"
```

### Issue: High latency on violation detection

**Solution**: Disable governance integration for faster processing:
```python
config = OrchestratorConfig(governance_integration=False)
```

### Issue: Memory usage growing

**Solution**: The orchestrator keeps telemetry history (last 1000 records). This is normal. For long-running deployments, use external storage.

### Issue: Auto-tuning not working

**Solution**: Check telemetry collection:
```python
telemetry = orchestrator.get_telemetry_summary(minutes=5)
print(f"Records: {telemetry['records']}")  # Should be > 0
```

---

## Performance Tips

1. **Disable governance for high-throughput**: Set `governance_integration=False` if processing >1000 req/s
2. **Adjust telemetry interval**: Increase to 10-15s for lower overhead
3. **Use async processing**: Always `await orchestrator.start()` to enable background tasks
4. **Cache decoy recommendations**: They don't change often for same attacker
5. **Batch violation reporting**: Group violations and process in batches

---

## API Reference

Full OpenAPI docs available at: `http://localhost:8000/docs`

Interactive API testing: `http://localhost:8000/redoc`

---

**Built with God-tier engineering standards.**
