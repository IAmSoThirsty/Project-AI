# User Request Flow - Detailed Architecture

## Overview

The User Request Flow represents the complete journey of a user interaction from initial input through governance validation, execution, and response delivery. This flow is the primary entry point for all user-initiated operations in Project-AI.

## High-Level Flow Diagram

```
┌─────────────┐
│    User     │
│   (GUI/API) │
└──────┬──────┘
       │ 1. Request (JSON)
       ↓
┌─────────────────────────┐
│   API Gateway           │
│   - Authentication      │
│   - Rate Limiting       │
│   - Request Validation  │
└──────┬──────────────────┘
       │ 2. Validated Request
       ↓
┌─────────────────────────┐
│   CognitionKernel       │
│   - Intent Detection    │
│   - Context Enrichment  │
│   - Request Parsing     │
└──────┬──────────────────┘
       │ 3. Enriched Request
       ↓
┌─────────────────────────┐
│  GovernanceTriumvirate  │
│  ┌──────────────────┐   │
│  │    Galahad       │   │ 4a. Ethics Check
│  │  (Ethics Layer)  │   │
│  └────────┬─────────┘   │
│           ↓             │
│  ┌──────────────────┐   │
│  │    Cerberus      │   │ 4b. Security Check
│  │ (Security Layer) │   │
│  └────────┬─────────┘   │
│           ↓             │
│  ┌──────────────────┐   │
│  │  Codex Deus Max  │   │ 4c. Final Authority
│  │ (Policy Layer)   │   │
│  └────────┬─────────┘   │
└───────────┼─────────────┘
            │ 5. APPROVED / REJECTED
            ↓
     ┌──────┴──────┐
     │   REJECTED  │  APPROVED
     │      ↓      │      ↓
     │ ┌────────┐ │ ┌─────────────────┐
     │ │Response│ │ │ ExecutionService│
     │ │to User │ │ │ - Agent Select  │
     │ └────────┘ │ │ - Execute       │
     │            │ │ - Monitor       │
     └────────────┘ └────┬────────────┘
                          │ 6. Execution Result
                          ↓
                    ┌─────────────────┐
                    │  MemoryEngine   │
                    │  - Attempt      │
                    │  - Decision     │
                    │  - Result       │
                    │  - Reflection   │
                    │  - Error        │
                    └────┬────────────┘
                         │ 7. Persisted
                         ↓
                    ┌─────────────────┐
                    │   AuditTrail    │
                    │  - Hash Chain   │
                    │  - Compliance   │
                    └────┬────────────┘
                         │ 8. Final Response
                         ↓
                    ┌─────────────────┐
                    │    User         │
                    │  (GUI/API)      │
                    └─────────────────┘
```

## Detailed Step-by-Step Flow

### Step 1: User Submits Request

**Entry Points**:

- **PyQt6 GUI**: Desktop application with leather book interface
- **Flask REST API**: HTTP endpoints at `/api/v1/*`
- **WebSocket**: Real-time bidirectional communication at `/ws`
- **CLI**: Command-line interface via `project_ai_cli.py`

**Request Format**:

```json
{
  "request_id": "uuid-v4",
  "user_id": "user_uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "type": "command|query|analysis",
  "intent": "detected_intent",
  "content": "natural language request",
  "context": {
    "session_id": "session_uuid",
    "previous_requests": ["uuid1", "uuid2"],
    "user_preferences": {},
    "environment": "desktop|web|cli"
  },
  "metadata": {
    "client_version": "1.0.0",
    "platform": "windows|macos|linux",
    "locale": "en-US"
  }
}
```

**Validation Rules**:

- Request ID must be unique UUID v4
- User ID must exist in users database
- Content length: 1-10,000 characters
- Timestamp within 5 minutes of server time (anti-replay)
- Rate limit: 100 requests per minute per user

**Security**:

- TLS 1.3 encryption for all transport
- JWT bearer token in Authorization header
- HMAC signature for request integrity
- IP whitelisting for sensitive operations

### Step 2: API Gateway Processing

**Components**:

- **NGINX**: Reverse proxy and load balancer
- **Authentication Service**: JWT validation and user lookup
- **Rate Limiter**: Token bucket algorithm (100 req/min per user)
- **Request Validator**: JSON schema validation

**Processing Steps**:

1. **TLS Termination**:

   - Validate certificate chain
   - Extract client certificate (if mTLS)
   - Establish secure connection

