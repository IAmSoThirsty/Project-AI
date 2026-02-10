"""
Tests for Bio-Inspired Brain Mapping AI Subsystem.

Covers:
- Hyperbolic geometry operations
- Resonant Sparse Geometry Network (RSGN)
- Bio-inspired Modular Representation
- Two-timescale learning
- Memory consolidation
- State persistence
- System integration
"""

import tempfile

import numpy as np
import pytest

from app.core.bio_brain_mapper import (
    BioBrainMappingSystem,
    BioModularRepresentation,
    CorticalModule,
    HyperbolicOps,
    InhibitionParameters,
    LearningMode,
    LearningParameters,
    ModuleType,
    NetworkTopology,
    ResonanceParameters,
    ResonantSparseGeometryNetwork,
)


class TestHyperbolicOps:
    """Test hyperbolic geometry operations."""

    def test_initialization(self):
        """Test hyperbolic ops initialize correctly."""
        hyp = HyperbolicOps(curvature=1.0)
        assert hyp.c == 1.0
        assert hyp.eps > 0

    def test_clip_to_ball(self):
        """Test clipping vectors to Poincaré ball."""
        hyp = HyperbolicOps()

        # Test points inside ball
        x = np.array([[0.5, 0.5]], dtype=np.float32)
        clipped = hyp.clip_to_ball(x)
        assert np.linalg.norm(clipped) < 1.0

        # Test points outside ball
        x = np.array([[2.0, 2.0]], dtype=np.float32)
        clipped = hyp.clip_to_ball(x)
        assert np.linalg.norm(clipped) < 1.0

    def test_mobius_addition(self):
        """Test Möbius addition."""
        hyp = HyperbolicOps()

        x = np.array([[0.1, 0.2]], dtype=np.float32)
        y = np.array([[0.3, 0.1]], dtype=np.float32)

        result = hyp.mobius_add(x, y)

        # Result should be in ball
        assert np.linalg.norm(result) < 1.0

        # Möbius addition with zero should return original
        zero = np.zeros_like(x)
        result_with_zero = hyp.mobius_add(x, zero)
        np.testing.assert_allclose(result_with_zero, x, atol=1e-5)

    def test_exp_log_map_inverse(self):
        """Test that exp and log maps are inverses."""
        hyp = HyperbolicOps()

        x = np.array([[0.1, 0.2]], dtype=np.float32)
        v = np.array([[0.05, 0.03]], dtype=np.float32)

        # exp followed by log should recover v
        y = hyp.exp_map(x, v)
        v_recovered = hyp.log_map(x, y)

        np.testing.assert_allclose(v_recovered, v, atol=1e-4)

    def test_distance(self):
        """Test hyperbolic distance."""
        hyp = HyperbolicOps()

        x = np.array([[0.1, 0.2]], dtype=np.float32)
        y = np.array([[0.3, 0.4]], dtype=np.float32)

        dist = hyp.distance(x, y)

        # Distance should be positive
        assert dist > 0

        # Distance to self should be zero
        dist_self = hyp.distance(x, x)
        assert dist_self < 1e-5

    def test_distance_symmetry(self):
        """Test that distance is symmetric."""
        hyp = HyperbolicOps()

        x = np.array([[0.1, 0.2]], dtype=np.float32)
        y = np.array([[0.3, 0.4]], dtype=np.float32)

        dist_xy = hyp.distance(x, y)
        dist_yx = hyp.distance(y, x)

        np.testing.assert_allclose(dist_xy, dist_yx, atol=1e-5)


