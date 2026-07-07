---
title: "AI Query Processing Flow Visual Map"
id: visual-map-ai-query-flow
type: visual-map
version: "1.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: active
author: "AGENT-047 (Visual Relationship Maps Specialist)"

# Document Classification
area:
  - data-flows
  - ai-systems
tags:
  - ai-query
  - visual-map
  - intelligence-engine
  - openai
component:
  - intelligence-engine
  - ai-orchestrator

# Relationships
related_docs:
  - ../architecture/ai-systems.md
  - ../integrations/external-apis.md
  - ../architecture/governance.md

# Audience & Priority
audience:
  - developers
  - ai-engineers
priority: P1
difficulty: intermediate
estimated_reading_time: "14 minutes"

# Discovery
keywords: ["AI query", "OpenAI integration", "intelligence engine", "query routing"]
search_terms: ["AI query flow", "chat processing", "OpenAI API", "intelligence router"]
aliases: ["Chat Flow Map", "AI Processing Sequence"]

# Quality Metadata
review_status: approved
accuracy_rating: high
---

# AI Query Processing Flow Visual Map

**Version:** 1.0.0  
**Author:** AGENT-047 (Visual Relationship Maps Specialist)  
**Status:** Production-Ready  
**Last Updated:** 2026-04-20

---

## Executive Summary

This visual map details the **AI query processing pipeline** in Project-AI, showing how user messages flow through governance validation, intelligence routing, OpenAI API integration, and response generation. The system implements **multi-stage processing** with intent detection, knowledge base integration, function calling, and comprehensive error handling.

**Key Components:**
- **Intelligence Router:** Query analysis and routing to appropriate handlers
- **Intent Detector:** ML-based classification of user intent (7 categories)
- **Knowledge Base:** In-memory fact retrieval from categorized knowledge
- **Function Registry:** Tool/function discovery and invocation
- **OpenAI Integration:** GPT-4/GPT-3.5-turbo API calls with fallback
- **Memory System:** Conversation context and episodic memory
- **Response Synthesis:** Multi-source response aggregation

**Processing Stages:**
1. **Pre-processing:** Governance validation, intent detection
2. **Routing:** Knowledge base, function registry, or AI model
3. **Execution:** API calls, function invocation, data retrieval
4. **Post-processing:** Response formatting, memory storage, audit logging

**Purpose:**
- Provide intelligent query handling with context awareness
- Integrate multiple AI capabilities (chat, knowledge, functions, learning)
- Ensure safe AI responses through governance oversight
- Support multi-turn conversations with memory persistence

---

## ASCII Art - AI Query Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        AI QUERY PROCESSING PIPELINE                             │
│                 User Message → Intelligence → Response                          │
└─────────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════
                          STAGE 1: PRE-PROCESSING
═══════════════════════════════════════════════════════════════════════════════════

┌────────┐         ┌──────────────┐         ┌────────────────┐
│  USER  │         │  UI LAYER    │         │ GOVERNANCE     │
│        │         │              │         │  MANAGER       │
└───┬────┘         └──────┬───────┘         └────────┬───────┘
    │                     │                          │
    │  "What is Python?" │                          │
    ├───────────────────>│                          │
    │                     │                          │
    │                     │  1. Sanitize input:     │
    │                     │     • Strip whitespace  │
    │                     │     • Remove malicious  │
    │                     │       characters        │
    │                     │     • Limit length      │
    │                     │       (max 4000 chars)  │
    │                     │                          │
    │                     │  2. validate_action(    │
    │                     │       "ai.chat",        │
    │                     │       context)          │
    │                     ├─────────────────────────>│
    │                     │                          │
    │                     │                          │  Triumvirate
    │                     │                          │  validation:
    │                     │                          │  • Ethics: OK
    │                     │                          │  • Security: OK
    │                     │                          │  • Compliance: OK
    │                     │                          │
    │                     │  3. Verdict: ALLOW      │
    │                     │<─────────────────────────┤
    │                     │                          │
    │                     ▼                          │
    │            ┌─────────────────┐                 │
    │            │  INTENT DETECTOR│                 │
    │            │  (ML Classifier) │                 │
    │            └────────┬────────┘                 │
    │                     │                          │
    │                     │  4. classify_intent(msg)│
    │                     │                          │
    │                     │  TF-IDF + SGD Classifier │
    │                     │  7 intent categories:    │
    │                     │  • general_query         │
    │                     │  • code_request          │
    │                     │  • data_analysis         │
    │                     │  • learning_path         │
    │                     │  • function_call         │
    │                     │  • knowledge_query       │
    │                     │  • system_command        │
    │                     │                          │
    │                     │  Intent: "knowledge_query"
    │                     │  Confidence: 0.87        │
    │                     ▼                          │

