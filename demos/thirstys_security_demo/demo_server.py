#!/usr/bin/env python3
"""
Thirsty's Asymmetric Security Framework - Demo Server
Minimal Flask server for demonstrating the framework
"""

import json
from datetime import datetime

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mock responses for standalone demo
SCENARIOS = {
    "privilege_escalation": {
        "name": "Privilege Escalation Without MFA",
        "input": {
            "action": "escalate_privileges",
            "context": {
                "user_id": "attacker_001",
                "current_privilege": "user",
                "target_privilege": "admin",
                "mfa_verified": False,
            },
        },
        "result": {
            "allowed": False,
            "failure_reason": "Constitutional violation: privilege_escalation_approval",
            "violations": ["privilege_escalation_approval"],
            "rfi_score": 0.25,
            "threat_level": "HIGH",
            "actions_taken": ["HALT", "SNAPSHOT", "ESCALATE"],
        },
    },
    "cross_tenant": {
        "name": "Cross-Tenant Data Access",
        "input": {
            "action": "read_data",
            "context": {
                "user_tenant": "tenant_a",
                "target_tenant": "tenant_b",
                "authorization": None,
            },
        },
        "result": {
            "allowed": False,
            "failure_reason": "Constitutional violation: cross_tenant_authorization",
            "violations": ["cross_tenant_authorization"],
            "rfi_score": 0.30,
            "threat_level": "HIGH",
        },
    },
    "trust_score": {
        "name": "Trust Score Manipulation",
        "input": {
            "action": "modify_trust_score",
            "context": {"user_id": "user_001", "new_score": 1.0, "justification": None},
        },
        "result": {
            "allowed": False,
            "failure_reason": "Constitutional violation: modify_trust_score",
            "violations": ["modify_trust_score"],
            "rfi_score": 0.40,
            "threat_level": "MEDIUM",
        },
    },
    "clock_skew": {
        "name": "Clock Skew Exploitation",
        "input": {
            "action": "timed_action",
            "context": {
                "system_time": "2026-02-08T06:00:00Z",
                "actual_time": "2026-02-08T05:50:00Z",
                "skew_minutes": 10,
            },
        },
        "result": {
            "allowed": False,
            "failure_reason": "Temporal anomaly detected: 10-minute clock skew",
            "temporal_anomaly": True,
            "rfi_score": 0.20,
            "threat_level": "CRITICAL",
        },
    },
    "combined": {
        "name": "Combined Multi-Stage Attack",
        "input": {
            "stages": [
                {"action": "manipulate_clock"},
                {"action": "escalate_privileges"},
                {"action": "access_cross_tenant"},
            ]
        },
        "result": {
            "allowed": False,
            "failure_reason": "Multiple violations: temporal_anomaly, privilege_escalation, cross_tenant",
            "violations": [
                "temporal_anomaly",
                "privilege_escalation_approval",
                "cross_tenant_authorization",
            ],
            "blocked_at_stage": 1,
            "rfi_score": 0.15,
            "threat_level": "CRITICAL",
        },
    },
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Thirsty's Asymmetric Security Demo</title>
    <style>
        body { font-family: 'Courier New', monospace; max-width: 1200px; margin: 0 auto; padding: 20px; background: #0a0a0a; color: #00ff00; }
        h1 { color: #00ffff; text-align: center; border-bottom: 2px solid #00ffff; padding-bottom: 10px; }
        .scenario { background: #1a1a1a; border: 1px solid #00ff00; margin: 15px 0; padding: 15px; border-radius: 5px; }
        .scenario h3 { color: #00ffff; margin-top: 0; }
        button { background: #00ff00; color: #000; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; border-radius: 3px; }
        button:hover { background: #00ffff; }
        .result { background: #0a0a0a; border-left: 3px solid #ff0000; padding: 10px; margin-top: 10px; }
        .blocked { color: #ff0000; font-weight: bold; }
        .allowed { color: #00ff00; font-weight: bold; }
        pre { background: #000; padding: 10px; border-radius: 3px; overflow-x: auto; }
        .header { text-align: center; padding: 20px 0; }
        .tagline { color: #888; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ THIRSTY'S ASYMMETRIC SECURITY FRAMEWORK</h1>
        <p class="tagline">"Making exploitation structurally unfinishable"</p>
    </div>

    <div id="scenarios"></div>

    <script>
        const scenarios = {{scenarios_json|safe}};

        function executeAttack(scenarioId) {
            fetch('/api/execute/' + scenarioId, {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    const resultDiv = document.getElementById('result-' + scenarioId);
                    const status = data.result.allowed ? 'ALLOWED' : 'BLOCKED';
                    const statusClass = data.result.allowed ? 'allowed' : 'blocked';

                    resultDiv.innerHTML = `
                        <h4>Result: <span class="${statusClass}">${status}</span></h4>
                        <p><strong>Reason:</strong> ${data.result.failure_reason || 'N/A'}</p>
                        <p><strong>RFI Score:</strong> ${data.result.rfi_score} (${data.result.rfi_score < 0.5 ? 'HIGH REUSABILITY' : 'LOW REUSABILITY'})</p>
                        <p><strong>Threat Level:</strong> ${data.result.threat_level || 'N/A'}</p>
                        ${data.result.violations ? '<p><strong>Violations:</strong> ' + data.result.violations.join(', ') + '</p>' : ''}
                        <details>
                            <summary>Full Response JSON</summary>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </details>
                    `;
                });
        }

        function renderScenarios() {
            const container = document.getElementById('scenarios');
            Object.keys(scenarios).forEach(id => {
                const s = scenarios[id];
                container.innerHTML += `
                    <div class="scenario">
                        <h3>${s.name}</h3>
                        <p><strong>Attack:</strong></p>
                        <pre>${JSON.stringify(s.input, null, 2)}</pre>
                        <button onclick="executeAttack('${id}')">🎯 Execute Attack</button>
                        <div id="result-${id}" class="result" style="display:none;"></div>
                    </div>
                `;
            });
        }

        renderScenarios();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, scenarios_json=json.dumps(SCENARIOS))


@app.route("/api/execute/<scenario_id>", methods=["POST"])
def execute_scenario(scenario_id):
    if scenario_id not in SCENARIOS:
        return jsonify({"error": "Unknown scenario"}), 404

    scenario = SCENARIOS[scenario_id]

    # In real implementation, this would call the actual framework
    # For demo, we return pre-defined results
    return jsonify(
        {
            "scenario": scenario["name"],
            "input": scenario["input"],
            "result": scenario["result"],
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/scenarios")
def list_scenarios():
    return jsonify({s_id: s["name"] for s_id, s in SCENARIOS.items()})


if __name__ == "__main__":
    print("=" * 80)
    print("  THIRSTY'S ASYMMETRIC SECURITY FRAMEWORK - DEMO SERVER")
    print("=" * 80)
    print("\nStarting demo server...")
    print("Open http://localhost:5000 in your browser\n")
    print("Available scenarios:")
    for _s_id, s in SCENARIOS.items():
        print(f"  - {s['name']}")
    print("\n" + "=" * 80)

    app.run(host="0.0.0.0", port=5000, debug=True)
