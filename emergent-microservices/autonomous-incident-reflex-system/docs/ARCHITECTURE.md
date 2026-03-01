# Architecture

## Autonomous Incident Reflex System - System Architecture

### Overview

This service follows a layered architecture pattern with clear separation of concerns.

### Components

```
┌─────────────────────────────────────────────────┐
│                 API Layer                        │
│  (FastAPI Routes, Request/Response Models)       │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────┐
│             Middleware Layer                      │
│  (Auth, Rate Limit, Metrics, Request ID)         │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────┐
│            Business Logic Layer                   │
│  (Services, Domain Logic, Validation)            │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────┐
│           Data Access Layer                       │
│  (Repositories, Database Abstraction)            │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────┐
│              Database                             │
│  (in_memory)     │
└──────────────────────────────────────────────────┘
```

### Layer Responsibilities

**API Layer**: HTTP request handling, serialization, OpenAPI documentation  
**Middleware Layer**: Cross-cutting concerns (auth, logging, metrics)  
**Business Logic**: Domain rules, validation, orchestration  
**Data Access**: Database operations, transaction management  

### Key Design Patterns

- **Repository Pattern**: Database abstraction
- **Dependency Injection**: Service instantiation
- **Middleware Chain**: Request processing pipeline
- **Observer Pattern**: Metrics and logging

### Technology Stack

- **Framework**: FastAPI (async)
- **Database**: in_memory
- **Metrics**: Prometheus
- **Logging**: Structured JSON
- **Container**: Docker
- **Orchestration**: Kubernetes
