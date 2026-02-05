"""
E2E Tests for Multi-Agent Interactions

Comprehensive tests for multi-agent systems including:
- Agent-to-agent communication protocols
- Multi-agent coordination and orchestration
- Agent collaboration workflows
- Conflict resolution between agents
- Agent state synchronization
- Performance and scalability testing
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import pytest

from e2e.utils.test_helpers import (
    get_timestamp_iso,
    load_json_file,
    save_json_file,
)


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    FAILED = "failed"


@dataclass
class Message:
    """Agent communication message."""
    sender: str
    receiver: str
    content: Any
    message_type: str
    timestamp: str = field(default_factory=get_timestamp_iso)
    message_id: str = field(default_factory=lambda: f"msg_{int(time.time() * 1000)}")


class Agent:
    """Simple agent for testing multi-agent interactions."""

    def __init__(self, agent_id: str, agent_type: str = "generic"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.inbox = queue.Queue()
        self.outbox = []
        self.state = {}
        self.running = False

    def send_message(self, receiver: str, content: Any, message_type: str = "data"):
        """Send a message to another agent."""
        msg = Message(
            sender=self.agent_id,
            receiver=receiver,
            content=content,
            message_type=message_type,
        )
        self.outbox.append(msg)
        return msg

    def receive_message(self, timeout: float = 1.0) -> Message | None:
        """Receive a message from inbox."""
        try:
            return self.inbox.get(timeout=timeout)
        except queue.Empty:
            return None

    def process_message(self, message: Message) -> dict:
        """Process a received message."""
        self.status = AgentStatus.BUSY
        result = {
            "agent": self.agent_id,
            "processed": True,
            "message_id": message.message_id,
            "timestamp": get_timestamp_iso(),
        }
        self.status = AgentStatus.IDLE
        return result

    def update_state(self, key: str, value: Any):
        """Update agent state."""
        self.state[key] = value

    def get_state(self) -> dict:
        """Get current agent state."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "state": self.state.copy(),
            "inbox_size": self.inbox.qsize(),
            "outbox_size": len(self.outbox),
        }


class MessageBroker:
    """Message broker for agent communication."""

    def __init__(self):
        self.agents = {}
        self.message_log = []

    def register_agent(self, agent: Agent):
        """Register an agent with the broker."""
        self.agents[agent.agent_id] = agent

    def deliver_message(self, message: Message):
        """Deliver a message to the target agent."""
        if message.receiver in self.agents:
            self.agents[message.receiver].inbox.put(message)
            self.message_log.append(message)
            return True
        return False

    def broadcast(self, sender: str, content: Any, message_type: str = "broadcast"):
        """Broadcast a message to all agents except sender."""
        for agent_id, agent in self.agents.items():
            if agent_id != sender:
                msg = Message(
                    sender=sender,
                    receiver=agent_id,
                    content=content,
                    message_type=message_type,
                )
                agent.inbox.put(msg)
                self.message_log.append(msg)

    def get_message_history(self) -> list[dict]:
        """Get message history."""
        return [
            {
                "sender": msg.sender,
                "receiver": msg.receiver,
                "type": msg.message_type,
                "timestamp": msg.timestamp,
            }
            for msg in self.message_log
        ]