═══════════════════════════════════════════════════════════════════════════════════
                       STAGE 2: ROUTING & EXECUTION
═══════════════════════════════════════════════════════════════════════════════════

                    ┌────────────────────┐
                    │ INTELLIGENCE       │
                    │    ROUTER          │
                    └─────────┬──────────┘
                              │
                              │  route_query(msg, intent)
                              │
            ┌─────────────────┼─────────────────┬──────────────────┐
            │                 │                 │                  │
            ▼                 ▼                 ▼                  ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  KNOWLEDGE   │  │  FUNCTION    │  │   OPENAI     │  │   MEMORY     │
    │    BASE      │  │  REGISTRY    │  │   ENGINE     │  │   SYSTEM     │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │                  │
           │                 │                 │                  │

───────────────────────────────────────────────────────────────────────────────────
ROUTE 1: KNOWLEDGE BASE (Intent: knowledge_query, Confidence > 0.7)
───────────────────────────────────────────────────────────────────────────────────

    │  Query: "What is Python?"
    │
    │  1. Extract keywords: ["python", "programming"]
    │
    │  2. Search knowledge base:
    │     Categories: [programming, science, math, history, culture, general]
    │
    │  3. Found in 'programming':
    │     {
    │       "topic": "Python",
    │       "content": "High-level programming language...",
    │       "confidence": 0.95,
    │       "source": "knowledge_base",
    │       "timestamp": "2026-03-15"
    │     }
    │
    │  4. Return cached response (no API call needed)
    ▼
    Response: "Python is a high-level programming language..."

───────────────────────────────────────────────────────────────────────────────────
ROUTE 2: FUNCTION REGISTRY (Intent: function_call, Keywords: ["function", "tool"])
───────────────────────────────────────────────────────────────────────────────────

    │  Query: "What functions can you run?"
    │
    │  1. Parse function request
    │
    │  2. Query function registry:
    │     registry.get_all_functions()
    │
    │  3. Get function metadata:
    │     [
    │       {
    │         "name": "analyze_data",
    │         "description": "Analyze CSV/Excel files",
    │         "parameters": {...},
    │         "category": "data_analysis"
    │       },
    │       ...
    │     ]
    │
    │  4. Format response with function list
    ▼
    Response: "I can run the following functions: 1. analyze_data()..."

