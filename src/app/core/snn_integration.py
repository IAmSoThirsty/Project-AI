"""
Spiking Neural Network (SNN) Integration for Project-AI

Provides comprehensive support for neuromorphic computing with multiple libraries:
- BindsNet: Reinforcement Learning on SNNs with continual learning
- Sinabs: Vision-optimized SNN library with hardware compatibility (SynSense)
- snnTorch: PyTorch-based SNN with excellent tutorials
- SpikingJelly: Deep learning framework for SNNs
- Norse: Deep learning with SNNs in PyTorch
- Brian2: Simulator for spiking neural networks
- Lava: Intel's Neuromorphic Computing framework
- Rockpool: SNN training and deployment library

Key Features:
- Continual learning without full retraining
- Weight transfer from standard CNNs to SNNs
- Hardware-ready deployment for neuromorphic chips (Intel Loihi, SynSense)
- Energy-efficient inference for edge AI
- Multiple backends for different use cases
"""

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Check for optional SNN dependencies
try:
    import torch  # noqa: F401
    import torch.nn as nn

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available - SNN features disabled")

try:
    import bindsnet  # noqa: F401
    from bindsnet.encoding import PoissonEncoder
    from bindsnet.learning import PostPre, WeightDependentPostPre  # noqa: F401
    from bindsnet.network import Network
    from bindsnet.network.nodes import Input, LIFNodes
    from bindsnet.network.topology import Connection

    BINDSNET_AVAILABLE = True
except ImportError:
    BINDSNET_AVAILABLE = False
    logger.warning("BindsNet not available - RL SNN features disabled")

try:
    import sinabs  # noqa: F401
    import sinabs.layers as sl
    from sinabs.from_torch import from_model

    SINABS_AVAILABLE = True
except ImportError:
    SINABS_AVAILABLE = False
    logger.warning("Sinabs not available - Vision SNN features disabled")

try:
    import snntorch as snn  # noqa: F401 - Imported to check availability
    import snntorch.functional as SF  # noqa: F401, N812 - Standard snnTorch alias

    SNNTORCH_AVAILABLE = True
except ImportError:
    SNNTORCH_AVAILABLE = False
    logger.warning("snnTorch not available")

try:
    import spikingjelly  # noqa: F401
    from spikingjelly.activation_based import functional, layer, neuron  # noqa: F401

    SPIKINGJELLY_AVAILABLE = True
except ImportError:
    SPIKINGJELLY_AVAILABLE = False
    logger.warning("SpikingJelly not available")

try:
    import norse  # noqa: F401
    from norse.torch import LIFCell, LIFParameters  # noqa: F401

    NORSE_AVAILABLE = True
except ImportError:
    NORSE_AVAILABLE = False
    logger.warning("Norse not available")

try:
    import brian2  # noqa: F401

    BRIAN2_AVAILABLE = True
except ImportError:
    BRIAN2_AVAILABLE = False
    logger.warning("Brian2 not available")

try:
    import lava  # noqa: F401
    from lava.magma.core.model.py.model import PyLoihiProcessModel  # noqa: F401
    from lava.magma.core.process.process import AbstractProcess  # noqa: F401

    LAVA_AVAILABLE = True
except ImportError:
    LAVA_AVAILABLE = False
    logger.warning("Lava (Intel) not available")

try:
    import rockpool  # noqa: F401
    from rockpool.nn.modules import LIF  # noqa: F401

    ROCKPOOL_AVAILABLE = True
except ImportError:
    ROCKPOOL_AVAILABLE = False
    logger.warning("Rockpool not available")

try:
    import nengo  # noqa: F401

    NENGO_AVAILABLE = True
except ImportError:
    NENGO_AVAILABLE = False
    logger.warning("Nengo not available")

try:
    import nir  # noqa: F401

    NIR_AVAILABLE = True
except ImportError:
    NIR_AVAILABLE = False
    logger.warning("NIR (Neuromorphic Intermediate Representation) not available")

# Note: NeurocoreX and RANC are not available on PyPI as standard packages
# They may require custom installation from source repositories
NEUROCOREX_AVAILABLE = False
RANC_AVAILABLE = False


