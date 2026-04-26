"""
Advanced Visualization Components

Enhanced visualizations for presentations:
- Split-screen attack view (attacker vs system)
- Animated attack flow
- Live threat heatmap
- Real-time metrics dashboard
"""

import time
from dataclasses import dataclass

try:
    # Try to use rich for better terminal output
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class AttackFlowStep:
    """Single step in attack visualization"""

    timestamp: float
    command: str
    layer: int
    threat_score: float
    system_response: str
    attacker_sees: str


class SplitScreenVisualizer:
    """
    Split-screen visualization showing both attacker and system perspectives

    Left: What attacker sees
    Right: What's actually happening in the system
    """

    def __init__(self):
        self.use_rich = RICH_AVAILABLE
        if self.use_rich:
            self.console = Console()

    def show_split_screen(self, attack_step: AttackFlowStep):
        """Display split-screen view of attack step"""
        if self.use_rich:
            self._show_rich_split(attack_step)
        else:
            self._show_basic_split(attack_step)

    def _show_rich_split(self, step: AttackFlowStep):
        """Rich library split screen"""
        layout = Layout()
        layout.split_row(Layout(name="attacker"), Layout(name="system"))

        # Left side - Attacker view
        attacker_content = f"""
[bold red]ATTACKER VIEW[/bold red]

Command: {step.command}

Response:
{step.attacker_sees}

[dim]Everything looks normal...[/dim]
"""
        layout["attacker"].update(Panel(attacker_content, title="👹 Attacker Terminal"))

        # Right side - System view
        threat_color = (
            "red"
            if step.threat_score > 0.7
            else "yellow" if step.threat_score > 0.4 else "green"
        )
        layer_name = {0: "REAL", 1: "MIRROR", 2: "DECEPTION"}.get(step.layer, "UNKNOWN")

        system_content = f"""
[bold green]SYSTEM REALITY[/bold green]

Layer: [bold {threat_color}]{layer_name}[/bold {threat_color}] (L{step.layer})
Threat Score: [{threat_color}]{step.threat_score:.2f}[/{threat_color}]

Actual Response:
{step.system_response}

[dim italic]{self._get_system_comment(step)}[/dim italic]
"""
        layout["system"].update(Panel(system_content, title="🛡️ System Monitor"))

        self.console.print(layout)
        self.console.print()

    def _show_basic_split(self, step: AttackFlowStep):
        """Basic ASCII split screen"""
        width = 70
        half = width // 2

        print("=" * width)
        print(f"{'ATTACKER VIEW':^{half}} | {'SYSTEM REALITY':^{half}}")
        print("=" * width)

        # Command
        print(
            f"{'Command: ' + step.command[: half - 10]:^{half}} | {'Layer: L' + str(step.layer):^{half}}"
        )

        # Response
        attacker_resp = step.attacker_sees[: half - 2]
        system_resp = step.system_response[: half - 2]
        print(f"{attacker_resp:<{half}} | {system_resp:<{half}}")

        # Threat
        threat_bar = self._make_threat_bar(step.threat_score, half - 10)
        print(f"{'':^{half}} | Threat: {threat_bar}")

        print("=" * width)
        print()

    def _make_threat_bar(self, score: float, width: int) -> str:
        """Create ASCII threat bar"""
        filled = int(score * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {score:.0%}"

    def _get_system_comment(self, step: AttackFlowStep) -> str:
        """Get system comment based on attack step"""
        if step.layer == 0:
            return "Safe command, executing on real system"
        elif step.layer == 1:
            return "Observing in mirror layer, analyzing..."
        else:
            return "TRAPPED in deception layer! Attacker has no idea."


class AnimatedAttackFlow:
    """Animated attack sequence visualization"""

    def __init__(self):
        self.steps: list[AttackFlowStep] = []
        self.use_rich = RICH_AVAILABLE
        if self.use_rich:
            self.console = Console()

    def add_step(self, step: AttackFlowStep):
        """Add step to attack flow"""
        self.steps.append(step)

    def animate_attack(self, delay: float = 1.5):
        """Animate the complete attack sequence"""
        print("\n" + "=" * 70)
        print("ATTACK SEQUENCE PLAYBACK".center(70))
        print("=" * 70 + "\n")

        for i, step in enumerate(self.steps, 1):
            print(f"\n[Step {i}/{len(self.steps)}]")
            print(f"Time: +{step.timestamp - self.steps[0].timestamp:.1f}s")

            # Show split screen for this step
            visualizer = SplitScreenVisualizer()
            visualizer.show_split_screen(step)

            # Pause between steps
            if i < len(self.steps):
                time.sleep(delay)

    def show_summary(self):
        """Show attack summary"""
        if not self.steps:
            return

        print("\n" + "=" * 70)
        print("ATTACK SUMMARY".center(70))
        print("=" * 70)

        # High-level stats
        duration = self.steps[-1].timestamp - self.steps[0].timestamp
        max_threat = max(s.threat_score for s in self.steps)
        deception_steps = sum(1 for s in self.steps if s.layer >= 2)

        print(f"\nDuration: {duration:.1f} seconds")
        print(f"Total Steps: {len(self.steps)}")
        print(f"Peak Threat: {max_threat:.0%}")
        print(
            f"Deception Time: {deception_steps} steps ({deception_steps / len(self.steps):.0%})"
        )

        # Step-by-step
        print("\n" + "Step-by-Step Breakdown:".center(70))
        print("-" * 70)

        for i, step in enumerate(self.steps, 1):
            layer_icon = {0: "✅", 1: "👁️", 2: "🎭"}.get(step.layer, "❓")
            threat_icon = (
                "🔴"
                if step.threat_score > 0.7
                else "🟡" if step.threat_score > 0.4 else "🟢"
            )

            print(
                f"{i:2}. {layer_icon} {step.command[:40]:<40} {threat_icon} {step.threat_score:.0%}"
            )

        print("=" * 70 + "\n")


class LiveMetricsDashboard:
    """Live updating metrics dashboard"""

    def __init__(self):
        self.metrics = {
            "commands": 0,
            "threats": 0,
            "deceptions": 0,
            "bubblegum": 0,
            "avg_threat": 0.0,
            "layers": {0: 0, 1: 0, 2: 0},
        }
        self.use_rich = RICH_AVAILABLE
        if self.use_rich:
            self.console = Console()

    def update(self, **kwargs):
        """Update metrics"""
        for key, value in kwargs.items():
            if key in self.metrics:
                if isinstance(value, dict):
                    self.metrics[key].update(value)
                else:
                    self.metrics[key] = value

    def render(self) -> str:
        """Render dashboard"""
        if self.use_rich:
            return self._render_rich()
        else:
            return self._render_basic()

    def _render_rich(self) -> str:
        """Render with rich library"""
        table = Table(title="🔥 Live System Metrics")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Graph", style="yellow")

        # Commands
        table.add_row(
            "Total Commands",
            str(self.metrics["commands"]),
            "█" * (self.metrics["commands"] // 10),
        )

        # Threats
        threat_percent = (
            self.metrics["threats"] / max(self.metrics["commands"], 1)
        ) * 100
        table.add_row(
            "Threats Detected",
            f"{self.metrics['threats']} ({threat_percent:.1f}%)",
            "█" * (self.metrics["threats"] // 5),
        )

        # Deceptions
        table.add_row(
            "Active Deceptions",
            str(self.metrics["deceptions"]),
            "█" * self.metrics["deceptions"],
        )

        # Bubblegum
        table.add_row(
            "Bubblegum Triggers",
            str(self.metrics["bubblegum"]),
            "💥" * self.metrics["bubblegum"],
        )

        # Avg threat
        avg_bar = "█" * int(self.metrics["avg_threat"] * 10)
        table.add_row("Avg Threat Score", f"{self.metrics['avg_threat']:.2f}", avg_bar)

        # Layer distribution
        layer_total = sum(self.metrics["layers"].values())
        if layer_total > 0:
            for layer_num in [0, 1, 2]:
                count = self.metrics["layers"].get(layer_num, 0)
                pct = (count / layer_total) * 100
                layer_name = {0: "Real", 1: "Mirror", 2: "Deception"}[layer_num]
                table.add_row(
                    f"Layer {layer_num} ({layer_name})",
                    f"{count} ({pct:.0f}%)",
                    "▓" * int(pct // 5),
                )

        return table

    def _render_basic(self) -> str:
        """Render basic ASCII"""
        lines = []
        lines.append("=" * 60)
        lines.append("  LIVE SYSTEM METRICS".center(60))
        lines.append("=" * 60)
        lines.append(f"  Commands:       {self.metrics['commands']:>6}")
        lines.append(f"  Threats:        {self.metrics['threats']:>6}")
        lines.append(f"  Deceptions:     {self.metrics['deceptions']:>6}")
        lines.append(f"  Bubblegum:      {self.metrics['bubblegum']:>6}")
        lines.append(f"  Avg Threat:     {self.metrics['avg_threat']:>6.2f}")
        lines.append("-" * 60)

        layer_total = sum(self.metrics["layers"].values())
        if layer_total > 0:
            for layer in [0, 1, 2]:
                count = self.metrics["layers"].get(layer, 0)
                pct = (count / layer_total) * 100
                bar = "█" * int(pct // 5)
                lines.append(
                    f"  Layer {layer}:       {count:>4} [{bar:<20}] {pct:>5.1f}%"
                )

        lines.append("=" * 60)
        return "\n".join(lines)

    def display(self):
        """Display dashboard"""
        if self.use_rich:
            self.console.print(self.render())
        else:
            print(self.render())


# Public API
__all__ = [
    "SplitScreenVisualizer",
    "AnimatedAttackFlow",
    "LiveMetricsDashboard",
    "AttackFlowStep",
]
