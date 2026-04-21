# Data Flow Query

**Purpose:** Track data sources, sinks, transformations, and flow patterns  
**Performance Target:** <2 seconds  
**Data Source:** YAML frontmatter metadata + architecture documentation

---

## Query 1: Data Sources (Entry Points)

Identifies all external data sources feeding the system.

```dataview
TABLE 
    file.link AS "Data Source",
    data-source-type AS "Type",
    data-format AS "Format",
    data-sensitivity AS "Sensitivity",
    validation-rules AS "Validation"
FROM "docs" OR ".github" OR "archive"
WHERE data-source-type != null OR contains(tags, "data-source")
SORT data-sensitivity DESC, file.name ASC
```

---

## Query 2: Data Sinks (Exit Points)

Identifies where data leaves the system (persistence, external APIs, logs).

```dataview
TABLE 
    file.link AS "Data Sink",
    data-sink-type AS "Type",
    persistence-layer AS "Storage",
    encryption-method AS "Encryption",
    retention-policy AS "Retention"
FROM "docs" OR ".github" OR "archive"
WHERE data-sink-type != null OR persistence-layer != null OR contains(tags, "data-sink")
SORT data-sensitivity DESC, file.name ASC
```

---

## Query 3: Data Transformations

Maps data transformation points (validation, sanitization, enrichment).

```dataview
TABLE 
    file.link AS "Transformation",
    transformation-type AS "Type",
    input-format AS "Input",
    output-format AS "Output",
    code-location AS "Code Location"
FROM "docs" OR ".github"
WHERE transformation-type != null OR (input-format != null AND output-format != null)
SORT transformation-type ASC, file.name ASC
```

---

## Query 4: Data Flow Paths

Traces complete data flow paths from source to sink.

```dataview
TABLE 
    file.link AS "Data Flow",
    data-source AS "Source",
    data-transformations AS "Transformations",
    data-sink AS "Sink",
    data-flow-pattern AS "Pattern"
FROM "docs" OR ".github"
WHERE data-source != null AND data-sink != null
SORT data-flow-pattern ASC
```

---

## Query 5: Sensitive Data Tracking

Identifies flows handling PII, credentials, or classified data.

```dataview
TABLE 
    file.link AS "Data Flow",
    data-sensitivity AS "Sensitivity",
    encryption-method AS "Encryption",
    access-control AS "Access Control",
    audit-logging AS "Audit Logging"
FROM "docs" OR ".github" OR "archive"
WHERE data-sensitivity = "High" OR data-sensitivity = "Critical" OR data-sensitivity = "PII"
SORT data-sensitivity DESC
```

---

## Query 6: Data Validation Points

Maps where data validation occurs (input validation, schema checks, sanitization).

```dataview
TABLE 
    file.link AS "Validation Point",
    validation-type AS "Type",
    validation-rules AS "Rules",
    error-handling AS "On Failure",
    code-location AS "Code Location"
FROM "docs" OR ".github"
WHERE validation-type != null OR validation-rules != null
SORT validation-type ASC
```

---

## Query 7: Data Persistence Inventory

Catalogs all persistence layers (databases, files, caches, logs).

```dataview
TABLE 
    file.link AS "Persistence Layer",
    persistence-type AS "Type",
    storage-format AS "Format",
    backup-strategy AS "Backup",
    encryption-at-rest AS "Encrypted"
FROM "docs" OR ".github" OR "archive"
WHERE persistence-layer != null OR persistence-type != null OR contains(tags, "persistence")
SORT persistence-type ASC, file.name ASC
```

---

## Query 8: Data Format Conversion

Identifies format conversion points (JSON→Dict, CSV→DataFrame, etc.).

```dataview
TABLE 
    file.link AS "Conversion",
    input-format AS "Input Format",
    output-format AS "Output Format",
    conversion-library AS "Library/Method",
    data-loss-risk AS "Data Loss Risk"
FROM "docs" OR ".github"
WHERE input-format != null AND output-format != null AND input-format != output-format
SORT input-format ASC, output-format ASC
```

---

## Query 9: Real-Time Data Streams

Tracks streaming data flows (WebSocket, event streams, live updates).

