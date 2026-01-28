# State Model Specification

**Version:** 1.0  
**Last Updated:** 2026-01-23  
**Status:** Specification

---

## Overview

The State Model defines how system state is managed, persisted, and recovered within the PACE system. It provides a unified approach to managing short-term state, long-term memory, episodic logs, and introspection records.

## Core Concepts

### State Types

1. **Short-Term State**: Active workflow state, session data, temporary variables
1. **Long-Term Memory**: Persistent knowledge, learned patterns, historical data
1. **Episodic Logs**: Recorded episodes of interactions and executions
1. **Introspection Records**: System self-monitoring and reflection data

### State Lifecycle

```
Create → Active → Checkpoint → Archive → Restore (if needed)
```

## Architecture

```
┌──────────────────────────────────────────┐
│       State Manager                       │
├──────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐         │
│  │  Memory    │  │  Episode   │         │
│  │   Store    │  │   Store    │         │
│  └────────────┘  └────────────┘         │
│                                          │
│  ┌────────────┐  ┌────────────┐         │
│  │ Checkpoint │  │ Persistence│         │
│  │  Manager   │  │   Layer    │         │
│  └────────────┘  └────────────┘         │
└──────────────────────────────────────────┘
```

## StateManager Implementation

### Core Class

```python
class StateManager:
    """
    Manages short-term state, long-term memory, episodic logs, and introspection records.
    
    The StateManager provides:
    - Key-value storage with namespacing
    - Episode recording and retrieval
    - Checkpoint/restore functionality
    - Persistence to backend storage
    """
    
    def __init__(self, config: dict):
        """
        Initialize the state manager.
        
        Args:
            config: Configuration containing:
                - backend: Storage backend (json, postgresql, mongodb)
                - data_dir: Directory for file-based storage
                - checkpoint_interval: Auto-checkpoint interval in seconds
                - retention_policy: Data retention settings
        """
        self.config = config
        self.backend = config.get("backend", "json")
        self.data_dir = config.get("data_dir", "./data/state")
        self.checkpoint_interval = config.get("checkpoint_interval", 60)
        
        # In-memory stores
        self.memory_store: Dict[str, Any] = {}
        self.episodes: List[Dict[str, Any]] = []
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        
        # Initialize persistence layer
        self.persistence = self._create_persistence_layer()
        
        # Load existing state
        self._load_state()
        
        # Start auto-checkpoint
        self._start_auto_checkpoint()
    
    def save_state(self, key: str, value: Any, namespace: str = "default") -> None:
        """
        Save a state value.
        
        Args:
            key: State key
            value: Value to store (must be serializable)
            namespace: Optional namespace for isolation
        """
        full_key = f"{namespace}:{key}"
        self.memory_store[full_key] = value
        
        # Persist asynchronously
        self.persistence.save(full_key, value)
    
    def load_state(self, key: str, default=None, namespace: str = "default"):
        """
        Load a state value.
        
        Args:
            key: State key
            default: Default value if key not found
            namespace: Optional namespace
            
        Returns:
            Stored value or default
        """
        full_key = f"{namespace}:{key}"
        return self.memory_store.get(full_key, default)
    
    def delete_state(self, key: str, namespace: str = "default") -> None:
        """
        Delete a state value.
        
        Args:
            key: State key
            namespace: Optional namespace
        """
        full_key = f"{namespace}:{key}"
        if full_key in self.memory_store:
            del self.memory_store[full_key]
            self.persistence.delete(full_key)
    
    def record_episode(self, data: dict) -> None:
        """
        Record an episode (interaction, execution, etc.).
        
        Args:
            data: Episode data to record
        """
        episode = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "episode_id": self._generate_episode_id()
        }
        self.episodes.append(episode)
        
        # Persist episode
        self.persistence.save_episode(episode)
        
        # Apply retention policy
        self._apply_retention_policy()
    
    def get_recent_episodes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent episodes.
        
        Args:
            limit: Maximum number of episodes to return
            
        Returns:
            List of recent episodes
        """
        return self.episodes[-limit:]
    
    def get_episodes_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get episodes matching criteria.
        
        Args:
            criteria: Search criteria
            
        Returns:
            List of matching episodes
        """
        results = []
        for episode in self.episodes:
            if self._matches_criteria(episode, criteria):
                results.append(episode)
        return results
    
    def checkpoint(self) -> str:
        """
        Create a checkpoint of current state.
        
        Returns:
            Checkpoint identifier
        """
        checkpoint_id = self._generate_checkpoint_id()
        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "memory_store": dict(self.memory_store),
            "episode_count": len(self.episodes)
        }
        self.checkpoints[checkpoint_id] = checkpoint
        
        # Persist checkpoint
        self.persistence.save_checkpoint(checkpoint)
        
        logger.info(f"Created checkpoint: {checkpoint_id}")
        return checkpoint_id
    
    def restore(self, checkpoint_id: str) -> None:
        """
        Restore state from a checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier
            
        Raises:
            StateError: If checkpoint not found
        """
        checkpoint = self.checkpoints.get(checkpoint_id)
        if not checkpoint:
            # Try loading from persistence
            checkpoint = self.persistence.load_checkpoint(checkpoint_id)
        
        if not checkpoint:
            raise StateError(f"Checkpoint '{checkpoint_id}' not found")
        
        # Restore state
        self.memory_store = dict(checkpoint["memory_store"])
        
        logger.info(f"Restored state from checkpoint: {checkpoint_id}")
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List available checkpoints.
        
        Returns:
            List of checkpoint metadata
        """
        return [
            {
                "checkpoint_id": cp["checkpoint_id"],
                "timestamp": cp["timestamp"],
                "episode_count": cp["episode_count"]
            }
            for cp in self.checkpoints.values()
        ]
    
    def clear_namespace(self, namespace: str) -> None:
        """
        Clear all state in a namespace.
        
        Args:
            namespace: Namespace to clear
        """
        prefix = f"{namespace}:"
        keys_to_delete = [k for k in self.memory_store.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            del self.memory_store[key]
            self.persistence.delete(key)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get state statistics.
        
        Returns:
            Statistics dictionary
        """
        namespaces = set()
        for key in self.memory_store.keys():
            if ":" in key:
                namespaces.add(key.split(":")[0])
        
        return {
            "total_keys": len(self.memory_store),
            "total_episodes": len(self.episodes),
            "total_checkpoints": len(self.checkpoints),
            "namespaces": list(namespaces),
            "memory_size_bytes": self._calculate_memory_size()
        }
    
    def _create_persistence_layer(self) -> 'PersistenceLayer':
        """Create persistence layer based on backend."""
        if self.backend == "json":
            return JSONPersistence(self.data_dir)
        elif self.backend == "postgresql":
            return PostgreSQLPersistence(self.config.get("db_config", {}))
        elif self.backend == "mongodb":
            return MongoDBPersistence(self.config.get("db_config", {}))
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
    
    def _load_state(self) -> None:
        """Load state from persistence."""
        self.memory_store = self.persistence.load_all_state()
        self.episodes = self.persistence.load_episodes()
    
    def _start_auto_checkpoint(self) -> None:
        """Start automatic checkpoint timer."""
        if self.checkpoint_interval > 0:
            # In real implementation, use threading.Timer or similar
            pass
    
    def _apply_retention_policy(self) -> None:
        """Apply data retention policy."""
        retention = self.config.get("retention_policy", {})
        max_episodes = retention.get("max_episodes", 10000)
        
        if len(self.episodes) > max_episodes:
            # Remove oldest episodes
            to_remove = len(self.episodes) - max_episodes
            self.episodes = self.episodes[to_remove:]
    
    def _matches_criteria(self, episode: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """Check if episode matches criteria."""
        for key, value in criteria.items():
            if key not in episode["data"] or episode["data"][key] != value:
                return False
        return True
    
    def _calculate_memory_size(self) -> int:
        """Calculate approximate memory size."""
        import sys
        return sys.getsizeof(self.memory_store) + sys.getsizeof(self.episodes)
    
    def _generate_episode_id(self) -> str:
        """Generate unique episode ID."""
        import uuid
        return f"episode-{uuid.uuid4().hex[:8]}"
    
    def _generate_checkpoint_id(self) -> str:
        """Generate unique checkpoint ID."""
        import uuid
        return f"checkpoint-{uuid.uuid4().hex[:8]}"
```

