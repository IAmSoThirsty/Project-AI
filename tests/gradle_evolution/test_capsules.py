"""
Tests for Capsule Engine and Replay Engine.

Tests deterministic build capsules, Merkle tree verification,
and forensic replay capabilities.
"""

import hashlib
import pytest
from pathlib import Path

from gradle_evolution.capsules.capsule_engine import (
    BuildCapsule,
    CapsuleEngine,
)
from gradle_evolution.capsules.replay_engine import ReplayEngine, ReplayResult


class TestBuildCapsule:
    """Test BuildCapsule component."""
    
    def test_capsule_creation(self, sample_build_capsule_data):
        """Test creating a build capsule."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        
        assert capsule.capsule_id == "test-capsule-001"
        assert len(capsule.tasks) == 3
        assert len(capsule.inputs) == 2
        assert len(capsule.outputs) == 2
        assert capsule.merkle_root is not None
    
    def test_merkle_root_computation(self, sample_build_capsule_data):
        """Test Merkle root is computed deterministically."""
        capsule1 = BuildCapsule(**sample_build_capsule_data)
        capsule2 = BuildCapsule(**sample_build_capsule_data)
        
        # Same inputs should produce same Merkle root
        assert capsule1.merkle_root == capsule2.merkle_root
    
    def test_merkle_root_changes_with_inputs(self, sample_build_capsule_data):
        """Test Merkle root changes when inputs change."""
        capsule1 = BuildCapsule(**sample_build_capsule_data)
        
        # Modify input
        modified_data = sample_build_capsule_data.copy()
        modified_data["inputs"]["src/main/java/Main.java"] = "differenthash"
        capsule2 = BuildCapsule(**modified_data)
        
        assert capsule1.merkle_root != capsule2.merkle_root
    
    def test_capsule_to_dict(self, sample_build_capsule_data):
        """Test converting capsule to dictionary."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        capsule_dict = capsule.to_dict()
        
        assert capsule_dict["capsule_id"] == "test-capsule-001"
        assert "merkle_root" in capsule_dict
        assert "timestamp" in capsule_dict
    
    def test_verify_integrity_valid(self, sample_build_capsule_data):
        """Test integrity verification for valid capsule."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        
        assert capsule.verify_integrity()
    
    def test_verify_integrity_invalid(self, sample_build_capsule_data):
        """Test integrity verification detects tampering."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        
        # Tamper with capsule (modify after creation)
        capsule.tasks.append("malicious_task")
        
        # Recompute to see change
        new_root = capsule._compute_merkle_root()
        assert new_root != capsule.merkle_root
    
    def test_capsule_immutability_hash(self, sample_build_capsule_data):
        """Test capsule hash represents immutability."""
        capsule = BuildCapsule(**sample_build_capsule_data)
        original_hash = capsule.merkle_root
        
        # Create identical capsule
        capsule2 = BuildCapsule(**sample_build_capsule_data)
        
        assert capsule2.merkle_root == original_hash


class TestCapsuleEngine:
    """Test CapsuleEngine component."""
    
    def test_initialization(self, capsule_storage):
        """Test engine initializes with storage."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        assert engine.storage_path == capsule_storage
        assert engine.capsules == {}
    
    def test_create_capsule(self, capsule_storage):
        """Test creating a new capsule."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        tasks = ["clean", "compile", "test"]
        inputs = {"src/Main.java": "abc123"}
        outputs = {"build/Main.class": "def456"}
        metadata = {"timestamp": "2024-01-01T00:00:00Z"}
        
        capsule = engine.create_capsule(tasks, inputs, outputs, metadata)
        
        assert capsule is not None
        assert capsule.capsule_id in engine.capsules
        assert len(capsule.tasks) == 3
    
    def test_get_capsule(self, capsule_storage, sample_build_capsule_data):
        """Test retrieving capsule by ID."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        capsule = BuildCapsule(**sample_build_capsule_data)
        engine.capsules[capsule.capsule_id] = capsule
        
        retrieved = engine.get_capsule(capsule.capsule_id)
        
        assert retrieved is not None
        assert retrieved.capsule_id == capsule.capsule_id
    
    def test_get_nonexistent_capsule(self, capsule_storage):
        """Test getting nonexistent capsule returns None."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        retrieved = engine.get_capsule("nonexistent-id")
        
        assert retrieved is None
    
    def test_verify_capsule(self, capsule_storage, sample_build_capsule_data):
        """Test verifying capsule integrity."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        capsule = BuildCapsule(**sample_build_capsule_data)
        engine.capsules[capsule.capsule_id] = capsule
        
        is_valid = engine.verify_capsule(capsule.capsule_id)
        
        assert is_valid
    
    def test_list_capsules(self, capsule_storage, sample_build_capsule_data):
        """Test listing all capsules."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        # Create multiple capsules
        for i in range(3):
            data = sample_build_capsule_data.copy()
            data["capsule_id"] = f"capsule-{i}"
            capsule = BuildCapsule(**data)
            engine.capsules[capsule.capsule_id] = capsule
        
        capsules = engine.list_capsules()
        
        assert len(capsules) == 3
    
    def test_persistence(self, capsule_storage, sample_build_capsule_data):
        """Test capsule persistence to disk."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        capsule = BuildCapsule(**sample_build_capsule_data)
        engine.capsules[capsule.capsule_id] = capsule
        engine.save()
        
        # Load in new engine
        new_engine = CapsuleEngine(storage_path=capsule_storage)
        new_engine.load()
        
        assert capsule.capsule_id in new_engine.capsules
    
    def test_hash_file(self, capsule_storage, temp_dir):
        """Test file hashing utility."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        file_hash = engine.hash_file(test_file)
        
        assert file_hash is not None
        assert len(file_hash) == 64  # SHA-256 hex length
    
    def test_compute_inputs_hash(self, capsule_storage, temp_dir):
        """Test computing input file hashes."""
        engine = CapsuleEngine(storage_path=capsule_storage)
        
        # Create test files
        file1 = temp_dir / "input1.txt"
        file1.write_text("content1")
        file2 = temp_dir / "input2.txt"
        file2.write_text("content2")
        
        input_files = [file1, file2]
        hashes = engine.compute_inputs_hash(input_files)
        
        assert len(hashes) == 2
        assert str(file1) in hashes or file1.name in str(hashes)