```dataview
TABLE 
    file.link AS "Stream",
    stream-type AS "Type",
    data-source AS "Source",
    consumers AS "Consumers",
    throughput-target AS "Throughput"
FROM "docs" OR ".github"
WHERE stream-type != null OR data-flow-pattern = "Streaming" OR data-flow-pattern = "Event-Driven"
SORT throughput-target DESC
```

---

## Query 10: Data Aggregation Points

Identifies where data is aggregated, summarized, or analyzed.

```dataview
TABLE 
    file.link AS "Aggregation",
    aggregation-type AS "Type",
    input-sources AS "Input Sources",
    output-format AS "Output",
    aggregation-frequency AS "Frequency"
FROM "docs" OR ".github"
WHERE aggregation-type != null OR contains(transformation-type, "Aggregation")
SORT aggregation-frequency ASC
```

---

## Query 11: Data Quality Checks

Maps data quality validation (completeness, consistency, accuracy).

```dataview
TABLE 
    file.link AS "Quality Check",
    quality-dimension AS "Dimension",
    validation-rules AS "Rules",
    failure-action AS "On Failure",
    monitoring-enabled AS "Monitored"
FROM "docs" OR ".github"
WHERE quality-dimension != null OR contains(tags, "data-quality")
SORT quality-dimension ASC
```

---

## Query 12: Data Lineage

Traces data lineage from original source through all transformations.

```dataview
TABLE 
    file.link AS "Data Asset",
    original-source AS "Original Source",
    transformation-chain AS "Transformations",
    current-location AS "Current Location",
    data-age AS "Age"
FROM "docs" OR ".github"
WHERE original-source != null AND transformation-chain != null
SORT original-source ASC
```

---

## Query 13: Data Caching Layers

Identifies caching mechanisms and cache invalidation strategies.

```dataview
TABLE 
    file.link AS "Cache",
    cache-type AS "Type",
    cache-key-pattern AS "Key Pattern",
    ttl AS "TTL",
    invalidation-strategy AS "Invalidation"
FROM "docs" OR ".github"
WHERE cache-type != null OR contains(tags, "cache")
SORT cache-type ASC
```

---

## Query 14: Data Encryption Points

Maps where data is encrypted/decrypted (at rest, in transit, in memory).

```dataview
TABLE 
    file.link AS "Encryption Point",
    encryption-stage AS "Stage",
    encryption-method AS "Method",
    key-management AS "Key Management",
    data-sensitivity AS "Sensitivity"
FROM "docs" OR ".github" OR "archive"
WHERE encryption-method != null OR encryption-stage != null
SORT data-sensitivity DESC, encryption-stage ASC
```

---

## Usage Instructions

### Running Queries

1. **Open Obsidian** in the Project-AI vault
2. **Create a new note** for data flow analysis
3. **Copy any query** above into the note
4. **Enter Reading View** (Ctrl+E or Cmd+E)
5. **Dataview renders results** automatically

### Interpreting Results

- **Data Source:** Where data originates (user input, API, file, sensor)
- **Data Sink:** Where data is stored/sent (database, file, external API)
- **Transformation:** How data is modified (validation, enrichment, aggregation)
- **Sensitivity:** High/Critical data requires encryption and audit logging
- **Flow Pattern:** Batch, Streaming, Event-Driven, Request/Reply

### Performance Optimization

If queries run slowly:

1. **Limit scope:** `FROM "docs/core"` for specific subsystems
2. **Add LIMIT:** Cap at 50-100 results for large datasets
3. **Filter by tags:** Use `tags` for targeted queries
4. **Cache results:** Save snapshots for historical comparison

### Common Use Cases

1. **Data Privacy Audit:** Query 5 (Sensitive Data Tracking)
2. **Performance Analysis:** Query 9 (Real-Time Streams)
3. **Security Review:** Query 14 (Encryption Points)
4. **Data Quality:** Query 11 (Quality Checks)
5. **Compliance:** Query 12 (Data Lineage)

---

## Metadata Requirements

For accurate results, ensure data flow documentation has:

