"""Registry dependency graph — plain text only."""

from __future__ import annotations

from taar.registry import Registry


def build_registry_graph(registry: Registry) -> dict[str, list[tuple[str, str]]]:
    return {
        "reader_writer": registry.reader_writer_edges,
        "watcher": registry.watcher_edges,
        "task_capability": sorted(
            (task.id, cap)
            for task in registry.tasks_by_id.values()
            for cap in task.required_capabilities
        ),
        "task_schedule": sorted(
            (task.id, task.schedule_id) for task in registry.tasks_by_id.values()
        ),
        "agent_command": sorted(
            (agent.id, command)
            for agent in registry.agents_by_id.values()
            for command in agent.allowed_commands
        ),
    }


def render_graph_text(registry: Registry) -> str:
    graph = build_registry_graph(registry)
    lines: list[str] = ["# TAAR Registry Graph", "", "## reader -> writer"]
    lines += [f"  {a} -> {b}" for a, b in graph["reader_writer"]] or ["  (none)"]
    lines += ["", "## watcher -> watched"]
    lines += [f"  {a} -> {b}" for a, b in graph["watcher"]] or ["  (none)"]
    lines += ["", "## task -> capability"]
    lines += [f"  {a} -> {b}" for a, b in graph["task_capability"]]
    lines += ["", "## task -> schedule"]
    lines += [f"  {a} -> {b}" for a, b in graph["task_schedule"]]
    lines += ["", "## agent -> command"]
    lines += [f"  {a} -> {b}" for a, b in graph["agent_command"]]
    return "\n".join(lines)
