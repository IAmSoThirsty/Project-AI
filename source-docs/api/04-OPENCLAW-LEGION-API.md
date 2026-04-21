---
title: OpenClaw Legion API
category: api
layer: api-layer
audience: [integrator, expert]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md, 02-FASTAPI-MAIN-ROUTES.md]
time_estimate: 20min
last_updated: 2025-06-09
version: 1.0.0
---

# OpenClaw Legion API

## Purpose

The Legion API enables **OpenClaw integration** - allowing external AI agents to access Project-AI capabilities through a governed interface. All requests flow through Triumvirate oversight.

**File**: `integrations/openclaw/api_endpoints.py` (185 lines)  
**Prefix**: `/openclaw`  
**Integration**: Legion agent (multi-personality AI system)  
**Governance**: Full Triumvirate + TARL enforcement

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   OPENCLAW (External Agent)                  │
│  • Discord bot, Telegram bot, Slack bot, etc.                │
│  • Sends messages to Legion API                              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼ POST /openclaw/message
┌──────────────────────────────────────────────────────────────┐
│                    Legion API (FastAPI)                      │
│  • Message processing                                         │
│  • Capability registry                                        │
│  • Health checks                                              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     Legion Agent                             │
│  1. Security validation (Cerberus)                           │
│  2. Intent parsing                                            │
│  3. Context retrieval (EED memory)                            │
│  4. Triumvirate governance                                    │
│  5. Capability execution                                      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              Project-AI Core Systems                         │
│  • AI Systems (FourLaws, Persona, Memory)                    │
│  • Intelligence Engine (OpenAI)                              │
│  • Image Generator                                            │
│  • User Manager                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Endpoints

### 1. Process Message - `POST /openclaw/message`

**Purpose**: Main message handler for OpenClaw agents

**Request**:
```bash
curl -X POST http://localhost:8001/openclaw/message \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Analyze current security threats",
    "user_id": "discord_user_12345",
    "platform": "discord",
    "metadata": {
      "channel": "security-ops",
      "guild": "Project-AI-Community"
    }
  }'
```

**Request Schema**:
```python
class OpenClawMessage(BaseModel):
    content: str  # Message content
    user_id: str  # Platform user ID
    platform: str = "openclaw"  # Source platform
    metadata: dict = {}  # Additional context
```

**Response**:
```json
{
  "response": "I've analyzed current threat landscape. Key findings:\n1. No active threats detected\n2. Firewall status: operational\n3. Last scan: 2 minutes ago",
  "agent_id": "legion_abc123",
  "status": "success",
  "governance": null
}
```

**Error Response**:
```json
{
  "detail": "Error processing message: Intent parsing failed"
}
```

**Processing Pipeline**:
1. **Security Validation** - Cerberus checks for malicious patterns
2. **Intent Parsing** - Extract action/capability from message
3. **Context Retrieval** - Load conversation history from EED
4. **Governance Check** - Triumvirate evaluation
5. **Capability Execution** - Execute through Project-AI systems
6. **Response Generation** - Format response for platform

**Use Cases**:
- Discord bot commands
- Telegram security alerts
- Slack workspace integration
- Multi-platform AI assistant

---

### 2. List Capabilities - `GET /openclaw/capabilities`

**Purpose**: Discover available Project-AI capabilities

**Request**:
```bash
curl http://localhost:8001/openclaw/capabilities
```

**Response**:
```json
{
  "capabilities": {
    "threat_analysis": {
      "subsystem": "Cerberus",
      "description": "Analyze current threat landscape",
      "risk_level": "high",
      "permissions": ["security.read", "cerberus.analyze"]
    },
    "scenario_forecast": {
      "subsystem": "Global Scenario Engine",
      "description": "Run Monte Carlo crisis simulations",
      "risk_level": "medium",
      "permissions": ["scenario.read", "scenario.simulate"]
    },
    "memory_recall": {
      "subsystem": "EED",
      "description": "Query episodic memory",
      "risk_level": "low",
      "permissions": ["memory.read"]
    }
  },
  "total_count": 3
}
```

