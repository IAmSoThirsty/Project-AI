# Component Architecture - Project-AI

## Overview

Project-AI implements a three-tier component architecture designed for ethical AI governance, scalability, and maintainability. The architecture separates concerns into Governance (Tier 1), Infrastructure (Tier 2), and Application (Tier 3) layers.

## Three-Tier Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     TIER 1: GOVERNANCE                         │
│                  (Core Decision Making)                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │ CognitionKernel  │  │ GovernanceTri... │  │ MemoryEngine ││
│  │                  │  │                  │  │              ││
│  │ • Intent         │  │ • Galahad       │  │ • 5 Channels ││
│  │   Detection      │  │ • Cerberus      │  │ • Recording  ││
│  │ • Context        │  │ • Codex Deus    │  │ • Retrieval  ││
│  │   Enrichment     │  │   Maximus       │  │ • Archival   ││
│  │ • Request        │  │ • Ethics        │  │ • Search     ││
│  │   Parsing        │  │ • Security      │  │              ││
│  └──────────────────┘  │ • Policy        │  └──────────────┘│
│                        └──────────────────┘                   │
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │ IdentityEngine   │  │  AuditTrail      │  │ PolicyEngine ││
│  │                  │  │                  │  │              ││
│  │ • User Auth      │  │ • Hash Chain     │  │ • RBAC       ││
│  │ • Session Mgmt   │  │ • Immutable Log  │  │ • Compliance ││
│  │ • Permissions    │  │ • Verification   │  │ • Rules      ││
│  │ • RBAC           │  │ • Export         │  │              ││
│  └──────────────────┘  └──────────────────┘  └──────────────┘│
└────────────────────────────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                  TIER 2: INFRASTRUCTURE                        │
│              (Execution & Communication)                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │ ExecutionService │  │   CouncilHub     │  │ MessageQueue ││
│  │                  │  │                  │  │              ││
│  │ • Agent Select   │  │ • Event Bus      │  │ • RabbitMQ   ││
│  │ • Orchestration  │  │ • Pub/Sub        │  │ • Job Queue  ││
│  │ • Timeout Mgmt   │  │ • WebSocket      │  │ • Priority   ││
│  │ • Result Aggr.   │  │ • SSE            │  │              ││
│  └──────────────────┘  └──────────────────┘  └──────────────┘│
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │  DatabasePool    │  │  CacheLayer      │  │ ObjectStore  ││
│  │                  │  │                  │  │              ││
│  │ • PostgreSQL     │  │ • Redis          │  │ • MinIO/S3   ││
│  │ • Connection     │  │ • Hot Data       │  │ • Files      ││
│  │   Pool           │  │ • Session Store  │  │ • Archives   ││
│  │ • Replicas       │  │                  │  │              ││
│  └──────────────────┘  └──────────────────┘  └──────────────┘│
└────────────────────────────────────────────────────────────────┘
                               ↓
┌────────────────────────────────────────────────────────────────┐
│                   TIER 3: APPLICATION                          │
│              (User Interface & External APIs)                  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │  Agent System    │  │   GUI Layer      │  │  REST API    ││
│  │                  │  │                  │  │              ││
│  │ • 30+ Agents     │  │ • PyQt6 Desktop  │  │ • Flask      ││
│  │ • Intelligence   │  │ • Leather Book   │  │ • OpenAPI    ││
│  │ • Analysis       │  │ • Dashboard      │  │ • JWT Auth   ││
│  │ • Utility        │  │ • Persona Panel  │  │              ││
│  └──────────────────┘  └──────────────────┘  └──────────────┘│
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │  Plugin System   │  │  CLI Interface   │  │ WebSocket API││
│  │                  │  │                  │  │              ││
│  │ • Discovery      │  │ • Commands       │  │ • Real-time  ││
│  │ • Loading        │  │ • Scripts        │  │ • Push       ││
│  │ • Lifecycle      │  │ • Automation     │  │ • Subscribe  ││
│  └──────────────────┘  └──────────────────┘  └──────────────┘│
└────────────────────────────────────────────────────────────────┘
```

## Component Interaction Patterns

### 1. Request-Response Pattern

```
User → GUI → API Gateway → CognitionKernel → GovernanceTriumvirate
       → ExecutionService → Agent → MemoryEngine → Response
