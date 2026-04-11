# Data Flow Diagram

**Sovereign Governance Substrate - Complete Data Architecture**

---

## 1. High-Level System Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL INTERFACES                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Web APIs │  │  Clients │  │ Webhooks │  │   CLI    │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │              │             │                  │
└───────┼─────────────┼──────────────┼─────────────┼──────────────────┘
        │             │              │             │
        └─────────────┴──────────────┴─────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │    PROJECT-AI ORCHESTRATOR              │
        │    (Core Coordination Engine)           │
        │                                         │
        │  • FastAPI/Flask Application            │
        │  • Request routing                      │
        │  • Business logic                       │
        │  • Authentication/Authorization         │
        │  • MCP Gateway integration              │
        └──────┬──────────────┬──────────────┬────┘
               │              │              │
      ┌────────┘              │              └────────┐
      │                       │                       │
      ▼                       ▼                       ▼
┌──────────┐          ┌──────────┐          ┌──────────┐
│PostgreSQL│          │  Redis   │          │   File   │
│ Primary  │          │  Cache   │          │ Storage  │
│ Database │          │  Queue   │          │ System   │
└────┬─────┘          └────┬─────┘          └────┬─────┘
     │                     │                      │
     ▼                     ▼                      ▼
┌──────────┐          ┌──────────┐          ┌──────────┐
│ Volume:  │          │ Volume:  │          │  Bind    │
│ postgres │          │  redis   │          │  Mounts  │
│  -data   │          │  -data   │          │ ./data/  │
└──────────┘          └──────────┘          └──────────┘
     │                     │                      │
     └─────────────────────┴──────────────────────┘
                          │
                          ▼
            ┌─────────────────────────┐
            │  HOST FILESYSTEM        │
            │  (Persistent Storage)   │
            └─────────────────────────┘
```

---

## 2. Detailed Data Flow by Operation Type

### 2.1 User Authentication Flow

```
[User Login Request]
        │
        ▼
┌───────────────────┐
│  Orchestrator API │
│  /auth/login      │
└────────┬──────────┘
         │
         ▼
┌─────────────────────────┐
│ 1. Check Redis Session  │ ◄───────┐
│    Key: user:session:*  │         │
└────────┬────────────────┘         │
         │ NOT FOUND                │ FOUND (cached)
         ▼                          │
┌─────────────────────────┐         │
│ 2. Query PostgreSQL     │         │
│    Table: users         │         │
│    Validate password    │         │
└────────┬────────────────┘         │
         │ VALID                    │
         ▼                          │
┌─────────────────────────┐         │
│ 3. Create Session       │         │
│    Table: user_sessions │         │
│    Insert session token │         │
└────────┬────────────────┘         │
         │                          │
         ▼                          │
┌─────────────────────────┐         │
│ 4. Cache in Redis       │─────────┘
│    SET user:session:*   │
│    TTL: session_timeout │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 5. Update audit_log     │
│    Table: audit_logs    │
│    Action: login        │
└────────┬────────────────┘
         │
         ▼
   [Return JWT Token]
```

### 2.2 AI Conversation Flow (Vector Memory)

```
[User Message]
        │
        ▼
┌────────────────────────┐
│ 1. Store Message       │
│    PostgreSQL          │
│    Table: messages     │
│    content TEXT        │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 2. Generate Embedding  │
│    OpenAI API          │
│    text-embedding-3    │
│    Dimensions: 1536    │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 3. Store Vector        │
│    PostgreSQL          │
│    Table: vector_memory│
│    embedding vector(1536)│
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 4. Similarity Search   │
│    pgvector query      │
│    <=> cosine distance │
│    Top 10 similar      │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 5. Cache Results       │
│    Redis               │
│    Key: embed:conv:*   │
│    TTL: 1 hour         │
└────────┬───────────────┘
         │
         ▼
   [AI Response with Context]
```

### 2.3 File Upload Flow

```
[File Upload Request]
        │
        ▼
┌────────────────────────┐
│ 1. Validate File       │
│    Size, Type, Virus   │
│    Scan (if enabled)   │
└────────┬───────────────┘
         │ VALID
         ▼
