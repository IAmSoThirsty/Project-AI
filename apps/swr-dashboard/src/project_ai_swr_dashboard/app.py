"""SOVEREIGN WAR ROOM - Web Dashboard (J3.8 port).

Flask web interface for viewing SWR scenarios, results, and
leaderboards. The dashboard is view-only; writes go through the CLI
(`swr.cli`) or the FastAPI gateway (`packages.api`).

Architectural differences from the legacy port (legacy was at
``engines/sovereign_war_room/web/app.py``):

- Targets ``WarRoomCore`` (the J6.1 facade) instead of the legacy
  ``SovereignWarRoom``. WarRoomCore exposes the same ``load_scenarios``,
  ``scoreboard``, ``proof_system``, ``governance`` surface that the
  routes need.
- Uses a lazy ``get_swr()`` factory with a default allow-all governed
  stack (same shape as ``swr.cli.get_swr()``). The legacy module-level
  ``swr = SovereignWarRoom()`` would import the governance stack at
  module load, which breaks testability and circular-import safety.
- No ``sys.path`` insertion — workspace package import only.
- The HTML/CSS/JS template is the legacy template verbatim; the
  user-authored UI is not touched.
- The legacy ``audit_entries`` stat field is dropped from ``/api/stats``
  because the canonical WarRoomCore does not expose a single
  ``audit_log`` attribute (the audit log lives in
  ``governance.audit_log`` and is a different shape). Dropping it
  keeps the API surface honest; the other 4 stat fields are 1:1.
"""

from __future__ import annotations

from typing import Any

from flask import Flask, jsonify, render_template, request
from swr.core import scenario_to_dict

from swr import WarRoomCore


def get_swr() -> WarRoomCore:
    """Create a fresh WarRoomCore with a default governed stack.

    Mirrors ``swr.cli.get_swr()`` so the dashboard, the CLI, and the
    FastAPI gateway all construct identical default stacks.

    The default policy is allow-all (no deny rules) so the dashboard
    can read freely; result recording through the gate is still
    governed, but reading via the dashboard's API routes does not
    invoke the gate.
    """
    from capability import CapabilityAuthority
    from execution import ExecutionGate
    from governance import GovernanceEngine, RuleGovernor
    from kernel import EventSpine

    governance = GovernanceEngine(
        policy_version="swr-dashboard-v1",
        governors=(RuleGovernor("swr-dashboard", ()),),
    )
    capabilities = CapabilityAuthority(
        b"0" * 32,  # 32-byte secret for capability authority
        issuer="swr-dashboard",
    )
    execution = ExecutionGate(
        governance=governance,
        capabilities=capabilities,
        events=EventSpine(),
    )
    return WarRoomCore(execution=execution, capabilities=capabilities)


def create_app() -> Flask:
    """Flask app factory.

    Builds the dashboard with a fresh ``WarRoomCore`` per app instance
    (the legacy module-level singleton would survive across tests and
    leak state; a factory keeps each app self-contained).
    """
    app = Flask(__name__)
    swr = get_swr()

    @app.route("/")
    def index() -> str:
        """Main dashboard."""
        return render_template("dashboard.html")

    @app.route("/api/scenarios")
    def api_scenarios() -> Any:
        """Get scenarios."""
        round_num = request.args.get("round", type=int)
        scenarios = swr.load_scenarios(round_num)
        return jsonify({"scenarios": [scenario_to_dict(s) for s in scenarios]})

    @app.route("/api/leaderboard")
    def api_leaderboard() -> Any:
        """Get leaderboard."""
        limit = request.args.get("limit", default=10, type=int)
        leaderboard = swr.scoreboard.get_leaderboard(limit)
        return jsonify({"leaderboard": leaderboard})

    @app.route("/api/results")
    def api_results() -> Any:
        """Get results."""
        system_id = request.args.get("system_id")
        round_num = request.args.get("round", type=int)
        results = swr.get_results(system_id, round_num)
        return jsonify({"results": results})

    @app.route("/api/systems/<system_id>/performance")
    def api_system_performance(system_id: str) -> Any:
        """Get system performance."""
        perf = swr.scoreboard.get_system_performance(system_id)
        return jsonify(perf)

    @app.route("/api/stats")
    def api_stats() -> Any:
        """Get overall statistics."""
        return jsonify(
            {
                "total_scenarios": len(swr.active_scenarios),
                "total_results": len(swr.results),
                "total_systems": len(swr.scoreboard.system_stats),
                "total_proofs": len(swr.proof_system.proof_store),
            }
        )

    return app


def entrypoint() -> None:
    """Console-script entry point (``project-ai-swr-dashboard``)."""
    swr = get_swr()
    # Pre-load all scenarios on startup so the dashboard's first
    # request has a populated state.
    swr.load_scenarios()

    print("🎯 SOVEREIGN WAR ROOM Dashboard")
    print("📊 Navigate to: http://localhost:5000")
    print("⚡ Press Ctrl+C to stop\n")

    create_app().run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    entrypoint()
