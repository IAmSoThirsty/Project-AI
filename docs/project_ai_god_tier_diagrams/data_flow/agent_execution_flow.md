# Agent Execution Flow - Dynamic Agent Selection and Orchestration

## Overview

The Agent Execution Flow implements a sophisticated system for dynamically selecting, orchestrating, and monitoring the execution of specialized AI agents. Project-AI features 30+ specialized agents, each optimized for specific task categories.

## Agent Architecture

```
                    ┌──────────────────────────────────┐
                    │   EXECUTION SERVICE              │
                    │                                  │
                    │  • Agent Selection               │
                    │  • Dependency Resolution         │
                    │  • Parallel Orchestration        │
                    │  • Timeout Management            │
                    │  • Result Aggregation            │
                    └──────────────────────────────────┘
                                   │
                                   ↓
                    ┌──────────────────────────────────┐
                    │      AGENT POOL                  │
                    │                                  │
                    │  30+ Specialized Agents          │
                    │  Dynamic instantiation           │
                    │  Resource pooling                │
                    └──────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ↓                          ↓                          ↓
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│  CORE AGENTS   │      │ ANALYSIS AGENTS│      │UTILITY AGENTS  │
│                │      │                │      │                │
│• Intelligence  │      │• Data Analysis │      │• Image Gen     │
│• Learning      │      │• Security Scan │      │• Location      │
│• Memory Search │      │• Pattern Detect│      │• Emergency     │
│• Command Exec  │      │• Forecasting   │      │• File Manager  │
└────────────────┘      └────────────────┘      └────────────────┘
```

## Agent Catalog

### Core Agents

#### 1. IntelligenceAgent
**Purpose**: General-purpose question answering and information retrieval

**Capabilities**:
- Natural language understanding
- OpenAI GPT integration
- Context-aware responses
- Multi-turn conversations

**Configuration**:
```python
{
    "agent_type": "IntelligenceAgent",
    "version": "1.2.0",
    "model": "gpt-4-turbo-preview",
    "max_tokens": 2048,
    "temperature": 0.7,
    "timeout_seconds": 30,
    "retry_attempts": 2
}
```

**Usage Pattern**:
```python
async def execute_intelligence_query(request: EnrichedRequest) -> AgentResult:
    """Execute general intelligence query."""
    
    agent = IntelligenceAgent(
        model="gpt-4-turbo-preview",
        temperature=0.7,
        max_tokens=2048
    )
    
    result = await agent.execute(
        prompt=request.content,
        context=request.context,
        conversation_history=get_conversation_history(request.user_id)
    )
    
    return AgentResult(
        status="success",
        output=result.response,
        tokens_used=result.tokens,
        execution_time_ms=result.duration
    )
```

#### 2. LearningAgent
**Purpose**: Process learning requests and update knowledge base

**Capabilities**:
- Human-in-the-loop approval
- Black Vault forbidden content filtering
- Knowledge base updates
- Learning path generation

**Configuration**:
```python
{
    "agent_type": "LearningAgent",
    "version": "1.0.0",
    "require_approval": true,
    "black_vault_enabled": true,
    "timeout_seconds": 60
}
```

**Workflow**:
```python
async def execute_learning_request(request: EnrichedRequest) -> AgentResult:
    """Process learning request with approval workflow."""
    
    agent = LearningAgent(require_approval=True)
    
    # Check Black Vault
    content_hash = hashlib.sha256(request.content.encode()).hexdigest()
    if content_hash in agent.black_vault:
        return AgentResult(
            status="failure",
            error="Content is in Black Vault (forbidden)",
            reason="Previously rejected by user"
        )
    
    # Request human approval
    approval = await agent.request_approval(
        content=request.content,
        user_id=request.user_id,
        rationale=agent.generate_approval_request(request)
    )
    
    if not approval.approved:
        # Add to Black Vault
        await agent.add_to_black_vault(content_hash, approval.reason)
        return AgentResult(
            status="failure",
            error="Learning request rejected",
            reason=approval.reason
        )
    
    # Process learning
    result = await agent.learn(
        content=request.content,
        category=agent.detect_category(request.content)
    )
    
    return AgentResult(
        status="success",
        output=f"Learned: {result.summary}",
        knowledge_updated=True
    )
```

#### 3. CommandExecutionAgent
**Purpose**: Execute system commands with safety validation

**Capabilities**:
- Command override system integration
- Master password validation
- Safety checks
- Audit logging

**Configuration**:
```python
{
    "agent_type": "CommandExecutionAgent",
    "version": "1.1.0",
    "require_override": true,
    "allowed_commands": ["ls", "cat", "grep", "find"],
    "dangerous_commands": ["rm", "del", "format", "shutdown"],
    "timeout_seconds": 300
}
```