┌────────────────────────┐
│ 2. Generate File ID    │
│    UUID v4             │
│    Hash: SHA256        │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 3. Save to Filesystem  │
│    Path: /app/data/    │
│      uploads/{user_id}/│
│      {file_id}.{ext}   │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 4. Store Metadata      │
│    PostgreSQL          │
│    Table: file_uploads │
│    (user_id, path,     │
│     size, hash, etc)   │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 5. Update Audit Log    │
│    Table: audit_logs   │
│    Action: file_upload │
└────────┬───────────────┘
         │
         ▼
   [Return File URL]
```

### 2.4 Task Queue Flow (Agent Orchestration)

```
[Task Creation Request]
        │
        ▼
┌────────────────────────┐
│ 1. Insert Task         │
│    PostgreSQL          │
│    Table: agent_tasks  │
│    Status: pending     │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 2. Check Dependencies  │
│    Table:              │
│    task_dependencies   │
└────────┬───────────────┘
         │ NO DEPS
         ▼
┌────────────────────────┐
│ 3. Publish to Redis    │
│    LPUSH task_queue    │
│    Task ID + Priority  │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 4. Worker Subscribes   │
│    BRPOP task_queue    │
│    Blocking wait       │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 5. Update Task Status  │
│    PostgreSQL          │
│    Status: running     │
│    worker_id: {id}     │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 6. Execute Task        │
│    Business Logic      │
│    External APIs       │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 7. Store Results       │
│    PostgreSQL          │
│    Status: completed   │
│    result JSONB        │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ 8. Publish Event       │
│    Redis Pub/Sub       │
│    Channel: task:done  │
└────────┬───────────────┘
         │
         ▼
   [Notify Subscribers]
```

### 2.5 Audit Trail Flow

```
[System Event]
        │
        ▼
┌────────────────────────┐
│ 1. Capture Event       │
│    Event metadata      │
│    Timestamp, actor    │
│    Action, resource    │
└────────┬───────────────┘
         │
         ├──────────────────────────┐
         │                          │
         ▼                          ▼
┌────────────────────┐    ┌────────────────────┐
│ 2A. PostgreSQL     │    │ 2B. File System    │
│ Table: audit_logs  │    │ Path: data/audit/  │
│ Structured data    │    │ {date}/{event}.log │
└────────┬───────────┘    └────────┬───────────┘
         │                          │
         ▼                          ▼
┌────────────────────┐    ┌────────────────────┐
│ 3A. Sovereign      │    │ 3B. Backup Script  │
│ Schema Integration │    │ Rotates old logs   │
│ reflex_audit table │    │ Compresses archives│
└────────┬───────────┘    └────────┬───────────┘
         │                          │
         └──────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ 4. Prometheus Metrics │
        │ Counter: audit_events │
        │ Labels: action, user  │
        └───────────┬───────────┘
                    │
                    ▼
            [Grafana Dashboard]
```

---

## 3. Service-Level Data Flow

### 3.1 Orchestrator → Database Interactions

```
┌─────────────────────────────────────────────┐
│         PROJECT-AI ORCHESTRATOR             │
│                                             │
│  ┌─────────────────────────────────┐       │
│  │  SQLAlchemy ORM / Raw SQL       │       │
│  │  Connection Pool: 20 + 10       │       │
│  └───────────┬─────────────────────┘       │
│              │                              │
└──────────────┼──────────────────────────────┘
               │
               │ TCP/IP (5432)
               │ Protocol: PostgreSQL Wire Protocol
               │
               ▼
┌──────────────────────────────────────────────┐
│           POSTGRESQL (pgvector)              │
│                                              │
│  ┌────────────────┐  ┌────────────────┐    │
│  │  Query Parser  │→ │ Query Planner  │    │
│  └────────────────┘  └────────┬───────┘    │
│                               │             │
│                               ▼             │
│                      ┌────────────────┐     │
│                      │  Execution     │     │
│                      │  Engine        │     │
│                      └────────┬───────┘     │
│                               │             │
│                               ▼             │
│  ┌────────────────────────────────────┐    │
│  │  Shared Buffers (256MB)            │    │
│  │  ┌──────┐ ┌──────┐ ┌──────┐       │    │
│  │  │ Data │ │ Index│ │Vector│       │    │
│  │  │ Pages│ │ Pages│ │ Data │       │    │
│  │  └──────┘ └──────┘ └──────┘       │    │
│  └────────────────┬───────────────────┘    │
│                   │                         │
│                   ▼                         │
│          ┌─────────────────┐               │
│          │  WAL (Write     │               │
│          │  Ahead Log)     │               │
│          └────────┬────────┘               │
│                   │                         │
└───────────────────┼─────────────────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ Docker Volume:   │
          │ postgres-data    │
          │                  │
          │ /var/lib/        │
          │ postgresql/data/ │
          └──────────────────┘