class BindsNetRLAgent:
    """
    Reinforcement Learning agent using BindsNet SNNs.

    Supports continual learning without full retraining, making it suitable
    for adaptive AI systems that learn from ongoing interactions.

    Features:
    - Spike-based RL with STDP (Spike-Timing-Dependent Plasticity)
    - Energy-efficient computation
    - Online learning capabilities
    - Suitable for edge deployment
    """

    def __init__(
        self,
        input_size: int = 784,
        hidden_size: int = 400,
        output_size: int = 10,
        dt: float = 1.0,
        learning_rate: float = 0.01,
        data_dir: str = "data/snn",
    ):
        """Initialize BindsNet RL agent.

        Args:
            input_size: Input dimension (e.g., 784 for 28x28 images)
            hidden_size: Hidden layer size
            output_size: Output dimension (number of actions/classes)
            dt: Simulation timestep in milliseconds
            learning_rate: Learning rate for STDP
            data_dir: Directory for saving/loading models
        """
        if not BINDSNET_AVAILABLE:
            raise ImportError(
                "BindsNet is not installed. Install with: pip install bindsnet"
            )

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.dt = dt
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Build SNN network
        self.network = Network(dt=dt)

        # Input layer (Poisson encoding)
        self.network.add_layer(
            Input(n=input_size, traces=True, trace_tc=5e-2), name="input"
        )

        # Hidden layer (Leaky Integrate-and-Fire neurons)
        self.network.add_layer(
            LIFNodes(
                n=hidden_size,
                traces=True,
                rest=-65.0,
                reset=-65.0,
                thresh=-52.0,
                refrac=5,
                tc_decay=100.0,
                trace_tc=5e-2,
            ),
            name="hidden",
        )

        # Output layer
        self.network.add_layer(
            LIFNodes(
                n=output_size,
                traces=True,
                rest=-65.0,
                reset=-65.0,
                thresh=-52.0,
                refrac=5,
                tc_decay=100.0,
                trace_tc=5e-2,
            ),
            name="output",
        )

        # Connections with STDP learning
        w_input_hidden = 0.3 * torch.rand(input_size, hidden_size)
        self.network.add_connection(
            Connection(
                source=self.network.layers["input"],
                target=self.network.layers["hidden"],
                w=w_input_hidden,
                update_rule=PostPre,
                nu=(learning_rate, learning_rate),
                wmin=0.0,
                wmax=1.0,
            ),
            source="input",
            target="hidden",
        )

        w_hidden_output = 0.3 * torch.rand(hidden_size, output_size)
        self.network.add_connection(
            Connection(
                source=self.network.layers["hidden"],
                target=self.network.layers["output"],
                w=w_hidden_output,
                update_rule=PostPre,
                nu=(learning_rate, learning_rate),
                wmin=0.0,
                wmax=1.0,
            ),
            source="hidden",
            target="output",
        )

        # Poisson encoder for input spikes
        self.encoder = PoissonEncoder(time=100, dt=dt)

        logger.info(
            f"BindsNet RL agent initialized: {input_size}→{hidden_size}→{output_size}"
        )

    def process_observation(
        self, observation: np.ndarray, time: int = 100
    ) -> torch.Tensor:
        """
        Process observation through SNN and return spike outputs.

        Args:
            observation: Input observation (e.g., sensor data, image)
            time: Simulation time in milliseconds

        Returns:
            Output spike trains
        """
        # Normalize observation
        obs_normalized = (observation - observation.min()) / (
            observation.max() - observation.min() + 1e-8
        )
        obs_tensor = torch.from_numpy(obs_normalized).float().flatten()

        # Encode as spikes
        spike_input = self.encoder(obs_tensor)

        # Run network
        self.network.run(inputs={"input": spike_input}, time=time)

        # Get output spikes
        output_spikes = self.network.layers["output"].s

        return output_spikes

    def select_action(self, observation: np.ndarray) -> int:
        """
        Select action based on SNN output.

        Args:
            observation: Current state observation

        Returns:
            Selected action index
        """
        output_spikes = self.process_observation(observation)

        # Sum spikes over time to get action scores
        action_scores = output_spikes.sum(dim=0)

        # Select action with highest spike count
        action = torch.argmax(action_scores).item()

        return action

    def update(self, reward: float):
        """
        Update network based on reward (reward-modulated STDP).

        Args:
            reward: Reward signal from environment
        """
        # Modulate learning based on reward
        # Positive reward strengthens recent connections
        if reward > 0:
            # Strengthen connections that led to positive reward
            for _conn_name, conn in self.network.connections.items():
                if hasattr(conn, "update_rule") and conn.update_rule is not None:
                    # Apply reward modulation
                    conn.w.data += reward * 0.01 * torch.sign(conn.w.data)
                    conn.w.data.clamp_(0.0, 1.0)

    def reset(self):
        """Reset network state between episodes."""
        self.network.reset_state_variables()

    def save(self, path: str | None = None):
        """Save network weights.

        Args:
            path: Save path (default: data_dir/bindsnet_weights.pt)
        """
        if path is None:
            path = self.data_dir / "bindsnet_weights.pt"

        weights = {}
        for conn_name, conn in self.network.connections.items():
            weights[conn_name] = conn.w.data.clone()

        torch.save(weights, path)
        logger.info(f"BindsNet weights saved to {path}")

    def load(self, path: str | None = None):
        """Load network weights.

        Args:
            path: Load path (default: data_dir/bindsnet_weights.pt)
        """
        if path is None:
            path = self.data_dir / "bindsnet_weights.pt"

        if not Path(path).exists():
            logger.warning(f"Weight file not found: {path}")
            return

        weights = torch.load(path)
        for conn_name, conn in self.network.connections.items():
            if conn_name in weights:
                conn.w.data = weights[conn_name].clone()

        logger.info(f"BindsNet weights loaded from {path}")