**Safety Pattern**:
```python
async def execute_command(request: EnrichedRequest) -> AgentResult:
    """Execute command with safety checks."""
    
    agent = CommandExecutionAgent()
    
    # Parse command
    command = agent.parse_command(request.content)
    
    # Check if dangerous
    if agent.is_dangerous(command):
        # Require command override
        override_valid = await command_override_system.validate(
            user_id=request.user_id,
            command=command,
            password=request.get('override_password')
        )
        
        if not override_valid:
            return AgentResult(
                status="failure",
                error="Command override required",
                requires_override=True
            )
    
    # Execute with timeout
    try:
        result = await asyncio.wait_for(
            agent.execute_command(command),
            timeout=300
        )
        
        return AgentResult(
            status="success",
            output=result.stdout,
            exit_code=result.returncode
        )
    except asyncio.TimeoutError:
        return AgentResult(
            status="failure",
            error="Command execution timeout"
        )
```

#### 4. MemorySearchAgent
**Purpose**: Search and retrieve memories from five-channel system

**Capabilities**:
- Full-text search across all channels
- Semantic similarity search
- Temporal filtering
- Aggregated results

**Configuration**:
```python
{
    "agent_type": "MemorySearchAgent",
    "version": "1.0.0",
    "search_channels": ["attempt", "decision", "result", "reflection", "error"],
    "max_results": 50,
    "similarity_threshold": 0.75,
    "timeout_seconds": 15
}
```

### Analysis Agents

#### 5. DataAnalysisAgent
**Purpose**: Analyze CSV, Excel, and JSON data

**Capabilities**:
- Statistical analysis
- K-means clustering
- Visualization generation
- Pattern detection

**Configuration**:
```python
{
    "agent_type": "DataAnalysisAgent",
    "version": "1.3.0",
    "max_file_size_mb": 100,
    "supported_formats": ["csv", "xlsx", "json"],
    "clustering_algorithms": ["kmeans", "dbscan", "hierarchical"],
    "timeout_seconds": 120
}
```

**Analysis Pipeline**:
```python
async def execute_data_analysis(request: EnrichedRequest) -> AgentResult:
    """Execute data analysis pipeline."""
    
    agent = DataAnalysisAgent(max_file_size_mb=100)
    
    # Load data
    data = await agent.load_data(
        file_path=request.get('file_path'),
        format=request.get('format', 'csv')
    )
    
    # Validate data
    if len(data) > 1_000_000:
        return AgentResult(
            status="failure",
            error="Dataset too large (> 1M rows)"
        )
    
    # Perform analysis
    results = await agent.analyze(
        data=data,
        operations=request.get('operations', ['summary', 'clustering'])
    )
    
    # Generate visualizations
    charts = await agent.generate_charts(
        data=data,
        results=results,
        chart_types=['scatter', 'histogram', 'correlation']
    )
    
    return AgentResult(
        status="success",
        output={
            'summary': results.summary,
            'statistics': results.statistics,
            'clusters': results.clusters,
            'charts': [chart.to_base64() for chart in charts]
        },
        execution_time_ms=results.duration
    )
```

#### 6. SecurityScanAgent
**Purpose**: Search security resources and CTF materials

**Capabilities**:
- GitHub API integration
- Security repository search
- CTF challenge discovery
- Vulnerability database queries

**Configuration**:
```python
{
    "agent_type": "SecurityScanAgent",
    "version": "1.0.0",
    "github_api_token": "env:GITHUB_TOKEN",
    "search_categories": ["ctf", "vulnerabilities", "exploits", "tools"],
    "timeout_seconds": 30
}
```

### Utility Agents

#### 7. ImageGenerationAgent
**Purpose**: Generate images using AI models

**Capabilities**:
- Stable Diffusion 2.1 integration
- OpenAI DALL-E 3 integration
- Content filtering
- Style presets

**Configuration**:
```python
{
    "agent_type": "ImageGenerationAgent",
    "version": "1.4.0",
    "backends": ["huggingface", "openai"],
    "default_backend": "huggingface",
    "content_filter_enabled": true,
    "styles": ["photorealistic", "digital_art", "oil_painting", "watercolor",
               "anime", "sketch", "abstract", "cyberpunk", "fantasy", "minimalist"],
    "timeout_seconds": 60
}
```

**Generation Workflow**:
```python
async def execute_image_generation(request: EnrichedRequest) -> AgentResult:
    """Generate image with content filtering."""
    
    agent = ImageGenerationAgent(backend="huggingface")
    
    # Content filter
    is_safe, reason = agent.check_content_filter(request.content)
    if not is_safe:
        return AgentResult(
            status="failure",
            error=f"Content filter: {reason}",
            content_filtered=True
        )
    
    # Generate image
    try:
        result = await asyncio.wait_for(
            agent.generate(
                prompt=request.content,
                style=request.get('style', 'photorealistic'),
                size=request.get('size', '512x512'),
                num_images=request.get('num_images', 1)
            ),
            timeout=60
        )
        
        return AgentResult(
            status="success",
            output={
                'images': result.image_paths,
                'metadata': result.metadata,
                'generation_time_s': result.duration
            }
        )
    except asyncio.TimeoutError:
        return AgentResult(
            status="failure",
            error="Image generation timeout (60s)"
        )
```

