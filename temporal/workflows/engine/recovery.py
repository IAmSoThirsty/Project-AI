"""
Failure Recovery Framework

Provides comprehensive failure recovery mechanisms including:
- Checkpoint/restore
- Partial failure handling
- Compensating transactions
- State recovery
"""

import asyncio
import json
import logging
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class RecoveryAction(Enum):
    """Recovery actions for failures"""
    RETRY = "retry"
    SKIP = "skip"
    ROLLBACK = "rollback"
    COMPENSATE = "compensate"
    FAIL = "fail"


@dataclass
class Checkpoint:
    """
    Workflow checkpoint for recovery
    
    Stores workflow state at a specific point for recovery.
    """
    id: str
    timestamp: datetime
    workflow_id: str
    state: Dict[str, Any]
    completed_nodes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert checkpoint to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "workflow_id": self.workflow_id,
            "state": self.state,
            "completed_nodes": self.completed_nodes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        """Create checkpoint from dictionary"""
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            workflow_id=data["workflow_id"],
            state=data["state"],
            completed_nodes=data.get("completed_nodes", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class RecoveryStrategy:
    """
    Strategy for recovering from failures
    
    Defines how to handle different types of failures.
    """
    name: str
    action: RecoveryAction
    max_retries: int = 3
    checkpoint_frequency: int = 5  # Checkpoint every N nodes
    compensating_action: Optional[Callable] = None
    rollback_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CheckpointManager:
    """
    Manages workflow checkpoints for recovery
    
    Provides checkpoint creation, storage, and retrieval.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize checkpoint manager
        
        Args:
            storage_path: Path to store checkpoints (None for in-memory)
        """
        self.storage_path = storage_path
        self.checkpoints: Dict[str, Checkpoint] = {}

        if storage_path:
            storage_path.mkdir(parents=True, exist_ok=True)

    async def create_checkpoint(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        completed_nodes: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Checkpoint:
        """
        Create a new checkpoint
        
        Args:
            workflow_id: ID of the workflow
            state: Current workflow state
            completed_nodes: List of completed node IDs
            metadata: Additional metadata
            
        Returns:
            Created checkpoint
        """
        checkpoint_id = f"{workflow_id}_{datetime.utcnow().isoformat()}"
        checkpoint = Checkpoint(
            id=checkpoint_id,
            timestamp=datetime.utcnow(),
            workflow_id=workflow_id,
            state=state.copy(),
            completed_nodes=completed_nodes.copy(),
            metadata=metadata or {},
        )

        # Store checkpoint
        self.checkpoints[checkpoint_id] = checkpoint

        # Persist to disk if configured
        if self.storage_path:
            await self._persist_checkpoint(checkpoint)

        logger.info(f"Created checkpoint: {checkpoint_id}")
        return checkpoint

    async def restore_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Restore a checkpoint
        
        Args:
            checkpoint_id: ID of checkpoint to restore
            
        Returns:
            Restored checkpoint or None if not found
        """
        # Try memory first
        if checkpoint_id in self.checkpoints:
            logger.info(f"Restored checkpoint from memory: {checkpoint_id}")
            return self.checkpoints[checkpoint_id]

        # Try loading from disk
        if self.storage_path:
            checkpoint = await self._load_checkpoint(checkpoint_id)
            if checkpoint:
                self.checkpoints[checkpoint_id] = checkpoint
                logger.info(f"Restored checkpoint from disk: {checkpoint_id}")
                return checkpoint

        logger.warning(f"Checkpoint not found: {checkpoint_id}")
        return None

    async def get_latest_checkpoint(
        self,
        workflow_id: str,
    ) -> Optional[Checkpoint]:
        """
        Get the latest checkpoint for a workflow
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Latest checkpoint or None
        """
        workflow_checkpoints = [
            cp for cp in self.checkpoints.values()
            if cp.workflow_id == workflow_id
        ]

        if not workflow_checkpoints:
            # Try loading from disk
            if self.storage_path:
                workflow_checkpoints = await self._load_workflow_checkpoints(workflow_id)

        if not workflow_checkpoints:
            return None

        return max(workflow_checkpoints, key=lambda cp: cp.timestamp)

    async def _persist_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Persist checkpoint to disk"""
        if not self.storage_path:
            return

        checkpoint_file = self.storage_path / f"{checkpoint.id}.json"
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
            logger.debug(f"Persisted checkpoint to: {checkpoint_file}")
        except Exception as e:
            logger.error(f"Failed to persist checkpoint: {e}", exc_info=True)

    async def _load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load checkpoint from disk"""
        if not self.storage_path:
            return None

        checkpoint_file = self.storage_path / f"{checkpoint_id}.json"
        if not checkpoint_file.exists():
            return None

        try:
            with open(checkpoint_file, "r") as f:
                data = json.load(f)
            return Checkpoint.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}", exc_info=True)
            return None

    async def _load_workflow_checkpoints(
        self,
        workflow_id: str,
    ) -> List[Checkpoint]:
        """Load all checkpoints for a workflow from disk"""
        if not self.storage_path:
            return []

        checkpoints = []
        for checkpoint_file in self.storage_path.glob(f"{workflow_id}_*.json"):
            try:
                with open(checkpoint_file, "r") as f:
                    data = json.load(f)
                checkpoints.append(Checkpoint.from_dict(data))
            except Exception as e:
                logger.error(
                    f"Failed to load checkpoint {checkpoint_file}: {e}",
                    exc_info=True,
                )

        return checkpoints


class FailureRecovery:
    """
    Comprehensive failure recovery system
    
    Handles workflow failures with checkpoint recovery, compensating
    transactions, and partial failure handling.
    """

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        default_strategy: Optional[RecoveryStrategy] = None,
    ):
        """
        Initialize failure recovery
        
        Args:
            checkpoint_manager: Manager for checkpoints
            default_strategy: Default recovery strategy
        """
        self.checkpoint_manager = checkpoint_manager
        self.default_strategy = default_strategy or RecoveryStrategy(
            name="default",
            action=RecoveryAction.RETRY,
            max_retries=3,
        )
        self.strategies: Dict[str, RecoveryStrategy] = {}
        self.recovery_log: List[Dict[str, Any]] = []

    def register_strategy(
        self,
        node_id: str,
        strategy: RecoveryStrategy,
    ) -> None:
        """
        Register recovery strategy for a specific node
        
        Args:
            node_id: ID of the node
            strategy: Recovery strategy to use
        """
        self.strategies[node_id] = strategy
        logger.info(f"Registered recovery strategy for {node_id}: {strategy.name}")

    async def handle_failure(
        self,
        workflow_id: str,
        node_id: str,
        error: Exception,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle node failure with recovery strategy
        
        Args:
            workflow_id: ID of the workflow
            node_id: ID of the failed node
            error: Exception that occurred
            context: Current execution context
            
        Returns:
            Recovery result with action taken
        """
        logger.error(f"Handling failure for node {node_id}: {error}")

        # Get recovery strategy
        strategy = self.strategies.get(node_id, self.default_strategy)

        # Log failure
        self._log_failure(workflow_id, node_id, error, strategy)

        # Execute recovery action
        result = await self._execute_recovery_action(
            workflow_id,
            node_id,
            error,
            context,
            strategy,
        )

        return result

    async def recover_from_checkpoint(
        self,
        workflow_id: str,
        checkpoint_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Recover workflow from checkpoint
        
        Args:
            workflow_id: ID of the workflow
            checkpoint_id: Specific checkpoint ID, or None for latest
            
        Returns:
            Recovered state or None
        """
        if checkpoint_id:
            checkpoint = await self.checkpoint_manager.restore_checkpoint(checkpoint_id)
        else:
            checkpoint = await self.checkpoint_manager.get_latest_checkpoint(workflow_id)

        if not checkpoint:
            logger.warning(f"No checkpoint found for workflow: {workflow_id}")
            return None

        logger.info(f"Recovering workflow from checkpoint: {checkpoint.id}")
        
        return {
            "checkpoint_id": checkpoint.id,
            "state": checkpoint.state,
            "completed_nodes": checkpoint.completed_nodes,
            "timestamp": checkpoint.timestamp.isoformat(),
        }

    async def _execute_recovery_action(
        self,
        workflow_id: str,
        node_id: str,
        error: Exception,
        context: Dict[str, Any],
        strategy: RecoveryStrategy,
    ) -> Dict[str, Any]:
        """Execute the recovery action based on strategy"""
        action = strategy.action

        if action == RecoveryAction.RETRY:
            return await self._handle_retry(workflow_id, node_id, strategy)

        elif action == RecoveryAction.SKIP:
            return await self._handle_skip(workflow_id, node_id)

        elif action == RecoveryAction.ROLLBACK:
            return await self._handle_rollback(workflow_id, node_id, strategy)

        elif action == RecoveryAction.COMPENSATE:
            return await self._handle_compensate(
                workflow_id,
                node_id,
                context,
                strategy,
            )

        elif action == RecoveryAction.FAIL:
            return await self._handle_fail(workflow_id, node_id, error)

        else:
            logger.error(f"Unknown recovery action: {action}")
            return {
                "action": "fail",
                "reason": f"Unknown recovery action: {action}",
            }

    async def _handle_retry(
        self,
        workflow_id: str,
        node_id: str,
        strategy: RecoveryStrategy,
    ) -> Dict[str, Any]:
        """Handle retry recovery action"""
        logger.info(f"Recovery action: RETRY for {node_id}")
        return {
            "action": "retry",
            "max_retries": strategy.max_retries,
            "node_id": node_id,
        }

    async def _handle_skip(
        self,
        workflow_id: str,
        node_id: str,
    ) -> Dict[str, Any]:
        """Handle skip recovery action"""
        logger.info(f"Recovery action: SKIP for {node_id}")
        return {
            "action": "skip",
            "node_id": node_id,
        }

    async def _handle_rollback(
        self,
        workflow_id: str,
        node_id: str,
        strategy: RecoveryStrategy,
    ) -> Dict[str, Any]:
        """Handle rollback recovery action"""
        logger.info(f"Recovery action: ROLLBACK for {node_id}")
        
        # Restore from latest checkpoint
        recovery_result = await self.recover_from_checkpoint(workflow_id)
        
        return {
            "action": "rollback",
            "node_id": node_id,
            "rollback_steps": strategy.rollback_steps,
            "checkpoint": recovery_result,
        }

    async def _handle_compensate(
        self,
        workflow_id: str,
        node_id: str,
        context: Dict[str, Any],
        strategy: RecoveryStrategy,
    ) -> Dict[str, Any]:
        """Handle compensate recovery action"""
        logger.info(f"Recovery action: COMPENSATE for {node_id}")

        if not strategy.compensating_action:
            logger.error("No compensating action defined")
            return {
                "action": "compensate",
                "success": False,
                "error": "No compensating action defined",
            }

        try:
            # Execute compensating action
            if asyncio.iscoroutinefunction(strategy.compensating_action):
                result = await strategy.compensating_action(context)
            else:
                result = strategy.compensating_action(context)

            return {
                "action": "compensate",
                "success": True,
                "result": result,
            }

        except Exception as e:
            logger.error(f"Compensating action failed: {e}", exc_info=True)
            return {
                "action": "compensate",
                "success": False,
                "error": str(e),
            }

    async def _handle_fail(
        self,
        workflow_id: str,
        node_id: str,
        error: Exception,
    ) -> Dict[str, Any]:
        """Handle fail recovery action"""
        logger.error(f"Recovery action: FAIL for {node_id}")
        return {
            "action": "fail",
            "node_id": node_id,
            "error": str(error),
        }

    def _log_failure(
        self,
        workflow_id: str,
        node_id: str,
        error: Exception,
        strategy: RecoveryStrategy,
    ) -> None:
        """Log failure for analysis"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "workflow_id": workflow_id,
            "node_id": node_id,
            "error": str(error),
            "error_type": type(error).__name__,
            "strategy": strategy.name,
            "action": strategy.action.value,
        }
        self.recovery_log.append(log_entry)