```

### 3.2 Orchestrator → Redis Interactions

```
┌─────────────────────────────────────────────┐
│         PROJECT-AI ORCHESTRATOR             │
│                                             │
│  ┌─────────────────────────────────┐       │
│  │  redis-py Client                │       │
│  │  Connection Pool: 50            │       │
│  └───────────┬─────────────────────┘       │
│              │                              │
└──────────────┼──────────────────────────────┘
               │
               │ TCP/IP (6379)
               │ Protocol: RESP (Redis Serialization Protocol)
               │
               ▼
┌──────────────────────────────────────────────┐
│               REDIS 7                        │
│                                              │
│  ┌────────────────────────────────────┐     │
│  │  Command Parser                    │     │
│  └────────────┬───────────────────────┘     │
│               │                              │
│               ▼                              │
│  ┌────────────────────────────────────┐     │
│  │  In-Memory Data Structures         │     │
│  │  ┌──────┐ ┌──────┐ ┌──────┐       │     │
│  │  │String│ │ List │ │ Hash │       │     │
│  │  └──────┘ └──────┘ └──────┘       │     │
│  │  ┌──────┐ ┌──────┐ ┌──────┐       │     │
│  │  │ Set  │ │ZSet  │ │Stream│       │     │
│  │  └──────┘ └──────┘ └──────┘       │     │
│  └────────────┬───────────────────────┘     │
│               │                              │
│               ▼                              │
│  ┌────────────────────────────────────┐     │
│  │  Persistence Layer                 │     │
│  │  ┌──────────────────────────┐     │     │
│  │  │ AOF (Append-Only File)   │     │     │
│  │  │ appendonly.aof           │     │     │
│  │  │ fsync: everysec          │     │     │
│  │  └──────────┬───────────────┘     │     │
│  └─────────────┼────────────────────┘      │
│                │                             │
└────────────────┼─────────────────────────────┘
                 │
                 ▼
        ┌──────────────────┐
        │ Docker Volume:   │
        │ redis-data       │
        │                  │
        │ /data/           │
        │ appendonly.aof   │
        └──────────────────┘
```

### 3.3 MCP Gateway Data Flow

```
┌─────────────────────────────────────────────┐
│            MCP GATEWAY                      │
│                                             │
│  ┌─────────────────────────────────┐       │
│  │  MCP Protocol Handler           │       │
│  │  • Server registration          │       │
│  │  • Tool invocation routing      │       │
│  │  • Response aggregation         │       │
│  └───────┬───────────┬─────────────┘       │
│          │           │                      │
└──────────┼───────────┼──────────────────────┘
           │           │
           │           │
           ▼           ▼
    ┌──────────┐  ┌──────────┐
    │PostgreSQL│  │  Redis   │
    │  (Shared)│  │  (DB 1)  │
    └──────────┘  └──────────┘
           │           │
           ▼           ▼
    ┌──────────────────────┐
    │  MCP Tables:         │
    │  • mcp_servers       │
    │  • mcp_tools         │
    │  • mcp_executions    │
    │                      │
    │  MCP Cache:          │
    │  • Tool metadata     │
    │  • Server status     │
    │  • Recent responses  │
    └──────────────────────┘
```

---

## 4. Data Persistence Layers

### 4.1 Three-Tier Storage Model

```
┌─────────────────────────────────────────────────────────────┐
│                    TIER 1: HOT DATA                         │
│                  (Redis In-Memory)                          │
│                                                             │
│  • Active sessions (TTL: 24h)                              │
│  • Task queue (real-time)                                  │
│  • API response cache (TTL: 1h)                            │
│  • Rate limiting counters (TTL: 1m)                        │
│                                                             │
│  Max Memory: 512MB | Eviction: LRU                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Cache Miss / Write-Through
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    TIER 2: WARM DATA                        │
│                 (PostgreSQL Active)                         │
│                                                             │
│  • User accounts (indexed)                                 │
│  • Recent conversations (30 days)                          │
│  • Vector embeddings (active set)                          │
│  • Audit logs (90 days)                                    │
│  • Knowledge base (frequently accessed)                    │
│                                                             │
│  Shared Buffers: 256MB | Effective Cache: 1GB              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ Archival Policy
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    TIER 3: COLD DATA                        │
│                  (File System Archive)                      │
│                                                             │
│  • Old audit logs (compressed)                             │
│  • Historical backups                                      │
│  • Archived conversations (>90 days)                       │
│  • Large file uploads                                      │
│                                                             │
│  Location: data/archive/ | Format: tar.gz                  │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Data Write Path (Full Flow)

