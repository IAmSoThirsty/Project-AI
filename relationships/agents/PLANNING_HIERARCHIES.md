# Planning Hierarchies

**Purpose:** Document task decomposition, planning workflows, agent coordination, and execution scheduling  
**Scope:** PlannerAgent, task dependencies, resource allocation, multi-agent coordination  

---

## 1. Planning System Architecture

Project-AI implements **hierarchical task planning** with PlannerAgent orchestrating multi-step executions.

### 1.1 Two Planner Implementations

**Legacy Planner** (`src/app/agents/planner.py`):
```python
# GOVERNANCE BYPASS: Legacy stub, NOT kernel-routed
class PlannerAgent:
    def __init__(self) -> None:
        self.enabled: bool = False
        self.tasks: dict = {}
```

**Production Planner** (`src/app/agents/planner_agent.py`):
```python
# Kernel-routed production planner
class PlannerAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.queue: list[dict[str, Any]] = []
        self._lock = threading.Lock()
```

**CRITICAL:** Use `planner_agent.py` for all production workflows. Legacy `planner.py` is deprecated.

---

## 2. Planning Hierarchy Levels

### 2.1 Five-Level Planning Architecture

```
Level 0: User Intent
    │
    ├─→ "Build a web scraper for news articles"
    │
    ▼
Level 1: Strategic Plan (PlannerAgent)
    │
    ├─→ 1. Design architecture
    ├─→ 2. Implement scraping logic
    ├─→ 3. Add data storage
    ├─→ 4. Create UI
    └─→ 5. Test and deploy
    │
    ▼
Level 2: Tactical Subtasks (Decomposition)
    │
    ├─→ 1.1 Define target websites
    ├─→ 1.2 Choose framework (Scrapy/BeautifulSoup)
    ├─→ 1.3 Design data schema
    │
    ├─→ 2.1 Write HTML parsing logic
    ├─→ 2.2 Handle pagination
    ├─→ 2.3 Implement error handling
    │
    ├─→ 3.1 Setup database (PostgreSQL)
    ├─→ 3.2 Create data models
    ├─→ 3.3 Implement CRUD operations
    │
    └─→ ...
    │
    ▼
Level 3: Operational Actions (Atomic Tasks)
    │
    ├─→ 1.1.1 Research target site structure
    ├─→ 1.1.2 Identify article selectors (CSS/XPath)
    ├─→ 1.1.3 Test selectors in browser console
    │
    ├─→ 1.2.1 Install Scrapy: `pip install scrapy`
    ├─→ 1.2.2 Create project: `scrapy startproject news_scraper`
    ├─→ 1.2.3 Generate spider: `scrapy genspider articles news.com`
    │
    └─→ ...
    │
    ▼
Level 4: Agent Execution (Delegated to Agents)
    │
    ├─→ ExpertAgent.research_selectors()
    ├─→ SandboxRunner.install_dependency("scrapy")
    ├─→ RefactorAgent.generate_spider_template()
    ├─→ CodeAdversaryAgent.test_scraper_resilience()
    └─→ DocGenerator.create_documentation()
    │
    ▼
Level 5: Tool Invocation (Lowest Level)
    │
    ├─→ BashRunner.execute("pip install scrapy")
    ├─→ FileWriter.create_file("spider.py", content)
    ├─→ HTTPClient.fetch("https://news.com/articles")
    └─→ DatabaseClient.insert(article_data)
```

---

## 3. PlannerAgent Operations

### 3.1 Task Scheduling

**Method:** `schedule(task: dict[str, Any]) -> None`

```python
# From planner_agent.py
def schedule(self, task: dict[str, Any]) -> None:
    """Schedule a task for execution.
    
    Routes through kernel for tracking and governance.
    """
    return self._execute_through_kernel(
        action=self._do_schedule,
        action_name="PlannerAgent.schedule",
        action_args=(task,),
        requires_approval=False,
        risk_level="low",
        metadata={"task_name": task.get("name"), "operation": "schedule"},
    )

def _do_schedule(self, task: dict[str, Any]) -> None:
    """Internal implementation of task scheduling."""
    with self._lock:
        self.queue.append(task)
    logger.info("Task scheduled: %s", task.get("name"))
```

**Task Schema:**

```python
task = {
    "id": str,                      # Unique task ID (UUID)
    "name": str,                    # Human-readable name
    "description": str,             # Detailed description
    "priority": int,                # 1 (highest) to 10 (lowest)
    "dependencies": list[str],      # Task IDs that must complete first
    "estimated_duration": int,      # Seconds
    "assigned_agent": str | None,   # Agent name (or None for auto-assign)
    "required_tools": list[str],    # Tool names
    "metadata": dict,               # Custom metadata
    "created_at": datetime,
    "scheduled_at": datetime | None,
    "started_at": datetime | None,
    "completed_at": datetime | None,
    "status": str,                  # "pending", "running", "completed", "failed"
}
```

