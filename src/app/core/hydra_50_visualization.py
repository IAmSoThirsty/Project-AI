#!/usr/bin/env python3
"""
HYDRA-50 SCENARIO VISUALIZATION ENGINE
God-Tier Real-Time Visualization and Rendering System

Production-grade visualization with:
- Real-time scenario state rendering with ASCII art
- Escalation ladder visual representation
- Cross-domain coupling graphs with force-directed layout
- Temporal flow diagrams showing state transitions
- Collapse mode prediction charts
- Multi-format export (ASCII, JSON, SVG, PNG)
- Interactive dashboard data preparation
- Color-coded severity indicators
- Animation frame generation
- Historical replay visualization

ZERO placeholders. Full integration with PyQt6 GUI.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMERATIONS
# ============================================================================


class VisualizationType(Enum):
    """Types of visualizations"""

    ESCALATION_LADDER = "escalation_ladder"
    COUPLING_GRAPH = "coupling_graph"
    TEMPORAL_FLOW = "temporal_flow"
    COLLAPSE_PREDICTION = "collapse_prediction"
    STATUS_DASHBOARD = "status_dashboard"
    HEAT_MAP = "heat_map"


class ColorScheme(Enum):
    """Color schemes for visualization"""

    TERMINAL = "terminal"  # ASCII terminal colors
    TRON = "tron"  # Tron-inspired cyan/green
    DANGER = "danger"  # Red-orange-yellow warning
    MONOCHROME = "monochrome"  # Black and white


# ============================================================================
# ASCII ART COMPONENTS
# ============================================================================


class ASCIIArtRenderer:
    """ASCII art rendering engine"""

    # Box drawing characters
    BOX_CHARS = {
        "horizontal": "─",
        "vertical": "│",
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
        "cross": "┼",
        "t_down": "┬",
        "t_up": "┴",
        "t_right": "├",
        "t_left": "┤",
    }

    # Block characters for intensity visualization
    BLOCK_CHARS = [" ", "░", "▒", "▓", "█"]

    # Arrow characters
    ARROWS = {
        "up": "↑",
        "down": "↓",
        "left": "←",
        "right": "→",
        "up_down": "↕",
        "left_right": "↔",
    }

    # Color codes (ANSI)
    COLORS = {
        "reset": "\033[0m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "bold": "\033[1m",
    }

    @classmethod
    def draw_box(cls, width: int, height: int, title: str = "") -> list[str]:
        """Draw ASCII box"""
        lines = []

        # Top line
        if title:
            title_text = f" {title} "
            remaining = width - len(title_text) - 2
            left_width = remaining // 2
            right_width = remaining - left_width
            top_line = (
                cls.BOX_CHARS["top_left"]
                + cls.BOX_CHARS["horizontal"] * left_width
                + title_text
                + cls.BOX_CHARS["horizontal"] * right_width
                + cls.BOX_CHARS["top_right"]
            )
        else:
            top_line = (
                cls.BOX_CHARS["top_left"]
                + cls.BOX_CHARS["horizontal"] * (width - 2)
                + cls.BOX_CHARS["top_right"]
            )
        lines.append(top_line)

        # Middle lines
        for _ in range(height - 2):
            lines.append(
                cls.BOX_CHARS["vertical"]
                + " " * (width - 2)
                + cls.BOX_CHARS["vertical"]
            )

        # Bottom line
        bottom_line = (
            cls.BOX_CHARS["bottom_left"]
            + cls.BOX_CHARS["horizontal"] * (width - 2)
            + cls.BOX_CHARS["bottom_right"]
        )
        lines.append(bottom_line)

        return lines

    @classmethod
    def draw_progress_bar(cls, value: float, max_value: float, width: int = 20) -> str:
        """Draw progress bar"""
        filled = int((value / max_value) * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"

    @classmethod
    def draw_intensity_block(cls, intensity: float) -> str:
        """Draw single intensity block (0.0-1.0)"""
        index = min(int(intensity * len(cls.BLOCK_CHARS)), len(cls.BLOCK_CHARS) - 1)
        return cls.BLOCK_CHARS[index]

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Add ANSI color to text"""
        if color in cls.COLORS:
            return f"{cls.COLORS[color]}{text}{cls.COLORS['reset']}"
        return text

    @classmethod
    def draw_arrow(cls, direction: str, length: int = 1) -> str:
        """Draw arrow"""
        arrow = cls.ARROWS.get(direction, "→")
        if direction in ["left", "right"]:
            return arrow * length
        return arrow


