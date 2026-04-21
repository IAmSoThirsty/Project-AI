# Integration Points Query

**Purpose:** Map system integrations, API contracts, and communication patterns  
**Performance Target:** <2 seconds  
**Data Source:** YAML frontmatter metadata + integration catalog

---

## Query 1: All Integration Points

Lists all documented integration points across the system.

```dataview
TABLE 
    file.link AS "Integration Point",
    integration-type AS "Type",
    provider-system AS "Provider",
    consumer-systems AS "Consumers",
    status AS "Status"
FROM "docs" OR ".github"
WHERE integration-type != null OR provider-system != null OR consumer-systems != null
SORT integration-type ASC, file.name ASC
```

---

## Query 2: Integration Points by Type

Groups integrations by type (API, Event, Data, Security, etc.).

```dataview
TABLE WITHOUT ID
    integration-type AS "Integration Type",
    length(rows) AS "Count",
    rows.file.link AS "Integration Points"
FROM "docs" OR ".github"
WHERE integration-type != null
GROUP BY integration-type
SORT length(rows) DESC
```

---

## Query 3: Provider-Consumer Matrix

Shows which systems provide services and which consume them.

```dataview
TABLE 
    file.link AS "Integration",
    provider-system AS "Provider System",
    consumer-systems AS "Consumer Systems",
    length(consumer-systems) AS "Consumer Count",
    api-contract AS "Contract"
FROM "docs" OR ".github"
WHERE provider-system != null AND consumer-systems != null
SORT length(consumer-systems) DESC
LIMIT 40
```

---

## Query 4: External Service Integrations

Identifies integrations with external third-party services.

```dataview
TABLE 
    file.link AS "Integration",
    external-service AS "External Service",
    integration-type AS "Type",
    authentication-method AS "Auth Method",
    status AS "Status"
FROM "docs" OR ".github" OR "archive"
WHERE external-service != null OR contains(tags, "external-integration")
SORT external-service ASC
```

---

## Query 5: API Contract Catalog

Lists all documented API contracts for integration validation.

```dataview
TABLE 
    file.link AS "Integration",
    api-contract AS "Contract Type",
    provider-system AS "Provider",
    integration-pattern AS "Pattern",
    code-location AS "Code Location"
FROM "docs" OR ".github"
WHERE api-contract != null
SORT provider-system ASC
```

---

## Query 6: Integration Patterns

Groups integrations by architectural pattern (Pub/Sub, RPC, Event-Driven, etc.).

```dataview
TABLE 
    file.link AS "Integration",
    integration-pattern AS "Pattern",
    provider-system AS "Provider",
    consumer-systems AS "Consumers",
    performance-target AS "Performance"
FROM "docs" OR ".github"
WHERE integration-pattern != null
SORT integration-pattern ASC, file.name ASC
```

---

## Query 7: Unstable Integrations

Identifies integrations that are deprecated, experimental, or broken.

```dataview
TABLE 
    file.link AS "Integration",
    status AS "Status",
    provider-system AS "Provider",
    consumer-systems AS "Consumers",
    known-issues AS "Known Issues"
FROM "docs" OR ".github" OR "archive"
WHERE status = "Deprecated" OR status = "Experimental" OR status = "Broken" OR status = "In Progress"
SORT status ASC, file.name ASC
```

---

## Query 8: Critical Integrations (High Fan-Out)

Identifies integrations with many consumers (failure = widespread impact).

```dataview
TABLE 
    file.link AS "Integration",
    provider-system AS "Provider",
    consumer-systems AS "Consumers",
    length(consumer-systems) AS "Consumer Count",
    error-handling AS "Error Strategy"
FROM "docs" OR ".github"
WHERE consumer-systems != null AND length(consumer-systems) > 3
SORT length(consumer-systems) DESC
LIMIT 30
```

---

## Query 9: Integration Health Dashboard

Real-time view of integration status across the system.

```dataview
TABLE 
    file.link AS "Integration",
    provider-system AS "Provider",
    status AS "Status",
    performance-target AS "Target",
    last-tested AS "Last Tested"
FROM "docs" OR ".github"
WHERE provider-system != null
SORT status ASC, last-tested DESC
```

---

## Query 10: Missing Integration Documentation

Identifies files that reference integrations but lack documentation.

```dataview
TABLE 
    file.link AS "File",
    integration-type AS "Type",
    provider-system AS "Provider",
    consumer-systems AS "Consumers"
FROM "docs" OR ".github"
WHERE (integration-type != null OR provider-system != null) AND (api-contract = null OR code-location = null)
SORT file.name ASC
```

---

## Query 11: Cross-Service Communication

Maps communication patterns between microservices/modules.