### 3.2 Task Execution

**Method:** `run_next() -> dict[str, Any]`

```python
def run_next(self) -> dict[str, Any]:
    """Execute the next task in the queue.
    
    Routes through kernel for governance and tracking.
    """
    return self._execute_through_kernel(
        action=self._do_run_next,
        action_name="PlannerAgent.run_next",
        requires_approval=False,
        risk_level="medium",  # Task execution has moderate risk
        metadata={"operation": "run_next"},
    )

def _do_run_next(self) -> dict[str, Any]:
    """Internal implementation of task execution."""
    with self._lock:
        if not self.queue:
            return {"success": False, "error": "empty"}
        task = self.queue.pop(0)  # FIFO queue
    
    logger.info("Executing task: %s", task.get("name"))
    time.sleep(0.01)  # Naive execution placeholder
    return {"success": True, "task": task}
```

**Execution Flow:**

```
PlannerAgent.run_next()
    │
    ├─→ Acquire lock (thread-safe)
    ├─→ Pop task from queue (FIFO)
    ├─→ Release lock
    │
    ├─→ Validate task dependencies
    │   └─→ All dependencies completed? → Proceed
    │       Any pending? → Re-queue task
    │
    ├─→ Assign to agent
    │   └─→ If assigned_agent specified → Route to that agent
    │       Else → Auto-assign based on task type
    │
    ├─→ Execute task
    │   └─→ kernel.route(task, source="planner", metadata={...})
    │
    ├─→ Update task status
    │   └─→ Status: "running" → "completed" or "failed"
    │
    └─→ Return result
```

### 3.3 Task Decomposition (Future Implementation)

**Planned Method:** `decompose(goal: str, max_depth: int = 5) -> list[dict]`

```python
def decompose(self, goal: str, max_depth: int = 5) -> list[dict]:
    """Decompose complex goal into hierarchical subtasks.
    
    Uses AI (OpenAI GPT-4) to break down goals into actionable tasks.
    
    Args:
        goal: High-level objective
        max_depth: Maximum decomposition depth (prevents infinite recursion)
    
    Returns:
        List of task dictionaries with dependencies
    """
    return self._execute_through_kernel(
        action=self._do_decompose,
        action_name="PlannerAgent.decompose",
        action_args=(goal, max_depth),
        requires_approval=True,  # Decomposition affects system behavior
        risk_level="medium",
        metadata={"goal": goal, "max_depth": max_depth, "operation": "decompose"},
    )

def _do_decompose(self, goal: str, max_depth: int) -> list[dict]:
    """Internal decomposition logic using OpenAI."""
    import openai
    
    # Prompt GPT-4 for task decomposition
    prompt = f"""
    Decompose the following goal into actionable subtasks:
    
    Goal: {goal}
    
    Requirements:
    - Maximum {max_depth} levels deep
    - Each task must be atomic and testable
    - Specify dependencies between tasks
    - Estimate duration for each task
    - Assign appropriate agents (ExpertAgent, RefactorAgent, etc.)
    
    Return JSON array of task objects.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,  # Low temperature for structured output
    )
    
    tasks = json.loads(response.choices[0].message.content)
    
    # Validate task structure
    for task in tasks:
        if not self._validate_task_schema(task):
            raise ValueError(f"Invalid task schema: {task}")
    
    # Schedule all tasks
    for task in tasks:
        self.schedule(task)
    
    return tasks
```

---

## 4. Task Dependencies

### 4.1 Dependency Graph

Tasks can have dependencies that must complete before execution:

```
Task Graph:
    
    T1: Setup environment
        │
        ├─→ T2: Install dependencies (depends on T1)
        │       │
        │       ├─→ T4: Run tests (depends on T2)
        │       │
        │       └─→ T5: Build project (depends on T2)
        │               │
        │               └─→ T7: Deploy (depends on T5, T6)
        │
        └─→ T3: Configure settings (depends on T1)
                │
                └─→ T6: Validate config (depends on T3)
                        │
                        └─→ T7: Deploy (depends on T5, T6)
```

**Execution Order:** T1 → (T2, T3) → (T4, T5, T6) → T7

### 4.2 Dependency Resolution Algorithm