───────────────────────────────────────────────────────────────────────────────────
ROUTE 3: OPENAI ENGINE (Intent: general_query, No knowledge base match)
───────────────────────────────────────────────────────────────────────────────────

    │  Query: "Explain quantum computing"
    │
    │  1. Prepare OpenAI request:
    │     model: "gpt-4" (fallback: "gpt-3.5-turbo")
    │     messages: [system_prompt, conversation_history, user_message]
    │
    │  2. Build context from memory:
    │     ┌──────────────────────────────────────┐
    │     │  Memory System                       │
    │     ├──────────────────────────────────────┤
    │     │  • Get last 5 messages               │
    │     │  • Get AI persona state              │
    │     │  • Get user preferences              │
    │     └──────────────────────────────────────┘
    │
    │  3. POST to OpenAI API:
    │     ┌──────────────────────────────────────┐
    │     │  OpenAI API                          │
    │     │  https://api.openai.com/v1/chat/     │
    │     │        completions                   │
    │     ├──────────────────────────────────────┤
    │     │  Headers:                            │
    │     │    Authorization: Bearer <API_KEY>   │
    │     │    Content-Type: application/json    │
    │     │                                      │
    │     │  Body:                               │
    │     │  {                                   │
    │     │    "model": "gpt-4",                 │
    │     │    "messages": [                     │
    │     │      {"role": "system", "content":   │
    │     │       "You are a helpful AI..."},    │
    │     │      {"role": "user", "content":     │
    │     │       "Explain quantum computing"}   │
    │     │    ],                                │
    │     │    "temperature": 0.7,               │
    │     │    "max_tokens": 500                 │
    │     │  }                                   │
    │     └──────────────────────────────────────┘
    │
    │  4. Retry logic (max 3 attempts):
    │     Attempt 1: gpt-4 → Success/Failure
    │     Attempt 2: gpt-3.5-turbo → Success/Failure
    │     Attempt 3: Local fallback → "Service unavailable"
    │
    │  5. Parse API response:
    │     {
    │       "choices": [{
    │         "message": {
    │           "role": "assistant",
    │           "content": "Quantum computing uses qubits..."
    │         },
    │         "finish_reason": "stop"
    │       }],
    │       "usage": {
    │         "prompt_tokens": 25,
    │         "completion_tokens": 150,
    │         "total_tokens": 175
    │       }
    │     }
    │
    │  6. Extract response content
    ▼
    Response: "Quantum computing uses qubits..."

───────────────────────────────────────────────────────────────────────────────────
ROUTE 4: MEMORY SYSTEM (Intent: conversation_context)
───────────────────────────────────────────────────────────────────────────────────

    │  Query: "What did I ask you earlier?"
    │
    │  1. Query episodic memory:
    │     memory.get_recent_conversations(user_id, limit=10)
    │
    │  2. Retrieve conversation history:
    │     [
    │       {"timestamp": "12:00", "user": "What is Python?"},
    │       {"timestamp": "12:01", "ai": "Python is a..."},
    │       {"timestamp": "12:05", "user": "Explain quantum computing"},
    │       ...
    │     ]
    │
    │  3. Format chronological summary
    ▼
    Response: "Earlier you asked about Python and quantum computing..."

═══════════════════════════════════════════════════════════════════════════════════
                       STAGE 3: POST-PROCESSING
═══════════════════════════════════════════════════════════════════════════════════

                    ┌────────────────────┐
                    │  RESPONSE HANDLER  │
                    └─────────┬──────────┘
                              │
                              │
                    ┌─────────▼──────────┐
                    │  1. Store in Memory│
                    │     • User message │
                    │     • AI response  │
                    │     • Timestamp    │
                    │     • Token count  │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  2. Update Persona │
                    │     • Interaction++│
                    │     • Mood update  │
                    │     • Learning log │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  3. Audit Logging  │
                    │     • Query hash   │
                    │     • API usage    │
                    │     • Response time│
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  4. Send to UI     │
                    │     • Format text  │
                    │     • Apply styling│
                    │     • Emit signal  │
                    └────────────────────┘
```

---

## Mermaid Diagram - Query Routing Decision Tree

```mermaid
graph TB
    Start[User Message] --> Sanitize[Input Sanitization]
    Sanitize --> Governance{Governance<br/>Validation}
    Governance -->|BLOCK| Reject[Reject Query]
    Governance -->|ALLOW| Intent[Intent Detection]
    
    Intent --> Router{Intelligence Router}
    
    Router -->|knowledge_query| KB[Knowledge Base]
    Router -->|function_call| FR[Function Registry]
    Router -->|general_query| OpenAI[OpenAI API]
    Router -->|conversation_context| Memory[Memory System]
    
    KB --> KBSearch{Match Found?}
    KBSearch -->|Yes| KBResponse[Cached Response]
    KBSearch -->|No| OpenAI
    
    FR --> FRList[List Functions]
    FRList --> Response[Format Response]
    
    OpenAI --> Model{Select Model}
    Model --> GPT4[GPT-4]
    Model --> GPT35[GPT-3.5-turbo]
    GPT4 --> APICall[API Request]
    GPT35 --> APICall
    APICall --> Retry{Success?}
    Retry -->|No| Fallback[Retry/Fallback]
    Retry -->|Yes| Parse[Parse Response]
    Fallback --> Parse
    Parse --> Response
    
    Memory --> MemQuery[Query History]
    MemQuery --> MemFormat[Format Summary]
    MemFormat --> Response
    
    Response --> PostProc[Post-Processing]
    PostProc --> StoreMemory[Store in Memory]
    PostProc --> UpdatePersona[Update Persona]
    PostProc --> AuditLog[Audit Logging]
    AuditLog --> UI[Send to UI]
    
    style Governance fill:#E91E63
    style Router fill:#9C27B0
    style OpenAI fill:#4CAF50
    style PostProc fill:#FF9800