```

### 2. Event-Driven Pattern

```
Event → CouncilHub → Subscribers → Handlers → Side Effects
```

### 3. Publish-Subscribe Pattern

```
Publisher → MessageQueue → Multiple Consumers → Processing
```

### 4. Command Pattern

```
Command → CommandHandler → Validation → Execution → Result
```

## Core Components

### Tier 1: Governance Components

#### CognitionKernel

**Purpose**: Central intelligence hub for request processing

**Responsibilities**:

- Intent detection using ML classifier
- Context enrichment from multiple sources
- Entity extraction (NER)
- Semantic parsing
- Request routing

**Key Interfaces**:

```python
class CognitionKernel:
    def detect_intent(self, text: str) -> IntentResult
    def enrich_context(self, request: Request, user: User) -> EnrichedRequest
    def extract_entities(self, text: str) -> List[Entity]
    def parse_semantics(self, text: str) -> SemanticParse
```

**Dependencies**:

- scikit-learn for intent classification
- spaCy for NER
- PostgreSQL for user context
- Redis for caching

**Performance**:

- Intent detection: < 50ms (P95)
- Context enrichment: < 100ms (P95)
- Throughput: 500 requests/sec

#### GovernanceTriumvirate

**Purpose**: Three-layer ethical and security validation

**Responsibilities**:

- Galahad: Ethics validation (Asimov's Laws)
- Cerberus: Security threat detection
- Codex Deus Maximus: Policy enforcement

**Key Interfaces**:

```python
class GovernanceTriumvirate:
    def validate(self, request: EnrichedRequest) -> GovernanceDecision

class Galahad:
    def validate_ethics(self, request: EnrichedRequest) -> GalahadDecision

class Cerberus:
    def validate_security(self, request: EnrichedRequest) -> CerberusDecision

class CodexDeusMaximus:
    def validate_policy(self, request: EnrichedRequest) -> FinalDecision
```

**Dependencies**:

- Rule engine for policy evaluation
- ML models for threat detection
- Audit trail for logging

**Performance**:

- Total validation: < 100ms (P95)
- Galahad: < 30ms
- Cerberus: < 40ms
- Codex: < 30ms

#### MemoryEngine

**Purpose**: Five-channel memory recording and retrieval

**Responsibilities**:

- Record operations across 5 channels
- Search and retrieve memories
- Archive old memories
- Provide context for future requests

**Key Interfaces**:

```python
class MemoryEngine:
    async def record(self, channel: str, operation_id: str, data: dict)
    async def record_complete_operation(self, operation: CompletedOperation)
    async def search(self, query: str, channels: List[str]) -> List[MemoryRecord]
    async def get_operation(self, operation_id: str) -> CompleteOperation
    async def archive_old_memories(self, cutoff_date: datetime)
```

**Dependencies**:

- PostgreSQL for hot storage
- MinIO/S3 for warm/cold storage
- Redis for caching recent memories

**Performance**:

- Single channel write: < 10ms (P95)
- All 5 channels (parallel): < 50ms (P95)
- Search: < 100ms (P95)
- Throughput: 1,000 writes/sec

#### IdentityEngine

**Purpose**: User authentication and authorization

**Responsibilities**:

- User authentication (OAuth2, OIDC)
- Session management
- Role-based access control (RBAC)
- Permission validation

**Key Interfaces**:

```python
class IdentityEngine:
    def authenticate(self, credentials: Credentials) -> AuthResult
    def create_session(self, user: User) -> Session
    def validate_session(self, session_id: str) -> bool
    def check_permission(self, user: User, resource: str, action: str) -> bool
