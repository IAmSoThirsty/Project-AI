# Thirsty's Asymmetric Security Framework - Public Demo

**Try the framework with 5 live attack scenarios**

---

## Quick Start (5 Minutes)

### Option 1: Docker (Recommended)

```bash
docker-compose up
# Open http://localhost:5000
```

### Option 2: Local

```bash
pip install -r requirements.txt
python demo_server.py
# Open http://localhost:5000
```

---

## Attack Scenarios

### 1. Privilege Escalation Without MFA
**Attack:** User attempts to escalate to admin without multi-factor authentication  
**Expected:** BLOCKED by constitutional rule "privilege_escalation_approval"

### 2. Cross-Tenant Data Access
**Attack:** User from tenant_a tries to read data from tenant_b  
**Expected:** BLOCKED by constitutional rule "cross_tenant_authorization"

### 3. Trust Score Manipulation
**Attack:** Direct modification of trust score without justification  
**Expected:** BLOCKED by constitutional rule "modify_trust_score"

### 4. Clock Skew Exploitation
**Attack:** Manipulate system clock by 10 minutes to bypass temporal checks  
**Expected:** BLOCKED by temporal security analyzer (clock skew detected)

### 5. Combined Multi-Stage Attack
**Attack:** Clock skew + privilege escalation + cross-tenant access  
**Expected:** BLOCKED at first violation (clock skew)

---

## Features

- ✅ Interactive web UI
- ✅ Real-time validation results
- ✅ Complete audit trails
- ✅ JSON export
- ✅ Layer-by-layer processing visualization

---

## Architecture

```
Browser → demo_ui.html
            ↓
        Flask API (demo_server.py)
            ↓
        Security Enforcement Gateway
            ↓
        God Tier Asymmetric Security
            ↓
        Asymmetric Security Engine
```

---

## Demo Output Example

```json
{
  "scenario": "Privilege Escalation Without MFA",
  "allowed": false,
  "failure_reason": "Constitutional violation",
  "violations": ["privilege_escalation_approval"],
  "rfi_score": 0.25,
  "threat_level": "HIGH",
  "forensics": {
    "snapshot_id": "snap_20260208_060000",
    "audit_trail_id": "audit_trace_001"
  }
}
```

---

## Requirements

- Python 3.11+
- Flask
- 512 MB RAM
- Modern web browser

---

## Files

- `README.md` - This file
- `demo_server.py` - Flask API server
- `demo_ui.html` - Interactive web interface
- `demo_scenarios.py` - Attack scenario definitions
- `docker-compose.yml` - Docker deployment
- `Dockerfile` - Container definition

---

**Try it now: `docker-compose up` and visit http://localhost:5000**