@pytest.mark.e2e
@pytest.mark.agents
class TestAgentCommunication:
    """E2E tests for agent-to-agent communication."""

    def test_direct_agent_messaging(self):
        """Test direct message passing between two agents."""
        # Arrange
        agent_a = Agent("agent_a", "worker")
        agent_b = Agent("agent_b", "worker")
        broker = MessageBroker()
        broker.register_agent(agent_a)
        broker.register_agent(agent_b)

        # Act
        msg = agent_a.send_message("agent_b", {"task": "process_data"}, "request")
        broker.deliver_message(msg)

        received_msg = agent_b.receive_message(timeout=1.0)

        # Assert
        assert received_msg is not None
        assert received_msg.sender == "agent_a"
        assert received_msg.receiver == "agent_b"
        assert received_msg.content["task"] == "process_data"

    def test_broadcast_messaging(self):
        """Test broadcasting messages to multiple agents."""
        # Arrange
        broker = MessageBroker()
        agents = [Agent(f"agent_{i}", "worker") for i in range(5)]

        for agent in agents:
            broker.register_agent(agent)

        # Act
        broker.broadcast("agent_0", {"announcement": "system_update"}, "broadcast")

        # Assert - All agents except sender should receive message
        for i, agent in enumerate(agents):
            if i == 0:
                # Sender should not receive broadcast
                msg = agent.receive_message(timeout=0.1)
                assert msg is None
            else:
                msg = agent.receive_message(timeout=1.0)
                assert msg is not None
                assert msg.sender == "agent_0"
                assert msg.content["announcement"] == "system_update"

    def test_message_routing(self):
        """Test message routing through broker."""
        # Arrange
        broker = MessageBroker()
        agents = [Agent(f"agent_{i}") for i in range(3)]

        for agent in agents:
            broker.register_agent(agent)

        # Act - Send messages in a chain
        msg1 = agents[0].send_message("agent_1", {"data": "step1"})
        msg2 = agents[1].send_message("agent_2", {"data": "step2"})

        broker.deliver_message(msg1)
        broker.deliver_message(msg2)

        # Assert
        msg_received_1 = agents[1].receive_message(timeout=1.0)
        msg_received_2 = agents[2].receive_message(timeout=1.0)

        assert msg_received_1.content["data"] == "step1"
        assert msg_received_2.content["data"] == "step2"

    def test_message_ordering(self):
        """Test that messages maintain order."""
        # Arrange
        broker = MessageBroker()
        sender = Agent("sender")
        receiver = Agent("receiver")

        broker.register_agent(sender)
        broker.register_agent(receiver)

        # Act - Send multiple messages
        messages = []
        for i in range(10):
            msg = sender.send_message("receiver", {"sequence": i})
            broker.deliver_message(msg)
            messages.append(msg)

        # Assert - Receive in order
        for i in range(10):
            received = receiver.receive_message(timeout=1.0)
            assert received is not None
            assert received.content["sequence"] == i

    def test_message_history_logging(self):
        """Test message history is properly logged."""
        # Arrange
        broker = MessageBroker()
        agents = [Agent(f"agent_{i}") for i in range(3)]

        for agent in agents:
            broker.register_agent(agent)

        # Act
        for i in range(5):
            msg = agents[i % 3].send_message(
                f"agent_{(i + 1) % 3}",
                {"iteration": i}
            )
            broker.deliver_message(msg)

        # Assert
        history = broker.get_message_history()
        assert len(history) == 5
        assert all("sender" in entry for entry in history)
        assert all("receiver" in entry for entry in history)