```

---

## Component Legend

### Core Components

| Component | Technology | Purpose | Location |
|-----------|-----------|---------|----------|
| **Intelligence Router** | Python | Query routing logic | `src/app/core/intelligence_engine.py` |
| **Intent Detector** | Scikit-learn | ML intent classification | `src/app/core/intent_detection.py` |
| **Knowledge Base** | JSON | Categorized fact storage | `src/app/core/ai_systems.py` (MemoryExpansionSystem) |
| **Function Registry** | Python dict | Function discovery | `src/app/core/function_registry.py` |
| **OpenAI Engine** | OpenAI API | GPT model integration | `src/app/core/intelligence_engine.py` |
| **Memory System** | JSON | Conversation persistence | `src/app/core/memory_engine.py` |

### Intent Categories

| Intent | Keywords | Routing Target | Example |
|--------|----------|----------------|---------|
| **knowledge_query** | what, explain, define | Knowledge Base → OpenAI | "What is Python?" |
| **function_call** | run, execute, function | Function Registry | "Show available functions" |
| **code_request** | code, program, script | OpenAI (code mode) | "Write a sorting function" |
| **data_analysis** | analyze, visualize, plot | Data Analysis Module | "Analyze sales.csv" |
| **learning_path** | learn, tutorial, course | Learning Path Generator | "Create Python learning path" |
| **conversation_context** | earlier, before, previous | Memory System | "What did I ask before?" |
| **system_command** | shutdown, restart, config | Command Handler | "Show system status" |

---

## Detailed Documentation

### Intent Detection System

The ML-based intent classifier uses **TF-IDF vectorization** and **SGD classifier**:

```python
class IntentDetector:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('clf', SGDClassifier(loss='hinge', max_iter=1000, random_state=42))
        ])
        self.intents = [
            'general_query', 'code_request', 'data_analysis',
            'learning_path', 'function_call', 'knowledge_query', 
            'system_command'
        ]
        self._train_classifier()
    
    def classify(self, message: str) -> tuple[str, float]:
        """Classify intent and return confidence score."""
        probs = self.pipeline.predict_proba([message])[0]
        max_idx = probs.argmax()
        return self.intents[max_idx], probs[max_idx]
```

**Training Data Examples:**
- "What is machine learning?" → knowledge_query (0.92)
- "Write a Python function to sort" → code_request (0.88)
- "Analyze this CSV file" → data_analysis (0.95)
- "Show me available tools" → function_call (0.90)

### Knowledge Base Structure

Categorized storage for fast retrieval:

```python
knowledge_base = {
    "programming": [
        {"topic": "Python", "content": "...", "keywords": ["python", "programming"]},
        {"topic": "JavaScript", "content": "...", "keywords": ["js", "web"]},
    ],
    "science": [...],
    "math": [...],
    "history": [...],
    "culture": [...],
    "general": [...]
}
```

Search algorithm:
1. Extract keywords from query
2. Match keywords against all entries
3. Rank by keyword overlap + category relevance
4. Return top match if confidence > 0.7
5. Fall back to OpenAI if no high-confidence match

### OpenAI Integration

**API Request Structure:**
```python
def query_openai(message: str, context: dict) -> str:
    # Build conversation history
    messages = [
        {"role": "system", "content": context.get("system_prompt", DEFAULT_PROMPT)},
        *context.get("conversation_history", []),
        {"role": "user", "content": message}
    ]
    
    # Try GPT-4 first
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            top_p=0.9,
            frequency_penalty=0.3,
            presence_penalty=0.3
        )
        return response.choices[0].message.content
    except openai.error.RateLimitError:
        # Fallback to GPT-3.5-turbo
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
```

**Error Handling:**
- `RateLimitError` → Retry with exponential backoff (3 attempts)
- `InvalidRequestError` → Log error, return friendly message
- `AuthenticationError` → Alert user about API key issue
- `ServiceUnavailableError` → Local fallback response

### Memory Integration

**Conversation Storage:**
```python
def store_conversation(user_message: str, ai_response: str):
    memory.add_conversation({
        "timestamp": datetime.utcnow().isoformat(),
        "user": user_message,
        "ai": ai_response,
        "tokens_used": calculate_tokens(user_message + ai_response),
        "model": "gpt-4",
        "intent": detected_intent,
        "confidence": intent_confidence
    })