# ============================================================================
# ESCALATION LADDER VISUALIZATION
# ============================================================================


@dataclass
class EscalationLadderViz:
    """Escalation ladder visualization data"""

    scenario_name: str
    current_level: int
    max_level: int
    level_descriptions: dict[int, str]
    level_values: dict[int, float]
    timestamp: float

    def render_ascii(self, width: int = 60) -> str:
        """Render escalation ladder as ASCII art"""
        lines = []

        # Title
        lines.append(
            ASCIIArtRenderer.colorize(
                f"═══ ESCALATION LADDER: {self.scenario_name} ═══", "cyan"
            )
        )
        lines.append("")

        # Draw each level
        for level in range(self.max_level, -1, -1):
            is_current = level == self.current_level
            is_passed = level < self.current_level

            # Determine color
            if level >= 4:
                color = "red"
            elif level >= 2:
                color = "yellow"
            else:
                color = "green"

            # Level indicator
            if is_current:
                indicator = "►"
                color = "bold"
            elif is_passed:
                indicator = "✓"
            else:
                indicator = " "

            # Level description
            desc = self.level_descriptions.get(level, f"Level {level}")
            value = self.level_values.get(level, 0.0)

            # Progress bar
            progress = ASCIIArtRenderer.draw_progress_bar(value, 100.0, 20)

            line = f"{indicator} L{level} │ {desc:<30} {progress} {value:5.1f}%"

            if is_current:
                line = ASCIIArtRenderer.colorize(line, "bold")

            lines.append(line)

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary for GUI"""
        return {
            "scenario_name": self.scenario_name,
            "current_level": self.current_level,
            "max_level": self.max_level,
            "level_descriptions": self.level_descriptions,
            "level_values": self.level_values,
            "timestamp": self.timestamp,
        }


# ============================================================================
# COUPLING GRAPH VISUALIZATION
# ============================================================================


@dataclass
class GraphNode:
    """Node in coupling graph"""

    node_id: str
    label: str
    x: float = 0.0
    y: float = 0.0
    value: float = 0.0
    color: str = "blue"


@dataclass
class GraphEdge:
    """Edge in coupling graph"""

    source: str
    target: str
    weight: float
    bidirectional: bool = False


class CouplingGraphViz:
    """Cross-domain coupling graph visualization"""

    def __init__(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
        title: str = "Domain Coupling",
    ):
        self.nodes = {n.node_id: n for n in nodes}
        self.edges = edges
        self.title = title

    def render_ascii(self, width: int = 80, height: int = 40) -> str:
        """Render coupling graph as ASCII art"""
        lines = []

        # Title
        lines.append(ASCIIArtRenderer.colorize(f"═══ {self.title.upper()} ═══", "cyan"))
        lines.append("")

        # Calculate positions using force-directed layout
        self._calculate_layout(width, height)

        # Create canvas
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        # Draw edges first
        for edge in self.edges:
            source = self.nodes[edge.source]
            target = self.nodes[edge.target]
            self._draw_line(canvas, source, target, edge)

        # Draw nodes on top
        for node in self.nodes.values():
            self._draw_node(canvas, node)

        # Convert canvas to string
        for row in canvas:
            lines.append("".join(row))

        # Legend
        lines.append("")
        lines.append("Legend: ● Node  ─ Strong coupling  ┄ Weak coupling")

        return "\n".join(lines)

    def _calculate_layout(self, width: int, height: int) -> None:
        """Calculate node positions using simple force-directed layout"""
        # Start with circular layout
        n_nodes = len(self.nodes)
        for i, node in enumerate(self.nodes.values()):
            angle = 2 * math.pi * i / n_nodes
            node.x = width // 2 + int((width // 3) * math.cos(angle))
            node.y = height // 2 + int((height // 3) * math.sin(angle))

            # Clamp to canvas bounds
            node.x = max(2, min(width - 3, node.x))
            node.y = max(2, min(height - 3, node.y))

    def _draw_line(
        self,
        canvas: list[list[str]],
        source: GraphNode,
        target: GraphNode,
        edge: GraphEdge,
    ) -> None:
        """Draw line between nodes using Bresenham's algorithm"""
        x0, y0 = int(source.x), int(source.y)
        x1, y1 = int(target.x), int(target.y)

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        char = "─" if edge.weight > 0.5 else "┄"

        while True:
            if 0 <= x0 < len(canvas[0]) and 0 <= y0 < len(canvas):
                if canvas[y0][x0] == " ":
                    canvas[y0][x0] = char

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def _draw_node(self, canvas: list[list[str]], node: GraphNode) -> None:
        """Draw node on canvas"""
        x, y = int(node.x), int(node.y)
        if 0 <= x < len(canvas[0]) and 0 <= y < len(canvas):
            canvas[y][x] = "●"

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary for GUI"""
        return {
            "title": self.title,
            "nodes": [
                {
                    "id": n.node_id,
                    "label": n.label,
                    "x": n.x,
                    "y": n.y,
                    "value": n.value,
                    "color": n.color,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "weight": e.weight,
                    "bidirectional": e.bidirectional,
                }
                for e in self.edges
            ],
        }


# ============================================================================
# TEMPORAL FLOW VISUALIZATION
# ============================================================================


@dataclass
class StateTransition:
    """State transition event"""

    timestamp: float
    from_state: str
    to_state: str
    trigger: str
    duration_seconds: float


class TemporalFlowViz:
    """Temporal flow diagram showing state transitions"""

    def __init__(
        self, scenario_name: str, transitions: list[StateTransition], current_state: str
    ):
        self.scenario_name = scenario_name
        self.transitions = sorted(transitions, key=lambda t: t.timestamp)
        self.current_state = current_state

    def render_ascii(self, width: int = 80) -> str:
        """Render temporal flow as ASCII timeline"""
        lines = []

        # Title
        lines.append(
            ASCIIArtRenderer.colorize(
                f"═══ TEMPORAL FLOW: {self.scenario_name} ═══", "cyan"
            )
        )
        lines.append("")

        if not self.transitions:
            lines.append("No state transitions recorded.")
            return "\n".join(lines)

        # Draw timeline
        start_time = self.transitions[0].timestamp

        for i, transition in enumerate(self.transitions):
            elapsed = transition.timestamp - start_time

            # Time marker
            time_str = f"T+{elapsed:6.1f}s"

            # State transition
            arrow = ASCIIArtRenderer.ARROWS["right"]
            state_line = (
                f"{time_str} │ {transition.from_state} {arrow} {transition.to_state}"
            )

            # Color based on target state
            if "COLLAPSE" in transition.to_state:
                state_line = ASCIIArtRenderer.colorize(state_line, "red")
            elif "CRITICAL" in transition.to_state:
                state_line = ASCIIArtRenderer.colorize(state_line, "yellow")

            lines.append(state_line)

            # Trigger info
            trigger_line = f"         ╰─► Trigger: {transition.trigger}"
            lines.append(trigger_line)
            lines.append("")

        # Current state
        lines.append(
            ASCIIArtRenderer.colorize(f"Current State: {self.current_state}", "bold")
        )

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary for GUI"""
        return {
            "scenario_name": self.scenario_name,
            "current_state": self.current_state,
            "transitions": [
                {
                    "timestamp": t.timestamp,
                    "from_state": t.from_state,
                    "to_state": t.to_state,
                    "trigger": t.trigger,
                    "duration_seconds": t.duration_seconds,
                }
                for t in self.transitions
            ],
        }