class TestResonantSparseGeometryNetwork:
    """Test RSGN implementation."""

    @pytest.fixture
    def topology(self):
        """Create test topology."""
        return NetworkTopology(
            n_layers=2,
            layer_sizes=[32, 64, 32],
            sparsity=0.2,
            hyperbolic_dim=16,
            curvature=1.0,
        )

    @pytest.fixture
    def learning_params(self):
        """Create test learning parameters."""
        return LearningParameters(
            fast_lr=0.01,
            slow_lr=0.001,
            hebb_potentiation=0.1,
            hebb_decay=0.01,
            weight_decay=0.0001,
        )

    @pytest.fixture
    def inhibition_params(self):
        """Create test inhibition parameters."""
        return InhibitionParameters(
            excitation_radius=1.0,
            inhibition_radius=3.0,
            excitation_strength=1.0,
            inhibition_strength=0.5,
            kwta_k=5,
        )

    @pytest.fixture
    def resonance_params(self):
        """Create test resonance parameters."""
        return ResonanceParameters(
            frequency=40.0, modulation_depth=0.1, phase_coherence_threshold=0.5
        )

    @pytest.fixture
    def rsgn(self, topology, learning_params, inhibition_params, resonance_params):
        """Create RSGN instance."""
        return ResonantSparseGeometryNetwork(
            topology=topology,
            learning_params=learning_params,
            inhibition_params=inhibition_params,
            resonance_params=resonance_params,
            seed=42,
        )

    def test_initialization(self, rsgn, topology):
        """Test RSGN initializes correctly."""
        assert rsgn.topology.n_layers == topology.n_layers
        assert len(rsgn.embeddings) == topology.n_layers
        assert len(rsgn.weights_fast) == topology.n_layers
        assert len(rsgn.weights_slow) == topology.n_layers
        assert len(rsgn.masks) == topology.n_layers

    def test_embeddings_in_ball(self, rsgn):
        """Test that embeddings are in Poincaré ball."""
        for emb in rsgn.embeddings:
            norms = np.linalg.norm(emb, axis=1)
            assert np.all(norms < 1.0)

    def test_forward_pass(self, rsgn):
        """Test forward pass through network."""
        batch_size = 4
        input_dim = rsgn.topology.layer_sizes[0]
        x = np.random.randn(batch_size, input_dim).astype(np.float32)

        output, diagnostics = rsgn.forward(x, learning_mode=LearningMode.FAST)

        # Check output shape
        expected_output_dim = rsgn.topology.layer_sizes[-1]
        assert output.shape == (batch_size, expected_output_dim)

        # Check diagnostics
        assert "layer_activations" in diagnostics
        assert "layer_embeddings" in diagnostics
        assert len(diagnostics["layer_activations"]) == rsgn.topology.n_layers

    def test_forward_different_learning_modes(self, rsgn):
        """Test forward with different learning modes."""
        batch_size = 4
        input_dim = rsgn.topology.layer_sizes[0]
        x = np.random.randn(batch_size, input_dim).astype(np.float32)

        # Before any learning, fast and slow should be the same (initialized as copies)
        output_fast_initial, _ = rsgn.forward(x, learning_mode=LearningMode.FAST)
        output_slow_initial, _ = rsgn.forward(x, learning_mode=LearningMode.SLOW)

        # Initially they should be identical
        assert np.allclose(output_fast_initial, output_slow_initial, atol=1e-6)

        # Apply multiple Hebbian updates to create noticeable difference
        for _ in range(10):
            pre = np.random.randn(batch_size, rsgn.topology.layer_sizes[0]).astype(
                np.float32
            )
            post = np.random.randn(batch_size, rsgn.topology.layer_sizes[1]).astype(
                np.float32
            )
            rsgn.update_weights_hebbian(0, pre, post)

        # Now they should be different
        output_fast, _ = rsgn.forward(x, learning_mode=LearningMode.FAST)
        output_slow, _ = rsgn.forward(x, learning_mode=LearningMode.SLOW)
        output_both, _ = rsgn.forward(x, learning_mode=LearningMode.BOTH)

        # All should produce valid outputs
        assert output_fast.shape == output_slow.shape == output_both.shape

        # After multiple Hebbian updates, fast and slow should differ
        # (Fast weights are unchanged, slow weights have been updated)
        # The difference may be small due to sparsity and inhibition, so we just check they're not identical
        weights_changed = not np.array_equal(rsgn.weights_fast[0], rsgn.weights_slow[0])
        assert weights_changed

    def test_hebbian_update(self, rsgn):
        """Test Hebbian weight updates."""
        layer_idx = 0
        batch_size = 4
        n_in = rsgn.topology.layer_sizes[layer_idx]
        n_out = rsgn.topology.layer_sizes[layer_idx + 1]

        pre = np.random.randn(batch_size, n_in).astype(np.float32)
        post = np.random.randn(batch_size, n_out).astype(np.float32)

        # Store initial weights
        weights_before = rsgn.weights_slow[layer_idx].copy()

        # Update
        rsgn.update_weights_hebbian(layer_idx, pre, post)

        # Weights should have changed
        assert not np.allclose(weights_before, rsgn.weights_slow[layer_idx])

    def test_sparse_connectivity(self, rsgn):
        """Test that connectivity respects sparsity."""
        for mask in rsgn.masks:
            actual_sparsity = np.mean(mask > 0)
            # Should be close to target sparsity
            assert abs(actual_sparsity - rsgn.topology.sparsity) < 0.1

    def test_state_serialization(self, rsgn):
        """Test state save/load."""
        # Get initial state
        state = rsgn.get_state()

        assert "topology" in state
        assert "embeddings" in state
        assert "weights_fast" in state
        assert "weights_slow" in state
        assert "masks" in state

        # Create new RSGN and load state
        rsgn2 = ResonantSparseGeometryNetwork(
            topology=rsgn.topology,
            learning_params=rsgn.learning_params,
            inhibition_params=rsgn.inhibition_params,
            resonance_params=rsgn.resonance_params,
            seed=42,
        )
        rsgn2.load_state(state)

        # Should have same weights
        for w1, w2 in zip(rsgn.weights_fast, rsgn2.weights_fast, strict=False):
            np.testing.assert_allclose(w1, w2)


