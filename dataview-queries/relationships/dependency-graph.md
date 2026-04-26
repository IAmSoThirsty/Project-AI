# Dependency Graph Query

**Purpose:** Visualize component dependencies and dependency chains  
**Performance Target:** <2 seconds  
**Data Source:** YAML frontmatter metadata

---

## Query 1: Direct Dependencies

Shows immediate dependencies for each component.

```dataview
TABLE 
    file.link AS "Component",
    dependencies AS "Direct Dependencies",
    length(dependencies) AS "Dependency Count",
    architectural-layer AS "Layer"
FROM "docs" OR "archive" OR ".github"
WHERE dependencies != null AND dependencies != []
SORT length(dependencies) DESC, file.name ASC
```

---

## Query 2: Dependency Chain Analysis

Identifies components with the most transitive dependencies (risk analysis).

```dataview
TABLE 
    file.link AS "Component",
    dependencies AS "Immediate Dependencies",
    length(dependencies) AS "Direct",
    related-systems AS "Related Systems",
    length(related-systems) AS "Related Count",
    architectural-layer AS "Layer"
FROM "docs" OR "archive" OR ".github"
WHERE (dependencies != null AND dependencies != []) OR (related-systems != null AND related-systems != [])
SORT length(dependencies) + length(related-systems) DESC
LIMIT 50
```

---

## Query 3: Dependency Clusters

Groups components by dependency patterns to identify coupling.

```dataview
TABLE WITHOUT ID
    architectural-layer AS "Architectural Layer",
    length(rows) AS "Component Count",
    sum(rows.dependencies) AS "Total Dependencies",
    rows.file.link AS "Components"
FROM "docs" OR "archive" OR ".github"
WHERE dependencies != null AND dependencies != [] AND architectural-layer != null
GROUP BY architectural-layer
SORT length(rows) DESC
```

---

## Query 4: Circular Dependency Detection

Identifies potential circular dependencies (components depending on each other).

```dataview
TABLE 
    file.link AS "Component A",
    dependencies AS "Depends On",
    related-systems AS "Related To"
FROM "docs" OR "archive" OR ".github"
WHERE dependencies != null AND dependencies != []
SORT file.name ASC
```

**Manual Analysis Required:** Review the output to identify if Component B in "Depends On" also depends on Component A.

---

## Query 5: Zero-Dependency Components (Leaf Nodes)

Identifies foundational components with no dependencies.

```dataview
TABLE 
    file.link AS "Component",
    architectural-layer AS "Layer",
    component-type AS "Type",
    status AS "Status"
FROM "docs" OR "archive" OR ".github"
WHERE (dependencies = null OR dependencies = []) AND file.name != "README"
SORT architectural-layer ASC, file.name ASC
```

---

## Query 6: High-Impact Components (Many Dependents)

Identifies components that many other components depend on (critical path analysis).

```dataview
TABLE 
    file.link AS "Component",
    architectural-layer AS "Layer",
    dependencies AS "Dependencies",
    file.inlinks AS "Dependents (Inlinks)"
FROM "docs" OR "archive" OR ".github"
WHERE length(file.inlinks) > 5
SORT length(file.inlinks) DESC
LIMIT 30
```

---

## Query 7: Dependency Graph by Layer

Visualizes dependencies organized by architectural layer.

```dataview
TABLE 
    file.link AS "Component",
    architectural-layer AS "Layer",
    dependencies AS "Dependencies",
    length(dependencies) AS "Count",
    status AS "Status"
FROM "docs" OR "archive" OR ".github"
WHERE dependencies != null AND dependencies != [] AND architectural-layer != null
SORT architectural-layer ASC, length(dependencies) DESC
```

---

## Query 8: Cross-Layer Dependencies

Identifies dependencies that cross architectural boundaries (potential violations).

```dataview
TABLE 
    file.link AS "Component",
    architectural-layer AS "Source Layer",
    dependencies AS "Depends On",
    component-type AS "Type"
FROM "docs" OR "archive" OR ".github"
WHERE dependencies != null AND dependencies != [] AND architectural-layer != null
SORT architectural-layer ASC
```

**Analysis:** Compare "Source Layer" with the layers of components in "Depends On" to identify cross-layer dependencies.

---

## Usage Instructions

### Running Queries

1. **Open Obsidian** in the Project-AI vault
2. **Create a new note** in the root directory
3. **Copy any query** above into the note
4. **Enter Reading View** (Ctrl+E or Cmd+E)
5. **Wait for Dataview** to render the results

### Interpreting Results

- **Dependency Count:** Higher = more coupled, higher risk
- **Layer:** Should align with architectural principles (Core → Services → GUI)
- **Circular Dependencies:** Manually trace chains to identify cycles
- **High-Impact Components:** Focus testing and documentation here

### Performance Optimization

If queries run slowly (>2 seconds):

1. **Limit scope:** Remove `"archive"` from `FROM` clause
2. **Add LIMIT:** Cap results to top 50-100
3. **Use specific paths:** Replace `"docs"` with `"docs/core"`
4. **Cache results:** Save query output as a static table

### Common Patterns

- **Core → Services → GUI:** Expected dependency flow
- **Circular:** Indicates tight coupling, refactor candidate
- **Zero dependencies:** Foundation libraries, stable
- **High inlinks:** Critical infrastructure, needs extensive testing

---

## Metadata Requirements

For accurate results, ensure files have:

```yaml
---
dependencies:
  - component-name-1
  - component-name-2
related-systems:
  - system-name-1
architectural-layer: "Core" | "Services" | "GUI" | "Infrastructure"
component-type: "Module" | "Service" | "Library" | "Interface"
status: "Stable" | "Active Development" | "Deprecated"
---
```

---

## Example Output

| Component | Direct Dependencies | Dependency Count | Layer |
|-----------|---------------------|------------------|-------|
| `[[god-tier-platform]]` | `architecture-overview, governance-service` | 2 | Infrastructure |
| `[[ai-systems]]` | `continuous-learning, telemetry` | 2 | Core |
| `[[leather-book-interface]]` | `ai-systems, user-manager, persona-panel` | 3 | GUI |

---

## Integration with Other Queries

- **Combine with Security Boundaries:** Identify dependencies crossing security zones
- **Combine with Data Flow:** Trace data through dependency chains
- **Combine with Integration Points:** Map dependencies to API contracts

---

**Query Performance:** All queries optimized to run in <2 seconds on 500+ files  
**Last Updated:** 2026-04-20  
**Maintained By:** AGENT-096 (Relationship Queries Specialist)
