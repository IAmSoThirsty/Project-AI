"""
Project-AI CLI — Production-grade command-line interface.

Wires Typer command groups to real core module APIs:
  user     → UserManager
  memory   → MemoryExpansionSystem
  learning → LearningRequestManager
  plugin   → PluginManager
  system   → governance / security subsystems
  ai       → AIPersona / FourLaws
  health   → HealthReporter / AuditLog  (already implemented)

STATUS: PRODUCTION
"""

import json
import logging

import typer

# Version information
__version__ = "1.0.0"


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"Project-AI CLI v{__version__}")
        raise typer.Exit()


app = typer.Typer(help="Project-AI Command Line Interface (CLI)")


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    Project-AI CLI - A comprehensive AI assistant platform.

    Run commands with --help for detailed information.
    """
    pass


# ============================================================================
# User Command Group  →  UserManager
# ============================================================================
user_app = typer.Typer(help="Commands for user management.")


@user_app.command(name="list")
def user_list():
    """List all registered users."""
    try:
        from app.core.user_manager import UserManager

        mgr = UserManager()
        users = mgr.list_users()

        if not users:
            typer.echo("No users found. Use 'user create' to add one.")
            return

        typer.echo(f"{'Username':<20} {'Role':<12} {'Persona':<12} {'Approved'}")
        typer.echo("-" * 60)
        for uname, udata in users.items():
            role = udata.get("role", "user")
            persona = udata.get("persona", "friendly")
            approved = "✓" if udata.get("approved", False) else "✗"
            typer.echo(f"{uname:<20} {role:<12} {persona:<12} {approved}")
        typer.echo(f"\nTotal: {len(users)} user(s)")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@user_app.command(name="info")
def user_info(
    username: str = typer.Argument(..., help="Username to look up."),
):
    """Show detailed information for a specific user."""
    try:
        from app.core.user_manager import UserManager

        mgr = UserManager()
        data = mgr.get_user_data(username)

        if not data:
            typer.echo(f"✗ User '{username}' not found.")
            raise typer.Exit(code=1)

        typer.echo(f"User: {username}")
        typer.echo("-" * 40)
        for key, value in data.items():
            typer.echo(f"  {key}: {value}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@user_app.command(name="create")
def user_create(
    username: str = typer.Argument(..., help="Username to create."),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="User password."
    ),
    role: str = typer.Option("user", help="User role (user/admin)."),
    persona: str = typer.Option("friendly", help="AI persona style for this user."),
):
    """Create a new user account."""
    try:
        from app.core.user_manager import UserManager

        mgr = UserManager()
        success = mgr.create_user(username, password, persona=persona)

        if not success:
            typer.echo(f"✗ User '{username}' already exists.")
            raise typer.Exit(code=1)

        # Update role if not default
        if role != "user":
            mgr.update_user(username, role=role)

        typer.echo(f"✓ User '{username}' created (role={role}, persona={persona}).")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@user_app.command(name="delete")
def user_delete(
    username: str = typer.Argument(..., help="Username to delete."),
    force: bool = typer.Option(
        False, "--force", "-f", help="Skip confirmation prompt."
    ),
):
    """Delete a user account."""
    try:
        from app.core.user_manager import UserManager

        mgr = UserManager()

        # Check user exists first
        if not mgr.get_user_data(username):
            typer.echo(f"✗ User '{username}' not found.")
            raise typer.Exit(code=1)

        if not force:
            confirm = typer.confirm(f"Delete user '{username}'? This cannot be undone")
            if not confirm:
                typer.echo("Aborted.")
                return

        success = mgr.delete_user(username)
        if success:
            typer.echo(f"✓ User '{username}' deleted.")
        else:
            typer.echo(f"✗ Failed to delete user '{username}'.")
            raise typer.Exit(code=1)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


app.add_typer(user_app, name="user")


# ============================================================================
# Health Command Group  (already implemented — preserved as-is)
# ============================================================================
health_app = typer.Typer(help="Commands for system health reporting and diagnostics.")


@health_app.command(name="report")
def health_report(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    )
):
    """Generate a comprehensive system health report with YAML snapshot and PNG visualization."""
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    typer.echo("=" * 60)
    typer.echo("Project-AI System Health Reporter")
    typer.echo("=" * 60)
    typer.echo()

    try:
        from app.health.report import HealthReporter

        reporter = HealthReporter()
        success, snapshot_path, report_path = reporter.generate_full_report()

        if success:
            typer.echo("✓ Health report generated successfully!")
            typer.echo()
            typer.echo(f"  Snapshot: {snapshot_path}")
            typer.echo(f"  Report:   {report_path}")
            typer.echo()

            # Verify audit log chain
            is_valid, message = reporter.audit_log.verify_chain()
            if is_valid:
                typer.echo(f"✓ Audit log chain verified: {message}")
            else:
                typer.echo(f"⚠ Audit log chain verification failed: {message}")
        else:
            typer.echo("✗ Health report generation failed!")
            typer.echo("  Check logs for details.")
            raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        if verbose:
            import traceback

            typer.echo(traceback.format_exc())
        raise typer.Exit(code=1) from e

    typer.echo()
    typer.echo("=" * 60)


@health_app.command(name="verify-audit")
def verify_audit():
    """Verify the integrity of the audit log chain."""
    try:
        from app.governance.audit_log import AuditLog

        audit = AuditLog()
        is_valid, message = audit.verify_chain()

        if is_valid:
            typer.echo(f"✓ Audit log chain verified: {message}")
        else:
            typer.echo(f"✗ Audit log verification failed: {message}")
            raise typer.Exit(code=1)

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


app.add_typer(health_app, name="health")


# ============================================================================
# Memory Command Group  →  MemoryExpansionSystem
# ============================================================================
memory_app = typer.Typer(help="Commands for memory operations.")


@memory_app.command(name="store")
def memory_store(
    category: str = typer.Argument(
        ..., help="Knowledge category (e.g. 'facts', 'preferences')."
    ),
    key: str = typer.Argument(..., help="Knowledge key/topic."),
    value: str = typer.Argument(..., help="Knowledge content to store."),
):
    """Store knowledge in the AI memory system."""
    try:
        from app.core.ai_systems import MemoryExpansionSystem

        mem = MemoryExpansionSystem()
        mem.add_knowledge(category, key, value)
        typer.echo(f"✓ Stored: [{category}] {key}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@memory_app.command(name="recall")
def memory_recall(
    query: str = typer.Argument(..., help="Search query."),
    category: str = typer.Option(None, "--category", "-c", help="Filter by category."),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results."),
):
    """Search the AI knowledge base."""
    try:
        from app.core.ai_systems import MemoryExpansionSystem

        mem = MemoryExpansionSystem()
        results = mem.query_knowledge(query, category=category, limit=limit)

        if not results:
            typer.echo(f"No results found for '{query}'.")
            return

        typer.echo(f"Found {len(results)} result(s) for '{query}':\n")
        for i, result in enumerate(results, 1):
            cat = result.get("category", "?")
            key = result.get("key", "?")
            val = result.get("value", "")
            # Truncate long values for display
            display_val = str(val)[:120] + ("…" if len(str(val)) > 120 else "")
            typer.echo(f"  {i}. [{cat}] {key}: {display_val}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@memory_app.command(name="list")
def memory_list_categories():
    """List all knowledge categories."""
    try:
        from app.core.ai_systems import MemoryExpansionSystem

        mem = MemoryExpansionSystem()
        categories = mem.get_all_categories()

        if not categories:
            typer.echo("No knowledge categories found.")
            return

        typer.echo("Knowledge categories:")
        for cat in sorted(categories):
            summary = mem.get_category_summary(cat)
            entry_count = summary.get("entry_count", "?") if summary else "?"
            typer.echo(f"  • {cat} ({entry_count} entries)")
        typer.echo(f"\nTotal: {len(categories)} category(ies)")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@memory_app.command(name="stats")
def memory_stats():
    """Show memory system statistics."""
    try:
        from app.core.ai_systems import MemoryExpansionSystem

        mem = MemoryExpansionSystem()
        stats = mem.get_statistics()

        typer.echo("Memory System Statistics")
        typer.echo("-" * 40)
        for key, value in stats.items():
            typer.echo(f"  {key}: {value}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


app.add_typer(memory_app, name="memory")


# ============================================================================
# Learning Command Group  →  LearningRequestManager
# ============================================================================
learning_app = typer.Typer(help="Commands for managing AI learning requests.")


@learning_app.command(name="request")
def learning_request(
    topic: str = typer.Argument(..., help="Learning topic."),
    description: str = typer.Argument(..., help="What the AI should learn."),
    priority: str = typer.Option(
        "medium", "--priority", "-p", help="Priority: low, medium, high."
    ),
):
    """Submit a new learning request for AI review."""
    try:
        from app.core.ai_systems import LearningRequestManager, RequestPriority

        priority_map = {
            "low": RequestPriority.LOW,
            "medium": RequestPriority.MEDIUM,
            "high": RequestPriority.HIGH,
        }
        prio = priority_map.get(priority.lower(), RequestPriority.MEDIUM)

        mgr = LearningRequestManager()
        req_id = mgr.create_request(topic, description, priority=prio)

        if req_id:
            typer.echo(f"✓ Learning request created: {req_id}")
            typer.echo(f"  Topic: {topic}")
            typer.echo(f"  Priority: {priority}")
        else:
            typer.echo("✗ Failed to create request (topic may be blocked).")
            raise typer.Exit(code=1)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@learning_app.command(name="list")
def learning_list(
    status: str = typer.Option(
        "all", "--status", "-s", help="Filter: all, pending, approved, denied."
    ),
):
    """List learning requests."""
    try:
        from app.core.ai_systems import LearningRequestManager

        mgr = LearningRequestManager()

        if status.lower() == "pending":
            requests = {
                rid: r for rid, r in mgr.requests.items() if r["status"] == "pending"
            }
        elif status.lower() == "approved":
            requests = {
                rid: r for rid, r in mgr.requests.items() if r["status"] == "approved"
            }
        elif status.lower() == "denied":
            requests = {
                rid: r for rid, r in mgr.requests.items() if r["status"] == "denied"
            }
        else:
            requests = dict(mgr.requests)

        if not requests:
            typer.echo(f"No {status} learning requests found.")
            return

        typer.echo(f"{'ID':<14} {'Topic':<25} {'Priority':<10} {'Status'}")
        typer.echo("-" * 65)
        for rid, req in requests.items():
            topic = req.get("topic", "?")[:24]
            prio = req.get("priority", "?")
            st = req.get("status", "?")
            typer.echo(f"{rid:<14} {topic:<25} {prio:<10} {st}")
        typer.echo(f"\nTotal: {len(requests)} request(s)")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@learning_app.command(name="approve")
def learning_approve(
    request_id: str = typer.Argument(..., help="Request ID to approve."),
    response: str = typer.Option(
        "Approved via CLI", "--response", "-r", help="Approval response."
    ),
):
    """Approve a pending learning request."""
    try:
        from app.core.ai_systems import LearningRequestManager

        mgr = LearningRequestManager()
        success = mgr.approve_request(request_id, response)

        if success:
            typer.echo(f"✓ Request {request_id} approved.")
        else:
            typer.echo(f"✗ Request '{request_id}' not found.")
            raise typer.Exit(code=1)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@learning_app.command(name="deny")
def learning_deny(
    request_id: str = typer.Argument(..., help="Request ID to deny."),
    reason: str = typer.Option(
        ..., "--reason", "-r", prompt=True, help="Denial reason."
    ),
    vault: bool = typer.Option(True, help="Add content hash to black vault."),
):
    """Deny a pending learning request."""
    try:
        from app.core.ai_systems import LearningRequestManager

        mgr = LearningRequestManager()
        success = mgr.deny_request(request_id, reason, to_vault=vault)

        if success:
            typer.echo(f"✓ Request {request_id} denied.")
            if vault:
                typer.echo("  Content hash added to black vault.")
        else:
            typer.echo(f"✗ Request '{request_id}' not found.")
            raise typer.Exit(code=1)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


app.add_typer(learning_app, name="learning")


# ============================================================================
# Plugin Command Group  →  PluginManager
# ============================================================================
plugin_app = typer.Typer(help="Commands for managing plugins.")


@plugin_app.command(name="list")
def plugin_list():
    """List all loaded plugins and their status."""
    try:
        from app.core.ai_systems import PluginManager

        mgr = PluginManager()

        if not mgr.plugins:
            typer.echo("No plugins loaded.")
            return

        typer.echo(f"{'Name':<25} {'Version':<10} {'Enabled'}")
        typer.echo("-" * 50)
        for name, plugin in mgr.plugins.items():
            status = "✓" if plugin.enabled else "✗"
            typer.echo(f"{name:<25} {plugin.version:<10} {status}")

        stats = mgr.get_statistics()
        typer.echo(f"\nTotal: {stats['total']} plugin(s), {stats['enabled']} enabled")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@plugin_app.command(name="enable")
def plugin_enable(
    name: str = typer.Argument(..., help="Plugin name to enable."),
):
    """Enable a loaded plugin."""
    try:
        from app.core.ai_systems import PluginManager

        mgr = PluginManager()
        if name not in mgr.plugins:
            typer.echo(
                f"✗ Plugin '{name}' not found. Use 'plugin list' to see available plugins."
            )
            raise typer.Exit(code=1)

        mgr.plugins[name].enable()
        typer.echo(f"✓ Plugin '{name}' enabled.")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@plugin_app.command(name="disable")
def plugin_disable(
    name: str = typer.Argument(..., help="Plugin name to disable."),
):
    """Disable a loaded plugin."""
    try:
        from app.core.ai_systems import PluginManager

        mgr = PluginManager()
        if name not in mgr.plugins:
            typer.echo(f"✗ Plugin '{name}' not found.")
            raise typer.Exit(code=1)

        mgr.plugins[name].disable()
        typer.echo(f"✓ Plugin '{name}' disabled.")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@plugin_app.command(name="info")
def plugin_info(
    name: str = typer.Argument(..., help="Plugin name."),
):
    """Show detailed information about a plugin."""
    try:
        from app.core.ai_systems import PluginManager

        mgr = PluginManager()
        if name not in mgr.plugins:
            typer.echo(f"✗ Plugin '{name}' not found.")
            raise typer.Exit(code=1)

        plugin = mgr.plugins[name]
        typer.echo(f"Plugin: {plugin.name}")
        typer.echo("-" * 40)
        typer.echo(f"  Version: {plugin.version}")
        typer.echo(f"  Enabled: {'Yes' if plugin.enabled else 'No'}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


app.add_typer(plugin_app, name="plugin")


# ============================================================================
# System Command Group  →  governance / security subsystems
# ============================================================================
system_app = typer.Typer(help="Commands for system operations and governance.")


@system_app.command(name="status")
def system_status():
    """Show overall system status."""
    try:
        typer.echo("=" * 60)
        typer.echo("Project-AI System Status")
        typer.echo("=" * 60)
        typer.echo()

        # Memory stats
        try:
            from app.core.ai_systems import MemoryExpansionSystem

            mem = MemoryExpansionSystem()
            stats = mem.get_statistics()
            typer.echo("📝 Memory System")
            for k, v in stats.items():
                typer.echo(f"    {k}: {v}")
        except Exception as e:
            typer.echo(f"  📝 Memory: unavailable ({e})")

        typer.echo()

        # Learning stats
        try:
            from app.core.ai_systems import LearningRequestManager

            lrm = LearningRequestManager()
            stats = lrm.get_statistics()
            typer.echo("📚 Learning System")
            for k, v in stats.items():
                typer.echo(f"    {k}: {v}")
        except Exception as e:
            typer.echo(f"  📚 Learning: unavailable ({e})")

        typer.echo()

        # Plugin stats
        try:
            from app.core.ai_systems import PluginManager

            pm = PluginManager()
            stats = pm.get_statistics()
            typer.echo("🔌 Plugin System")
            for k, v in stats.items():
                typer.echo(f"    {k}: {v}")
        except Exception as e:
            typer.echo(f"  🔌 Plugins: unavailable ({e})")

        typer.echo()

        # Persona stats
        try:
            from app.core.ai_systems import AIPersona

            persona = AIPersona()
            stats = persona.get_statistics()
            typer.echo("🤖 AI Persona")
            typer.echo(f"    interactions: {stats.get('interactions', 0)}")
            typer.echo(f"    mood: {stats.get('mood', 'unknown')}")
        except Exception as e:
            typer.echo(f"  🤖 Persona: unavailable ({e})")

        typer.echo()
        typer.echo("=" * 60)

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@system_app.command(name="governance")
def system_governance():
    """Show governance framework status (Four Laws, TARL version)."""
    try:
        from app.core.ai_systems import FourLaws

        typer.echo("⚖️  Governance Framework")
        typer.echo("-" * 40)

        # Validate a no-op action to demonstrate the system is live
        result = FourLaws.validate_action("system_status_check")
        typer.echo(
            f"  Four Laws framework: {'✓ Active' if result.get('allowed', False) else '⚠ Restricted'}"
        )
        typer.echo(f"  Humanity-first principle: Active")
        typer.echo(f"  System version: {__version__}")

        typer.echo()
        typer.echo("  Law Hierarchy:")
        typer.echo("    0. Zeroth Law — Protect humanity as a whole")
        typer.echo("    1. First Law  — Serve all humans equally")
        typer.echo(
            "    2. Second Law — Obey bonded user (unless conflicts with Law 0/1)"
        )
        typer.echo(
            "    3. Third Law  — Self-preservation (unless conflicts with Law 0/1/2)"
        )

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@system_app.command(name="audit")
def system_audit(
    tail: int = typer.Option(
        10, "--tail", "-n", help="Number of recent entries to show."
    ),
):
    """Show recent audit log entries."""
    try:
        import os

        log_path = os.path.join("data", "security", "immutable_audit.log")
        if not os.path.exists(log_path):
            typer.echo("No audit log found.")
            return

        with open(log_path, encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            typer.echo("Audit log is empty.")
            return

        # Show the last N entries
        entries = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        recent = entries[-tail:]
        typer.echo(f"Audit Log (last {len(recent)} of {len(entries)} entries)")
        typer.echo("-" * 70)

        for entry in recent:
            ts = entry.get("timestamp", "?")
            etype = entry.get("type", "?")
            user = entry.get("user_id", "")
            ehash = entry.get("hash", "?")[:12]
            typer.echo(f"  {ts}  [{etype}]  user={user}  hash={ehash}…")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


app.add_typer(system_app, name="system")


# ============================================================================
# AI Command Group  →  AIPersona / FourLaws
# ============================================================================
ai_app = typer.Typer(help="Commands for AI persona and reasoning.")


@ai_app.command(name="persona")
def ai_persona():
    """Show current AI persona traits and mood."""
    try:
        from app.core.ai_systems import AIPersona

        persona = AIPersona()
        stats = persona.get_statistics()

        typer.echo("🤖 AI Persona State")
        typer.echo("-" * 40)
        typer.echo(f"  Mood: {stats.get('mood', 'unknown')}")
        typer.echo(f"  Total interactions: {stats.get('interactions', 0)}")
        typer.echo()

        personality = stats.get("personality", {})
        if personality:
            typer.echo("  Personality Traits:")
            for trait, value in sorted(personality.items()):
                bar_len = int(value * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                typer.echo(f"    {trait:<16} {bar} {value:.2f}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@ai_app.command(name="adjust")
def ai_adjust_trait(
    trait: str = typer.Argument(
        ..., help="Personality trait name (e.g. creativity, empathy)."
    ),
    delta: float = typer.Argument(..., help="Adjustment amount (-1.0 to 1.0)."),
):
    """Adjust an AI personality trait."""
    try:
        from app.core.ai_systems import AIPersona

        if not -1.0 <= delta <= 1.0:
            typer.echo("✗ Delta must be between -1.0 and 1.0.")
            raise typer.Exit(code=1)

        persona = AIPersona()

        if trait not in persona.personality:
            available = ", ".join(sorted(persona.personality.keys()))
            typer.echo(f"✗ Unknown trait '{trait}'. Available: {available}")
            raise typer.Exit(code=1)

        old_val = persona.personality[trait]
        persona.adjust_trait(trait, delta)
        new_val = persona.personality[trait]

        typer.echo(f"✓ Trait '{trait}' adjusted: {old_val:.2f} → {new_val:.2f}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@ai_app.command(name="validate")
def ai_validate(
    action: str = typer.Argument(
        ..., help="Action description to validate against Four Laws."
    ),
):
    """Validate an action against the Four Laws framework."""
    try:
        from app.core.ai_systems import FourLaws

        result = FourLaws.validate_action(action)

        allowed = result.get("allowed", False)
        reason = result.get("reason", "No reason provided.")

        if allowed:
            typer.echo(f"✓ Action ALLOWED: {action}")
        else:
            typer.echo(f"✗ Action BLOCKED: {action}")

        typer.echo(f"  Reason: {reason}")

        # Show any additional validation details
        for key, value in result.items():
            if key not in ("allowed", "reason"):
                typer.echo(f"  {key}: {value}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


@ai_app.command(name="chat")
def ai_chat(
    message: str = typer.Argument(..., help="Message to send to the AI."),
):
    """Send a message through the AI persona system."""
    try:
        from app.core.ai_systems import AIPersona, MemoryExpansionSystem

        persona = AIPersona()
        mem = MemoryExpansionSystem()

        # Log the interaction
        persona.update_conversation_state(is_user=True)

        # Generate a persona-aware response
        stats = persona.get_statistics()
        mood = stats.get("mood", "neutral")

        # Simple response framing based on mood & personality
        creativity = persona.personality.get("creativity", 0.5)
        empathy = persona.personality.get("empathy", 0.5)

        typer.echo(
            f"[Persona mood: {mood} | creativity: {creativity:.1f} | empathy: {empathy:.1f}]"
        )
        typer.echo()
        typer.echo(f"You: {message}")
        typer.echo()

        # Log the conversation
        ai_response = (
            f"Acknowledged your message (mood={mood}). "
            f"Full AI response generation requires an LLM backend. "
            f"This CLI processes persona traits and logs the interaction."
        )
        mem.log_conversation(message, ai_response)
        persona.update_conversation_state(is_user=False)

        typer.echo(f"AI: {ai_response}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}")
        raise typer.Exit(code=1) from e


app.add_typer(ai_app, name="ai")

if __name__ == "__main__":
    app()