## Persistence Layer

### PersistenceLayer Interface

```python
class PersistenceLayer(ABC):
    """Base interface for persistence backends."""
    
    @abstractmethod
    def save(self, key: str, value: Any) -> None:
        """Save a key-value pair."""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """Load a value by key."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key-value pair."""
        pass
    
    @abstractmethod
    def load_all_state(self) -> Dict[str, Any]:
        """Load all state."""
        pass
    
    @abstractmethod
    def save_episode(self, episode: Dict[str, Any]) -> None:
        """Save an episode."""
        pass
    
    @abstractmethod
    def load_episodes(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load episodes."""
        pass
    
    @abstractmethod
    def save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """Save a checkpoint."""
        pass
    
    @abstractmethod
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load a checkpoint."""
        pass
```

### JSON Persistence Implementation

```python
class JSONPersistence(PersistenceLayer):
    """JSON file-based persistence."""
    
    def __init__(self, data_dir: str):
        """
        Initialize JSON persistence.
        
        Args:
            data_dir: Directory for JSON files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.state_file = os.path.join(data_dir, "state.json")
        self.episodes_file = os.path.join(data_dir, "episodes.json")
        self.checkpoints_dir = os.path.join(data_dir, "checkpoints")
        os.makedirs(self.checkpoints_dir, exist_ok=True)
    
    def save(self, key: str, value: Any) -> None:
        """Save a key-value pair."""
        state = self.load_all_state()
        state[key] = value
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def load(self, key: str) -> Optional[Any]:
        """Load a value by key."""
        state = self.load_all_state()
        return state.get(key)
    
    def delete(self, key: str) -> None:
        """Delete a key-value pair."""
        state = self.load_all_state()
        if key in state:
            del state[key]
            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)
    
    def load_all_state(self) -> Dict[str, Any]:
        """Load all state."""
        if not os.path.exists(self.state_file):
            return {}
        
        with open(self.state_file, "r") as f:
            return json.load(f)
    
    def save_episode(self, episode: Dict[str, Any]) -> None:
        """Save an episode."""
        episodes = self.load_episodes()
        episodes.append(episode)
        with open(self.episodes_file, "w") as f:
            json.dump(episodes, f, indent=2)
    
    def load_episodes(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load episodes."""
        if not os.path.exists(self.episodes_file):
            return []
        
        with open(self.episodes_file, "r") as f:
            episodes = json.load(f)
        
        if limit:
            return episodes[-limit:]
        return episodes
    
    def save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """Save a checkpoint."""
        checkpoint_id = checkpoint["checkpoint_id"]
        checkpoint_file = os.path.join(self.checkpoints_dir, f"{checkpoint_id}.json")
        with open(checkpoint_file, "w") as f:
            json.dump(checkpoint, f, indent=2)
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load a checkpoint."""
        checkpoint_file = os.path.join(self.checkpoints_dir, f"{checkpoint_id}.json")
        if not os.path.exists(checkpoint_file):
            return None
        
        with open(checkpoint_file, "r") as f:
            return json.load(f)
```