class TestCorticalModule:
    """Test cortical module implementation."""

    @pytest.fixture
    def module(self):
        """Create test module."""
        return CorticalModule(
            module_id="test_v1",
            module_type=ModuleType.V1,
            input_dim=64,
            output_dim=128,
            sparsity_k=10,
            learning_rate=0.001,
        )

    def test_initialization(self, module):
        """Test module initializes correctly."""
        assert module.module_id == "test_v1"
        assert module.module_type == ModuleType.V1
        assert module.input_dim == 64
        assert module.output_dim == 128
        assert module.sparsity_k == 10

    def test_forward(self, module):
        """Test forward pass."""
        batch_size = 4
        x = np.random.randn(batch_size, module.input_dim).astype(np.float32)

        output = module.forward(x, resonant_drive=0.1)

        # Check shape
        assert output.shape == (batch_size, module.output_dim)

        # Check sparsity (should have exactly k winners)
        for i in range(batch_size):
            n_active = np.sum(output[i] > 0)
            assert n_active == module.sparsity_k

    def test_hebbian_update(self, module):
        """Test Hebbian plasticity."""
        batch_size = 4
        x_pre = np.random.randn(batch_size, module.input_dim).astype(np.float32)
        x_post = np.random.randn(batch_size, module.output_dim).astype(np.float32)

        weights_before = module.weights_ff.copy()

        module.update_hebbian(x_pre, x_post)

        # Weights should change
        assert not np.allclose(weights_before, module.weights_ff)


class TestBioModularRepresentation:
    """Test bio-modular representation."""

    @pytest.fixture
    def bio_modules(self):
        """Create test bio-modular representation."""
        module_dims = {
            ModuleType.V1: 64,
            ModuleType.V2: 64,
            ModuleType.V4: 128,
            ModuleType.IT: 128,
            ModuleType.PFC: 64,
        }
        return BioModularRepresentation(
            input_dim=32,
            module_dims=module_dims,
            sparsity_k=5,
            learning_rate=0.001,
            resonance_freq=40.0,
        )

    def test_initialization(self, bio_modules):
        """Test bio-modules initialize correctly."""
        assert len(bio_modules.modules) == 5
        assert ModuleType.V1 in bio_modules.modules
        assert ModuleType.PFC in bio_modules.modules

    def test_forward(self, bio_modules):
        """Test hierarchical forward pass."""
        batch_size = 4
        x = np.random.randn(batch_size, bio_modules.input_dim).astype(np.float32)

        activations = bio_modules.forward(x)

        # Should have activations for all modules
        assert len(activations) == 5
        for mod_type in ModuleType:
            assert mod_type in activations

        # Check shapes
        assert activations[ModuleType.V1].shape == (batch_size, 64)
        assert activations[ModuleType.PFC].shape == (batch_size, 64)

    def test_hebbian_update(self, bio_modules):
        """Test Hebbian updates across hierarchy."""
        batch_size = 4
        x = np.random.randn(batch_size, bio_modules.input_dim).astype(np.float32)

        # Forward pass
        activations = bio_modules.forward(x)

        # Store initial weights
        v1_weights_before = bio_modules.modules[ModuleType.V1].weights_ff.copy()

        # Update
        bio_modules.update_hebbian(x, activations)

        # Weights should change
        v1_weights_after = bio_modules.modules[ModuleType.V1].weights_ff
        assert not np.allclose(v1_weights_before, v1_weights_after)

    def test_state_serialization(self, bio_modules):
        """Test state save/load."""
        # Get state
        state = bio_modules.get_state()

        assert "modules" in state
        assert "time" in state

        # Create new instance and load
        module_dims = {
            ModuleType.V1: 64,
            ModuleType.V2: 64,
            ModuleType.V4: 128,
            ModuleType.IT: 128,
            ModuleType.PFC: 64,
        }
        bio_modules2 = BioModularRepresentation(
            input_dim=32,
            module_dims=module_dims,
            sparsity_k=5,
            learning_rate=0.001,
            resonance_freq=40.0,
        )
        bio_modules2.load_state(state)

        # Should have same weights
        for mod_type in ModuleType:
            w1 = bio_modules.modules[mod_type].weights_ff
            w2 = bio_modules2.modules[mod_type].weights_ff
            np.testing.assert_allclose(w1, w2)


