"""
Visualization Components for Holographic Defense

Real-time visual displays for demonstrations:
- Layer status visualization
- Threat heatmap
- Attack flow diagram
- Performance metrics dashboard
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class VisualizationMode(Enum):
    """Display modes"""

    COMPACT = "compact"
    DETAILED = "detailed"
    PRESENTATION = "presentation"


@dataclass
class LayerVisualization:
    """Visual representation of layer state"""

    layer_id: int
    layer_type: str
    user_count: int
    activity_level: float  # 0.0 - 1.0
    threat_count: int


class ASCIIArt:
    """ASCII art for visual appeal"""

    @staticmethod
    def logo() -> str:
        """Thirst of Gods logo"""
        return """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        ████████╗██╗  ██╗██╗██████╗ ███████╗████████╗            ║
║        ╚══██╔══╝██║  ██║██║██╔══██╗██╔════╝╚══██╔══╝            ║
║           ██║   ███████║██║██████╔╝███████╗   ██║               ║
║           ██║   ██╔══██║██║██╔══██╗╚════██║   ██║               ║
║           ██║   ██║  ██║██║██║  ██║███████║   ██║               ║
║           ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝               ║
║                                                                   ║
║                    OF GODS - Holographic Defense                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

    @staticmethod
    def layer_diagram() -> str:
        """3-layer architecture diagram"""
        return """
┌─────────────────────────────────────────────────────────────┐
│                    HOLOGRAPHIC LAYERS                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 2+: ┌──────────────────────────────────┐            │
│  DECEPTION │  🍯 Honeypot Environment         │ [TRAP]     │
│            │  • Fake files, fake root          │            │
│            │  • Attacker thinks they're winning│            │
│            └──────────────────────────────────┘            │
│                         ▲                                    │
│                         │ Malicious Activity Detected        │
│                         │                                    │
│  Layer 1:  ┌──────────────────────────────────┐            │
│  MIRROR    │  👁️  Observation Sandbox          │ [OBSERVE]  │
│            │  • Commands execute here FIRST    │            │
│            │  • AI analyzes behavior           │            │
│            └──────────────────────────────────┘            │
│                         ▲                                    │
│                         │ All Commands                       │
│                         │                                    │
│  Layer 0:  ┌──────────────────────────────────┐            │
│  REAL      │  🔒 Actual System (Hidden)        │ [PROTECTED]│
│            │  • Only safe verified commands    │            │
│            │  • Completely isolated            │            │
│            └──────────────────────────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
"""

    @staticmethod
    def bubblegum_banner() -> str:
        """Bubblegum protocol banner"""
        return """
╔═══════════════════════════════════════════════════════════════╗
║                                                                ║
║     💥  BUBBLEGUM PROTOCOL ACTIVATED  💥                      ║
║                                                                ║
║     "I have come here today for two reasons,                  ║
║      To Chew BubbleGum And Kick Ass.                          ║
║                                                                ║
║      And I am ALL OUT, of Bubblegum."                         ║
║                                                                ║
╚═══════════════════════════════════════════════════════════════╝
"""


class ThreatHeatmap:
    """Real-time threat activity visualization"""

    def __init__(self, width: int = 60, height: int = 10):
        self.width = width
        self.height = height
        self.activity_grid: list[list[float]] = []
        self._initialize_grid()

    def _initialize_grid(self):
        """Initialize empty grid"""
        self.activity_grid = [
            [0.0 for _ in range(self.width)] for _ in range(self.height)
        ]

    def record_threat(self, x: float, y: float, intensity: float):
        """Record a threat event at position"""
        grid_x = int(x * self.width)
        grid_y = int(y * self.height)

        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.activity_grid[grid_y][grid_x] = min(
                self.activity_grid[grid_y][grid_x] + intensity, 1.0
            )

    def decay(self, rate: float = 0.1):
        """Decay all activity over time"""
        for y in range(self.height):
            for x in range(self.width):
                self.activity_grid[y][x] = max(0.0, self.activity_grid[y][x] - rate)

    def render(self) -> str:
        """Render heatmap as ASCII"""
        chars = [" ", "░", "▒", "▓", "█"]

        lines = ["┌" + "─" * self.width + "┐"]

        for row in self.activity_grid:
            line = "│"
            for cell in row:
                char_idx = int(cell * (len(chars) - 1))
                line += chars[char_idx]
            line += "│"
            lines.append(line)

        lines.append("└" + "─" * self.width + "┘")

        return "\n".join(lines)