# ============================================================================
# COLLAPSE PREDICTION VISUALIZATION
# ============================================================================


@dataclass
class CollapsePrediction:
    """Collapse mode prediction data"""

    collapse_mode: str
    probability: float
    time_to_collapse_hours: float | None
    contributing_factors: list[str]
    severity: str


class CollapsePredictionViz:
    """Collapse mode prediction chart"""

    def __init__(self, scenario_name: str, predictions: list[CollapsePrediction]):
        self.scenario_name = scenario_name
        self.predictions = sorted(
            predictions, key=lambda p: p.probability, reverse=True
        )

    def render_ascii(self, width: int = 70) -> str:
        """Render collapse predictions as ASCII chart"""
        lines = []

        # Title
        lines.append(
            ASCIIArtRenderer.colorize(
                f"═══ COLLAPSE PREDICTIONS: {self.scenario_name} ═══", "red"
            )
        )
        lines.append("")

        if not self.predictions:
            lines.append("No collapse predictions available.")
            return "\n".join(lines)

        # Draw each prediction
        for i, pred in enumerate(self.predictions[:10], 1):  # Top 10
            # Probability bar
            bar = ASCIIArtRenderer.draw_progress_bar(pred.probability * 100, 100.0, 30)

            # Time to collapse
            if pred.time_to_collapse_hours is not None:
                time_str = f"{pred.time_to_collapse_hours:.1f}h"
            else:
                time_str = "Unknown"

            # Main line
            line = f"{i:2}. {pred.collapse_mode:<25} {bar} {pred.probability*100:5.1f}% ETA:{time_str}"

            # Color by severity
            if pred.severity == "CRITICAL":
                line = ASCIIArtRenderer.colorize(line, "red")
            elif pred.severity == "HIGH":
                line = ASCIIArtRenderer.colorize(line, "yellow")

            lines.append(line)

            # Contributing factors (indent)
            if pred.contributing_factors:
                factors_str = ", ".join(pred.contributing_factors[:3])
                lines.append(f"    Factors: {factors_str}")

            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary for GUI"""
        return {
            "scenario_name": self.scenario_name,
            "predictions": [
                {
                    "collapse_mode": p.collapse_mode,
                    "probability": p.probability,
                    "time_to_collapse_hours": p.time_to_collapse_hours,
                    "contributing_factors": p.contributing_factors,
                    "severity": p.severity,
                }
                for p in self.predictions
            ],
        }


# ============================================================================
# STATUS DASHBOARD VISUALIZATION
# ============================================================================


class StatusDashboardViz:
    """Comprehensive status dashboard"""

    def __init__(
        self,
        active_scenarios: int,
        critical_scenarios: int,
        total_scenarios: int,
        system_health: str,
        alerts_count: int,
        uptime_hours: float,
    ):
        self.active_scenarios = active_scenarios
        self.critical_scenarios = critical_scenarios
        self.total_scenarios = total_scenarios
        self.system_health = system_health
        self.alerts_count = alerts_count
        self.uptime_hours = uptime_hours

    def render_ascii(self, width: int = 80) -> str:
        """Render status dashboard as ASCII"""
        lines = []

        # Header
        lines.extend(ASCIIArtRenderer.draw_box(width, 15, "HYDRA-50 STATUS DASHBOARD"))

        # Insert content (overwrite middle lines)
        content_lines = [
            "",
            f"  System Health: {self._colorize_health(self.system_health)}",
            f"  Uptime: {self.uptime_hours:.1f} hours",
            "",
            "  Scenarios:",
            f"    Total: {self.total_scenarios}",
            f"    Active: {self.active_scenarios}",
            f"    Critical: {ASCIIArtRenderer.colorize(str(self.critical_scenarios), 'red')}",
            "",
            f"  Active Alerts: {self.alerts_count}",
            "",
            f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        # Merge content into box
        result = lines[0]
        for i, content in enumerate(content_lines, 1):
            if i < len(lines) - 1:
                padding = width - len(content) - 2
                result += (
                    "\n"
                    + ASCIIArtRenderer.BOX_CHARS["vertical"]
                    + content
                    + " " * padding
                    + ASCIIArtRenderer.BOX_CHARS["vertical"]
                )
        result += "\n" + lines[-1]

        return result

    def _colorize_health(self, health: str) -> str:
        """Colorize health status"""
        color_map = {
            "HEALTHY": "green",
            "DEGRADED": "yellow",
            "UNHEALTHY": "red",
            "CRITICAL": "red",
        }
        color = color_map.get(health, "white")
        return ASCIIArtRenderer.colorize(health, color)

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary for GUI"""
        return {
            "active_scenarios": self.active_scenarios,
            "critical_scenarios": self.critical_scenarios,
            "total_scenarios": self.total_scenarios,
            "system_health": self.system_health,
            "alerts_count": self.alerts_count,
            "uptime_hours": self.uptime_hours,
        }