```
[Application Write]
        │
        ▼
┌────────────────────┐
│ 1. Write to Redis  │ ◄─── Cache-aside pattern
│    (cache update)  │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ 2. Begin TX        │
│    PostgreSQL      │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ 3. Write to Table  │
│    INSERT/UPDATE   │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ 4. Update Indexes  │
│    B-Tree, GIN,    │
│    IVFFlat         │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ 5. Write WAL       │
│    (Write-Ahead    │
│     Logging)       │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ 6. Commit TX       │
│    fsync to disk   │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ 7. Redis Pub/Sub   │
│    Notify watchers │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ 8. Audit Log       │
│    Record change   │
└────────┬───────────┘
         │
         ▼
   [Write Complete]
```

---

## 5. Backup and Recovery Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKUP STRATEGY                          │
└─────────────────────────────────────────────────────────────┘

POSTGRESQL BACKUP
─────────────────
┌──────────────┐
│  PostgreSQL  │
│  Primary DB  │
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ WAL Archive  │  │  pg_dump     │
│ Continuous   │  │  Daily Full  │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌──────────────────┐
       │  Backup Storage  │
       │  /backups/pgsql/ │
       └──────────────────┘

REDIS BACKUP
────────────
┌──────────────┐
│    Redis     │
│  In-Memory   │
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ AOF File     │  │  RDB Snapshot│
│ Continuous   │  │  On Shutdown │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌──────────────────┐
       │  redis-data      │
       │  Docker Volume   │
       └──────────────────┘

FILE SYSTEM BACKUP
──────────────────
┌──────────────┐
│ Application  │
│ Data Files   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  tar + gzip  │
│  Daily Cron  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  data/backups/   │
│  {date}.tar.gz   │
└──────────────────┘
```

---

## 6. Monitoring Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 APPLICATION METRICS                         │
└─────────────────────────────────────────────────────────────┘

        ┌──────────────┐       ┌──────────────┐
        │ Orchestrator │       │  MCP Gateway │
        │  /metrics    │       │  /metrics    │
        └──────┬───────┘       └──────┬───────┘
               │                      │
               └──────────┬───────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │   PROMETHEUS   │
                 │   Scraper      │
                 │   15s interval │
                 └────────┬───────┘
                          │
                          ▼
                 ┌────────────────┐
                 │ Time-Series DB │
                 │ 15 day retention│
                 │ prometheus-data│
                 └────────┬───────┘
                          │
                          ▼
                 ┌────────────────┐
                 │    GRAFANA     │
                 │   Dashboards   │
                 │   Alerts       │
                 └────────────────┘
```

---

## 7. Summary Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE DATA FLOW                       │
│                                                             │
│  User Request                                               │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────┐                                               │
│  │  API    │─────────┬────────────┬────────────┐          │
│  └─────────┘         │            │            │          │
│       │              │            │            │          │
│       │              ▼            ▼            ▼          │
│       │         ┌────────┐  ┌────────┐  ┌────────┐       │
│       │         │ Redis  │  │Postgres│  │ Files  │       │
│       │         │ Cache  │  │  ACID  │  │ Blob   │       │
│       │         └───┬────┘  └───┬────┘  └───┬────┘       │
│       │             │           │           │            │
│       │             └───────┬───┴───────────┘            │
│       │                     │                            │
│       │                     ▼                            │
│       │            ┌─────────────────┐                   │
│       │            │ Docker Volumes  │                   │
│       │            │ & Bind Mounts   │                   │
│       │            └────────┬────────┘                   │
│       │                     │                            │
│       │                     ▼                            │
│       │            ┌─────────────────┐                   │
│       │            │ Host Filesystem │                   │
│       │            │ Persistent Disk │                   │
│       │            └─────────────────┘                   │
│       │                                                   │
│       ▼                                                   │
│  [Response]                                               │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

**END OF DATA FLOW DIAGRAM**