```python
def resolve_dependencies(self, task_id: str) -> bool:
    """Check if all dependencies are satisfied.
    
    Args:
        task_id: Task to check
    
    Returns:
        True if all dependencies completed, False otherwise
    """
    task = self.get_task(task_id)
    dependencies = task.get("dependencies", [])
    
    # No dependencies → ready to execute
    if not dependencies:
        return True
    
    # Check each dependency
    for dep_id in dependencies:
        dep_task = self.get_task(dep_id)
        
        # Dependency not found → cannot resolve
        if dep_task is None:
            logger.error(f"Dependency {dep_id} not found for task {task_id}")
            return False
        
        # Dependency not completed → not ready
        if dep_task.get("status") != "completed":
            return False
    
    # All dependencies completed
    return True

def get_ready_tasks(self) -> list[dict]:
    """Get all tasks with satisfied dependencies.
    
    Returns:
        List of tasks ready for execution
    """
    ready_tasks = []
    
    for task in self.queue:
        if task.get("status") == "pending" and self.resolve_dependencies(task["id"]):
            ready_tasks.append(task)
    
    # Sort by priority (1 = highest)
    ready_tasks.sort(key=lambda t: t.get("priority", 5))
    
    return ready_tasks
```

### 4.3 Circular Dependency Detection

```python
def detect_circular_dependencies(self, task_graph: dict) -> list[list[str]]:
    """Detect circular dependencies using DFS.
    
    Args:
        task_graph: {task_id: [dependency_ids]}
    
    Returns:
        List of circular dependency chains
    """
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(task_id: str, path: list[str]) -> None:
        visited.add(task_id)
        rec_stack.add(task_id)
        path.append(task_id)
        
        for dep_id in task_graph.get(task_id, []):
            if dep_id not in visited:
                dfs(dep_id, path.copy())
            elif dep_id in rec_stack:
                # Cycle detected
                cycle_start = path.index(dep_id)
                cycle = path[cycle_start:] + [dep_id]
                cycles.append(cycle)
        
        rec_stack.remove(task_id)
    
    for task_id in task_graph:
        if task_id not in visited:
            dfs(task_id, [])
    
    return cycles

# Example usage
task_graph = {
    "T1": ["T2"],
    "T2": ["T3"],
    "T3": ["T1"],  # Circular dependency!
}

cycles = planner.detect_circular_dependencies(task_graph)
# → [["T1", "T2", "T3", "T1"]]

if cycles:
    raise ValueError(f"Circular dependencies detected: {cycles}")
```

---

## 5. Planning Authority & Constraints

### 5.1 Decision Authorities

From `agent_operational_extensions.py` → `PlannerDecisionContract`:

**Task Decomposition:**
```python
DecisionAuthority(
    decision_type="task_decomposition",
    authorization_level=AuthorizationLevel.AUTONOMOUS,
    constraints={
        "max_subtasks": 20,        # Limit decomposition breadth
        "max_depth": 5,            # Limit decomposition depth
        "must_be_achievable": True,  # Tasks must be executable
    },
    override_conditions=["user_explicit_simplification"],
    rationale_required=True,
    audit_required=True,
)
```

**Planning Horizon:**
```python
DecisionAuthority(
    decision_type="planning_horizon_extension",
    authorization_level=AuthorizationLevel.SUPERVISED,
    constraints={
        "max_planning_horizon_days": 30,      # Max 30-day planning window
        "requires_user_approval_beyond": 7,   # >7 days needs user approval
    },
    override_conditions=["emergency_long_term_planning"],
    rationale_required=True,
    audit_required=True,
)
```

**Cross-Agent Coordination:**
```python
DecisionAuthority(
    decision_type="cross_agent_call",
    authorization_level=AuthorizationLevel.SUPERVISED,
    constraints={
        "max_agents_per_plan": 5,                # Max 5 agents per plan
        "no_circular_dependencies": True,         # Prevent infinite loops
        "coordination_protocol_required": True,   # Must use kernel routing
    },
    override_conditions=["complex_multi_agent_coordination"],
    rationale_required=True,
    audit_required=True,
)
```

**Resource Allocation:**
```python
DecisionAuthority(
    decision_type="resource_allocation",
    authorization_level=AuthorizationLevel.SUPERVISED,
    constraints={
        "budget_constraint_checked": True,        # Check resource limits
        "resource_availability_verified": True,   # Verify resources exist
    },
    override_conditions=["emergency_resource_override"],
    rationale_required=True,
    audit_required=True,
)
```

### 5.2 Planning Constraints Validation