class PerformanceMetrics:
    """Performance metrics dashboard"""

    def __init__(self):
        self.metrics: dict[str, Any] = {
            "total_commands": 0,
            "threats_detected": 0,
            "deceptions_active": 0,
            "bubblegum_triggers": 0,
            "avg_detection_time_ms": 0.0,
            "layer_switches": 0,
        }

    def update(self, metric_name: str, value: Any):
        """Update a metric"""
        if metric_name in self.metrics:
            if isinstance(self.metrics[metric_name], (int, float)):
                self.metrics[metric_name] = value

    def increment(self, metric_name: str):
        """Increment a counter metric"""
        if metric_name in self.metrics:
            if isinstance(self.metrics[metric_name], int):
                self.metrics[metric_name] += 1

    def render(self, mode: VisualizationMode = VisualizationMode.COMPACT) -> str:
        """Render metrics display"""
        if mode == VisualizationMode.COMPACT:
            return self._render_compact()
        elif mode == VisualizationMode.DETAILED:
            return self._render_detailed()
        else:
            return self._render_presentation()

    def _render_compact(self) -> str:
        """Compact metrics display"""
        return f"""
Commands: {self.metrics["total_commands"]} | Threats: {self.metrics["threats_detected"]} | Active Traps: {self.metrics["deceptions_active"]} | Bubblegum: {self.metrics["bubblegum_triggers"]}
"""

    def _render_detailed(self) -> str:
        """Detailed metrics display"""
        return f"""
┌─────────────────────────────────────────┐
│         PERFORMANCE METRICS              │
├─────────────────────────────────────────┤
│ Total Commands:        {self.metrics["total_commands"]:>10}       │
│ Threats Detected:      {self.metrics["threats_detected"]:>10}       │
│ Active Deceptions:     {self.metrics["deceptions_active"]:>10}       │
│ Bubblegum Triggers:    {self.metrics["bubblegum_triggers"]:>10}       │
│ Avg Detection Time:    {self.metrics["avg_detection_time_ms"]:>7.2f} ms    │
│ Layer Switches:        {self.metrics["layer_switches"]:>10}       │
└─────────────────────────────────────────┘
"""

    def _render_presentation(self) -> str:
        """Presentation mode - large and bold"""
        return f"""
╔═════════════════════════════════════════════════════════╗
║                                                          ║
║            📊 SYSTEM PERFORMANCE METRICS                 ║
║                                                          ║
╠═════════════════════════════════════════════════════════╣
║                                                          ║
║   Total Commands Processed:        {self.metrics["total_commands"]:>10}          ║
║   Threats Detected:                {self.metrics["threats_detected"]:>10}          ║
║   Active Deception Layers:         {self.metrics["deceptions_active"]:>10}          ║
║   Bubblegum Triggers:              {self.metrics["bubblegum_triggers"]:>10}          ║
║                                                          ║
║   Average Detection Time:          {self.metrics["avg_detection_time_ms"]:>7.2f} ms       ║
║   Layer Transitions:               {self.metrics["layer_switches"]:>10}          ║
║                                                          ║
╚═════════════════════════════════════════════════════════╝
"""


class AttackFlowDiagram:
    """Visualize attack progression"""

    @staticmethod
    def render(attack_chain: list[str]) -> str:
        """Render attack flow diagram"""
        if not attack_chain:
            return "No attack activity"

        lines = ["┌" + "─" * 60 + "┐"]
        lines.append("│" + "  ATTACK FLOW".center(60) + "│")
        lines.append("├" + "─" * 60 + "┤")

        for i, step in enumerate(attack_chain, 1):
            lines.append(f"│ {i}. {step:<56} │")
            if i < len(attack_chain):
                lines.append("│     ↓".ljust(61) + "│")

        lines.append("└" + "─" * 60 + "┘")

        return "\n".join(lines)


class DemoVisualizer:
    """Main visualization orchestrator for demos"""

    def __init__(self):
        self.heatmap = ThreatHeatmap()
        self.metrics = PerformanceMetrics()

    def show_intro(self):
        """Display introduction screen"""
        print(ASCIIArt.logo())
        print("\nRevolutionary Multi-Layer Security Architecture")
        print("=" * 70)
        print(ASCIIArt.layer_diagram())
        input("\nPress Enter to begin demonstration...")

    def show_threat_detected(self, threat_info: dict[str, Any]):
        """Display threat detection alert"""
        print("")
        print("╔" + "═" * 60 + "╗")
        print("║" + " ⚠️  THREAT DETECTED".center(60) + "║")
        print("╠" + "═" * 60 + "╣")
        print(f"║  Type: {threat_info.get('type', 'Unknown'):<52} ║")
        print(f"║  Level: {threat_info.get('level', 'Unknown'):<51} ║")
        print(f"║  Confidence: {threat_info.get('confidence', 0):.1%}".ljust(61) + "║")
        print("╚" + "═" * 60 + "╝")
        print("")

    def show_layer_transition(self, from_layer: int, to_layer: int, reason: str):
        """Display layer transition"""
        print("\n" + "─" * 70)
        print(f"🔄 LAYER TRANSITION: Layer {from_layer} → Layer {to_layer}")
        print(f"   Reason: {reason}")
        print("─" * 70 + "\n")
        self.metrics.increment("layer_switches")

    def show_bubblegum(self):
        """Display Bubblegum protocol activation"""
        print(ASCIIArt.bubblegum_banner())
        self.metrics.increment("bubblegum_triggers")

    def show_metrics(self, mode: VisualizationMode = VisualizationMode.DETAILED):
        """Display current metrics"""
        print(self.metrics.render(mode))

    def show_heatmap(self):
        """Display threat heatmap"""
        print("\n🔥 THREAT ACTIVITY HEATMAP")
        print(self.heatmap.render())

    def update_display(self):
        """Update all visual elements"""
        self.heatmap.decay(0.05)  # Gradual decay
        # In a real implementation, this would refresh the display


# Public API
__all__ = [
    "DemoVisualizer",
    "PerformanceMetrics",
    "ThreatHeatmap",
    "AttackFlowDiagram",
    "ASCIIArt",
    "VisualizationMode",
]