**Capability Structure**:
- `subsystem` (str) - Project-AI subsystem
- `description` (str) - Human-readable description
- `risk_level` (str) - "low" | "medium" | "high" | "critical"
- `permissions` (list[str]) - Required permissions

---

### 3. Execute Capability - `POST /openclaw/execute`

**Purpose**: Execute specific capability by ID

**⚠️ Status**: Phase 1 placeholder - full execution in Phase 2

**Request**:
```bash
curl -X POST http://localhost:8001/openclaw/execute \
  -H "Content-Type: application/json" \
  -d '{
    "capability_id": "threat_analysis",
    "params": {
      "scope": "global",
      "time_range": "24h"
    },
    "user_id": "discord_user_12345"
  }'
```

**Request Schema**:
```python
class CapabilityRequest(BaseModel):
    capability_id: str
    params: dict = {}
    user_id: str
```

**Response** (Phase 1):
```json
{
  "capability_id": "threat_analysis",
  "status": "phase1_placeholder",
  "message": "Full capability execution in Phase 2"
}
```

**Planned Phase 2 Response**:
```json
{
  "capability_id": "threat_analysis",
  "status": "success",
  "result": {
    "threat_count": 0,
    "active_threats": [],
    "firewall_status": "operational",
    "last_scan": "2025-06-09T14:30:00Z"
  },
  "governance": {
    "approved_by": "Triumvirate",
    "tarl_version": "1.0"
  }
}
```

---

### 4. Health Check - `GET /openclaw/health`

**Purpose**: Legion agent health and status

**Request**:
```bash
curl http://localhost:8001/openclaw/health
```

**Response**:
```json
{
  "agent": "Legion",
  "version": "1.0.0-phase1",
  "status": "operational",
  "agent_id": "legion_abc123",
  "tagline": "For we are many, and we are one",
  "subsystems": {
    "triumvirate": "ready",
    "cerberus": "active",
    "eed": "online",
    "tarl": "enforcing"
  }
}
```

---

### 5. Detailed Status - `GET /openclaw/status`

**Purpose**: Extended status with metrics

**Request**:
```bash
curl http://localhost:8001/openclaw/status
```

**Response**:
```json
{
  "agent_id": "legion_abc123",
  "conversations": 42,
  "security": {
    "enabled": true,
    "hydra_active": true
  }
}
```

---

## Legion Agent Architecture

### Multi-Personality System

Legion is a **multi-personality AI agent** with specialized capabilities:

```python
class LegionAgent:
    """
    Multi-personality AI agent integrating Project-AI capabilities.
    
    Personalities:
    - Galahad: Ethics & alignment advisor
    - Cerberus: Security & threat detection
    - Analyst: Data analysis & insights
    - Executor: Task automation & orchestration
    """
    
    def __init__(self, api_url: str):
        self.agent_id = f"legion_{uuid.uuid4().hex[:6]}"
        self.conversation_history = []
        self.eed_memory = EEDMemory()  # Episodic memory
        self.security_wrapper = SecurityWrapper()  # Cerberus integration
    
    async def process_message(
        self, 
        message: str, 
        user_id: str,
        platform: str = "openclaw",
        metadata: dict = None
    ) -> str:
        """Process message through full pipeline"""
        # 1. Security validation
        if not self.security_wrapper.validate(message):
            return "Security validation failed"
        
        # 2. Intent parsing
        intent = self.parse_intent(message)
        
        # 3. Context retrieval
        context = self.eed_memory.recall(user_id, limit=5)
        
        # 4. Triumvirate governance
        governance_result = await self.check_governance(intent)
        if governance_result["verdict"] == "deny":
            return f"Governance denied: {governance_result['reason']}"
        
        # 5. Capability execution
        result = await self.execute_capability(intent, context)
        
        # 6. Store in memory
        self.eed_memory.store(user_id, message, result)
        
        return result
```

### EED Memory (Episodic Event-Driven)

