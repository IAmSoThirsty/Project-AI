"""
DAG (Directed Acyclic Graph) Executor

Provides workflow definition and execution as directed acyclic graphs with:
- Dependency management
- Parallel execution
- Cycle detection
- Topological sorting
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """Status of a DAG node during execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGNode:
    """
    A node in the workflow DAG
    
    Attributes:
        id: Unique identifier for the node
        task: Callable task to execute
        dependencies: List of node IDs this node depends on
        metadata: Additional metadata for the node
        status: Current execution status
        result: Result from task execution
        error: Error if task failed
        retries: Number of retries attempted
    """
    id: str
    task: Callable
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    retries: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, DAGNode):
            return self.id == other.id
        return False


@dataclass
class DAG:
    """
    Directed Acyclic Graph for workflow definition
    
    Manages workflow structure with dependency tracking and validation.
    """
    name: str
    nodes: Dict[str, DAGNode] = field(default_factory=dict)
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: DAGNode) -> None:
        """Add a node to the DAG"""
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists in DAG")
        self.nodes[node.id] = node

    def add_edge(self, from_node_id: str, to_node_id: str) -> None:
        """Add a dependency edge from one node to another"""
        if from_node_id not in self.nodes:
            raise ValueError(f"Node {from_node_id} not found in DAG")
        if to_node_id not in self.nodes:
            raise ValueError(f"Node {to_node_id} not found in DAG")
        
        to_node = self.nodes[to_node_id]
        if from_node_id not in to_node.dependencies:
            to_node.dependencies.append(from_node_id)

    def validate(self) -> bool:
        """
        Validate the DAG structure
        
        Checks for:
        - All dependencies exist
        - No cycles
        - At least one node
        """
        if not self.nodes:
            raise ValueError("DAG must contain at least one node")

        # Check all dependencies exist
        for node in self.nodes.values():
            for dep_id in node.dependencies:
                if dep_id not in self.nodes:
                    raise ValueError(
                        f"Node {node.id} depends on non-existent node {dep_id}"
                    )

        # Check for cycles
        if self._has_cycle():
            raise ValueError("DAG contains a cycle")

        return True

    def _has_cycle(self) -> bool:
        """Detect cycles using DFS with color marking"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node_id: WHITE for node_id in self.nodes}

        def visit(node_id: str) -> bool:
            if color[node_id] == GRAY:
                return True  # Cycle detected
            if color[node_id] == BLACK:
                return False  # Already processed

            color[node_id] = GRAY
            node = self.nodes[node_id]
            
            for dep_id in node.dependencies:
                if visit(dep_id):
                    return True

            color[node_id] = BLACK
            return False

        for node_id in self.nodes:
            if color[node_id] == WHITE:
                if visit(node_id):
                    return True

        return False

    def topological_sort(self) -> List[List[str]]:
        """
        Return nodes in topological order, grouped by execution level
        
        Nodes at the same level can be executed in parallel.
        """
        in_degree = {node_id: 0 for node_id in self.nodes}
        
        # Calculate in-degrees
        for node in self.nodes.values():
            for dep_id in node.dependencies:
                in_degree[dep_id] += 1

        result = []
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]

        while queue:
            # All nodes in current queue can be executed in parallel
            result.append(queue[:])
            next_queue = []

            for node_id in queue:
                node = self.nodes[node_id]
                for dep_id in node.dependencies:
                    in_degree[dep_id] -= 1
                    if in_degree[dep_id] == 0:
                        next_queue.append(dep_id)

            queue = next_queue

        # Check if all nodes were processed
        if sum(in_degree.values()) != 0:
            raise ValueError("DAG contains a cycle")

        return result

    def get_ready_nodes(self) -> List[DAGNode]:
        """Get nodes ready for execution (all dependencies completed)"""
        ready = []
        for node in self.nodes.values():
            if node.status != NodeStatus.PENDING:
                continue

            # Check if all dependencies are completed
            all_deps_completed = all(
                self.nodes[dep_id].status == NodeStatus.COMPLETED
                for dep_id in node.dependencies
            )

            if all_deps_completed:
                ready.append(node)

        return ready


class DAGExecutor:
    """
    Executes a DAG workflow with parallel execution and error handling
    """

    def __init__(
        self,
        max_parallel: int = 10,
        fail_fast: bool = False,
        continue_on_error: bool = False,
    ):
        """
        Initialize DAG executor
        
        Args:
            max_parallel: Maximum number of nodes to execute in parallel
            fail_fast: Stop execution on first failure
            continue_on_error: Continue executing independent nodes after failure
        """
        self.max_parallel = max_parallel
        self.fail_fast = fail_fast
        self.continue_on_error = continue_on_error
        self.execution_log: List[Dict[str, Any]] = []

    async def execute(self, dag: DAG, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the DAG workflow
        
        Args:
            dag: DAG to execute
            context: Shared context passed to all tasks
            
        Returns:
            Execution result with status and outputs
        """
        dag.validate()
        context = context or {}
        
        logger.info(f"Starting DAG execution: {dag.name}")
        start_time = datetime.utcnow()

        try:
            execution_levels = dag.topological_sort()
            
            for level_idx, level_nodes in enumerate(execution_levels):
                logger.info(f"Executing level {level_idx}: {len(level_nodes)} nodes")
                
                # Execute nodes at this level in parallel
                await self._execute_level(dag, level_nodes, context)

                # Check for failures
                failed_nodes = [
                    node_id for node_id in level_nodes
                    if dag.nodes[node_id].status == NodeStatus.FAILED
                ]

                if failed_nodes and self.fail_fast:
                    logger.error(f"Failing fast due to failures: {failed_nodes}")
                    break

            # Collect results
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            return self._build_result(dag, duration)

        except Exception as e:
            logger.error(f"DAG execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "execution_log": self.execution_log,
            }

    async def _execute_level(
        self,
        dag: DAG,
        node_ids: List[str],
        context: Dict[str, Any],
    ) -> None:
        """Execute all nodes at a given level in parallel"""
        semaphore = asyncio.Semaphore(self.max_parallel)

        async def execute_node(node_id: str):
            async with semaphore:
                node = dag.nodes[node_id]
                
                # Skip if dependencies failed and not continuing on error
                if not self.continue_on_error:
                    failed_deps = [
                        dep_id for dep_id in node.dependencies
                        if dag.nodes[dep_id].status == NodeStatus.FAILED
                    ]
                    if failed_deps:
                        logger.warning(
                            f"Skipping {node_id} due to failed dependencies: {failed_deps}"
                        )
                        node.status = NodeStatus.SKIPPED
                        return

                await self._execute_node(node, context)

        # Execute all nodes in parallel
        await asyncio.gather(
            *[execute_node(node_id) for node_id in node_ids],
            return_exceptions=True,
        )

    async def _execute_node(self, node: DAGNode, context: Dict[str, Any]) -> None:
        """Execute a single node"""
        logger.info(f"Executing node: {node.id}")
        node.status = NodeStatus.RUNNING
        node.start_time = datetime.utcnow()

        log_entry = {
            "node_id": node.id,
            "start_time": node.start_time.isoformat(),
            "status": "running",
        }

        try:
            # Execute task
            if asyncio.iscoroutinefunction(node.task):
                result = await node.task(context, node.metadata)
            else:
                result = node.task(context, node.metadata)

            node.result = result
            node.status = NodeStatus.COMPLETED
            log_entry["status"] = "completed"
            log_entry["result"] = result

            logger.info(f"Node {node.id} completed successfully")

        except Exception as e:
            node.error = e
            node.status = NodeStatus.FAILED
            log_entry["status"] = "failed"
            log_entry["error"] = str(e)

            logger.error(f"Node {node.id} failed: {e}", exc_info=True)

        finally:
            node.end_time = datetime.utcnow()
            duration = (node.end_time - node.start_time).total_seconds()
            log_entry["end_time"] = node.end_time.isoformat()
            log_entry["duration_seconds"] = duration
            self.execution_log.append(log_entry)

    def _build_result(self, dag: DAG, duration: float) -> Dict[str, Any]:
        """Build execution result summary"""
        completed = sum(
            1 for node in dag.nodes.values()
            if node.status == NodeStatus.COMPLETED
        )
        failed = sum(
            1 for node in dag.nodes.values()
            if node.status == NodeStatus.FAILED
        )
        skipped = sum(
            1 for node in dag.nodes.values()
            if node.status == NodeStatus.SKIPPED
        )

        status = "completed" if failed == 0 else "failed"

        return {
            "status": status,
            "duration_seconds": duration,
            "total_nodes": len(dag.nodes),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "node_results": {
                node_id: {
                    "status": node.status.value,
                    "result": node.result,
                    "error": str(node.error) if node.error else None,
                    "duration_seconds": (
                        (node.end_time - node.start_time).total_seconds()
                        if node.start_time and node.end_time
                        else None
                    ),
                }
                for node_id, node in dag.nodes.items()
            },
            "execution_log": self.execution_log,
        }