```python
def validate_plan(self, plan: list[dict]) -> tuple[bool, str]:
    """Validate plan against authority constraints.
    
    Args:
        plan: List of tasks
    
    Returns:
        (is_valid, reason)
    """
    # Constraint 1: Max subtasks
    if len(plan) > 20:
        return False, f"Plan exceeds max subtasks (20): {len(plan)} tasks"
    
    # Constraint 2: Max depth
    max_depth = max(task.get("depth", 0) for task in plan)
    if max_depth > 5:
        return False, f"Plan exceeds max depth (5): depth {max_depth}"
    
    # Constraint 3: Max agents
    agents_used = set(task.get("assigned_agent") for task in plan if task.get("assigned_agent"))
    if len(agents_used) > 5:
        return False, f"Plan uses too many agents (5): {len(agents_used)} agents"
    
    # Constraint 4: Circular dependencies
    task_graph = {task["id"]: task.get("dependencies", []) for task in plan}
    cycles = self.detect_circular_dependencies(task_graph)
    if cycles:
        return False, f"Circular dependencies detected: {cycles}"
    
    # Constraint 5: Planning horizon
    max_duration = sum(task.get("estimated_duration", 0) for task in plan)
    if max_duration > 7 * 24 * 3600:  # 7 days in seconds
        # Requires user approval for >7 day plans
        approval = kernel.route(
            task="approve_long_term_plan",
            source="planner",
            metadata={"duration_days": max_duration / (24 * 3600)}
        )
        if not approval:
            return False, "User denied long-term plan approval"
    
    return True, "Plan validated"
```

---

## 6. Multi-Agent Coordination

### 6.1 Agent Assignment Strategies

**Strategy 1: Manual Assignment**

```python
task = {
    "id": "refactor-auth",
    "name": "Refactor authentication module",
    "assigned_agent": "RefactorAgent",  # Explicitly assigned
    "required_tools": ["ast_parser", "code_formatter"],
}
```

**Strategy 2: Auto-Assignment by Task Type**

```python
def auto_assign_agent(self, task: dict) -> str:
    """Automatically assign agent based on task type.
    
    Args:
        task: Task dictionary
    
    Returns:
        Agent name
    """
    task_type = task.get("type")
    
    assignment_rules = {
        "code_refactor": "RefactorAgent",
        "documentation": "DocGenerator",
        "testing": "TestQAGenerator",
        "security_audit": "CodeAdversaryAgent",
        "research": "ExpertAgent",
        "sandbox_execution": "SandboxRunner",
        "dependency_audit": "DependencyAuditor",
        "long_context": "LongContextAgent",
    }
    
    return assignment_rules.get(task_type, "ExpertAgent")  # Default to ExpertAgent
```

**Strategy 3: Load Balancing**

```python
def load_balanced_assign(self, task: dict, agent_load: dict[str, int]) -> str:
    """Assign agent based on current load.
    
    Args:
        task: Task dictionary
        agent_load: {agent_name: active_task_count}
    
    Returns:
        Least-loaded compatible agent
    """
    compatible_agents = self.get_compatible_agents(task)
    
    # Sort by load (ascending)
    sorted_agents = sorted(compatible_agents, key=lambda a: agent_load.get(a, 0))
    
    return sorted_agents[0]  # Least loaded agent
```

### 6.2 Agent Coordination Protocol

**Coordination via Kernel Routing:**

```python
# PlannerAgent coordinates multiple agents for complex task
def coordinate_agents(self, plan: list[dict]) -> dict:
    """Coordinate multiple agents to execute plan.
    
    Args:
        plan: List of tasks with agent assignments
    
    Returns:
        Execution results
    """
    results = {}
    
    for task in plan:
        # Check dependencies
        if not self.resolve_dependencies(task["id"]):
            # Dependencies not ready → skip for now
            continue
        
        # Route to assigned agent via kernel
        agent_name = task.get("assigned_agent", self.auto_assign_agent(task))
        
        result = kernel.route(
            task=task["description"],
            source="planner",
            metadata={
                "task_id": task["id"],
                "target_agent": agent_name,
                "coordination": True,
                "planner_id": self.id,
            },
        )
        
        # Store result
        results[task["id"]] = result
        
        # Update task status
        task["status"] = "completed" if result.get("success") else "failed"
        task["completed_at"] = datetime.now(UTC)
    
    return results
```

**Agent Communication Pattern:**

```
PlannerAgent
    │
    ├─→ Task 1: RefactorAgent
    │   └─→ kernel.route(task, target_agent="RefactorAgent")
    │       └─→ RefactorAgent executes → returns result
    │           └─→ PlannerAgent receives result
    │
    ├─→ Task 2: TestQAGenerator (depends on Task 1)
    │   └─→ Wait for Task 1 completion
    │       └─→ kernel.route(task, target_agent="TestQAGenerator")
    │           └─→ TestQAGenerator executes → returns result
    │
    └─→ Task 3: DocGenerator (depends on Task 1, Task 2)
        └─→ Wait for Task 1, Task 2 completion
            └─→ kernel.route(task, target_agent="DocGenerator")
                └─→ DocGenerator executes → returns result
```

### 6.3 Coordination Failure Handling