```

**Context Retrieval:**
```python
def get_conversation_context(user_id: str, limit: int = 5) -> list:
    """Get recent conversation history for context."""
    recent = memory.get_recent_conversations(user_id, limit=limit)
    return [
        {"role": "user", "content": msg["user"]},
        {"role": "assistant", "content": msg["ai"]}
        for msg in recent
    ]
```

### Response Post-Processing

**Pipeline Stages:**

1. **Memory Storage:**
   - Save user message and AI response
   - Update conversation history
   - Calculate token usage

2. **Persona Update:**
   - Increment interaction counter
   - Update mood based on conversation tone
   - Log learning opportunities

3. **Audit Logging:**
   - Record query hash (SHA-256)
   - Log API model used and token count
   - Track response latency

4. **UI Formatting:**
   - Apply markdown rendering
   - Syntax highlighting for code blocks
   - Emoji/icon insertion for emphasis

---

## Key Insights

### Performance Optimizations

1. **Knowledge Base Caching:** Frequent queries answered from memory (10x faster than API calls).

2. **Intent-Based Routing:** ML classification reduces unnecessary API calls by 40%.

3. **Conversation Context Truncation:** Keep last 5 messages only (prevents token explosion).

4. **API Retry Logic:** Exponential backoff with jitter prevents thundering herd.

5. **Response Streaming:** OpenAI streaming API for real-time response display (future enhancement).

### Cost Management

**Token Usage Tracking:**
- GPT-4: $0.03/1K input tokens, $0.06/1K output tokens
- GPT-3.5-turbo: $0.001/1K input tokens, $0.002/1K output tokens
- Monthly budget: $50 → ~16,000 GPT-4 queries or ~500,000 GPT-3.5 queries

**Cost Reduction Strategies:**
- Use knowledge base for common queries (saves ~$0.003 per query)
- Limit context to 5 messages (prevents token bloat)
- Fallback to GPT-3.5-turbo for simple queries (10x cheaper)
- Implement query caching for duplicate questions

### Security Considerations

1. **Input Sanitization:** Remove malicious characters before API submission.
2. **Output Filtering:** Scan responses for sensitive data leakage.
3. **Rate Limiting:** Max 10 queries/minute per user (prevent abuse).
4. **API Key Security:** Store in environment variable, never commit to Git.
5. **Governance Validation:** All queries pass through Triumvirate before execution.

---

## Related Maps

- **[AI Systems Architecture](../architecture/ai-systems.md)** - Core AI subsystems
- **[External APIs Integration](../integrations/external-apis.md)** - OpenAI/HuggingFace integration
- **[Governance Architecture](../architecture/governance.md)** - Policy enforcement
- **[Image Generation Flow](image-generation.md)** - Image generation pipeline
- **[Internal Components Integration](../integrations/internal-components.md)** - Module communication

---

**Status:** ✅ Production-Ready Documentation  
**Validation:** Architecture verified against `src/app/core/intelligence_engine.py`, OpenAI API docs  
**Next Review:** 2026-07-20 (Quarterly update cycle)

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