@pytest.mark.e2e
@pytest.mark.agents
class TestAgentCoordination:
    """E2E tests for multi-agent coordination."""

    def test_task_distribution(self):
        """Test distributing tasks among multiple agents."""
        # Arrange
        broker = MessageBroker()
        coordinator = Agent("coordinator", "coordinator")
        workers = [Agent(f"worker_{i}", "worker") for i in range(5)]

        broker.register_agent(coordinator)
        for worker in workers:
            broker.register_agent(worker)

        tasks = [{"task_id": i, "data": f"task_{i}"} for i in range(10)]

        # Act - Distribute tasks
        for i, task in enumerate(tasks):
            worker_id = f"worker_{i % len(workers)}"
            msg = coordinator.send_message(worker_id, task, "task")
            broker.deliver_message(msg)

        # Assert - Each worker got tasks
        for worker in workers:
            received_tasks = []
            while True:
                msg = worker.receive_message(timeout=0.1)
                if msg is None:
                    break
                received_tasks.append(msg.content)

            assert len(received_tasks) == 2  # 10 tasks / 5 workers

    def test_leader_election(self):
        """Test leader election among agents."""
        # Arrange
        agents = [Agent(f"agent_{i}") for i in range(5)]

        # Simulate voting
        votes = {}
        for agent in agents:
            # Each agent votes for agent with highest ID
            vote = max(a.agent_id for a in agents)
            votes[agent.agent_id] = vote

        # Act - Count votes
        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        leader = max(vote_counts.items(), key=lambda x: x[1])[0]

        # Assert
        assert leader == "agent_4"  # Highest ID
        assert vote_counts[leader] == 5  # Unanimous

    def test_consensus_protocol(self):
        """Test reaching consensus among agents."""
        # Arrange
        agents = [Agent(f"agent_{i}") for i in range(5)]

        # Each agent proposes a value
        proposals = {
            "agent_0": 10,
            "agent_1": 10,
            "agent_2": 10,
            "agent_3": 15,
            "agent_4": 10,
        }

        # Act - Simple majority consensus
        value_counts = {}
        for value in proposals.values():
            value_counts[value] = value_counts.get(value, 0) + 1

        consensus_value = max(value_counts.items(), key=lambda x: x[1])[0]
        has_consensus = value_counts[consensus_value] > len(agents) / 2

        # Assert
        assert has_consensus
        assert consensus_value == 10
        assert value_counts[consensus_value] == 4

    def test_work_stealing(self):
        """Test work stealing between agents."""
        # Arrange
        agents = [Agent(f"agent_{i}") for i in range(3)]

        # Give uneven workload
        work_queues = {
            "agent_0": [1, 2, 3, 4, 5],
            "agent_1": [],
            "agent_2": [6],
        }

        # Act - Implement work stealing
        while any(len(wq) > 1 for wq in work_queues.values()):
            for agent_id, queue in work_queues.items():
                if len(queue) > 1:
                    # Find idle agent
                    for other_id, other_queue in work_queues.items():
                        if other_id != agent_id and len(other_queue) == 0:
                            # Steal work
                            stolen_work = queue.pop()
                            other_queue.append(stolen_work)
                            break

        # Assert - Work should be distributed
        queue_sizes = [len(q) for q in work_queues.values()]
        assert max(queue_sizes) - min(queue_sizes) <= 1  # Balanced

    def test_barrier_synchronization(self):
        """Test barrier synchronization for agents."""
        # Arrange
        num_agents = 5
        agents = [Agent(f"agent_{i}") for i in range(num_agents)]
        barrier_count = [0]
        lock = threading.Lock()

        def agent_work(agent_id: int):
            # Simulate work
            time.sleep(0.1 * agent_id)

            # Reach barrier
            with lock:
                barrier_count[0] += 1

            # Wait for all agents
            while barrier_count[0] < num_agents:
                time.sleep(0.01)

        # Act
        threads = []
        start_time = time.time()

        for i in range(num_agents):
            thread = threading.Thread(target=agent_work, args=(i,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join(timeout=2.0)

        duration = time.time() - start_time

        # Assert
        assert barrier_count[0] == num_agents
        # Should take at least as long as slowest agent
        assert duration >= 0.4  # Slowest is 0.1 * 4


@pytest.mark.e2e
@pytest.mark.agents
class TestAgentCollaboration:
    """E2E tests for agent collaboration workflows."""

    def test_pipeline_processing(self):
        """Test pipeline processing with multiple agents."""
        # Arrange
        broker = MessageBroker()
        agents = [
            Agent("input_agent", "input"),
            Agent("process_agent", "processor"),
            Agent("output_agent", "output"),
        ]

        for agent in agents:
            broker.register_agent(agent)

        # Act - Process through pipeline
        data = {"value": 10}

        # Stage 1: Input
        msg1 = agents[0].send_message("process_agent", data)
        broker.deliver_message(msg1)

        msg = agents[1].receive_message(timeout=1.0)
        processed_data = msg.content.copy()
        processed_data["value"] *= 2  # Process

        # Stage 2: Process
        msg2 = agents[1].send_message("output_agent", processed_data)
        broker.deliver_message(msg2)

        msg = agents[2].receive_message(timeout=1.0)
        final_data = msg.content

        # Assert
        assert final_data["value"] == 20

    def test_map_reduce_workflow(self):
        """Test map-reduce workflow with agents."""
        # Arrange
        mappers = [Agent(f"mapper_{i}") for i in range(3)]
        reducer = Agent("reducer")

        data = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        # Act - Map phase
        map_results = []
        chunk_size = len(data) // len(mappers)

        for i, mapper in enumerate(mappers):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < len(mappers) - 1 else len(data)
            chunk = data[start_idx:end_idx]

            # Map: square each number
            mapped = [x ** 2 for x in chunk]
            map_results.extend(mapped)

        # Reduce phase
        total = sum(map_results)

        # Assert
        assert total == sum(x ** 2 for x in data)
        assert len(map_results) == len(data)

    def test_collaborative_decision_making(self):
        """Test collaborative decision making among agents."""
        # Arrange
        agents = [Agent(f"expert_{i}") for i in range(4)]

        # Each agent provides a recommendation
        recommendations = {
            "expert_0": {"action": "buy", "confidence": 0.8},
            "expert_1": {"action": "buy", "confidence": 0.7},
            "expert_2": {"action": "sell", "confidence": 0.6},
            "expert_3": {"action": "buy", "confidence": 0.9},
        }

        # Act - Aggregate recommendations
        action_scores = {}
        for rec in recommendations.values():
            action = rec["action"]
            confidence = rec["confidence"]

            if action not in action_scores:
                action_scores[action] = []
            action_scores[action].append(confidence)

        # Calculate weighted decision
        final_decision = max(
            action_scores.items(),
            key=lambda x: sum(x[1]) / len(x[1])
        )

        # Assert
        assert final_decision[0] == "buy"
        assert len(final_decision[1]) == 3  # 3 votes for buy

    def test_peer_review_workflow(self):
        """Test peer review workflow among agents."""
        # Arrange
        author = Agent("author")
        reviewers = [Agent(f"reviewer_{i}") for i in range(3)]

        work = {
            "id": "work_001",
            "content": "Agent implementation",
            "quality_score": 0,
        }

        # Act - Each reviewer scores the work
        reviews = []
        for reviewer in reviewers:
            review = {
                "reviewer_id": reviewer.agent_id,
                "score": 8,  # Out of 10
                "comments": "Good work",
            }
            reviews.append(review)

        # Calculate final score
        avg_score = sum(r["score"] for r in reviews) / len(reviews)
        work["quality_score"] = avg_score
        work["approved"] = avg_score >= 7

        # Assert
        assert work["approved"]
        assert work["quality_score"] == 8
        assert len(reviews) == 3

    def test_resource_sharing(self):
        """Test resource sharing between agents."""
        # Arrange
        agents = [Agent(f"agent_{i}") for i in range(3)]

        shared_resources = {
            "cpu": 100,
            "memory": 1000,
            "storage": 5000,
        }

        # Act - Agents request resources
        requests = [
            {"agent": "agent_0", "cpu": 30, "memory": 300, "storage": 1000},
            {"agent": "agent_1", "cpu": 40, "memory": 400, "storage": 2000},
            {"agent": "agent_2", "cpu": 20, "memory": 200, "storage": 1500},
        ]

        allocations = []
        for req in requests:
            can_allocate = all(
                req[res] <= shared_resources[res]
                for res in ["cpu", "memory", "storage"]
            )

            if can_allocate:
                for res in ["cpu", "memory", "storage"]:
                    shared_resources[res] -= req[res]
                allocations.append(req["agent"])

        # Assert
        assert len(allocations) == 3
        assert shared_resources["cpu"] == 10
        assert shared_resources["memory"] == 100


@pytest.mark.e2e
@pytest.mark.agents
class TestAgentConflictResolution:
    """E2E tests for agent conflict resolution."""

    def test_resource_conflict_resolution(self):
        """Test resolving resource conflicts between agents."""
        # Arrange
        agents = [Agent(f"agent_{i}") for i in range(3)]
        available_resource = 100

        # Competing requests
        requests = [
            {"agent": "agent_0", "amount": 60, "priority": 2},
            {"agent": "agent_1", "amount": 50, "priority": 1},
            {"agent": "agent_2", "amount": 40, "priority": 3},
        ]

        # Act - Resolve by priority
        requests.sort(key=lambda x: x["priority"], reverse=True)

        allocations = []
        remaining = available_resource

        for req in requests:
            if req["amount"] <= remaining:
                allocations.append(req)
                remaining -= req["amount"]

        # Assert
        assert len(allocations) == 2  # Only 2 can be satisfied
        assert allocations[0]["agent"] == "agent_2"  # Highest priority
        assert remaining == 0

    def test_priority_based_scheduling(self):
        """Test priority-based task scheduling."""
        # Arrange
        tasks = [
            {"id": "task_1", "priority": 5, "duration": 10},
            {"id": "task_2", "priority": 10, "duration": 5},
            {"id": "task_3", "priority": 3, "duration": 8},
            {"id": "task_4", "priority": 7, "duration": 6},
        ]

        # Act - Schedule by priority
        scheduled = sorted(tasks, key=lambda x: x["priority"], reverse=True)

        # Assert
        assert scheduled[0]["id"] == "task_2"  # Highest priority
        assert scheduled[-1]["id"] == "task_3"  # Lowest priority

    def test_deadlock_detection(self):
        """Test detecting deadlock between agents."""
        # Arrange
        # Agent A waits for resource from B
        # Agent B waits for resource from A
        waiting_for = {
            "agent_a": "agent_b",
            "agent_b": "agent_a",
        }

        # Act - Detect cycle in wait-for graph
        def has_cycle(graph, start):
            visited = set()
            current = start

            while current not in visited:
                visited.add(current)
                if current not in graph:
                    return False
                current = graph[current]
                if current == start:
                    return True

            return False

        deadlock = has_cycle(waiting_for, "agent_a")

        # Assert
        assert deadlock

    def test_conflict_arbitration(self):
        """Test arbitration of conflicts by coordinator."""
        # Arrange
        coordinator = Agent("coordinator", "coordinator")
        agents = [Agent(f"agent_{i}") for i in range(2)]

        conflicts = [
            {
                "agent_0": {"action": "write", "target": "resource_x"},
                "agent_1": {"action": "write", "target": "resource_x"},
            }
        ]

        # Act - Coordinator resolves conflict
        for conflict in conflicts:
            # Simple resolution: first come, first served
            resolved = list(conflict.keys())[0]
            winner = resolved

        # Assert
        assert winner in ["agent_0", "agent_1"]

    def test_negotiation_protocol(self):
        """Test negotiation protocol between agents."""
        # Arrange
        buyer = Agent("buyer")
        seller = Agent("seller")

        # Initial positions
        buyer_offer = 80
        seller_ask = 120

        max_rounds = 10
        agreement_threshold = 5

        # Act - Negotiate
        for round_num in range(max_rounds):
            # Buyer increases offer
            buyer_offer += 4
            # Seller decreases ask
            seller_ask -= 4

            if abs(buyer_offer - seller_ask) <= agreement_threshold:
                agreed_price = (buyer_offer + seller_ask) / 2
                break
        else:
            agreed_price = None

        # Assert
        assert agreed_price is not None
        assert 95 <= agreed_price <= 105


@pytest.mark.e2e
@pytest.mark.agents
@pytest.mark.slow
class TestAgentStateSynchronization:
    """E2E tests for agent state synchronization."""

    def test_state_replication(self, test_temp_dir):
        """Test replicating state across agents."""
        # Arrange
        state_dir = Path(test_temp_dir) / "state"
        state_dir.mkdir(parents=True, exist_ok=True)

        primary = Agent("primary")
        replicas = [Agent(f"replica_{i}") for i in range(3)]

        # Primary state
        primary_state = {
            "counter": 42,
            "data": {"key": "value"},
            "timestamp": get_timestamp_iso(),
        }
        primary.state = primary_state.copy()

        # Act - Replicate to all replicas
        for replica in replicas:
            replica.state = primary_state.copy()
            save_json_file(
                replica.get_state(),
                state_dir / f"{replica.agent_id}.json"
            )

        # Assert - All replicas have same state
        for replica in replicas:
            assert replica.state["counter"] == primary_state["counter"]
            assert replica.state["data"] == primary_state["data"]

    def test_eventual_consistency(self, test_temp_dir):
        """Test eventual consistency among distributed agents."""
        # Arrange
        agents = [Agent(f"agent_{i}") for i in range(5)]

        # Initial divergent states
        for i, agent in enumerate(agents):
            agent.update_state("value", i * 10)

        # Act - Gossip protocol for convergence
        rounds = 10
        for _ in range(rounds):
            for agent in agents:
                # Pick random peer
                import random
                peer = random.choice(agents)
                if peer != agent:
                    # Take average of values
                    avg = (agent.state["value"] + peer.state["value"]) / 2
                    agent.update_state("value", avg)
                    peer.update_state("value", avg)

        # Assert - Values should converge
        values = [agent.state["value"] for agent in agents]
        variance = max(values) - min(values)
        assert variance < 5  # Should be close

    def test_snapshot_consistency(self, test_temp_dir):
        """Test taking consistent snapshots of agent states."""
        # Arrange
        state_dir = Path(test_temp_dir) / "snapshots"
        state_dir.mkdir(parents=True, exist_ok=True)

        agents = [Agent(f"agent_{i}") for i in range(3)]

        for i, agent in enumerate(agents):
            agent.update_state("counter", i * 100)

        # Act - Take snapshot
        snapshot_time = get_timestamp_iso()
        snapshot = {
            "timestamp": snapshot_time,
            "agents": {},
        }

        for agent in agents:
            snapshot["agents"][agent.agent_id] = agent.get_state()

        save_json_file(snapshot, state_dir / "snapshot.json")

        # Assert
        loaded_snapshot = load_json_file(state_dir / "snapshot.json")
        assert len(loaded_snapshot["agents"]) == 3
        assert "timestamp" in loaded_snapshot

    def test_state_recovery_from_checkpoint(self, test_temp_dir):
        """Test recovering agent state from checkpoint."""
        # Arrange
        checkpoint_dir = Path(test_temp_dir) / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        agent = Agent("agent_1")
        agent.update_state("processed_items", 1000)
        agent.update_state("last_checkpoint", get_timestamp_iso())

        # Save checkpoint
        checkpoint_file = checkpoint_dir / "agent_1_checkpoint.json"
        save_json_file(agent.get_state(), checkpoint_file)

        # Simulate failure and recovery
        agent = None  # Agent crashes

        # Act - Recover from checkpoint
        recovered_agent = Agent("agent_1")
        checkpoint_data = load_json_file(checkpoint_file)
        recovered_agent.state = checkpoint_data["state"]

        # Assert
        assert recovered_agent.state["processed_items"] == 1000
        assert "last_checkpoint" in recovered_agent.state

    def test_distributed_transaction(self):
        """Test distributed transaction across multiple agents."""
        # Arrange
        agents = [Agent(f"agent_{i}") for i in range(3)]

        for agent in agents:
            agent.update_state("balance", 100)

        # Act - Coordinated transaction (transfer 30 from each to agent_0)
        transaction = {
            "id": "tx_001",
            "operations": [
                {"agent": "agent_1", "amount": -30},
                {"agent": "agent_2", "amount": -30},
                {"agent": "agent_0", "amount": 60},
            ],
        }

        # Execute all or nothing
        success = True
        for op in transaction["operations"]:
            agent_id = op["agent"]
            agent_idx = int(agent_id.split("_")[1])
            new_balance = agents[agent_idx].state["balance"] + op["amount"]

            if new_balance < 0:
                success = False
                break

        if success:
            for op in transaction["operations"]:
                agent_id = op["agent"]
                agent_idx = int(agent_id.split("_")[1])
                agents[agent_idx].state["balance"] += op["amount"]

        # Assert
        assert success
        assert agents[0].state["balance"] == 160
        assert agents[1].state["balance"] == 70
        assert agents[2].state["balance"] == 70