class SinabsVisionSNN:
    """
    Vision-optimized SNN using Sinabs library.

    Supports weight transfer from standard CNNs (Caffe2) to SNNs,
    enabling deployment on neuromorphic hardware (SynSense).

    Features:
    - CNN to SNN conversion
    - Hardware-ready models for neuromorphic chips
    - Energy-efficient vision processing
    - Compatible with SynSense Speck/Dynap-CNN chips
    """

    def __init__(
        self,
        input_shape: tuple = (1, 28, 28),
        num_classes: int = 10,
        data_dir: str = "data/snn",
    ):
        """Initialize Sinabs vision SNN.

        Args:
            input_shape: Input image shape (C, H, W)
            num_classes: Number of output classes
            data_dir: Directory for saving/loading models
        """
        if not SINABS_AVAILABLE:
            raise ImportError(
                "Sinabs is not installed. Install with: pip install sinabs"
            )

        self.input_shape = input_shape
        self.num_classes = num_classes
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Build SNN model
        self.model = self._build_model()

        logger.info(
            f"Sinabs vision SNN initialized: {input_shape} → {num_classes} classes"
        )

    def _build_model(self) -> nn.Module:
        """Build Sinabs SNN model for vision tasks."""
        c, h, w = self.input_shape

        # Simple CNN architecture that can be converted to SNN
        model = nn.Sequential(
            # Conv block 1
            nn.Conv2d(c, 32, kernel_size=3, padding=1),
            sl.IAFSqueeze(batch_size=1, min_v_mem=-1.0),  # Spiking activation
            nn.AvgPool2d(2),
            # Conv block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            sl.IAFSqueeze(batch_size=1, min_v_mem=-1.0),
            nn.AvgPool2d(2),
            # Flatten and FC
            nn.Flatten(),
            nn.Linear((h // 4) * (w // 4) * 64, 128),
            sl.IAFSqueeze(batch_size=1, min_v_mem=-1.0),
            nn.Linear(128, self.num_classes),
            sl.IAFSqueeze(batch_size=1, min_v_mem=-1.0),
        )

        return model

    def forward(self, x: torch.Tensor, num_steps: int = 100) -> torch.Tensor:
        """
        Forward pass through SNN.

        Args:
            x: Input tensor (B, C, H, W)
            num_steps: Number of time steps for spiking simulation

        Returns:
            Output spike counts
        """
        # Reset neuron states
        for layer in self.model:
            if hasattr(layer, "reset_states"):
                layer.reset_states()

        # Accumulate spikes over time
        spike_count = torch.zeros(x.shape[0], self.num_classes)

        for _ in range(num_steps):
            output = self.model(x)
            spike_count += output

        return spike_count

    def predict(self, x: np.ndarray) -> int:
        """
        Predict class for input image.

        Args:
            x: Input image (C, H, W) or (H, W)

        Returns:
            Predicted class index
        """
        # Prepare input
        if len(x.shape) == 2:
            x = x[np.newaxis, ...]  # Add channel dimension

        x_tensor = torch.from_numpy(x).float().unsqueeze(0)  # Add batch dimension

        # Forward pass
        output = self.forward(x_tensor)

        # Get prediction
        pred = torch.argmax(output, dim=1).item()

        return pred

    @staticmethod
    def convert_from_pytorch(pytorch_model: nn.Module) -> nn.Module:
        """
        Convert standard PyTorch CNN to Sinabs SNN.

        This enables transfer learning from pre-trained models.

        Args:
            pytorch_model: Standard PyTorch model (e.g., ResNet, VGG)

        Returns:
            Sinabs SNN model with transferred weights
        """
        if not SINABS_AVAILABLE:
            raise ImportError("Sinabs is required for model conversion")

        # Convert model using Sinabs automatic conversion
        snn_model = from_model(
            pytorch_model,
            input_shape=(1, 28, 28),  # Adjust based on model
            add_spiking_output=True,
            batch_size=1,
        )

        logger.info("Converted PyTorch model to Sinabs SNN")
        return snn_model

    def save(self, path: str | None = None):
        """Save SNN model.

        Args:
            path: Save path (default: data_dir/sinabs_model.pt)
        """
        if path is None:
            path = self.data_dir / "sinabs_model.pt"

        torch.save(self.model.state_dict(), path)
        logger.info(f"Sinabs model saved to {path}")

    def load(self, path: str | None = None):
        """Load SNN model.

        Args:
            path: Load path (default: data_dir/sinabs_model.pt)
        """
        if path is None:
            path = self.data_dir / "sinabs_model.pt"

        if not Path(path).exists():
            logger.warning(f"Model file not found: {path}")
            return

        self.model.load_state_dict(torch.load(path))
        logger.info(f"Sinabs model loaded from {path}")

    def export_for_hardware(self, path: str | None = None):
        """
        Export model for SynSense neuromorphic hardware.

        Args:
            path: Export path (default: data_dir/sinabs_hardware.pt)
        """
        if path is None:
            path = self.data_dir / "sinabs_hardware.pt"

        # Export model in hardware-compatible format
        # Note: Actual hardware deployment requires SynSense SDK
        torch.save(
            {
                "model": self.model.state_dict(),
                "input_shape": self.input_shape,
                "num_classes": self.num_classes,
            },
            path,
        )

        logger.info(f"Model exported for hardware deployment: {path}")
        logger.info("Note: Use SynSense SDK for actual hardware deployment")


class SNNManager:
    """
    Manager for SNN models in Project-AI.

    Provides high-level interface for:
    - Continual learning (BindsNet)
    - Vision processing (Sinabs)
    - Model conversion and deployment
    """

    def __init__(self, data_dir: str = "data/snn"):
        """Initialize SNN manager.

        Args:
            data_dir: Directory for SNN models and data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.bindsnet_agent: BindsNetRLAgent | None = None
        self.sinabs_vision: SinabsVisionSNN | None = None

        logger.info("SNNManager initialized")

    def create_rl_agent(
        self, input_size: int = 784, hidden_size: int = 400, output_size: int = 10
    ) -> BindsNetRLAgent:
        """Create BindsNet RL agent for continual learning.

        Args:
            input_size: Input dimension
            hidden_size: Hidden layer size
            output_size: Number of actions

        Returns:
            BindsNet RL agent
        """
        self.bindsnet_agent = BindsNetRLAgent(
            input_size=input_size,
            hidden_size=hidden_size,
            output_size=output_size,
            data_dir=str(self.data_dir),
        )
        return self.bindsnet_agent

    def create_vision_snn(
        self, input_shape: tuple = (1, 28, 28), num_classes: int = 10
    ) -> SinabsVisionSNN:
        """Create Sinabs vision SNN.

        Args:
            input_shape: Input image shape (C, H, W)
            num_classes: Number of classes

        Returns:
            Sinabs vision SNN
        """
        self.sinabs_vision = SinabsVisionSNN(
            input_shape=input_shape,
            num_classes=num_classes,
            data_dir=str(self.data_dir),
        )
        return self.sinabs_vision

    def get_capabilities(self) -> dict[str, bool]:
        """Get available SNN capabilities.

        Returns:
            Dictionary of available features and libraries
        """
        return {
            # Core dependencies
            "pytorch": TORCH_AVAILABLE,
            # SNN Libraries
            "bindsnet": BINDSNET_AVAILABLE,
            "sinabs": SINABS_AVAILABLE,
            "snntorch": SNNTORCH_AVAILABLE,
            "spikingjelly": SPIKINGJELLY_AVAILABLE,
            "norse": NORSE_AVAILABLE,
            "brian2": BRIAN2_AVAILABLE,
            "lava": LAVA_AVAILABLE,
            "rockpool": ROCKPOOL_AVAILABLE,
            "nengo": NENGO_AVAILABLE,
            "nir": NIR_AVAILABLE,
            "neurocorex": NEUROCOREX_AVAILABLE,
            "ranc": RANC_AVAILABLE,
            # Feature capabilities
            "rl_continual_learning": BINDSNET_AVAILABLE,
            "vision_snn": SINABS_AVAILABLE or SNNTORCH_AVAILABLE,
            "hardware_deployment": SINABS_AVAILABLE
            or LAVA_AVAILABLE
            or ROCKPOOL_AVAILABLE,
            "neural_engineering": NENGO_AVAILABLE,
            "intermediate_representation": NIR_AVAILABLE,
            "intel_loihi": LAVA_AVAILABLE,
            "synsense_hardware": SINABS_AVAILABLE,
            "brain_simulation": BRIAN2_AVAILABLE or NENGO_AVAILABLE,
        }


# Convenience function
def create_snn_manager(data_dir: str = "data/snn") -> SNNManager:
    """Create SNN manager for Project-AI.

    Args:
        data_dir: Directory for SNN models

    Returns:
        SNNManager instance
    """
    return SNNManager(data_dir=data_dir)
