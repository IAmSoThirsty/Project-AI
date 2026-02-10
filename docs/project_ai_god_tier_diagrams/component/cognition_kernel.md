# CognitionKernel - Central Intelligence Hub

## Overview

The CognitionKernel is the central intelligence component of Project-AI, responsible for understanding user intent, enriching context, and routing requests to appropriate handlers. It acts as the "brain" that transforms raw user input into actionable, context-rich requests.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    COGNITION KERNEL                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              INPUT PROCESSING PIPELINE                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                │
│    ┌───────────────────────┼───────────────────────┐        │
│    ↓                       ↓                       ↓        │
│  ┌──────────┐        ┌────────────┐        ┌─────────────┐ │
│  │ Intent   │        │  Entity    │        │  Semantic   │ │
│  │ Detector │        │ Extractor  │        │   Parser    │ │
│  │          │        │            │        │             │ │
│  │ • ML     │        │ • NER      │        │ • Grammar   │ │
│  │ • 30+    │        │ • spaCy    │        │ • Rules     │ │
│  │   cats   │        │ • Custom   │        │ • Pattern   │ │
│  └──────────┘        └────────────┘        └─────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            CONTEXT ENRICHMENT ENGINE                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                │
│    ┌───────────────────────┼───────────────────────┐        │
│    ↓                       ↓                       ↓        │
│  ┌──────────┐        ┌────────────┐        ┌─────────────┐ │
│  │   User   │        │  Session   │        │   Memory    │ │
│  │ Context  │        │  History   │        │  Context    │ │
│  │          │        │            │        │             │ │
│  │ • Profile│        │ • Previous │        │ • Relevant  │ │
│  │ • Prefs  │        │   ops      │        │   memories  │ │
│  │ • Perms  │        │ • Patterns │        │ • Knowledge │ │
│  └──────────┘        └────────────┘        └─────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               REQUEST ROUTER                           │ │
│  │  Maps intent → appropriate handler/agent              │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## Intent Detection System

### Machine Learning Classifier

```python
class IntentDetector:
    """
    ML-based intent classification system.
    
    Uses:
    - TF-IDF vectorization
    - Logistic Regression classifier
    - 30+ intent categories
    - Confidence scoring
    """
    
    def __init__(self):
        # Load pre-trained models
        self.vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
        self.classifier = joblib.load('models/intent_classifier.pkl')
        self.intent_mapping = self._load_intent_mapping()
        
        logger.info(f"IntentDetector initialized with {len(self.intent_mapping)} intents")
    
    def detect_intent(self, text: str) -> IntentResult:
        """
        Detect user intent from natural language text.
        
        Args:
            text: User's natural language input
        
        Returns:
            IntentResult with primary intent, confidence, and alternatives
        """
        # Preprocess text
        preprocessed = self._preprocess_text(text)
        
        # Vectorize
        features = self.vectorizer.transform([preprocessed])
        
        # Predict
        intent_label = self.classifier.predict(features)[0]
        probabilities = self.classifier.predict_proba(features)[0]
        confidence = probabilities.max()
        
        # Get alternative intents (top 3)
        top_indices = np.argsort(probabilities)[-3:][::-1]
        alternatives = [
            (self.classifier.classes_[idx], probabilities[idx])
            for idx in top_indices[1:]  # Exclude primary intent
        ]
        
        # Extract entities
        entities = self.extract_entities(text)
        
        return IntentResult(
            intent=intent_label,
            confidence=confidence,
            alternatives=alternatives,
            entities=entities,
            preprocessed_text=preprocessed
        )
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for intent detection.
        
        Steps:
        1. Lowercase
        2. Remove special characters (keep alphanumeric and spaces)
        3. Remove extra whitespace
        4. Lemmatization (optional)
        """
        # Lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities from text.
        
        Uses spaCy for NER:
        - PERSON: people names
        - ORG: organizations
        - DATE: dates and times
        - GPE: geopolitical entities
        - CARDINAL: numbers
        - etc.
        """
        import spacy
        
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        entities = []
        for ent in doc.ents:
            entities.append(Entity(
                type=ent.label_,
                value=ent.text,
                span=(ent.start_char, ent.end_char)
            ))
        
        return entities
```

### Intent Categories (30+)