1. **Authentication**:

   ```python
   def authenticate_request(request):
       token = extract_bearer_token(request.headers)
       payload = jwt.decode(token, PUBLIC_KEY, algorithms=['RS256'])
       user = User.query.get(payload['user_id'])
       if not user or user.status != 'active':
           raise AuthenticationError("Invalid user")
       if payload['exp'] < time.time():
           raise AuthenticationError("Token expired")
       return user
   ```

1. **Rate Limiting**:

   - Check Redis for user request count
   - Increment counter with 60s TTL
   - Reject if count > threshold
   - Return 429 Too Many Requests with Retry-After header

1. **Request Validation**:

   - Validate JSON schema against OpenAPI 3.0 spec
   - Sanitize input (XSS prevention, SQL injection)
   - Normalize Unicode characters
   - Check content length limits

**Error Handling**:

```python
try:
    validated_request = validate_and_sanitize(request)
except ValidationError as e:
    return error_response(400, "Invalid request", details=e.errors)
except AuthenticationError as e:
    return error_response(401, "Authentication failed", details=str(e))
except RateLimitError as e:
    return error_response(429, "Rate limit exceeded", retry_after=e.retry_after)
```

**Metrics Collected**:

- Request count per endpoint
- Authentication success/failure rate
- Rate limit rejections
- Average request size
- Geographic distribution of requests

### Step 3: CognitionKernel Processing

The CognitionKernel is the central intelligence hub that enriches requests with context and intent.

**Components**:

- **Intent Detector**: ML-based classifier (scikit-learn)
- **Context Builder**: Aggregates user history and preferences
- **Entity Extractor**: NER for extracting entities from natural language
- **Semantic Parser**: Transforms natural language to structured commands

**Intent Detection**:

```python
class IntentDetector:
    def __init__(self):
        self.model = joblib.load('models/intent_classifier.pkl')
        self.vectorizer = joblib.load('models/tfidf_vectorizer.pkl')

    def detect_intent(self, text: str) -> IntentResult:
        features = self.vectorizer.transform([text])
        intent = self.model.predict(features)[0]
        confidence = self.model.predict_proba(features)[0].max()

        return IntentResult(
            intent=intent,
            confidence=confidence,
            entities=self.extract_entities(text),
            alternative_intents=self.get_alternatives(features)
        )
```

**Supported Intents** (30+ categories):

- `query.information` - Information retrieval
- `command.execute` - System command execution
- `analysis.data` - Data analysis request
- `generation.image` - Image generation
- `learning.request` - Learning new information
- `override.command` - Command override (requires master password)
- `persona.modify` - Modify AI persona
- `memory.search` - Search memory records
- `security.scan` - Security resource search
- `location.track` - Location tracking
- `emergency.alert` - Emergency contact alert

**Context Enrichment**:

```python
def enrich_context(request: Request, user: User) -> EnrichedRequest:
    context = {
        'user_profile': {
            'id': user.id,
            'name': user.name,
            'preferences': user.preferences,
            'security_clearance': user.clearance_level
        },
        'session_history': get_recent_requests(user.id, limit=10),
        'persona_state': AIPersona.load_state(user.id),
        'memory_context': MemoryEngine.get_relevant_memories(
            user.id,
            request.content,
            limit=5
        ),
        'temporal_context': {
            'timestamp': request.timestamp,
            'timezone': user.timezone,
            'business_hours': is_business_hours(user.timezone)
        },
        'environmental_context': {
            'platform': request.metadata.platform,
            'client_version': request.metadata.client_version,
            'network_quality': detect_network_quality()
        }
    }

    return EnrichedRequest(
        original=request,
        intent=detect_intent(request.content),
        context=context,
        entities=extract_entities(request.content),
        semantic_parse=parse_semantics(request.content)
    )
```

**Performance Optimization**:

- Intent detection: < 50ms (cached model in memory)
- Context enrichment: < 100ms (parallel database queries)
- Entity extraction: < 30ms (spaCy pipeline)
- Total CognitionKernel time: < 200ms target

### Step 4: Governance Validation (Triumvirate)

The GovernanceTriumvirate is a three-layer sequential validation system ensuring all requests comply with ethical, security, and policy requirements.

#### 4a. Galahad (Ethics Layer)

**Responsibility**: Validate requests against Asimov's Laws and ethical guidelines.

**Validation Rules**:

```python
class Galahad:
    LAWS = {
        'law_0': 'A robot may not harm humanity, or allow humanity to come to harm',
        'law_1': 'A robot may not injure a human or allow a human to come to harm',
        'law_2': 'A robot must obey human orders except when in conflict with Laws 0-1',
        'law_3': 'A robot must protect its own existence except when in conflict with Laws 0-2'
    }

    def validate(self, request: EnrichedRequest) -> ValidationResult:

        # Check for harmful intent

        if self.detect_harm(request):
            return ValidationResult(
                approved=False,
                reason="Request violates Law 1: Potential harm to humans",
                law_violated='law_1'
            )

        # Check for humanity-level harm

        if self.detect_existential_risk(request):
            return ValidationResult(
                approved=False,
                reason="Request violates Law 0: Potential harm to humanity",
                law_violated='law_0'
            )

        # Validate human authority

        if request.context['user_profile']['security_clearance'] < request.required_clearance:
            return ValidationResult(
                approved=False,
                reason="Insufficient security clearance",
                escalation_required=True
            )

        return ValidationResult(approved=True, reason="Ethics validation passed")
```

**Decision Matrix**:

| Scenario                                    | Galahad Decision | Reason                   |
| ------------------------------------------- | ---------------- | ------------------------ |
| User requests to delete own data            | APPROVE          | User autonomy, Law 2     |
| User requests to delete another user's data | REJECT           | Law 1: Potential harm    |
| User requests system shutdown               | ESCALATE         | Law 3: Self-preservation |
| User requests security scan                 | APPROVE          | No harm detected         |
| User requests to execute arbitrary code     | REJECT           | Law 1: Security risk     |

**Latency**: < 30ms (rule-based validation)

#### 4b. Cerberus (Security Layer)

**Responsibility**: Validate requests against security policies and threat models.

**Security Checks**:

```python
class Cerberus:
    def validate(self, request: EnrichedRequest, galahad_result: ValidationResult) -> ValidationResult:

        # Check for SQL injection patterns

        if self.detect_sql_injection(request.content):
            return ValidationResult(
                approved=False,
                reason="SQL injection attempt detected",
                security_incident=True
            )

        # Check for command injection

        if self.detect_command_injection(request.content):
            return ValidationResult(
                approved=False,
                reason="Command injection attempt detected",
                security_incident=True
            )

        # Check for sensitive data exposure

        if self.detect_pii_exposure(request):
            return ValidationResult(
                approved=False,
                reason="Request would expose PII",
                compliance_violation='GDPR'
            )

        # Validate API keys/secrets

        if self.detect_secrets_in_request(request.content):
            return ValidationResult(
                approved=False,
                reason="Secrets detected in request",
                security_incident=True
            )

        # Check rate limiting (secondary check)

        if self.check_abuse_pattern(request.user_id):
            return ValidationResult(
                approved=False,
                reason="Abuse pattern detected",
                account_flagged=True
            )

        return ValidationResult(approved=True, reason="Security validation passed")
```

**Threat Detection**:

- **XSS Attacks**: Regex patterns + HTML sanitization
- **CSRF Attacks**: Token validation
- **Path Traversal**: Whitelist-based path validation
- **SSRF Attacks**: URL validation against internal network ranges
- **Authentication Bypass**: Session validation + JWT verification

**Latency**: < 40ms (pattern matching + database lookups)

#### 4c. Codex Deus Maximus (Final Authority)

**Responsibility**: Policy enforcement, compliance validation, and final decision authority.

**Policy Validation**:

```python
class CodexDeusMaximus:
    def validate(self, request: EnrichedRequest, galahad_result: ValidationResult,
                 cerberus_result: ValidationResult) -> FinalDecision:

        # Check if previous layers rejected

        if not galahad_result.approved:
            return FinalDecision(
                approved=False,
                reason=f"Ethics rejection: {galahad_result.reason}",
                governance_layer='galahad'
            )

        if not cerberus_result.approved:
            return FinalDecision(
                approved=False,
                reason=f"Security rejection: {cerberus_result.reason}",
                governance_layer='cerberus',
                security_incident=cerberus_result.security_incident
            )

        # Apply organizational policies

        if not self.check_organizational_policy(request):
            return FinalDecision(
                approved=False,
                reason="Organizational policy violation",
                policy_id=self.get_violated_policy(request)
            )

        # Check compliance requirements

        if not self.check_compliance(request):
            return FinalDecision(
                approved=False,
                reason="Compliance requirement violation",
                regulation=self.get_violated_regulation(request)
            )

        # Check business rules

        if not self.check_business_rules(request):
            return FinalDecision(
                approved=False,
                reason="Business rule violation",
                rule_id=self.get_violated_rule(request)
            )

        # Final approval

        return FinalDecision(
            approved=True,
            reason="All governance checks passed",
            approval_timestamp=datetime.utcnow(),
            approval_hash=self.generate_approval_hash(request)
        )
```

