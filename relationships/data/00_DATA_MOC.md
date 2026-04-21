# Data Systems MOC - Persistence, Schemas & Infrastructure

> **📍 Location**: `relationships/data/00_DATA_MOC.md`  
> **🎯 Purpose**: Data architecture and persistence layer documentation  
> **👥 Audience**: Database engineers, data architects, developers  
> **🔄 Status**: Production-Ready ✓

---

## 🗺️ Data Architecture

```
Data Systems
│
├─💾 PERSISTENCE LAYER
│  ├─ [[00-DATA-INFRASTRUCTURE-OVERVIEW.md|Infrastructure Overview]] ⭐ Main
│  ├─ [[01_persistence_patterns.md|Persistence Patterns]]
│  └─ [[02_database_schemas.md|Database Schemas]]
│
├─🔒 DATA SECURITY
│  ├─ [[DATA_ENCRYPTION_PRIVACY_AUDIT_REPORT.md|Encryption Audit]]
│  ├─ [[DATABASE_PERSISTENCE_AUDIT_REPORT.md|Database Audit]]
│  └─ [[docs/ASYMMETRIC_SECURITY_FRAMEWORK.md|Asymmetric Security]]
│
└─🔄 DATA FLOWS
   └─ [[relationships/core-ai/00-INDEX.md|Core AI Data Flows]]
```

---

## 📊 Data Storage Patterns

### JSON Persistence (Local Tier)
- **Users**: `data/users.json`
- **AI Persona**: `data/ai_persona/state.json`
- **Memory**: `data/memory/knowledge.json`
- **Learning Requests**: `data/learning_requests/requests.json`

### Database (Situational/God Tier)
- **PostgreSQL**: Production database
- **Schema**: Defined in `02_database_schemas.md`

---

## 📋 Metadata

```yaml
---
title: "Data Systems MOC"
type: moc
category: data
audience: [database-engineers, data-architects, developers]
status: production
version: 1.0.0
created: 2025-01-20
tags:
  - moc
  - data
  - persistence
  - database
  - schemas
related_mocs:
  - "[[docs/00_INDEX.md|Master Index]]"
  - "[[docs/security_compliance/00_SECURITY_MOC.md|Security MOC]]"
  - "[[relationships/core-ai/00-INDEX.md|Core AI MOC]]"
---
```

---

**MOC Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Status**: Production-Ready ✓