```dataview
TABLE 
    file.link AS "Integration",
    provider-system AS "From",
    consumer-systems AS "To",
    communication-protocol AS "Protocol",
    data-format AS "Format"
FROM "docs" OR ".github"
WHERE communication-protocol != null OR data-format != null
SORT provider-system ASC
```

---

## Query 12: Authentication & Authorization Matrix

Shows which integrations require authentication and what methods are used.

```dataview
TABLE 
    file.link AS "Integration",
    provider-system AS "Provider",
    authentication-method AS "Auth Method",
    authorization-level AS "Authorization",
    security-boundary AS "Security Zone"
FROM "docs" OR ".github"
WHERE authentication-method != null OR authorization-level != null
SORT security-boundary ASC, authentication-method ASC
```

---

## Usage Instructions

### Running Queries

1. **Open Obsidian** in the Project-AI vault
2. **Create a new note** or open existing integration documentation
3. **Copy any query** above into the note
4. **Enter Reading View** (Ctrl+E or Cmd+E)
5. **Results render automatically** via Dataview plugin

### Interpreting Results

- **Provider System:** The system exposing the API/service
- **Consumer Systems:** Systems that depend on the provider
- **Integration Type:** API, Event, Data, Security, etc.
- **Status:** Stable, Experimental, Deprecated, Broken
- **Performance Target:** Expected latency/throughput

### Performance Optimization

If queries run slowly:

1. **Narrow scope:** `FROM "docs/core"` instead of `FROM "docs"`
2. **Add LIMIT:** Cap at 50-100 results for large datasets
3. **Use specific tags:** Filter by `tags` for targeted queries
4. **Cache results:** Save static snapshots for historical analysis

### Common Use Cases

1. **Integration Health Check:** Run Query 9 daily
2. **Failure Impact Analysis:** Query 8 shows critical dependencies
3. **External Service Audit:** Query 4 for third-party risk assessment
4. **API Contract Validation:** Query 5 for contract testing
5. **Deprecation Planning:** Query 7 for migration candidates

---

## Metadata Requirements

For accurate results, ensure integration documentation has:

```yaml
---
integration-type: "API" | "Event" | "Data" | "Security" | "External"
provider-system: "system-name"
consumer-systems:
  - consumer-1
  - consumer-2
api-contract: "REST" | "gRPC" | "Event Bus" | "Direct Call"
integration-pattern: "Request/Reply" | "Pub/Sub" | "Event-Driven" | "Polling"
authentication-method: "JWT" | "API Key" | "OAuth2" | "None"
authorization-level: "Public" | "Authenticated" | "Admin" | "System"
communication-protocol: "HTTP" | "WebSocket" | "AMQP" | "gRPC"
data-format: "JSON" | "Protobuf" | "XML" | "Binary"
code-location: "src/app/core/module.py:123-456"
error-handling: "Retry" | "Fail-Fast" | "Circuit Breaker" | "Fallback"
performance-target: "<100ms" | "<1s" | "<5s"
status: "Stable" | "Experimental" | "Deprecated" | "Broken"
last-tested: 2026-04-20
security-boundary: "Public" | "Internal" | "Core" | "Kernel"
external-service: "OpenAI" | "Hugging Face" | "GitHub" | null
---
```

---

## Example Output

### Query 1: All Integration Points

| Integration Point | Type | Provider | Consumers | Status |
|-------------------|------|----------|-----------|--------|
| `[[FourLaws-Ethics]]` | Security | FourLaws | `[All AI Systems]` | Stable |
| `[[OpenAI-API]]` | External | Intelligence Engine | `[Chat, Learning, Image Gen]` | Stable |
| `[[Memory-Context]]` | Data | MemoryEngine | `[Intelligence Engine]` | Stable |

### Query 3: Provider-Consumer Matrix

| Integration | Provider System | Consumer Systems | Consumer Count | Contract |
|-------------|-----------------|------------------|----------------|----------|
| `[[FourLaws]]` | FourLaws | `[AIPersona, Memory, Learning, Override, Plugin]` | 5 | Direct Call |
| `[[User-Auth]]` | UserManager | `[GUI, Web API, CLI]` | 3 | REST API |

---

## Integration with Other Queries

- **Combine with Dependency Graph:** Trace integration chains through dependencies
- **Combine with Data Flow:** Map data transformations across integrations
- **Combine with Security Boundaries:** Validate authorization across zones

---

## Integration Catalog Reference

See `INTEGRATION_POINTS_CATALOG.md` for:
- Detailed API contracts
- Code examples
- Error handling strategies
- Performance benchmarks
- Integration patterns

**Total Documented Integrations:** 80+  
**External Service Integrations:** 12+  
**Core AI Integrations:** 15+

---

**Query Performance:** All queries optimized to run in <2 seconds  
**Last Updated:** 2026-04-20  
**Maintained By:** AGENT-096 (Relationship Queries Specialist)