## State Namespacing

### Namespace Usage

```python
# System state
state_manager.save_state("config", config_data, namespace="system")

# User state
state_manager.save_state("preferences", user_prefs, namespace="user:john")

# Workflow state
state_manager.save_state("status", workflow_status, namespace="workflow:wf123")

# Agent state
state_manager.save_state("context", agent_context, namespace="agent:agent1")
```

## Episode Recording

### Episode Structure

```python
{
    "episode_id": "episode-abc123",
    "timestamp": "2026-01-23T12:00:00Z",
    "data": {
        "identity_phase": "bonded",
        "goal": {...},
        "plan": {...},
        "result": {...},
        "explanation": "..."
    }
}
```

### Episode Queries

```python
# Get recent episodes
recent = state_manager.get_recent_episodes(limit=10)

# Get episodes by criteria
criteria = {"identity_phase": "bonded", "goal.type": "diagnostic"}
episodes = state_manager.get_episodes_by_criteria(criteria)
```

## Checkpoint and Recovery

### Creating Checkpoints

```python
# Manual checkpoint
checkpoint_id = state_manager.checkpoint()

# Auto-checkpointing (configured in config)
config = {
    "checkpoint_interval": 60,  # seconds
    "max_checkpoints": 10
}
```

### Restoring State

```python
# List checkpoints
checkpoints = state_manager.list_checkpoints()

# Restore from checkpoint
state_manager.restore("checkpoint-xyz789")
```

## Memory Management

### Memory Limits

```python
config = {
    "memory_limits": {
        "max_state_keys": 10000,
        "max_episodes": 10000,
        "max_memory_mb": 512
    }
}
```

### Cleanup Policies

```python
config = {
    "retention_policy": {
        "max_episodes": 10000,
        "max_age_days": 90,
        "archive_old_episodes": True
    }
}
```

## Integration with Other Components

### Workflow State

```python
# Workflow engine saves workflow state
workflow_id = "wf123"
state_manager.save_state(
    "current_step",
    step_data,
    namespace=f"workflow:{workflow_id}"
)
```

### Agent State

```python
# Agent coordinator saves agent state
agent_id = "agent1"
state_manager.save_state(
    "current_task",
    task_data,
    namespace=f"agent:{agent_id}"
)
```

### Identity State

```python
# Identity manager saves identity data
state_manager.save_state(
    "bonded_identity",
    identity_data,
    namespace="identity"
)
```

## Configuration

```yaml
state:
  backend: "json"  # json, postgresql, mongodb
  data_dir: "./data/state"
  checkpoint_interval: 60  # seconds
  
  retention_policy:
    max_episodes: 10000
    max_age_days: 90
    archive_old_episodes: true
  
  memory_limits:
    max_state_keys: 10000
    max_episodes: 10000
    max_memory_mb: 512
  
  persistence:
    async_writes: true
    batch_size: 100
    flush_interval: 5  # seconds
```

## Monitoring

### State Metrics

- Total keys stored
- Total episodes recorded
- Memory usage
- Checkpoint frequency
- Persistence latency

### State Health Checks

```python
stats = state_manager.get_statistics()
print(f"State health: {stats}")
```

## See Also

- [MODULE_CONTRACTS.md](MODULE_CONTRACTS.md) - StateManager interface
- [WORKFLOW_ENGINE.md](WORKFLOW_ENGINE.md) - Workflow state integration
- [AGENT_MODEL.md](AGENT_MODEL.md) - Agent state integration