#### 8. LocationTrackingAgent
**Purpose**: IP geolocation and GPS tracking

**Capabilities**:
- IP geolocation
- GPS coordinate tracking
- Encrypted history storage
- Location-based services

**Configuration**:
```python
{
    "agent_type": "LocationTrackingAgent",
    "version": "1.0.0",
    "geolocation_api": "ipapi.co",
    "encryption_enabled": true,
    "history_retention_days": 90,
    "timeout_seconds": 10
}
```

#### 9. EmergencyAlertAgent
**Purpose**: Send emergency alerts to contacts

**Capabilities**:
- Email alerts
- SMS notifications
- Emergency contact management
- Alert escalation

**Configuration**:
```python
{
    "agent_type": "EmergencyAlertAgent",
    "version": "1.0.0",
    "smtp_server": "env:SMTP_SERVER",
    "sms_provider": "twilio",
    "max_contacts": 5,
    "timeout_seconds": 30
}
```

## Agent Selection Logic

### Intent-Based Selection

```python
class AgentSelector:
    """Dynamically select agents based on request intent."""
    
    INTENT_AGENT_MAPPING = {
        # Core intents
        'query.information': IntelligenceAgent,
        'query.definition': IntelligenceAgent,
        'query.explanation': IntelligenceAgent,
        
        # Command intents
        'command.execute': CommandExecutionAgent,
        'command.override': CommandExecutionAgent,
        
        # Analysis intents
        'analysis.data': DataAnalysisAgent,
        'analysis.pattern': DataAnalysisAgent,
        'analysis.clustering': DataAnalysisAgent,
        
        # Generation intents
        'generation.image': ImageGenerationAgent,
        'generation.report': ReportGenerationAgent,
        
        # Learning intents
        'learning.request': LearningAgent,
        'learning.update': LearningAgent,
        
        # Memory intents
        'memory.search': MemorySearchAgent,
        'memory.recall': MemorySearchAgent,
        
        # Security intents
        'security.scan': SecurityScanAgent,
        'security.audit': SecurityAuditAgent,
        
        # Utility intents
        'location.track': LocationTrackingAgent,
        'emergency.alert': EmergencyAlertAgent,
        'file.manage': FileManagementAgent,
        
        # Persona intents
        'persona.modify': PersonaManagementAgent,
        'persona.query': PersonaManagementAgent
    }
    
    def select_agent(self, request: EnrichedRequest) -> Agent:
        """
        Select appropriate agent based on request intent.
        
        Args:
            request: Enriched request with detected intent
        
        Returns:
            Instantiated agent ready for execution
        """
        intent = request.intent.intent
        
        # Get agent class from mapping
        agent_class = self.INTENT_AGENT_MAPPING.get(intent, DefaultAgent)
        
        # Load agent configuration
        config = self._load_agent_config(agent_class.__name__)
        
        # Instantiate agent
        agent = agent_class(**config)
        
        logger.info(f"Selected agent: {agent_class.__name__} for intent: {intent}")
        
        return agent
    
    def select_multi_agent(self, request: EnrichedRequest) -> List[Agent]:
        """
        Select multiple agents for complex requests.
        
        Some requests require multiple agents working together.
        Example: "Analyze this data and generate a report with charts"
        Requires: DataAnalysisAgent + ReportGenerationAgent
        """
        # Detect if request requires multiple agents
        sub_intents = self._detect_sub_intents(request)
        
        if len(sub_intents) > 1:
            agents = [
                self.select_agent(EnrichedRequest(intent=Intent(intent=intent)))
                for intent in sub_intents
            ]
            return agents
        
        return [self.select_agent(request)]
```

### Dependency Resolution

Some operations require multiple agents in sequence:

```python
class AgentOrchestrator:
    """Orchestrate multi-agent workflows with dependency resolution."""
    
    def build_execution_graph(self, agents: List[Agent]) -> ExecutionGraph:
        """
        Build directed acyclic graph (DAG) of agent dependencies.
        
        Example:
            DataLoadAgent → DataAnalysisAgent → ReportGenerationAgent
        """
        graph = ExecutionGraph()
        
        for agent in agents:
            # Add agent as node
            graph.add_node(agent)
            
            # Add dependencies
            for dependency in agent.dependencies:
                graph.add_edge(dependency, agent)
        
        # Topological sort for execution order
        execution_order = graph.topological_sort()
        
        return ExecutionGraph(nodes=agents, order=execution_order)
    
    async def execute_graph(self, graph: ExecutionGraph, 
                           request: EnrichedRequest) -> List[AgentResult]:
        """
        Execute agents in dependency order.
        
        Args:
            graph: Execution graph with dependencies
            request: Original request
        
        Returns:
            List of agent results in execution order
        """
        results = {}
        
        for agent in graph.execution_order:
            # Get results from dependencies
            dependency_results = {
                dep: results[dep]
                for dep in agent.dependencies
                if dep in results
            }
            
            # Execute agent with dependency results
            result = await agent.execute(
                request=request,
                dependency_results=dependency_results
            )
            
            results[agent] = result
            
            # Stop if agent failed
            if result.status != 'success':
                logger.error(f"Agent {agent.__class__.__name__} failed: {result.error}")
                break
        
        return list(results.values())
```

## Parallel Execution

For independent operations, agents can execute in parallel:

```python
async def execute_parallel(agents: List[Agent], 
                          request: EnrichedRequest) -> List[AgentResult]:
    """
    Execute multiple independent agents in parallel.
    
    Example: Search multiple data sources simultaneously
    """
    tasks = [
        agent.execute(request)
        for agent in agents
    ]
    
    # Wait for all with timeout
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(AgentResult(
                status='failure',
                error=str(result),
                agent=agents[i].__class__.__name__
            ))
        else:
            processed_results.append(result)
    
    return processed_results
```

## Timeout Management

All agents have configurable timeouts:

```python
async def execute_with_timeout(agent: Agent, 
                               request: EnrichedRequest,
                               timeout: int = None) -> AgentResult:
    """Execute agent with timeout protection."""
    
    timeout = timeout or agent.timeout_seconds
    
    try:
        result = await asyncio.wait_for(
            agent.execute(request),
            timeout=timeout
        )
        
        return result
        
    except asyncio.TimeoutError:
        logger.warning(f"Agent {agent.__class__.__name__} timeout after {timeout}s")
        
        # Record timeout in memory
        await memory_engine.record_error(
            channel='error',
            operation_id=request.id,
            error={
                'type': 'TimeoutError',
                'agent': agent.__class__.__name__,
                'timeout_seconds': timeout,
                'message': f'Agent execution exceeded {timeout}s timeout'
            }
        )
        
        return AgentResult(
            status='failure',
            error=f'Execution timeout after {timeout}s',
            timeout=True
        )
```

## Resource Management

### Agent Pooling

```python
class AgentPool:
    """Pool of pre-instantiated agents for performance."""
    
    def __init__(self, pool_size: int = 10):
        self.pools = {
            IntelligenceAgent: asyncio.Queue(maxsize=pool_size),
            DataAnalysisAgent: asyncio.Queue(maxsize=pool_size),
            # ... other agents
        }
        
        # Pre-populate pools
        for agent_class, queue in self.pools.items():
            for _ in range(pool_size):
                agent = agent_class()
                queue.put_nowait(agent)
    
    async def acquire(self, agent_class: Type[Agent]) -> Agent:
        """Acquire agent from pool."""
        queue = self.pools.get(agent_class)
        if not queue:
            # Not pooled, create new instance
            return agent_class()
        
        try:
            # Try to get from pool with timeout
            agent = await asyncio.wait_for(queue.get(), timeout=1.0)
            return agent
        except asyncio.TimeoutError:
            # Pool exhausted, create new instance
            logger.warning(f"Agent pool exhausted for {agent_class.__name__}")
            return agent_class()
    
    async def release(self, agent: Agent):
        """Return agent to pool."""
        agent_class = type(agent)
        queue = self.pools.get(agent_class)
        
        if queue and not queue.full():
            # Reset agent state
            await agent.reset()
            queue.put_nowait(agent)
```

## Performance Characteristics

### Latency Targets (P95)
- Simple agent (IntelligenceAgent): < 1s
- Medium agent (DataAnalysisAgent): < 30s
- Complex agent (ImageGenerationAgent): < 60s

### Throughput
- Concurrent agents: 50+
- Agents/second: 100+

## Monitoring

```python
# Prometheus metrics
agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_type', 'status']
)

agent_execution_duration_seconds = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration',
    ['agent_type']
)

agent_timeout_total = Counter(
    'agent_timeout_total',
    'Total agent timeouts',
    ['agent_type']
)

agent_pool_size = Gauge(
    'agent_pool_size',
    'Current agent pool size',
    ['agent_type']
)
```

## Related Documentation

- [User Request Flow](./user_request_flow.md)
- [Memory Recording Flow](./memory_recording_flow.md)
- [Component Architecture - Agent System](../component/agent_system.md)