```yaml
---
# Data Sources
data-source-type: "User Input" | "API" | "File" | "Database" | "Sensor"
data-format: "JSON" | "CSV" | "XML" | "Binary" | "Text"
data-sensitivity: "Public" | "Internal" | "Confidential" | "High" | "Critical" | "PII"
validation-rules: ["schema-validation", "sanitization", "type-checking"]

# Data Sinks
data-sink-type: "Database" | "File" | "API" | "Log" | "Cache"
persistence-layer: "SQLite" | "JSON File" | "PostgreSQL" | "Redis"
encryption-method: "Fernet" | "AES-256" | "TLS" | "bcrypt" | "None"
retention-policy: "7 days" | "90 days" | "1 year" | "Indefinite"

# Transformations
transformation-type: "Validation" | "Sanitization" | "Enrichment" | "Aggregation"
input-format: "JSON"
output-format: "Dict"
conversion-library: "json.loads" | "pandas.read_csv" | "xmltodict"
data-loss-risk: "None" | "Low" | "Medium" | "High"

# Data Flow
data-source: "User Chat Input"
data-transformations:
  - "Input Validation"
  - "Intent Detection"
  - "Context Enrichment"
data-sink: "Conversation Log (JSON)"
data-flow-pattern: "Request/Reply" | "Event-Driven" | "Streaming" | "Batch"

# Data Quality
quality-dimension: "Completeness" | "Consistency" | "Accuracy" | "Timeliness"
failure-action: "Reject" | "Log Warning" | "Use Default" | "Retry"
monitoring-enabled: true | false

# Data Lineage
original-source: "User Input"
transformation-chain:
  - "Input Validation → Sanitization → Storage"
current-location: "data/memory/conversations.json"
data-age: "Real-time" | "24 hours" | "7 days"

# Caching
cache-type: "In-Memory" | "Redis" | "File-Based"
cache-key-pattern: "user:{user_id}:session:{session_id}"
ttl: "5 minutes" | "1 hour" | "24 hours"
invalidation-strategy: "TTL" | "Event-Based" | "Manual"

# Encryption
encryption-stage: "At Rest" | "In Transit" | "In Memory" | "In Use"
key-management: "Environment Variable" | "KMS" | "Hardcoded" | "User-Provided"

# Streaming
stream-type: "WebSocket" | "Event Bus" | "Message Queue"
throughput-target: "100 msg/sec" | "1000 msg/sec"

# Aggregation
aggregation-type: "Sum" | "Average" | "Count" | "Group By"
input-sources: ["source-1", "source-2"]
aggregation-frequency: "Real-time" | "Every 5 min" | "Daily"
---
```

---

## Example Output

### Query 1: Data Sources

| Data Source | Type | Format | Sensitivity | Validation |
|-------------|------|--------|-------------|------------|
| `[[User Chat Input]]` | User Input | Text | Internal | `[sanitization, intent-detection]` |
| `[[OpenAI API Response]]` | API | JSON | Internal | `[schema-validation]` |
| `[[GPS Coordinates]]` | Sensor | JSON | High | `[range-check, encryption]` |

### Query 4: Data Flow Paths

| Data Flow | Source | Transformations | Sink | Pattern |
|-----------|--------|-----------------|------|---------|
| `[[Chat Processing]]` | User Input | `[Validation, Intent, Memory]` | Conversation Log | Request/Reply |
| `[[Learning Request]]` | User Request | `[Ethics Check, Approval, Execution]` | Knowledge Base | Event-Driven |

### Query 5: Sensitive Data Tracking

| Data Flow | Sensitivity | Encryption | Access Control | Audit Logging |
|-----------|-------------|------------|----------------|---------------|
| `[[Location Tracking]]` | High | Fernet | Admin | Enabled |
| `[[User Passwords]]` | Critical | bcrypt | System | Enabled |
| `[[Emergency Contacts]]` | PII | AES-256 | User | Enabled |

---

## Integration with Other Queries

- **Combine with Dependency Graph:** Trace data flow through dependent components
- **Combine with Integration Points:** Map data exchange at integration boundaries
- **Combine with Security Boundaries:** Validate data encryption across zones

---

## Data Flow Catalog Reference

See these files for detailed data flow documentation:
- `INTEGRATION_POINTS_CATALOG.md` - API data contracts
- `SECURITY.md` - Encryption and data protection
- `docs/core/data_analysis.md` - Data processing pipelines
- `docs/core/memory_engine.md` - Memory persistence flows
- `docs/core/user_manager.md` - User data handling

---

**Query Performance:** All queries optimized to run in <2 seconds  
**Last Updated:** 2026-04-20  
**Maintained By:** AGENT-096 (Relationship Queries Specialist)
