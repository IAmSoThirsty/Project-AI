# Query Pattern (CQRS) in Project-AI

## Overview

Queries are read-only operations that retrieve data from denormalized read models. They are separated from commands (writes) to optimize for different access patterns and scale independently.

## Query Architecture

```
Client Query → Query Handler → Read Model Database → Results
```

## Query Base Classes

```python

# application/queries/base.py

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

@dataclass
class Query(ABC):
    """Base query for CQRS read operations."""
    filters: Dict[str, Any] = field(default_factory=dict)
    page: int = 1
    page_size: int = 20
    sort_by: Optional[str] = None
    sort_order: str = "asc"

@dataclass
class QueryResult:
    """Result of query execution."""
    data: List[Dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 20
    has_more: bool = False
```

## Query Handlers

```python

# application/query_handlers/user_query_handler.py

import logging
from typing import List
from uuid import UUID
from application.queries.base import Query, QueryResult

logger = logging.getLogger(__name__)

class GetUserQuery(Query):
    """Query: Get user by ID."""
    user_id: UUID = None

class GetUsersQuery(Query):
    """Query: Get users with filtering."""
    pass

class UserQueryHandler:
    """Handler for user queries."""

    def __init__(self, read_model_store):
        self.store = read_model_store

    def handle_get_user(self, query: GetUserQuery) -> QueryResult:
        """Get single user."""
        user = self.store.get_user(query.user_id)

        if not user:
            return QueryResult(data=[], total_count=0)

        return QueryResult(
            data=[user],
            total_count=1,
            page=1,
            page_size=1
        )

    def handle_get_users(self, query: GetUsersQuery) -> QueryResult:
        """Get users with pagination."""
        users = self.store.get_users(
            filters=query.filters,
            page=query.page,
            page_size=query.page_size,
            sort_by=query.sort_by,
            sort_order=query.sort_order
        )

        total = self.store.count_users(query.filters)

        return QueryResult(
            data=users,
            total_count=total,
            page=query.page,
            page_size=query.page_size,
            has_more=(query.page * query.page_size) < total
        )
```

## Related Documentation

- **[Command Pattern](../command/README.md)** - CQRS write side
- **[Read Models](query_models.md)** - Denormalized views
- **[Event Projections](../event/event_projections.md)** - Read model updates