class TestReplayEngine:
    """Test ReplayEngine component."""
    
    def test_initialization(self, capsule_storage):
        """Test replay engine initializes."""
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        
        assert replay_engine.capsule_engine == capsule_engine
        assert replay_engine.replay_history == []
    
    def test_replay_capsule(self, capsule_storage, sample_build_capsule_data):
        """Test replaying a build capsule."""
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        
        # Create and store capsule
        capsule = BuildCapsule(**sample_build_capsule_data)
        capsule_engine.capsules[capsule.capsule_id] = capsule
        
        # Replay
        result = replay_engine.replay_build(capsule.capsule_id)
        
        assert isinstance(result, ReplayResult)
        assert result.capsule_id == capsule.capsule_id
    
    def test_replay_nonexistent_capsule(self, capsule_storage):
        """Test replaying nonexistent capsule raises error."""
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        
        with pytest.raises(ValueError, match="Capsule not found"):
            replay_engine.replay_build("nonexistent-id")
    
    def test_verify_replay_consistency(self, capsule_storage, sample_build_capsule_data):
        """Test verifying replay produces consistent results."""
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        
        capsule = BuildCapsule(**sample_build_capsule_data)
        capsule_engine.capsules[capsule.capsule_id] = capsule
        
        # Replay multiple times
        result1 = replay_engine.replay_build(capsule.capsule_id)
        result2 = replay_engine.replay_build(capsule.capsule_id)
        
        # Should produce consistent output hashes
        assert result1.output_hash == result2.output_hash
    
    def test_get_replay_history(self, capsule_storage, sample_build_capsule_data):
        """Test retrieving replay history."""
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        
        capsule = BuildCapsule(**sample_build_capsule_data)
        capsule_engine.capsules[capsule.capsule_id] = capsule
        
        # Perform replays
        replay_engine.replay_build(capsule.capsule_id)
        replay_engine.replay_build(capsule.capsule_id)
        
        history = replay_engine.get_replay_history()
        
        assert len(history) == 2
    
    def test_forensic_analysis(self, capsule_storage, sample_build_capsule_data):
        """Test forensic analysis of capsule."""
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        
        capsule = BuildCapsule(**sample_build_capsule_data)
        capsule_engine.capsules[capsule.capsule_id] = capsule
        
        analysis = replay_engine.forensic_analysis(capsule.capsule_id)
        
        assert "capsule_id" in analysis
        assert "input_analysis" in analysis
        assert "output_analysis" in analysis
    
    def test_compare_capsules(self, capsule_storage, sample_build_capsule_data):
        """Test comparing two capsules."""
        capsule_engine = CapsuleEngine(storage_path=capsule_storage)
        replay_engine = ReplayEngine(capsule_engine)
        
        # Create two similar capsules
        capsule1 = BuildCapsule(**sample_build_capsule_data)
        
        data2 = sample_build_capsule_data.copy()
        data2["capsule_id"] = "test-capsule-002"
        capsule2 = BuildCapsule(**data2)
        
        capsule_engine.capsules[capsule1.capsule_id] = capsule1
        capsule_engine.capsules[capsule2.capsule_id] = capsule2
        
        comparison = replay_engine.compare_capsules(
            capsule1.capsule_id,
            capsule2.capsule_id
        )
        
        assert "differences" in comparison
        assert "similarities" in comparison