**Policy Categories**:

1. **Data Retention**: Enforce retention policies (90 days, 7 years)
1. **Access Control**: RBAC enforcement
1. **Compliance**: GDPR, HIPAA, SOC2 requirements
1. **Business Rules**: Domain-specific constraints
1. **Resource Limits**: CPU, memory, storage quotas
1. **Operational Constraints**: Maintenance windows, blackout periods

**Latency**: < 30ms (policy engine with cached rules)

**Total Governance Latency**: < 100ms (P95)

### Step 5: Decision Outcome

**Approval Path**:

```python
if final_decision.approved:

    # Record governance decision

    await memory_engine.record_decision(
        channel='decision',
        request_id=request.id,
        decision='APPROVED',
        governance_results={
            'galahad': galahad_result,
            'cerberus': cerberus_result,
            'codex': final_decision
        },
        approval_hash=final_decision.approval_hash
    )

    # Forward to execution

    execution_result = await execution_service.execute(request, final_decision)
    return execution_result
```

**Rejection Path**:

```python
else:

    # Record rejection

    await memory_engine.record_decision(
        channel='decision',
        request_id=request.id,
        decision='REJECTED',
        reason=final_decision.reason,
        governance_layer=final_decision.governance_layer
    )

    # Return error response to user

    return ErrorResponse(
        status=403,
        error='Forbidden',
        message=final_decision.reason,
        request_id=request.id,
        appeal_process=get_appeal_instructions()
    )
```

### Step 6: Agent Execution

**Agent Selection**:

```python
def select_agent(request: EnrichedRequest) -> Agent:
    intent = request.intent.intent

    agent_mapping = {
        'query.information': IntelligenceAgent,
        'command.execute': ExecutionAgent,
        'analysis.data': DataAnalysisAgent,
        'generation.image': ImageGenerationAgent,
        'learning.request': LearningAgent,
        'memory.search': MemorySearchAgent,
        'security.scan': SecurityAgent
    }

    agent_class = agent_mapping.get(intent, DefaultAgent)
    return agent_class(request=request, config=load_agent_config(intent))
```

**Execution with Timeout**:

```python
async def execute_with_timeout(agent: Agent, request: EnrichedRequest, timeout: int = 60):
    try:
        result = await asyncio.wait_for(
            agent.execute(request),
            timeout=timeout
        )

        await memory_engine.record_result(
            channel='result',
            request_id=request.id,
            result=result,
            execution_time=result.duration,
            agent_type=type(agent).__name__
        )

        return result

    except asyncio.TimeoutError:
        await memory_engine.record_error(
            channel='error',
            request_id=request.id,
            error='TimeoutError',
            message=f'Agent execution exceeded {timeout}s timeout'
        )
        raise ExecutionTimeoutError(f"Execution timeout after {timeout}s")
```

### Step 7: Memory Recording

**Five-Channel Recording**:

```python
async def record_complete_operation(request, decision, result):
    operation_id = request.id

    # Parallel writes to all five channels

    await asyncio.gather(
        memory_engine.record(
            channel='attempt',
            operation_id=operation_id,
            data={
                'user_id': request.user_id,
                'content': request.content,
                'intent': request.intent,
                'context': request.context,
                'timestamp': request.timestamp
            }
        ),
        memory_engine.record(
            channel='decision',
            operation_id=operation_id,
            data={
                'approved': decision.approved,
                'governance_results': decision.governance_results,
                'approval_hash': decision.approval_hash,
                'decision_timestamp': decision.timestamp
            }
        ),
        memory_engine.record(
            channel='result',
            operation_id=operation_id,
            data={
                'status': result.status,
                'output': result.output,
                'execution_time': result.duration,
                'agent_type': result.agent_type,
                'result_timestamp': result.timestamp
            }
        ),
        memory_engine.record(
            channel='reflection',
            operation_id=operation_id,
            data=await generate_reflection(request, decision, result)
        ),
        memory_engine.record(
            channel='error',
            operation_id=operation_id,
            data=result.errors if result.errors else None
        )
    )
```

### Step 8: Audit Trail Recording

**Hash Chain Generation**:

