"""
SOVEREIGN WAR ROOM - Web Dashboard

Flask web interface for viewing scenarios, results, and leaderboards.
"""

import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swr import SovereignWarRoom

app = Flask(__name__)
swr = SovereignWarRoom()


@app.route("/")
def index():
    """Main dashboard."""
    return render_template("dashboard.html")


@app.route("/api/scenarios")
def api_scenarios():
    """Get scenarios."""
    round_num = request.args.get("round", type=int)
    scenarios = swr.load_scenarios(round_num)
    return jsonify({
        "scenarios": [s.model_dump() for s in scenarios]
    })


@app.route("/api/leaderboard")
def api_leaderboard():
    """Get leaderboard."""
    limit = request.args.get("limit", default=10, type=int)
    leaderboard = swr.scoreboard.get_leaderboard(limit)
    return jsonify({"leaderboard": leaderboard})


@app.route("/api/results")
def api_results():
    """Get results."""
    system_id = request.args.get("system_id")
    round_num = request.args.get("round", type=int)
    results = swr.get_results(system_id, round_num)
    return jsonify({"results": results})


@app.route("/api/systems/<system_id>/performance")
def api_system_performance(system_id):
    """Get system performance."""
    perf = swr.scoreboard.get_system_performance(system_id)
    return jsonify(perf)


@app.route("/api/stats")
def api_stats():
    """Get overall statistics."""
    return jsonify({
        "total_scenarios": len(swr.active_scenarios),
        "total_results": len(swr.results),
        "total_systems": len(swr.scoreboard.system_stats),
        "total_proofs": len(swr.proof_system.proof_store),
        "audit_entries": len(swr.governance.audit_log)
    })


if __name__ == "__main__":
    # Load all scenarios on startup
    swr.load_scenarios()

    print("🎯 SOVEREIGN WAR ROOM Dashboard")
    print("📊 Navigate to: http://localhost:5000")
    print("⚡ Press Ctrl+C to stop\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