```python
INTENT_CATEGORIES = {
    # Query intents
    'query.information': 'General information retrieval',
    'query.definition': 'Define a term or concept',
    'query.explanation': 'Explain how something works',
    'query.comparison': 'Compare two or more things',
    'query.status': 'Check status of something',
    
    # Command intents
    'command.execute': 'Execute a system command',
    'command.override': 'Override with master password',
    'command.cancel': 'Cancel an operation',
    'command.retry': 'Retry a failed operation',
    
    # Analysis intents
    'analysis.data': 'Analyze dataset',
    'analysis.pattern': 'Find patterns in data',
    'analysis.clustering': 'Cluster similar items',
    'analysis.statistics': 'Calculate statistics',
    'analysis.forecast': 'Forecast future values',
    
    # Generation intents
    'generation.image': 'Generate an image',
    'generation.report': 'Generate a report',
    'generation.code': 'Generate code',
    'generation.text': 'Generate text content',
    
    # Learning intents
    'learning.request': 'Learn new information',
    'learning.update': 'Update existing knowledge',
    'learning.forget': 'Forget specific information',
    
    # Memory intents
    'memory.search': 'Search past memories',
    'memory.recall': 'Recall specific memory',
    'memory.delete': 'Delete memories',
    
    # Security intents
    'security.scan': 'Search security resources',
    'security.audit': 'Perform security audit',
    'security.report': 'Report security issue',
    
    # Utility intents
    'location.track': 'Track location',
    'location.query': 'Query location info',
    'emergency.alert': 'Send emergency alert',
    'file.manage': 'Manage files',
    'file.upload': 'Upload file',
    'file.download': 'Download file',
    
    # Persona intents
    'persona.modify': 'Modify AI persona',
    'persona.query': 'Query persona state',
    'persona.reset': 'Reset persona to default',
    
    # System intents
    'system.configure': 'Configure system settings',
    'system.status': 'Check system status',
    'system.help': 'Get help',
    'system.exit': 'Exit application'
}
```

### Training Data Format

```python
training_data = [
    {
        'text': 'What is the capital of France?',
        'intent': 'query.information',
        'entities': [
            {'type': 'GPE', 'value': 'France', 'span': [23, 29]}
        ]
    },
    {
        'text': 'Generate an image of a sunset over mountains',
        'intent': 'generation.image',
        'entities': [
            {'type': 'SUBJECT', 'value': 'sunset over mountains', 'span': [23, 45]}
        ]
    },
    {
        'text': 'Analyze the sales data from last quarter',
        'intent': 'analysis.data',
        'entities': [
            {'type': 'DATA_TYPE', 'value': 'sales data', 'span': [12, 22]},
            {'type': 'DATE', 'value': 'last quarter', 'span': [28, 40]}
        ]
    },
    # ... thousands more examples
]
```

## Context Enrichment Engine

### User Context

```python
async def get_user_context(user_id: str) -> UserContext:
    """
    Retrieve comprehensive user context.
    
    Returns:
        UserContext with profile, preferences, and permissions
    """
    # Fetch from database
    user = await db.fetchrow(
        """
        SELECT id, name, email, created_at, preferences, security_clearance
        FROM users
        WHERE id = $1
        """,
        user_id
    )
    
    # Get user's active roles
    roles = await db.fetch(
        """
        SELECT r.name, r.permissions
        FROM user_roles ur
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = $1
        """,
        user_id
    )
    
    # Get user's persona state
    persona_state = await AIPersona.load_state(user_id)
    
    return UserContext(
        user_id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        preferences=user.preferences,
        security_clearance=user.security_clearance,
        roles=[r['name'] for r in roles],
        permissions=list(set(
            perm for role in roles 
            for perm in role['permissions']
        )),
        persona_state=persona_state
    )
```

### Session History

```python
async def get_session_history(session_id: str, limit: int = 10) -> List[Operation]:
    """
    Get recent operations from current session.
    
    Args:
        session_id: Current session ID
        limit: Maximum number of operations to retrieve
    
    Returns:
        List of recent operations in reverse chronological order
    """
    operations = await db.fetch(
        """
        SELECT 
            operation_id,
            intent,
            content,
            result_summary,
            timestamp
        FROM memory_attempt a
        LEFT JOIN memory_result r USING (operation_id)
        WHERE session_id = $1
        ORDER BY timestamp DESC
        LIMIT $2
        """,
        session_id, limit
    )
    
    return [
        Operation(
            id=op['operation_id'],
            intent=op['intent'],
            content=op['content'],
            result=op['result_summary'],
            timestamp=op['timestamp']
        )
        for op in operations
    ]
```