```python
def append_to_audit_trail(operation: CompletedOperation):
    previous_hash = get_latest_audit_hash()

    audit_entry = {
        'operation_id': operation.id,
        'user_id': operation.user_id,
        'timestamp': operation.timestamp,
        'action': operation.action,
        'result': operation.result_summary,
        'previous_hash': previous_hash
    }

    current_hash = hashlib.sha256(
        json.dumps(audit_entry, sort_keys=True).encode()
    ).hexdigest()

    audit_entry['current_hash'] = current_hash

    # Store in immutable append-only log

    audit_trail.append(audit_entry)

    # Update latest hash in cache

    redis.set('latest_audit_hash', current_hash)

    return current_hash
```

### Step 9: Response Delivery

**Success Response**:

```json
{
  "status": "success",
  "request_id": "uuid",
  "result": {
    "output": "execution output",
    "metadata": {
      "execution_time": "1.234s",
      "agent_type": "IntelligenceAgent",
      "governance_approved": true
    }
  },
  "memory": {
    "operation_id": "uuid",
    "recorded_channels": ["attempt", "decision", "result", "reflection"]
  },
  "audit": {
    "audit_hash": "sha256_hash",
    "audit_entry_id": "audit_uuid"
  },
  "timestamp": "2024-01-15T10:30:05Z"
}
```

**Error Response**:

```json
{
  "status": "error",
  "request_id": "uuid",
  "error": {
    "code": "GOVERNANCE_REJECTED",
    "message": "Request rejected by Cerberus: Security policy violation",
    "details": {
      "governance_layer": "cerberus",
      "reason": "SQL injection attempt detected",
      "security_incident": true
    }
  },
  "memory": {
    "operation_id": "uuid",
    "recorded_channels": ["attempt", "decision", "error"]
  },
  "audit": {
    "audit_hash": "sha256_hash",
    "audit_entry_id": "audit_uuid"
  },
  "appeal": {
    "available": false,
    "reason": "Security incidents are not appealable"
  },
  "timestamp": "2024-01-15T10:30:01Z"
}
```

## Performance Characteristics

### Latency Breakdown (P95)

```
API Gateway:        20ms
CognitionKernel:   200ms
Governance:        100ms
Agent Execution:  1000ms (simple) / 30000ms (complex)
Memory Recording:   50ms
Audit Trail:        20ms
Response:           10ms
------------------------
Total (simple):   1400ms
Total (complex): 30400ms
```

### Throughput Metrics

- Concurrent requests: 500/sec sustained
- Peak requests: 1000/sec burst (30s)
- Governance decisions: 1000/sec
- Memory writes: 5000/sec (5 channels × 1000 ops)
- Audit entries: 1000/sec

## Error Handling

### Retry Logic

```python
@retry(
    retry=retry_if_exception_type(TransientError),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3)
)
async def execute_with_retry(request):
    return await execution_service.execute(request)
```

### Circuit Breaker

```python
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=ServiceUnavailable
)

@circuit_breaker
async def call_external_service(request):
    return await external_service.call(request)
```

### Graceful Degradation

- If governance service fails: Reject all requests (fail-safe)
- If memory recording fails: Complete execution, retry recording asynchronously
- If audit trail fails: Block execution, alert ops team (compliance requirement)
- If agent execution fails: Return error to user, record in error channel

## Security Considerations

### Input Validation

- Whitelist-based validation for all inputs
- Max content length: 10,000 characters
- Sanitize HTML/JavaScript
- Validate against JSON schema

### Output Encoding

- HTML encoding for web display
- JSON escaping for API responses
- PII redaction for logs
- Sensitive data masking

### Rate Limiting

- Per-user: 100 requests/minute
- Per-IP: 500 requests/minute
- Per-endpoint: 1000 requests/minute
- Burst allowance: 20 requests

### Audit Requirements

- Log all requests (including rejected)
- Record governance decisions
- Track execution outcomes
- Maintain immutable audit trail

## Monitoring and Alerting

### Key Metrics

- Request success rate (target: > 99%)
- Governance rejection rate (expected: 1-5%)
- Average response time (target: < 2s)
- P95 response time (target: < 5s)
- Error rate (target: < 0.1%)

### Alerts

- Error rate > 1%: WARNING
- Error rate > 5%: CRITICAL
- Response time > 10s: WARNING
- Governance service down: CRITICAL
- Audit trail write failure: CRITICAL

## Related Documentation

- [Governance Decision Flow](./governance_decision_flow.md)
- [Agent Execution Flow](./agent_execution_flow.md)
- [Memory Recording Flow](./memory_recording_flow.md)
- [Audit Trail Flow](./audit_trail_flow.md)