```python
def handle_coordination_failure(self, task: dict, failure: dict) -> dict:
    """Handle agent coordination failures.
    
    Args:
        task: Failed task
        failure: Failure details
    
    Returns:
        Recovery action
    """
    failure_mode = failure.get("mode")
    
    if failure_mode == "agent_unavailable":
        # Re-assign to different agent
        alternative_agent = self.find_alternative_agent(task)
        return {"action": "reassign", "agent": alternative_agent}
    
    elif failure_mode == "dependency_failure":
        # Re-execute dependency
        failed_dep = failure.get("dependency_id")
        return {"action": "retry_dependency", "task_id": failed_dep}
    
    elif failure_mode == "timeout":
        # Increase timeout and retry
        return {"action": "retry", "timeout_multiplier": 2}
    
    elif failure_mode == "resource_exhausted":
        # Wait for resources and retry
        return {"action": "queue", "retry_after": 300}  # 5 minutes
    
    else:
        # Unknown failure → escalate to user
        return {"action": "escalate", "reason": failure.get("message")}
```

---

## 7. Resource Allocation

### 7.1 Resource Types

**Computational Resources:**
```python
resources = {
    "cpu_cores": 8,
    "memory_gb": 16,
    "disk_gb": 100,
    "gpu_count": 1,
}
```

**API Resources:**
```python
api_limits = {
    "openai_tokens_per_minute": 10000,
    "openai_requests_per_minute": 60,
    "huggingface_requests_per_hour": 1000,
}
```

**Agent Resources:**
```python
agent_capacity = {
    "RefactorAgent": {"max_concurrent_tasks": 3},
    "DocGenerator": {"max_concurrent_tasks": 5},
    "ExpertAgent": {"max_concurrent_tasks": 2},
    "SandboxRunner": {"max_concurrent_tasks": 1},  # Heavy resource usage
}
```

### 7.2 Resource Allocation Algorithm

```python
def allocate_resources(self, plan: list[dict]) -> dict[str, dict]:
    """Allocate resources for task execution.
    
    Args:
        plan: List of tasks
    
    Returns:
        {task_id: allocated_resources}
    """
    allocations = {}
    available_resources = self.get_available_resources()
    
    for task in plan:
        required = task.get("required_resources", {})
        
        # Check if resources available
        if self.can_allocate(required, available_resources):
            # Allocate resources
            allocations[task["id"]] = required
            
            # Deduct from available pool
            for resource, amount in required.items():
                available_resources[resource] -= amount
        else:
            # Insufficient resources → queue task
            task["status"] = "queued"
            logger.warning(f"Insufficient resources for task {task['id']}, queuing")
    
    return allocations

def can_allocate(self, required: dict, available: dict) -> bool:
    """Check if required resources are available.
    
    Args:
        required: {resource_name: amount}
        available: {resource_name: amount}
    
    Returns:
        True if allocation possible
    """
    for resource, amount in required.items():
        if available.get(resource, 0) < amount:
            return False
    return True
```

### 7.3 Resource Monitoring

```python
def monitor_resource_usage(self) -> dict:
    """Monitor real-time resource usage.
    
    Returns:
        {resource_name: {used, available, total, percentage}}
    """
    import psutil
    
    return {
        "cpu": {
            "used": psutil.cpu_percent(),
            "available": 100 - psutil.cpu_percent(),
            "total": 100,
            "percentage": psutil.cpu_percent(),
        },
        "memory": {
            "used": psutil.virtual_memory().used / (1024**3),  # GB
            "available": psutil.virtual_memory().available / (1024**3),
            "total": psutil.virtual_memory().total / (1024**3),
            "percentage": psutil.virtual_memory().percent,
        },
        "disk": {
            "used": psutil.disk_usage("/").used / (1024**3),
            "available": psutil.disk_usage("/").free / (1024**3),
            "total": psutil.disk_usage("/").total / (1024**3),
            "percentage": psutil.disk_usage("/").percent,
        },
    }
```

---

## 8. Execution Strategies

### 8.1 Sequential Execution

**Use Case:** Tasks with strict dependencies, linear workflows

```python
def execute_sequential(self, plan: list[dict]) -> list[dict]:
    """Execute tasks sequentially (FIFO).
    
    Args:
        plan: Ordered list of tasks
    
    Returns:
        Execution results
    """
    results = []
    
    for task in plan:
        result = self.execute_task(task)
        results.append(result)
        
        if not result.get("success"):
            # Stop on first failure
            logger.error(f"Task {task['id']} failed, aborting plan")
            break
    
    return results
```

### 8.2 Parallel Execution

**Use Case:** Independent tasks, no shared resources

```python
import asyncio

async def execute_parallel(self, plan: list[dict]) -> list[dict]:
    """Execute independent tasks in parallel.
    
    Args:
        plan: List of independent tasks
    
    Returns:
        Execution results
    """
    # Create async tasks
    async_tasks = [
        self.execute_task_async(task) for task in plan
    ]
    
    # Execute all in parallel
    results = await asyncio.gather(*async_tasks)
    
    return results

async def execute_task_async(self, task: dict) -> dict:
    """Execute single task asynchronously."""
    result = await asyncio.to_thread(self.execute_task, task)
    return result
```