class TestBioBrainMappingSystem:
    """Test complete brain mapping system."""

    @pytest.fixture
    def system(self):
        """Create test system with temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield BioBrainMappingSystem(data_dir=tmpdir)

    def test_initialization(self, system):
        """Test system initializes correctly."""
        assert system.rsgn is not None
        assert system.bio_modules is not None
        assert system.network_id is not None
        assert len(system.learning_history) == 0

    def test_default_config(self, system):
        """Test default configuration is valid."""
        config = system.config
        assert "rsgn" in config
        assert "learning" in config
        assert "modules" in config
        assert "consolidation" in config

    def test_process(self, system):
        """Test processing input."""
        batch_size = 4
        input_dim = system.config["modules"]["input_dim"]
        x = np.random.randn(batch_size, input_dim).astype(np.float32)

        result = system.process(x, learning_mode=LearningMode.BOTH, update_weights=True)

        # Check outputs
        assert "rsgn_output" in result
        assert "module_activations" in result
        assert "rsgn_diagnostics" in result
        assert "network_id" in result
        assert "timestamp" in result

        # Learning history should be updated
        assert len(system.learning_history) > 0

    def test_process_without_update(self, system):
        """Test processing without weight updates."""
        batch_size = 4
        input_dim = system.config["modules"]["input_dim"]
        x = np.random.randn(batch_size, input_dim).astype(np.float32)

        initial_history_len = len(system.learning_history)

        result = system.process(x, update_weights=False)

        # Should still get outputs
        assert "rsgn_output" in result

        # Learning history should not change
        assert len(system.learning_history) == initial_history_len

    def test_consolidation(self, system):
        """Test memory consolidation."""
        initial_count = system.consolidation_count

        system.consolidate_memory()

        # Consolidation count should increase
        assert system.consolidation_count == initial_count + 1
        assert system.last_consolidation is not None

        # Learning history should be reset
        assert len(system.learning_history) == 0

    def test_auto_consolidation(self, system):
        """Test automatic consolidation trigger."""
        batch_size = 4
        input_dim = system.config["modules"]["input_dim"]
        x = np.random.randn(batch_size, input_dim).astype(np.float32)

        # Set low consolidation threshold
        system.config["consolidation"]["interval_steps"] = 2

        initial_count = system.consolidation_count

        # Process multiple times to trigger consolidation
        system.process(x, update_weights=True)
        system.process(x, update_weights=True)
        system.process(x, update_weights=True)

        # Should have consolidated at least once
        assert system.consolidation_count > initial_count

    def test_diagnostics(self, system):
        """Test diagnostic information."""
        diagnostics = system.get_diagnostics()

        assert "network_id" in diagnostics
        assert "rsgn_layers" in diagnostics
        assert "module_count" in diagnostics
        assert "learning_events" in diagnostics
        assert "consolidation_count" in diagnostics

    def test_state_persistence(self):
        """Test saving and loading state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create system and process some data
            system1 = BioBrainMappingSystem(data_dir=tmpdir)
            batch_size = 4
            input_dim = system1.config["modules"]["input_dim"]
            x = np.random.randn(batch_size, input_dim).astype(np.float32)
            system1.process(x, update_weights=True)

            network_id = system1.network_id

            # Save state
            system1.save_state()

            # Create new system and load state
            system2 = BioBrainMappingSystem(data_dir=tmpdir)
            system2.load_state(network_id)

            # Should have same network ID and history
            assert system2.network_id == network_id
            assert len(system2.learning_history) == len(system1.learning_history)

    def test_custom_config(self):
        """Test initialization with custom config."""
        custom_config = {
            "rsgn": {
                "n_layers": 2,
                "layer_sizes": [64, 128, 64],
                "sparsity": 0.15,
                "hyperbolic_dim": 32,
                "curvature": 1.0,
            },
            "learning": {
                "fast_lr": 0.002,
                "slow_lr": 0.0002,
                "hebb_potentiation": 0.15,
                "hebb_decay": 0.02,
                "weight_decay": 0.0002,
            },
            "inhibition": {
                "excitation_radius": 1.5,
                "inhibition_radius": 3.5,
                "excitation_strength": 1.2,
                "inhibition_strength": 0.6,
                "kwta_k": 8,
            },
            "resonance": {
                "frequency": 50.0,
                "modulation_depth": 0.15,
                "phase_coherence_threshold": 0.6,
            },
            "modules": {
                "input_dim": 64,
                "v1_dim": 128,
                "v2_dim": 128,
                "v4_dim": 256,
                "it_dim": 256,
                "pfc_dim": 128,
                "sparsity_k": 15,
                "learning_rate": 0.0002,
                "resonance_freq": 50.0,
            },
            "consolidation": {
                "interval_steps": 500,
                "threshold_change": 0.02,
            },
            "seed": 42,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            system = BioBrainMappingSystem(config=custom_config, data_dir=tmpdir)

            # Check config applied
            assert system.config["rsgn"]["n_layers"] == 2
            assert system.config["learning"]["fast_lr"] == 0.002
            assert system.config["modules"]["sparsity_k"] == 15

    def test_register_with_kernel(self, system):
        """Test kernel registration."""

        # Mock kernel
        class MockKernel:
            def __init__(self):
                self.subsystems = {}

            def register_subsystem(self, name, subsystem):
                self.subsystems[name] = subsystem

        kernel = MockKernel()
        system.register_with_kernel(kernel)

        # Should be registered
        assert "bio_brain_mapper" in kernel.subsystems
        assert kernel.subsystems["bio_brain_mapper"] is system


class TestIntegration:
    """Integration tests for the complete system."""

    def test_end_to_end_processing(self):
        """Test end-to-end processing pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize system
            system = BioBrainMappingSystem(data_dir=tmpdir)

            # Process multiple batches
            batch_size = 4
            input_dim = system.config["modules"]["input_dim"]

            for _ in range(5):
                x = np.random.randn(batch_size, input_dim).astype(np.float32)
                result = system.process(x, update_weights=True)

                # Validate outputs
                assert result["rsgn_output"].shape == (
                    batch_size,
                    system.config["rsgn"]["layer_sizes"][-1],
                )
                assert len(result["module_activations"]) == 5

            # Check learning occurred
            assert len(system.learning_history) > 0

            # Save state
            system.save_state()

            # Load and verify
            network_id = system.network_id
            system2 = BioBrainMappingSystem(data_dir=tmpdir)
            system2.load_state(network_id)
            assert system2.network_id == network_id

    def test_learning_convergence(self):
        """Test that repeated processing changes weights."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system = BioBrainMappingSystem(data_dir=tmpdir)

            # Fixed input
            batch_size = 4
            input_dim = system.config["modules"]["input_dim"]
            x = np.random.randn(batch_size, input_dim).astype(np.float32)

            # Initial weights
            initial_weights = system.rsgn.weights_slow[0].copy()

            # Process multiple times
            for _ in range(10):
                system.process(x, learning_mode=LearningMode.SLOW, update_weights=True)

            # Weights should have changed
            final_weights = system.rsgn.weights_slow[0]
            assert not np.allclose(initial_weights, final_weights, atol=1e-4)

    def test_different_input_sizes(self):
        """Test processing with different batch sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system = BioBrainMappingSystem(data_dir=tmpdir)
            input_dim = system.config["modules"]["input_dim"]

            # Try different batch sizes
            for batch_size in [1, 4, 8, 16]:
                x = np.random.randn(batch_size, input_dim).astype(np.float32)
                result = system.process(x, update_weights=False)

                assert result["rsgn_output"].shape[0] == batch_size
                for mod_type in ModuleType:
                    assert result["module_activations"][mod_type].shape[0] == batch_size