```

**Dependencies**:

- PostgreSQL for user storage
- Redis for session storage
- OAuth2 providers (optional)

**Security Features**:

- bcrypt password hashing
- JWT tokens (RS256)
- Session timeout (30 min idle, 24 hr absolute)
- Multi-factor authentication (optional)

#### AuditTrail

**Purpose**: Immutable logging with hash chaining

**Responsibilities**:

- Append audit entries
- Verify chain integrity
- Export compliance reports
- Merkle tree construction

**Key Interfaces**:

```python
class AuditTrail:
    async def append(self, event_type: str, event_data: dict) -> AuditEntry
    async def verify_chain(self, start_seq: int, end_seq: int) -> VerificationResult
    async def export_compliance_report(self, start_date: datetime,
                                       end_date: datetime) -> ComplianceReport
```

**Dependencies**:

- PostgreSQL for immutable storage
- Redis for latest hash cache

**Performance**:

- Append: < 20ms (P95)
- Verify 1000 entries: < 2s
- Throughput: 10,000 entries/sec

### Tier 2: Infrastructure Components

#### ExecutionService

**Purpose**: Agent orchestration and execution management

**Responsibilities**:

- Dynamic agent selection
- Multi-agent orchestration
- Timeout management
- Result aggregation
- Agent pooling

**Key Interfaces**:

```python
class ExecutionService:
    async def execute(self, request: EnrichedRequest,
                     governance_decision: GovernanceDecision) -> ExecutionResult
    async def execute_parallel(self, agents: List[Agent],
                              request: EnrichedRequest) -> List[AgentResult]
    async def execute_sequential(self, agents: List[Agent],
                                 request: EnrichedRequest) -> List[AgentResult]
```

**Dependencies**:

- Agent pool
- MessageQueue for async operations
- MemoryEngine for result recording

**Performance**:

- Simple execution: < 1s (P95)
- Complex execution: < 30s (P95)
- Concurrent agents: 50+

#### CouncilHub

**Purpose**: Event bus and real-time communication

**Responsibilities**:

- Event publishing and subscription
- WebSocket management
- Server-Sent Events (SSE)
- Real-time notifications

**Key Interfaces**:

```python
class CouncilHub:
    def publish(self, event: Event, channel: str)
    def subscribe(self, channel: str, handler: Callable)
    async def send_to_user(self, user_id: str, message: dict)
```

**Dependencies**:

- WebSocket library
- Redis for pub/sub
- MessageQueue for persistence

**Performance**:

- Event latency: < 10ms
- WebSocket connections: 10,000+
- Events/sec: 50,000+

#### DatabasePool

**Purpose**: Database connection management

**Responsibilities**:

- Connection pooling
- Read replica routing
- Query optimization
- Transaction management

**Key Interfaces**:

```python
class DatabasePool:
    async def execute(self, query: str, *args) -> Any
    async def fetch(self, query: str, *args) -> List[dict]
    async def fetchrow(self, query: str, *args) -> dict
    async def transaction(self) -> Transaction
```

**Configuration**:

- Pool size: 25 connections
- Read replicas: up to 5
- Connection timeout: 30s
- Idle timeout: 10 min

#### CacheLayer

**Purpose**: High-performance caching

**Responsibilities**:

- Hot data caching
- Session storage
- Rate limit tracking
- Latest hash caching

**Key Interfaces**:

```python
class CacheLayer:
    async def get(self, key: str) -> Optional[bytes]
    async def set(self, key: str, value: bytes, ttl: int = None)
    async def delete(self, key: str)
    async def exists(self, key: str) -> bool