### 8.3 Priority-Based Execution

**Use Case:** Mixed priority tasks, optimize for important tasks first

```python
import heapq

def execute_priority(self, plan: list[dict]) -> list[dict]:
    """Execute tasks by priority (1 = highest).
    
    Args:
        plan: List of tasks with priorities
    
    Returns:
        Execution results
    """
    # Create priority queue (min-heap)
    priority_queue = []
    for task in plan:
        priority = task.get("priority", 5)  # Default mid-priority
        heapq.heappush(priority_queue, (priority, task))
    
    results = []
    
    while priority_queue:
        priority, task = heapq.heappop(priority_queue)
        
        # Check dependencies
        if not self.resolve_dependencies(task["id"]):
            # Re-queue with lower priority (wait for dependencies)
            heapq.heappush(priority_queue, (priority + 1, task))
            continue
        
        # Execute
        result = self.execute_task(task)
        results.append(result)
    
    return results
```

### 8.4 Adaptive Execution (Future)

**Use Case:** Learn from execution history, optimize task ordering

```python
def execute_adaptive(self, plan: list[dict], history: list[dict]) -> list[dict]:
    """Execute tasks with adaptive ordering based on historical performance.
    
    Args:
        plan: List of tasks
        history: Past execution history
    
    Returns:
        Execution results
    """
    # Analyze historical performance
    performance_stats = self.analyze_execution_history(history)
    
    # Reorder plan based on learned patterns
    optimized_plan = self.optimize_task_order(plan, performance_stats)
    
    # Execute optimized plan
    return self.execute_priority(optimized_plan)

def analyze_execution_history(self, history: list[dict]) -> dict:
    """Analyze historical execution data.
    
    Returns:
        {task_type: {avg_duration, success_rate, resource_usage}}
    """
    stats = {}
    
    for execution in history:
        task_type = execution.get("type")
        
        if task_type not in stats:
            stats[task_type] = {
                "total_executions": 0,
                "total_duration": 0,
                "successes": 0,
                "failures": 0,
            }
        
        stats[task_type]["total_executions"] += 1
        stats[task_type]["total_duration"] += execution.get("duration", 0)
        
        if execution.get("success"):
            stats[task_type]["successes"] += 1
        else:
            stats[task_type]["failures"] += 1
    
    # Compute averages
    for task_type, data in stats.items():
        data["avg_duration"] = data["total_duration"] / data["total_executions"]
        data["success_rate"] = data["successes"] / data["total_executions"]
    
    return stats
```

---

## 9. Planning Telemetry & Analytics

### 9.1 Execution Metrics

```python
@dataclass
class PlanningMetrics:
    """Metrics for planning performance."""
    
    plan_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_duration: float  # seconds
    avg_task_duration: float
    resource_utilization: dict  # {resource: percentage}
    agents_used: list[str]
    dependency_violations: int
    constraint_violations: int
    user_interventions: int

# Track metrics
metrics = PlanningMetrics(
    plan_id="plan-12345",
    total_tasks=15,
    completed_tasks=13,
    failed_tasks=2,
    total_duration=1824.5,
    avg_task_duration=121.6,
    resource_utilization={"cpu": 67.3, "memory": 45.2, "disk": 12.1},
    agents_used=["RefactorAgent", "DocGenerator", "TestQAGenerator"],
    dependency_violations=0,
    constraint_violations=1,  # Planning horizon exceeded
    user_interventions=1,  # User approved long-term plan
)
```

### 9.2 Performance Dashboards (Future)

**Real-Time Planning Dashboard:**

```
╔══════════════════════════════════════════════════════════╗
║              PlannerAgent Dashboard                      ║
╠══════════════════════════════════════════════════════════╣
║ Active Plans: 3                                          ║
║ Queued Tasks: 12                                         ║
║ Running Tasks: 5                                         ║
║ Completed Tasks (Today): 47                              ║
║ Failed Tasks (Today): 3                                  ║
╠══════════════════════════════════════════════════════════╣
║ Resource Utilization:                                    ║
║   CPU: ████████████░░░░░░░░░░  67%                       ║
║   Memory: ██████░░░░░░░░░░░░░░  45%                      ║
║   Disk: ██░░░░░░░░░░░░░░░░░░░░  12%                      ║
╠══════════════════════════════════════════════════════════╣
║ Top Agents:                                              ║
║   1. RefactorAgent (15 tasks)                            ║
║   2. DocGenerator (12 tasks)                             ║
║   3. TestQAGenerator (8 tasks)                           ║
╠══════════════════════════════════════════════════════════╣
║ Recent Failures:                                         ║
║   • Task "refactor-auth" - Timeout (300s)                ║
║   • Task "generate-docs" - Agent unavailable             ║
║   • Task "run-tests" - Dependency failure                ║
╚══════════════════════════════════════════════════════════╝
```