```python
class EEDMemory:
    """Long-term episodic memory for conversation context"""
    
    def store(self, user_id: str, message: str, response: str):
        """Store conversation turn"""
        self.memory_db[user_id].append({
            "timestamp": datetime.now(),
            "message": message,
            "response": response
        })
    
    def recall(self, user_id: str, limit: int = 5) -> list:
        """Retrieve recent conversations"""
        return self.memory_db[user_id][-limit:]
```

### Security Wrapper (Cerberus Integration)

```python
class SecurityWrapper:
    """Cerberus-powered security validation"""
    
    def validate(self, message: str) -> bool:
        """Check for malicious patterns"""
        # SQL injection patterns
        if re.search(r"(DROP|DELETE|INSERT|UPDATE)\s+", message, re.I):
            return False
        
        # Command injection
        if re.search(r"[;&|`$()]", message):
            return False
        
        # XSS patterns
        if re.search(r"<script|javascript:", message, re.I):
            return False
        
        return True
```

---

## Integration Examples

### Discord Bot

```python
import discord
import requests

client = discord.Client()
LEGION_API = "http://localhost:8001/openclaw/message"

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith("!legion"):
        # Extract command
        content = message.content[7:].strip()
        
        # Send to Legion
        response = requests.post(LEGION_API, json={
            "content": content,
            "user_id": str(message.author.id),
            "platform": "discord",
            "metadata": {
                "channel": message.channel.name,
                "guild": message.guild.name if message.guild else "DM"
            }
        })
        
        # Reply
        result = response.json()
        await message.channel.send(result["response"])

client.run("YOUR_DISCORD_TOKEN")
```

### Telegram Bot

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

LEGION_API = "http://localhost:8001/openclaw/message"

async def legion_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract message
    message = " ".join(context.args)
    
    # Send to Legion
    response = requests.post(LEGION_API, json={
        "content": message,
        "user_id": str(update.effective_user.id),
        "platform": "telegram",
        "metadata": {
            "chat_type": update.effective_chat.type
        }
    })
    
    # Reply
    result = response.json()
    await update.message.reply_text(result["response"])

app = Application.builder().token("YOUR_TELEGRAM_TOKEN").build()
app.add_handler(CommandHandler("legion", legion_command))
app.run_polling()
```

---

## Security Model

### Governance Flow

```
User Message → Legion API
    │
    ▼
Security Wrapper (Cerberus)
    ├─ Malicious patterns? → BLOCK
    ├─ Injection attempts? → BLOCK
    └─ Clean? → CONTINUE
    │
    ▼
Intent Parser
    │
    ▼
Triumvirate Governance
    ├─ Galahad: Ethics check
    ├─ Cerberus: Threat assessment
    └─ CodexDeus: Final arbitration
    │
    ├─ ALLOW → Execute capability
    ├─ DENY → Return error
    └─ DEGRADE → Require extra approval
```

### Rate Limiting (Recommended)

```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/message")
@limiter.limit("30 per minute")  # Prevent abuse
async def process_message(request: Request, message: OpenClawMessage):
    ...
```

---

## Future Enhancements (Phase 2)

1. **Full Capability Execution**
   - Threat analysis with real-time data
   - Scenario simulations
   - Memory queries with semantic search

2. **Webhook Support**
   - Async capability execution
   - Result callbacks to OpenClaw

3. **Multi-Agent Orchestration**
   - Legion → Project-AI → External APIs
   - Agent swarm coordination

4. **Advanced Permissions**
   - Role-based access control
   - Capability-level permissions
   - User quotas

---

## Related Documentation

- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - API architecture
- **[02-FASTAPI-MAIN-ROUTES.md](./02-FASTAPI-MAIN-ROUTES.md)** - Triumvirate governance
- **[integrations/openclaw/README.md](../../integrations/openclaw/README.md)** - Legion implementation

---

**Next**: See [05-CONTRARIAN-FIREWALL-API.md](./05-CONTRARIAN-FIREWALL-API.md) for advanced threat detection.