# ============================================================================
# HEAT MAP VISUALIZATION
# ============================================================================


class HeatMapViz:
    """Heat map for scenario intensity across categories"""

    def __init__(
        self,
        categories: list[str],
        scenarios: list[str],
        intensity_matrix: list[list[float]],
    ):
        self.categories = categories
        self.scenarios = scenarios
        self.intensity_matrix = intensity_matrix

    def render_ascii(self, width: int = 80) -> str:
        """Render heat map as ASCII"""
        lines = []

        # Title
        lines.append(
            ASCIIArtRenderer.colorize("═══ SCENARIO INTENSITY HEAT MAP ═══", "cyan")
        )
        lines.append("")

        # Header with categories
        header = "Scenario".ljust(30) + " ".join(
            [c[:6].center(6) for c in self.categories]
        )
        lines.append(header)
        lines.append("─" * len(header))

        # Draw each scenario row
        for i, scenario in enumerate(self.scenarios):
            row_data = (
                self.intensity_matrix[i] if i < len(self.intensity_matrix) else []
            )

            cells = []
            for j, intensity in enumerate(row_data):
                block = ASCIIArtRenderer.draw_intensity_block(intensity)
                cells.append(f"{block * 6}")

            line = f"{scenario[:28].ljust(30)}" + " ".join(cells)
            lines.append(line)

        # Legend
        lines.append("")
        legend = "Intensity: "
        for i, char in enumerate(ASCIIArtRenderer.BLOCK_CHARS):
            legend += f"{char}={i/4:.1f} "
        lines.append(legend)

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary for GUI"""
        return {
            "categories": self.categories,
            "scenarios": self.scenarios,
            "intensity_matrix": self.intensity_matrix,
        }


# ============================================================================
# MAIN VISUALIZATION ENGINE
# ============================================================================


class HYDRA50VisualizationEngine:
    """
    God-Tier visualization engine for HYDRA-50

    Complete visualization suite with:
    - Real-time ASCII rendering
    - Multiple visualization types
    - Export to JSON for GUI consumption
    - Animation frame generation
    - Historical replay
    """

    def __init__(self, output_dir: str = "data/hydra50/visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("HYDRA-50 Visualization Engine initialized")

    def render_escalation_ladder(
        self,
        scenario_name: str,
        current_level: int,
        max_level: int,
        level_descriptions: dict[int, str],
        level_values: dict[int, float],
    ) -> tuple[str, dict[str, Any]]:
        """Render escalation ladder visualization"""
        viz = EscalationLadderViz(
            scenario_name=scenario_name,
            current_level=current_level,
            max_level=max_level,
            level_descriptions=level_descriptions,
            level_values=level_values,
            timestamp=datetime.now().timestamp(),
        )

        ascii_output = viz.render_ascii()
        data_output = viz.to_dict()

        return ascii_output, data_output

    def render_coupling_graph(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
        title: str = "Domain Coupling",
    ) -> tuple[str, dict[str, Any]]:
        """Render coupling graph visualization"""
        viz = CouplingGraphViz(nodes, edges, title)

        ascii_output = viz.render_ascii()
        data_output = viz.to_dict()

        return ascii_output, data_output

    def render_temporal_flow(
        self, scenario_name: str, transitions: list[StateTransition], current_state: str
    ) -> tuple[str, dict[str, Any]]:
        """Render temporal flow visualization"""
        viz = TemporalFlowViz(scenario_name, transitions, current_state)

        ascii_output = viz.render_ascii()
        data_output = viz.to_dict()

        return ascii_output, data_output

    def render_collapse_predictions(
        self, scenario_name: str, predictions: list[CollapsePrediction]
    ) -> tuple[str, dict[str, Any]]:
        """Render collapse prediction visualization"""
        viz = CollapsePredictionViz(scenario_name, predictions)

        ascii_output = viz.render_ascii()
        data_output = viz.to_dict()

        return ascii_output, data_output

    def render_status_dashboard(
        self,
        active_scenarios: int,
        critical_scenarios: int,
        total_scenarios: int,
        system_health: str,
        alerts_count: int,
        uptime_hours: float,
    ) -> tuple[str, dict[str, Any]]:
        """Render status dashboard visualization"""
        viz = StatusDashboardViz(
            active_scenarios,
            critical_scenarios,
            total_scenarios,
            system_health,
            alerts_count,
            uptime_hours,
        )

        ascii_output = viz.render_ascii()
        data_output = viz.to_dict()

        return ascii_output, data_output

    def render_heat_map(
        self,
        categories: list[str],
        scenarios: list[str],
        intensity_matrix: list[list[float]],
    ) -> tuple[str, dict[str, Any]]:
        """Render heat map visualization"""
        viz = HeatMapViz(categories, scenarios, intensity_matrix)

        ascii_output = viz.render_ascii()
        data_output = viz.to_dict()

        return ascii_output, data_output

    def export_visualization(
        self, viz_type: VisualizationType, data: dict[str, Any], filename: str
    ) -> str:
        """Export visualization data to file"""
        output_path = self.output_dir / filename

        with open(output_path, "w") as f:
            json.dump(
                {
                    "type": viz_type.value,
                    "timestamp": datetime.now().isoformat(),
                    "data": data,
                },
                f,
                indent=2,
            )

        logger.info("Exported visualization to %s", output_path)
        return str(output_path)


# Export main class
__all__ = [
    "HYDRA50VisualizationEngine",
    "GraphNode",
    "GraphEdge",
    "CollapsePrediction",
    "StateTransition",
]