---

## 10. Tool Access (PlannerAgent)

From `agent_operational_extensions.py`:

```python
"PlannerAgent": {
    "task_decomposer": ToolAccessLevel.FULL_ACCESS,      # AI-powered task decomposition
    "resource_allocator": ToolAccessLevel.FULL_ACCESS,   # Resource management
    "agent_coordinator": ToolAccessLevel.LIMITED_WRITE,  # Cross-agent coordination (via kernel)
    "memory_system": ToolAccessLevel.READ_ONLY,          # Access past execution history
    "governance_system": ToolAccessLevel.READ_ONLY,      # View governance state (cannot modify)
}
```

**Tool Usage Examples:**

```python
# Task Decomposer
decomposed_tasks = planner.use_tool(
    "task_decomposer",
    goal="Build web scraper",
    max_depth=5
)

# Resource Allocator
allocation = planner.use_tool(
    "resource_allocator",
    tasks=plan,
    available_resources=get_available_resources()
)

# Agent Coordinator (via kernel)
result = planner.use_tool(
    "agent_coordinator",
    task=task,
    target_agent="RefactorAgent",
    coordination_metadata={"planner_id": planner.id}
)

# Memory System (read-only)
history = planner.use_tool(
    "memory_system",
    operation="query",
    filter={"task_type": "refactoring", "limit": 10}
)
```

---

## 11. Testing & Validation

### 11.1 Unit Tests

```python
# tests/test_planner_agent.py

def test_task_scheduling():
    planner = PlannerAgent(kernel=kernel)
    
    task = {"id": "t1", "name": "Test task", "priority": 1}
    planner.schedule(task)
    
    assert len(planner.queue) == 1
    assert planner.queue[0]["id"] == "t1"

def test_dependency_resolution():
    planner = PlannerAgent(kernel=kernel)
    
    # Create task graph
    t1 = {"id": "t1", "status": "completed", "dependencies": []}
    t2 = {"id": "t2", "status": "pending", "dependencies": ["t1"]}
    t3 = {"id": "t3", "status": "pending", "dependencies": ["t2"]}
    
    planner.tasks = {"t1": t1, "t2": t2, "t3": t3}
    
    # t2 should be ready (t1 completed)
    assert planner.resolve_dependencies("t2") == True
    
    # t3 should not be ready (t2 pending)
    assert planner.resolve_dependencies("t3") == False

def test_circular_dependency_detection():
    planner = PlannerAgent(kernel=kernel)
    
    task_graph = {
        "t1": ["t2"],
        "t2": ["t3"],
        "t3": ["t1"],  # Circular!
    }
    
    cycles = planner.detect_circular_dependencies(task_graph)
    
    assert len(cycles) == 1
    assert "t1" in cycles[0] and "t2" in cycles[0] and "t3" in cycles[0]
```

### 11.2 Integration Tests

```python
def test_multi_agent_coordination():
    planner = PlannerAgent(kernel=kernel)
    refactor_agent = RefactorAgent(kernel=kernel)
    doc_generator = DocGenerator(kernel=kernel)
    
    # Create plan
    plan = [
        {"id": "t1", "name": "Refactor code", "assigned_agent": "RefactorAgent"},
        {"id": "t2", "name": "Generate docs", "assigned_agent": "DocGenerator", "dependencies": ["t1"]},
    ]
    
    # Execute plan
    results = planner.coordinate_agents(plan)
    
    # Verify execution order
    assert results["t1"]["completed_at"] < results["t2"]["started_at"]
    
    # Verify both tasks completed
    assert results["t1"]["success"] == True
    assert results["t2"]["success"] == True
```

---

## 12. Summary

**Planning Hierarchy Principles:**

1. **5-Level Decomposition:** User Intent → Strategic → Tactical → Operational → Agent Execution
2. **Dependency Resolution:** Automatic dependency checking, circular dependency detection
3. **Authority Constraints:** Max 20 subtasks, depth 5, 5 agents, 7-day autonomous horizon
4. **Multi-Agent Coordination:** Kernel-routed agent communication, load balancing, failure handling
5. **Resource Allocation:** CPU/memory/disk tracking, API rate limits, agent capacity management
6. **Execution Strategies:** Sequential, parallel, priority-based, adaptive (ML-driven)
7. **Telemetry & Analytics:** Real-time metrics, performance dashboards, historical analysis
8. **Tool Access Control:** Task decomposer, resource allocator, agent coordinator (limited write)

**Current State:**
- PlannerAgent implemented with kernel routing
- Basic task scheduling/execution operational
- Dependency resolution architecture complete
- Advanced features (decomposition, adaptive execution) planned for future