### Memory Context

```python
async def get_relevant_memories(user_id: str, query: str, 
                                limit: int = 5) -> List[MemoryRecord]:
    """
    Retrieve relevant memories for context.
    
    Uses semantic similarity search on past operations.
    
    Args:
        user_id: User ID
        query: Current query text
        limit: Maximum memories to return
    
    Returns:
        List of relevant memory records
    """
    # Calculate query embedding (if using vector similarity)
    # For now, use simple text search
    
    memories = await db.fetch(
        """
        SELECT 
            a.operation_id,
            a.content,
            a.intent,
            r.output_content,
            a.timestamp,
            ts_rank(
                to_tsvector('english', a.content),
                plainto_tsquery('english', $2)
            ) as relevance
        FROM memory_attempt a
        LEFT JOIN memory_result r USING (operation_id)
        WHERE a.user_id = $1
        AND to_tsvector('english', a.content) @@ plainto_tsquery('english', $2)
        ORDER BY relevance DESC, a.timestamp DESC
        LIMIT $3
        """,
        user_id, query, limit
    )
    
    return [
        MemoryRecord(
            operation_id=m['operation_id'],
            content=m['content'],
            intent=m['intent'],
            result=m['output_content'],
            timestamp=m['timestamp'],
            relevance=m['relevance']
        )
        for m in memories
    ]
```

### Complete Context Enrichment

```python
async def enrich_context(request: Request, user: User) -> EnrichedRequest:
    """
    Enrich request with comprehensive context.
    
    Combines:
    - User context (profile, prefs, permissions)
    - Session history (recent operations)
    - Memory context (relevant past interactions)
    - Temporal context (time, timezone)
    - Environmental context (platform, network)
    
    Args:
        request: Raw user request
        user: Authenticated user
    
    Returns:
        EnrichedRequest with full context
    """
    # Parallel context fetching for performance
    user_context, session_history, memory_context = await asyncio.gather(
        get_user_context(user.id),
        get_session_history(request.session_id, limit=10),
        get_relevant_memories(user.id, request.content, limit=5)
    )
    
    # Temporal context
    now = datetime.utcnow()
    user_tz = pytz.timezone(user.timezone)
    local_time = now.astimezone(user_tz)
    
    temporal_context = {
        'utc_timestamp': now.isoformat(),
        'local_timestamp': local_time.isoformat(),
        'timezone': user.timezone,
        'is_business_hours': is_business_hours(local_time),
        'day_of_week': local_time.strftime('%A'),
        'time_of_day': get_time_of_day(local_time)  # morning/afternoon/evening/night
    }
    
    # Environmental context
    environmental_context = {
        'platform': request.metadata.get('platform', 'unknown'),
        'client_version': request.metadata.get('client_version', 'unknown'),
        'network_quality': detect_network_quality(request),
        'device_type': detect_device_type(request.user_agent)
    }
    
    return EnrichedRequest(
        original=request,
        intent=request.intent,
        user_context=user_context,
        session_history=session_history,
        memory_context=memory_context,
        temporal_context=temporal_context,
        environmental_context=environmental_context,
        entities=request.entities,
        enrichment_timestamp=now
    )
```

## Semantic Parser

```python
class SemanticParser:
    """
    Parse natural language into structured semantic representation.
    
    Identifies:
    - Action verbs
    - Objects/subjects
    - Modifiers
    - Constraints
    """
    
    def parse(self, text: str) -> SemanticParse:
        """
        Parse text into semantic components.
        
        Args:
            text: Natural language text
        
        Returns:
            SemanticParse with structured components
        """
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        
        # Extract action verbs
        actions = [
            token.lemma_ for token in doc 
            if token.pos_ == 'VERB'
        ]
        
        # Extract objects
        objects = [
            chunk.text for chunk in doc.noun_chunks
        ]
        
        # Extract modifiers
        modifiers = [
            token.text for token in doc
            if token.pos_ in ['ADJ', 'ADV']
        ]
        
        # Extract constraints (prepositional phrases)
        constraints = []
        for token in doc:
            if token.pos_ == 'ADP':  # Preposition
                prep_phrase = ' '.join([
                    child.text for child in token.subtree
                ])
                constraints.append(prep_phrase)
        
        return SemanticParse(
            actions=actions,
            objects=objects,
            modifiers=modifiers,
            constraints=constraints,
            dependency_tree=self._build_dependency_tree(doc)
        )
```