```

**Implementation**:

- Redis backend
- TTL support
- LRU eviction
- Pub/sub capability

### Tier 3: Application Components

#### Agent System

**Purpose**: 30+ specialized agents for task execution

**Agent Categories**:

- Core: Intelligence, Learning, Command, Memory
- Analysis: Data, Security, Pattern, Forecasting
- Utility: Image, Location, Emergency, File

**Key Interfaces**:

```python
class Agent(ABC):
    @abstractmethod
    async def execute(self, request: EnrichedRequest) -> AgentResult

    async def reset(self)
    def validate_input(self, request: EnrichedRequest) -> bool
```

**Performance**:

- Simple agent: < 1s
- Medium agent: < 30s
- Complex agent: < 60s

#### GUI Layer (PyQt6)

**Purpose**: Desktop user interface

**Components**:

- LeatherBookInterface: Main window
- LeatherBookDashboard: 6-zone dashboard
- PersonaPanel: AI configuration
- ImageGenerationInterface: Image gen UI

**Key Features**:

- Tron-themed login page
- Real-time chat interface
- Dashboard with stats
- Drag-and-drop file handling

#### REST API (Flask)

**Purpose**: HTTP API for external integrations

**Endpoints**:

- `/api/v1/request` - Submit user request
- `/api/v1/operations/{id}` - Get operation status
- `/api/v1/memory/search` - Search memories
- `/api/v1/audit/export` - Export audit trail

**Features**:

- OpenAPI 3.0 documentation
- JWT authentication
- Rate limiting
- CORS support

## Component Communication

### Synchronous Communication

- HTTP/REST for request-response
- gRPC for internal service calls (future)
- Direct method calls within process

### Asynchronous Communication

- RabbitMQ for job queues
- Redis pub/sub for events
- WebSocket for real-time updates

### Data Flow

- Request flows top-down (Tier 1 → 2 → 3)
- Events flow through CouncilHub
- Memory writes are parallel
- Audit trail is append-only

## Deployment Architecture

### Standalone Mode

```
Single Process:

  - All Tier 1 components
  - All Tier 2 components
  - GUI or API (not both)

```

### Distributed Mode

```
Multiple Processes:

  - Governance Service (Tier 1)
  - Execution Service (Tier 2)
  - API Service (Tier 3)
  - GUI Application (separate)

```

### Container Deployment

```
Docker Compose:

  - app (main application)
  - postgres (database)
  - redis (cache)
  - rabbitmq (message queue)
  - minio (object storage)
  - prometheus (metrics)
  - grafana (visualization)

```

## Scalability Patterns

### Horizontal Scaling

- ExecutionService: stateless, can run multiple instances
- API Service: stateless, behind load balancer
- Agent Pool: shared across instances via Redis

### Vertical Scaling

- CognitionKernel: CPU-intensive (ML models)
- Database: memory-intensive (large datasets)
- MemoryEngine: I/O-intensive (disk writes)

### Data Partitioning

- PostgreSQL: monthly partitions on timestamp
- Memory records: partitioned by user_id
- Audit trail: partitioned by date

## Monitoring and Observability

### Metrics (Prometheus)

- Request rates per component
- Response times (histograms)
- Error rates
- Resource utilization

### Logging (Structured JSON)

- Component-specific loggers
- Correlation IDs across components
- Log levels (DEBUG → FATAL)
- Automatic PII redaction

### Tracing (Jaeger)

- Distributed tracing across components
- Request flow visualization
- Performance bottleneck identification

## Related Documentation

- [CognitionKernel Architecture](./cognition_kernel.md)
- [GovernanceTriumvirate Architecture](./governance_triumvirate.md)
- [MemoryEngine Architecture](./memory_engine.md)
- [IdentityEngine Architecture](./identity_engine.md)
- [Agent System Architecture](./agent_system.md)

## Component Diagrams

- [cognition_kernel.puml](./cognition_kernel.puml)
- [governance_triumvirate.puml](./governance_triumvirate.puml)
- [memory_engine.puml](./memory_engine.puml)
- [identity_engine.puml](./identity_engine.puml)
- [agent_system.puml](./agent_system.puml)