**Related Documentation:**
- AGENT_ORCHESTRATION.md (kernel routing patterns)
- VALIDATION_CHAINS.md (governance validation)
- AGENT_TOOL_ACCESS.md (tool permissions)

---

**File:** `relationships/agents/PLANNING_HIERARCHIES.md`  
**Version:** 1.0  
**Last Updated:** 2025-01-27

---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/agents/planner_agent.py]]

---


---

## RELATED SYSTEMS

### GUI Integration ([[../gui/00_MASTER_INDEX|GUI Master Index]])

| GUI Component | Planning Integration | Use Case | Documentation |
|---------------|---------------------|----------|---------------|
| [[../gui/03_HANDLER_RELATIONSHIPS\|DashboardHandlers]] | Learning path generation | Multi-step learning workflows | Section 3 learning paths |
| [[../gui/02_PANEL_RELATIONSHIPS\|ProactiveActionsPanel]] | Complex action triggers | Task decomposition buttons (future) | Section 3 navigation |
| [[../gui/01_DASHBOARD_RELATIONSHIPS\|Dashboard]] | Progress display (future) | Task completion visualization | Planned feature |
| [[../gui/04_UTILS_RELATIONSHIPS\|AsyncWorker]] | Task execution | Background task processing | Section 3 async worker |

### Core AI Integration ([[../core-ai/00-INDEX|Core AI Index]])

| Planning Operation | Core AI System | Purpose | Documentation |
|-------------------|----------------|---------|---------------|
| **Task Scheduling** | [[../core-ai/04-LearningRequestManager-Relationship-Map\|LearningRequestManager]] | Learning task prioritization | Section 3.1 task scheduling |
| **Resource Allocation** | [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Task memory management | Section 7.1 resource types |
| **Constraint Validation** | [[../core-ai/01-FourLaws-Relationship-Map\|FourLaws]] | Task ethics checking | Section 5.2 constraints validation |
| **Agent Assignment** | [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Personality-based task matching | Section 6.1 assignment strategies |
| **Priority Setting** | [[../core-ai/04-LearningRequestManager-Relationship-Map\|Learning]] | CRITICAL/HIGH/MEDIUM/LOW | Section 8.3 priority execution |

### Planning Hierarchy with GUI

**User-Triggered Multi-Step Workflow:**
```
[[../gui/03_HANDLER_RELATIONSHIPS#learning-path-generation|User Clicks "Generate Learning Path"]] → 
DashboardHandler._on_generate_learning_path(topic) → 
[[../core-ai/04-LearningRequestManager-Relationship-Map|LearningRequestManager.create_request()]] → 
PlannerAgent.decompose_learning_task() → 
Level 1: Strategic Plan → 
Level 2: Tactical Subtasks → 
Level 3: Operational Actions → 
Level 4: Agent Delegation → 
Level 5: Tool Invocation → 
[[../gui/01_DASHBOARD_RELATIONSHIPS|Dashboard Progress Display]]
```

### Resource Allocation with Core Systems

| Resource Type | Core AI System | PlannerAgent Use | Documentation |
|---------------|----------------|------------------|---------------|
| **Computational** | [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Mood-based CPU allocation | Section 7.1 resource types |
| **Memory** | [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Knowledge base capacity | Section 7.2 allocation algorithm |
| **API Calls** | [[../core-ai/06-CommandOverride-Relationship-Map\|Override]] | Rate limiting (unless bypassed) | Section 7.1 resource types |
| **Agent Availability** | All agents via CouncilHub | Multi-agent task distribution | Section 6.2 coordination protocol |

### Task Dependencies with Learning System

**Learning Request → Planned Execution:**
```
[[../core-ai/04-LearningRequestManager-Relationship-Map|Learning Request Created]] → 
Admin Approval → 
PlannerAgent.schedule_learning_task() → 
Dependency Graph Construction → 
Resource Allocation → 
Agent Assignment → 
Execution Strategy Selection → 
[[../gui/01_DASHBOARD_RELATIONSHIPS|GUI Progress Updates]]
```

### Priority-Based Execution

Integrates with [[../core-ai/04-LearningRequestManager-Relationship-Map|LearningRequestManager]] priorities:

| Priority | Execution Strategy | GUI Feedback | Documentation |
|----------|-------------------|--------------|---------------|
| `CRITICAL` | Immediate, sequential | Real-time progress bar | Section 8.3 priority execution |
| `HIGH` | Next in queue, parallel if resources available | Notification on start | Section 8.2 parallel execution |
| `MEDIUM` | Standard scheduling | Batch notifications | Section 8.1 sequential execution |
| `LOW` | Background, opportunistic | Silent execution, summary on complete | Section 8.4 adaptive execution |

---

**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Status:** ✅ Cross-linked with GUI and Core AI systems