## Request Routing

```python
class RequestRouter:
    """
    Route enriched requests to appropriate handlers.
    
    Based on:
    - Intent category
    - User permissions
    - System state
    - Resource availability
    """
    
    def __init__(self):
        self.intent_routes = self._load_intent_routes()
        self.fallback_handler = DefaultHandler()
    
    def route(self, request: EnrichedRequest) -> RequestHandler:
        """
        Route request to appropriate handler.
        
        Args:
            request: Enriched request with intent and context
        
        Returns:
            RequestHandler capable of processing the request
        """
        intent = request.intent.intent
        
        # Check if user has permission for this intent
        if not self._check_permission(request.user_context, intent):
            return PermissionDeniedHandler()
        
        # Get handler for intent
        handler_class = self.intent_routes.get(intent)
        
        if handler_class is None:
            logger.warning(f"No handler found for intent: {intent}")
            return self.fallback_handler
        
        # Instantiate handler
        return handler_class(request)
    
    def _check_permission(self, user_context: UserContext, intent: str) -> bool:
        """Check if user has permission for intent."""
        required_permission = self._get_required_permission(intent)
        return required_permission in user_context.permissions
```

## Performance Optimization

### Caching Strategy

```python
class CognitionKernelCache:
    """
    Cache frequently used data for performance.
    
    Caches:
    - User contexts (5 min TTL)
    - Intent predictions (10 min TTL)
    - Memory searches (2 min TTL)
    """
    
    def __init__(self):
        self.redis = get_redis_connection()
    
    async def get_user_context(self, user_id: str) -> Optional[UserContext]:
        """Get cached user context."""
        cached = await self.redis.get(f'user_context:{user_id}')
        if cached:
            return UserContext.from_json(cached.decode())
        return None
    
    async def set_user_context(self, user_id: str, context: UserContext):
        """Cache user context."""
        await self.redis.set(
            f'user_context:{user_id}',
            context.to_json(),
            ex=300  # 5 minutes
        )
```

### Batch Processing

```python
async def process_batch(requests: List[Request]) -> List[EnrichedRequest]:
    """
    Process multiple requests in batch for efficiency.
    
    Benefits:
    - Shared database queries
    - Batch ML inference
    - Reduced context switches
    """
    # Extract all user IDs
    user_ids = list(set(req.user_id for req in requests))
    
    # Fetch all user contexts in single query
    user_contexts = await fetch_user_contexts_batch(user_ids)
    
    # Batch intent detection
    intents = batch_detect_intents([req.content for req in requests])
    
    # Enrich all requests
    enriched = []
    for req, intent in zip(requests, intents):
        req.intent = intent
        req.user_context = user_contexts[req.user_id]
        enriched.append(req)
    
    return enriched
```

## Performance Characteristics

### Latency Targets (P95)
- Intent detection: < 50ms
- Entity extraction: < 30ms
- Context enrichment: < 100ms
- **Total CognitionKernel**: < 200ms

### Throughput
- Requests/second: 500+
- Batch processing: 1000+ requests/batch

### Resource Usage
- CPU: 2 cores @ 80% (ML inference)
- Memory: 2GB (models loaded)
- Network: minimal (database queries)

## Monitoring

```python
# Prometheus metrics
intent_detection_duration_seconds = Histogram(
    'intent_detection_duration_seconds',
    'Intent detection duration'
)

context_enrichment_duration_seconds = Histogram(
    'context_enrichment_duration_seconds',
    'Context enrichment duration'
)

intent_confidence = Histogram(
    'intent_confidence',
    'Intent classification confidence',
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
)

intent_distribution = Counter(
    'intent_distribution',
    'Intent category distribution',
    ['intent']
)
```

## Related Documentation

- [GovernanceTriumvirate](./governance_triumvirate.md)
- [MemoryEngine](./memory_engine.md)
- [Agent System](./agent_system.md)
- [User Request Flow](../data_flow/user_request_flow.md)
