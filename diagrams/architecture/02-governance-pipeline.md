# Governance Pipeline Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        USER[User Request]
        API[API Endpoint]
        CLI[CLI Command]
        GUI[GUI Action]
    end

    subgraph "Governance Pipeline (src/app/core/governance/)"
        INTAKE[Request Intake<br/>Normalization]
        
        subgraph "Validation Tier 1: Constitutional"
            CONST[Constitutional Validator<br/>Asimov's Laws]
            ETHICS[Ethics Checker<br/>Harm Assessment]
            BOUNDS[Boundary Validator<br/>Permission Scope]
        end

        subgraph "Validation Tier 2: Security"
            AUTH[Authentication<br/>User Identity]
            AUTHZ[Authorization<br/>RBAC Policies]
            RATE[Rate Limiting<br/>Quota Management]
            INPUT[Input Sanitization<br/>XSS/SQL Injection]
        end

        subgraph "Validation Tier 3: Business Logic"
            CONTEXT[Context Validator<br/>State Requirements]
            DEPS[Dependency Checker<br/>Prerequisites]
            RESOURCE[Resource Availability<br/>Capacity Check]
        end

        DECISION{All Validators<br/>Pass?}
        AUDIT[Audit Logger<br/>Immutable Trail]
        EXEC[Execution Engine]
        MONITOR[Runtime Monitor<br/>Anomaly Detection]
    end

    subgraph "AI Oversight"
        OVERSIGHT[Oversight Agent<br/>Safety Validation]
        PLANNER[Planner Agent<br/>Task Decomposition]
        VALIDATOR[Validator Agent<br/>Output Check]
        EXPLAIN[Explainability<br/>Decision Trace]
    end

    subgraph "Data Layer"
        AUDIT_LOG[audit_logs/<br/>Governance Events]
        BLACK_V[Black Vault<br/>Denied Actions]
        POLICY[Policies<br/>YAML Configuration]
        METRICS[Metrics DB<br/>Telemetry]
    end

    subgraph "Response Layer"
        SUCCESS[Success Response<br/>+ Explanation]
        FAILURE[Failure Response<br/>+ Reason]
        PARTIAL[Partial Success<br/>+ Warnings]
    end

    %% Flow: Input to Pipeline
    USER --> INTAKE
    API --> INTAKE
    CLI --> INTAKE
    GUI --> INTAKE

    %% Flow: Tier 1 Validation
    INTAKE --> CONST
    CONST --> ETHICS
    ETHICS --> BOUNDS
    BOUNDS --> DECISION

    %% Flow: Tier 2 Validation
    INTAKE --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> RATE
    RATE --> INPUT
    INPUT --> DECISION

    %% Flow: Tier 3 Validation
    INTAKE --> CONTEXT
    CONTEXT --> DEPS
    DEPS --> RESOURCE
    RESOURCE --> DECISION

    %% Decision Flow
    DECISION -->|All Pass| EXEC
    DECISION -->|Any Fail| AUDIT
    AUDIT --> BLACK_V
    AUDIT --> AUDIT_LOG

    %% Execution Monitoring
    EXEC --> MONITOR
    MONITOR --> OVERSIGHT
    MONITOR --> PLANNER
    MONITOR --> VALIDATOR

    %% AI Oversight
    OVERSIGHT -.safety check.-> EXEC
    PLANNER -.decompose task.-> EXEC
    VALIDATOR -.validate output.-> EXEC
    EXPLAIN --> AUDIT_LOG

    %% Logging & Metrics
    EXEC --> AUDIT_LOG
    MONITOR --> METRICS
    OVERSIGHT --> AUDIT_LOG
    VALIDATOR --> AUDIT_LOG

    %% Response Generation
    EXEC --> SUCCESS
    AUDIT --> FAILURE
    MONITOR --> PARTIAL

    %% Policy Configuration
    POLICY -.configures.-> CONST
    POLICY -.configures.-> AUTHZ
    POLICY -.configures.-> RATE

    %% Styling
    classDef inputClass fill:#00ff00,stroke:#00ffff,stroke-width:2px,color:#000
    classDef tier1Class fill:#dc2626,stroke:#ef4444,stroke-width:3px,color:#fff
    classDef tier2Class fill:#ca8a04,stroke:#eab308,stroke-width:3px,color:#000
    classDef tier3Class fill:#2563eb,stroke:#3b82f6,stroke-width:3px,color:#fff
    classDef decisionClass fill:#7c2d12,stroke:#f97316,stroke-width:4px,color:#fff
    classDef aiClass fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    classDef dataClass fill:#065f46,stroke:#10b981,stroke-width:2px,color:#fff
    classDef responseClass fill:#1e3a8a,stroke:#60a5fa,stroke-width:2px,color:#fff

    class USER,API,CLI,GUI inputClass
    class CONST,ETHICS,BOUNDS tier1Class
    class AUTH,AUTHZ,RATE,INPUT tier2Class
    class CONTEXT,DEPS,RESOURCE tier3Class
    class DECISION decisionClass
    class OVERSIGHT,PLANNER,VALIDATOR,EXPLAIN aiClass
    class AUDIT_LOG,BLACK_V,POLICY,METRICS dataClass
    class SUCCESS,FAILURE,PARTIAL responseClass
```

## Pipeline Flow

### 1. Request Intake (Normalization)

All requests are normalized to a standard format:

```python
{
    "action": str,          # What operation
    "context": dict,        # Environmental state
    "user_id": str,         # Who initiated
    "timestamp": datetime,  # When requested
    "metadata": dict        # Additional info
}
```

### 2. Three-Tier Validation

**Tier 1: Constitutional (Highest Priority)**
- Validates against Asimov's Three Laws
- Checks for harm to humans, humanity, self-preservation
- Immutable rules enforced at code level

**Tier 2: Security**
- Authentication: User identity verification (bcrypt)
- Authorization: RBAC policy enforcement
- Rate Limiting: Quota management per user/endpoint
- Input Sanitization: XSS, SQL injection, path traversal prevention

**Tier 3: Business Logic**
- Context Validation: Required state/preconditions met
- Dependency Checking: Prerequisites satisfied
- Resource Availability: CPU, memory, API quotas

### 3. Decision Point

All validators must pass for action execution:

```python
is_allowed, reason = governance_pipeline.validate(request)
if not is_allowed:
    audit_log.record_denial(request, reason)
    black_vault.add_fingerprint(request)
    return FailureResponse(reason)
```

### 4. AI Oversight (Runtime)

Four agents monitor execution:

- **Oversight Agent**: Safety validation during execution
- **Planner Agent**: Task decomposition for complex actions
- **Validator Agent**: Output validation before return
- **Explainability Agent**: Decision trace generation

### 5. Audit Trail

Immutable logging of all governance events:

```json
{
    "event_id": "uuid",
    "timestamp": "ISO-8601",
    "action": "requested_action",
    "user_id": "user123",
    "decision": "allowed|denied",
    "validators": {
        "constitutional": "pass",
        "security": "pass",
        "business": "fail"
    },
    "reason": "Insufficient resource quota",
    "fingerprint": "sha256_hash"
}
```

### Black Vault Pattern

Denied actions are fingerprinted (SHA-256) and stored:

```python
content_hash = hashlib.sha256(action.encode()).hexdigest()
if content_hash in black_vault:
    return "This action has been permanently denied"
```

### Policy Configuration

YAML-based policy files in `policies/`:

```yaml
# constitutional_policies.yaml
four_laws:
  priority: 1
  immutable: true
  validators:
    - harm_to_humans: strict
    - harm_to_humanity: strict
    - self_preservation: moderate

# security_policies.yaml
rate_limits:
  api_calls_per_minute: 60
  learning_requests_per_day: 10
  image_generation_per_hour: 5

# rbac_policies.yaml
roles:
  admin:
    permissions: ["*"]
  user:
    permissions: ["read", "execute", "request_learning"]
```

## Integration Points

### Temporal Workflow Integration

```python
# Governance as Temporal Activity
@activity.defn
async def validate_governance(request: dict) -> tuple[bool, str]:
    return await governance_pipeline.validate(request)
```

### Web API Integration

```python
@app.before_request
def governance_middleware():
    request_obj = normalize_request(flask.request)
    is_allowed, reason = governance_pipeline.validate(request_obj)
    if not is_allowed:
        return jsonify({"error": reason}), 403
```

### GUI Integration

```python
# In LeatherBookDashboard
def handle_user_action(self, action: str):
    is_allowed, reason = self.governance.validate_action(
        action,
        context={"is_user_order": True}
    )
    if not is_allowed:
        self.show_error_dialog(reason)
        return
    self.execute_action(action)
```

## Monitoring & Metrics

Runtime telemetry collected:

- **Throughput**: Requests/second, latency percentiles
- **Validation**: Pass/fail rates per tier, common denial reasons
- **Anomalies**: Unusual patterns, potential attacks
- **Resource Usage**: CPU, memory, API quota consumption

Metrics exported to ClickHouse/Prometheus for visualization.
