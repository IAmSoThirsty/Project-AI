"""
REST API Server for Simulation Control
Implements Simulation API Endpoints (Section II.10)
"""

import os
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit

from app.miniature_office.agents.agent import Agent, Manager
from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.canonical_bundle import get_canonical_bundle
from app.miniature_office.core.consigliere import get_consigliere
from app.miniature_office.core.entity import get_registry
from app.miniature_office.core.floor_specifications import (
    ProgrammingLanguage,
    get_all_floors,
    get_floor_specification,
)
from app.miniature_office.core.head_of_security import ThreatLevel, get_head_of_security
from app.miniature_office.core.mission import Task
from app.miniature_office.core.simulation import (
    SimulationConfig,
    SimulationEngine,
    create_simulation,
)
from app.miniature_office.core.world import Floor, Office, create_world, get_world
from app.miniature_office.departments.department import (
    Department,
    get_department_registry,
)
from app.miniature_office.interfaces.contract import get_elevator_protocol
from app.miniature_office.server.security import add_security_headers, configure_cors
from app.miniature_office.tools.supply_store import (
    Tool,
    ToolMetadata,
    ToolTag,
    get_supply_store,
)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security: Require SECRET_KEY in production
secret_key = os.getenv("SECRET_KEY")
if os.getenv("FLASK_ENV") == "production" and not secret_key:
    raise RuntimeError("SECRET_KEY environment variable must be set in production mode")
app.config["SECRET_KEY"] = secret_key or "dev-secret-key-only-for-testing"

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max request size

# Configure CORS
configure_cors(app)

# Configure SocketIO with CORS
cors_origins = os.getenv("CORS_ORIGINS", "*")
socketio = SocketIO(app, cors_allowed_origins=cors_origins)


# Apply security headers to all responses
@app.after_request
def apply_security_headers(response):
    return add_security_headers(response)


# Get client directory path
CLIENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client")

# Global simulation instance
simulation: Optional[SimulationEngine] = None


def init_simulation():
    """Initialize the simulation with a default world"""
    global simulation

    # Create world
    world = create_world("world-001", "Miniature Office IDE")

    # Create Python floor
    python_floor = Floor("floor-python", "Python")
    world.add_floor(python_floor)

    # Create Python department
    python_dept = Department("dept-python", "Python Development", "Python")
    dept_registry = get_department_registry()
    dept_registry.register_department(python_dept)
    python_floor.department = python_dept

    # Create an office
    office1 = Office("office-1", python_dept)
    python_floor.add_office(office1)

    # Create manager
    manager = Manager("mgr-001", "Alice Manager", python_dept.entity_id)
    office1.set_manager(manager)
    python_dept.add_agent(manager)

    # The department auto-spawns assistant agents for missing roles
    # which should have already happened during registration

    # Add some tools to supply store
    supply_store = get_supply_store()

    python_tool = Tool(
        "tool-python",
        "Python Interpreter",
        ToolMetadata(
            tag=ToolTag.COMPILER,
            version="3.11.0",
            trust_score=0.9,
            security_rating=4,
            capabilities={"python", "scripting"},
        ),
    )
    supply_store.add_tool(python_tool)

    pytest_tool = Tool(
        "tool-pytest",
        "PyTest Framework",
        ToolMetadata(
            tag=ToolTag.TEST_FRAMEWORK,
            version="7.4.0",
            trust_score=0.95,
            security_rating=4,
            capabilities={"testing", "python"},
        ),
    )
    supply_store.add_tool(pytest_tool)

    # Create a sample task
    task1 = Task(
        "task-001",
        "Implement User Authentication",
        "Create secure user authentication system",
        None,
        None,
    )
    task1.add_precondition("Requirements document exists")
    task1.add_postcondition("Authentication module is implemented")
    task1.add_acceptance_criterion("Unit tests pass")
    task1.add_acceptance_criterion("Security review complete")

    # Create JavaScript floor
    js_floor = Floor("floor-javascript", "JavaScript")
    world.add_floor(js_floor)

    js_dept = Department("dept-javascript", "Frontend Development", "JavaScript")
    dept_registry.register_department(js_dept)
    js_floor.department = js_dept

    # Create simulation
    simulation = create_simulation(
        world,
        SimulationConfig(
            tick_duration_ms=1000, auto_assign_tasks=True
        ),  # 1 second per tick
    )

    # Register event handlers to broadcast via WebSocket
    simulation.register_handler(
        "tick_start", lambda data: socketio.emit("tick_start", data)
    )
    simulation.register_handler(
        "tick_end", lambda data: socketio.emit("tick_end", data)
    )

    return simulation


@app.route("/")
def index():
    """Serve the main HTML page"""
    return send_from_directory(CLIENT_DIR, "index.html")


@app.route("/health")
def health_check():
    """Health check endpoint for monitoring and load balancers"""
    if simulation:
        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "miniature-office",
                    "version": "0.1.0",
                    "simulation": "running",
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "status": "starting",
                    "service": "miniature-office",
                    "version": "0.1.0",
                    "simulation": "initializing",
                }
            ),
            503,
        )


@app.route("/metrics")
def metrics():
    """Prometheus-compatible metrics endpoint"""
    if not simulation:
        return "# Simulation not ready\n", 503

    world = get_world()
    registry = get_registry()
    audit_log = get_audit_log()

    # Generate Prometheus format metrics
    metrics_output = []
    metrics_output.append(
        "# HELP minioffice_world_time Current simulation time in ticks"
    )
    metrics_output.append("# TYPE minioffice_world_time counter")
    metrics_output.append(f"minioffice_world_time {world.time}")

    metrics_output.append("# HELP minioffice_floors_total Total number of floors")
    metrics_output.append("# TYPE minioffice_floors_total gauge")
    metrics_output.append(f"minioffice_floors_total {len(world.floors)}")

    from app.miniature_office.core.entity import EntityType

    agent_count = len(registry.get_by_type(EntityType.AGENT))
    metrics_output.append("# HELP minioffice_agents_total Total number of agents")
    metrics_output.append("# TYPE minioffice_agents_total gauge")
    metrics_output.append(f"minioffice_agents_total {agent_count}")

    # Count artifacts (tasks are tracked as artifacts or separate system)
    artifact_count = len(registry.get_by_type(EntityType.ARTIFACT))
    metrics_output.append("# HELP minioffice_artifacts_total Total number of artifacts")
    metrics_output.append("# TYPE minioffice_artifacts_total gauge")
    metrics_output.append(f"minioffice_artifacts_total {artifact_count}")

    # Count all events from audit log by getting all types
    event_count = sum(
        len(audit_log.get_events_by_type(et))
        for et in [
            EventType.ENTITY_CREATED,
            EventType.ENTITY_UPDATED,
            EventType.RELATIONSHIP_DECLARED,
            EventType.TASK_STATE_CHANGED,
            EventType.AGENT_ACTION,
            EventType.SECURITY_EVENT,
        ]
    )
    metrics_output.append(
        "# HELP minioffice_audit_events_total Total number of audit events"
    )
    metrics_output.append("# TYPE minioffice_audit_events_total counter")
    metrics_output.append(f"minioffice_audit_events_total {event_count}")

    return (
        "\n".join(metrics_output) + "\n",
        200,
        {"Content-Type": "text/plain; version=0.0.4"},
    )


@app.route("/api")
def api_index():
    """API documentation"""
    return jsonify(
        {
            "name": "Miniature Office - Cognitive IDE",
            "version": "0.1.0",
            "description": "A spatialized, agent-orchestrated development environment",
            "endpoints": {
                "GET /": "Main application interface",
                "GET /health": "Health check endpoint",
                "GET /metrics": "Prometheus metrics endpoint",
                "GET /api": "API documentation",
                "GET /api/world/state": "Get current world state",
                "POST /api/world/step": "Advance simulation by one tick",
                "POST /api/world/start": "Start continuous simulation",
                "POST /api/world/stop": "Stop simulation",
                "GET /api/agents/<id>/status": "Get agent status",
                "GET /api/agents": "List all agents",
                "GET /api/tasks/<id>": "Get task details",
                "GET /api/tasks": "List all tasks",
                "GET /api/contracts": "List all contracts",
                "GET /api/departments": "List all departments",
                "GET /api/audit/events": "Get audit events",
                "GET /api/supply-store": "Get supply store inventory",
                "GET /api/consigliere": "Get Consigliere state",
                "POST /api/consigliere/explain": "Request explanation from Consigliere",
                "POST /api/consigliere/translate": "Request translation from Consigliere",
                "POST /api/consigliere/preview": "Preview consequences",
                "POST /api/consigliere/draft": "Prepare draft directive",
                "POST /api/consigliere/command/manager": "Issue directive to manager",
                "POST /api/consigliere/command/agent": "Update agent directive",
                "POST /api/consigliere/coordinate": "Coordinate cross-floor work",
                "POST /api/consigliere/assess": "Assess feasibility of request",
                "GET /api/security": "Get Head of Security state",
                "POST /api/security/grant": "Grant permission",
                "POST /api/security/revoke": "Revoke permission",
                "POST /api/security/audit": "Trigger security audit",
                "POST /api/security/lockdown": "Trigger lockdown",
                "POST /api/security/block": "Block delivery",
                "GET /api/floors": "List all floor specifications",
                "GET /api/floors/<language>": "Get specific floor specification",
            },
        }
    )


# ===== World Endpoints =====


@app.route("/api/world/state", methods=["GET"])
def get_world_state():
    """
    Get current world state.
    Endpoint: /world/state
    """
    if not simulation:
        return jsonify({"error": "Simulation not initialized"}), 500

    return jsonify(simulation.get_state())


@app.route("/api/world/step", methods=["POST"])
def step_simulation():
    """
    Advance simulation by one tick.
    Endpoint: /world/step
    """
    if not simulation:
        return jsonify({"error": "Simulation not initialized"}), 500

    simulation.step()

    return jsonify(
        {
            "success": True,
            "time": simulation.world.time,
            "tick_count": simulation.tick_count,
        }
    )


@app.route("/api/world/start", methods=["POST"])
def start_simulation():
    """Start continuous simulation"""
    if not simulation:
        return jsonify({"error": "Simulation not initialized"}), 500

    if simulation.is_running:
        return jsonify({"error": "Simulation already running"}), 400

    # Start in background thread
    socketio.start_background_task(simulation.run)

    return jsonify({"success": True, "message": "Simulation started"})


@app.route("/api/world/stop", methods=["POST"])
def stop_simulation():
    """Stop simulation"""
    if not simulation:
        return jsonify({"error": "Simulation not initialized"}), 500

    simulation.stop()

    return jsonify({"success": True, "message": "Simulation stopped"})


# ===== Agent Endpoints =====


@app.route("/api/agents/<agent_id>/status", methods=["GET"])
def get_agent_status(agent_id: str):
    """
    Get agent status.
    Endpoint: /agents/{id}/status
    """
    registry = get_registry()
    agent = registry.get(agent_id)

    if not agent or not isinstance(agent, Agent):
        return jsonify({"error": "Agent not found"}), 404

    return jsonify(
        {
            "agent_id": agent.entity_id,
            "name": agent.name,
            "role": agent.role.value,
            "status": agent.status,
            "department_id": agent.department_id,
            "current_task_id": agent.current_task_id,
            "capabilities": agent.capabilities.to_dict(),
            "task_history": agent.task_history,
        }
    )


@app.route("/api/agents", methods=["GET"])
def list_agents():
    """List all agents"""
    from app.miniature_office.core.entity import EntityType

    registry = get_registry()
    agents = registry.get_by_type(EntityType.AGENT)

    return jsonify(
        {
            "agents": [
                {
                    "agent_id": a.entity_id,
                    "name": a.name,
                    "role": a.role.value if hasattr(a, "role") else "unknown",
                    "status": a.status if hasattr(a, "status") else "unknown",
                }
                for a in agents
                if isinstance(a, Agent)
            ]
        }
    )


# ===== Task Endpoints =====


@app.route("/api/tasks/<task_id>", methods=["GET"])
def get_task(task_id: str):
    """
    Get task details.
    Endpoint: /tasks/{id}
    """
    registry = get_registry()
    task = registry.get(task_id)

    if not task or not isinstance(task, Task):
        return jsonify({"error": "Task not found"}), 404

    return jsonify(
        {
            "task_id": task.entity_id,
            "name": task.name,
            "description": task.description,
            "state": task.state.value,
            "assigned_agent_id": task.assigned_agent_id,
            "ambiguity_score": task.ambiguity_score,
            "blocked_reason": task.blocked_reason,
            "preconditions": [
                {"description": c.description, "is_satisfied": c.is_satisfied}
                for c in task.preconditions
            ],
            "postconditions": [
                {"description": c.description, "is_satisfied": c.is_satisfied}
                for c in task.postconditions
            ],
            "acceptance_criteria": [
                {"description": c.description, "is_met": c.is_met}
                for c in task.acceptance_criteria
            ],
            "state_history": task.state_history,
        }
    )


@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    """List all tasks"""
    from app.miniature_office.core.entity import EntityType

    registry = get_registry()
    # Tasks are stored as ARTIFACT entities
    all_entities = registry.get_by_type(EntityType.ARTIFACT)
    tasks = [e for e in all_entities if isinstance(e, Task)]

    return jsonify(
        {
            "tasks": [
                {
                    "task_id": t.entity_id,
                    "name": t.name,
                    "state": t.state.value,
                    "assigned_agent_id": t.assigned_agent_id,
                }
                for t in tasks
            ]
        }
    )


# ===== Contract Endpoints =====


@app.route("/api/contracts", methods=["GET"])
def list_contracts():
    """List all contracts"""
    elevator = get_elevator_protocol()

    return jsonify({"contracts": [c.to_dict() for c in elevator.contracts.values()]})


# ===== Department Endpoints =====


@app.route("/api/departments", methods=["GET"])
def list_departments():
    """List all departments"""
    dept_registry = get_department_registry()

    return jsonify(
        {
            "departments": [
                {
                    "department_id": d.entity_id,
                    "name": d.name,
                    "domain": d.domain,
                    "is_fully_staffed": d.is_fully_staffed(),
                    "missing_roles": [r.value for r in d.get_missing_roles()],
                }
                for d in dept_registry.departments.values()
            ]
        }
    )


# ===== Audit Endpoints =====


@app.route("/api/audit/events", methods=["GET"])
def get_audit_events():
    """Get audit events"""
    audit_log = get_audit_log()

    # Get query parameters
    event_type = request.args.get("type")
    actor_id = request.args.get("actor_id")
    target_id = request.args.get("target_id")
    limit = int(request.args.get("limit", 100))

    # Get events based on filters
    if event_type:
        from app.miniature_office.core.audit import EventType

        events = audit_log.get_events_by_type(EventType(event_type))
    elif actor_id:
        events = audit_log.get_events_by_actor(actor_id)
    elif target_id:
        events = audit_log.get_events_by_target(target_id)
    else:
        # Get all events
        events = list(audit_log.graph.events.values())

    # Limit results
    events = sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]

    return jsonify({"events": [e.to_dict() for e in events]})


# ===== Supply Store Endpoints =====


@app.route("/api/supply-store", methods=["GET"])
def get_supply_store_inventory():
    """Get supply store inventory"""
    store = get_supply_store()

    return jsonify(
        {
            "tools": [t.to_dict() for t in store.tools.values()],
            "available_count": len(store.get_available_tools()),
            "checked_out_count": len(
                [t for t in store.tools.values() if not t.is_available]
            ),
        }
    )


# ===== Consigliere Endpoints (Advisory Executive) =====


@app.route("/api/consigliere", methods=["GET"])
def get_consigliere_state():
    """Get Consigliere state and capabilities"""
    consigliere = get_consigliere()
    return jsonify(consigliere.to_dict())


@app.route("/api/consigliere/explain", methods=["POST"])
def consigliere_explain():
    """
    Request explanation from Consigliere.

    Body: {
        "type": "why_blocked" | "why_decision" | "what_options",
        "entity_id": "...",  # for why_blocked, why_decision
        "situation": "...",  # for what_options
        "context": {}  # optional
    }
    """
    data = request.get_json()
    consigliere = get_consigliere()

    explanation_type = data.get("type")
    entity_id = data.get("entity_id")
    situation = data.get("situation")
    context = data.get("context", {})

    if explanation_type == "why_blocked":
        if not entity_id:
            return jsonify({"error": "entity_id required for why_blocked"}), 400
        explanation = consigliere.explain_why_blocked(entity_id, context)
    elif explanation_type == "why_decision":
        if not entity_id:
            return jsonify({"error": "entity_id required for why_decision"}), 400
        explanation = consigliere.explain_why_decision(entity_id, context)
    elif explanation_type == "what_options":
        if not situation:
            return jsonify({"error": "situation required for what_options"}), 400
        explanation = consigliere.explain_what_options(situation, context)
    else:
        return jsonify({"error": f"Unknown explanation type: {explanation_type}"}), 400

    return jsonify(explanation.to_dict())


@app.route("/api/consigliere/translate", methods=["POST"])
def consigliere_translate():
    """
    Request translation from Consigliere.

    Body: {
        "text": "civilizational text to translate"
    }
    """
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "text required"}), 400

    consigliere = get_consigliere()
    translation = consigliere.translate_civilization_to_human(text)

    return jsonify(translation.to_dict())


@app.route("/api/consigliere/preview", methods=["POST"])
def consigliere_preview():
    """
    Preview consequences of an action.

    Body: {
        "action": "proposed action description",
        "context": {}  # optional
    }
    """
    data = request.get_json()
    action = data.get("action")
    context = data.get("context", {})

    if not action:
        return jsonify({"error": "action required"}), 400

    consigliere = get_consigliere()
    preview = consigliere.preview_consequences(action, context)

    return jsonify(preview.to_dict())


@app.route("/api/consigliere/draft", methods=["POST"])
def consigliere_draft():
    """
    Prepare draft directive.

    Body: {
        "goal": "what to accomplish",
        "language": "python" | "rust" | etc.,
        "constraints": []  # optional
    }
    """
    data = request.get_json()
    goal = data.get("goal")
    language = data.get("language")
    constraints = data.get("constraints", [])

    if not goal or not language:
        return jsonify({"error": "goal and language required"}), 400

    consigliere = get_consigliere()
    draft = consigliere.prepare_draft_directive(goal, language, constraints)

    return jsonify(draft.to_dict())


@app.route("/api/consigliere/command/manager", methods=["POST"])
def consigliere_command_manager():
    """
    Issue directive to manager (Consigliere executive authority).

    Body: {
        "manager_id": "...",
        "directive": "what to do",
        "priority": "normal" | "high" | "critical"  # optional
    }
    """
    data = request.get_json()
    manager_id = data.get("manager_id")
    directive = data.get("directive")
    priority = data.get("priority", "normal")

    if not manager_id or not directive:
        return jsonify({"error": "manager_id and directive required"}), 400

    consigliere = get_consigliere()
    result = consigliere.issue_directive_to_manager(manager_id, directive, priority)

    return jsonify(result)


@app.route("/api/consigliere/command/agent", methods=["POST"])
def consigliere_command_agent():
    """
    Update agent directive (Consigliere executive authority).

    Body: {
        "agent_id": "...",
        "new_directive": "updated task",
        "justification": "why changing"
    }
    """
    data = request.get_json()
    agent_id = data.get("agent_id")
    new_directive = data.get("new_directive")
    justification = data.get("justification")

    if not agent_id or not new_directive or not justification:
        return (
            jsonify({"error": "agent_id, new_directive, and justification required"}),
            400,
        )

    consigliere = get_consigliere()
    result = consigliere.update_agent_directive(agent_id, new_directive, justification)

    return jsonify(result)


@app.route("/api/consigliere/coordinate", methods=["POST"])
def consigliere_coordinate():
    """
    Coordinate cross-floor work (Consigliere executive authority).

    Body: {
        "floor_ids": ["floor-python", "floor-rust"],
        "coordination_plan": "description of coordination"
    }
    """
    data = request.get_json()
    floor_ids = data.get("floor_ids")
    coordination_plan = data.get("coordination_plan")

    if not floor_ids or not coordination_plan:
        return jsonify({"error": "floor_ids and coordination_plan required"}), 400

    consigliere = get_consigliere()
    result = consigliere.coordinate_cross_floor_work(floor_ids, coordination_plan)

    return jsonify(result)


@app.route("/api/consigliere/assess", methods=["POST"])
def consigliere_assess():
    """
    Assess feasibility of request (Consigliere tells you if it's possible).

    Body: {
        "request": "what you want to do",
        "context": {}  # optional
    }
    """
    data = request.get_json()
    request_text = data.get("request")

    if not request_text:
        return jsonify({"error": "request required"}), 400

    consigliere = get_consigliere()

    # Simple feasibility check (in real system would be more sophisticated)
    if any(word in request_text.lower() for word in ["impossible", "cannot", "unable"]):
        result = consigliere.tell_human_impossible(
            request=request_text,
            reason="Request contains constraints that appear contradictory or infeasible",
            alternatives=[
                "Simplify requirements",
                "Split into multiple tasks",
                "Adjust constraints",
            ],
        )
    else:
        result = consigliere.tell_human_feasible(
            request=request_text,
            approach="Route to appropriate floor, allocate resources, coordinate execution",
            estimated_resources={"agent_time": 15, "manager_attention": 3},
        )

    return jsonify(result)


# ===== Head of Security Endpoints (Security Sovereign) =====


@app.route("/api/security", methods=["GET"])
def get_security_state():
    """Get Head of Security state and capabilities"""
    security = get_head_of_security()
    return jsonify(security.to_dict())


@app.route("/api/security/grant", methods=["POST"])
def security_grant():
    """
    Grant permission.

    Body: {
        "entity_id": "...",
        "resource": "tool_name or operation",
        "justification": "why this is needed",
        "expires_in_hours": 24  # optional
    }
    """
    data = request.get_json()
    entity_id = data.get("entity_id")
    resource = data.get("resource")
    justification = data.get("justification")
    expires_in_hours = data.get("expires_in_hours")

    if not entity_id or not resource or not justification:
        return (
            jsonify({"error": "entity_id, resource, and justification required"}),
            400,
        )

    security = get_head_of_security()
    permission = security.grant_tool_access(
        entity_id, resource, justification, expires_in_hours
    )

    return jsonify(permission.to_dict())


@app.route("/api/security/revoke", methods=["POST"])
def security_revoke():
    """
    Revoke permission.

    Body: {
        "permission_id": "...",
        "reason": "why revoking"
    }
    """
    data = request.get_json()
    permission_id = data.get("permission_id")
    reason = data.get("reason")

    if not permission_id or not reason:
        return jsonify({"error": "permission_id and reason required"}), 400

    security = get_head_of_security()
    success = security.revoke_access(permission_id, reason)

    return jsonify({"success": success})


@app.route("/api/security/audit", methods=["POST"])
def security_audit():
    """
    Trigger security audit.

    Body: {
        "type": "full_system" | "floor" | "cross_floor",
        "scope": [],  # for floor or cross_floor
        "reason": "why auditing"
    }
    """
    data = request.get_json()
    audit_type = data.get("type", "full_system")
    scope = data.get("scope", [])
    reason = data.get("reason", "Manual audit trigger")

    security = get_head_of_security()

    if audit_type == "full_system":
        audit = security.trigger_full_audit(reason)
    elif audit_type == "cross_floor":
        audit = security.trigger_cross_floor_review(scope, reason)
    else:
        return jsonify({"error": f"Unknown audit type: {audit_type}"}), 400

    return jsonify(audit.to_dict())


@app.route("/api/security/lockdown", methods=["POST"])
def security_lockdown():
    """
    Trigger lockdown.

    Body: {
        "scope": "building" | "floor:<floor_id>",
        "reason": "emergency reason",
        "threat_level": "low" | "medium" | "high" | "critical"
    }
    """
    data = request.get_json()
    scope = data.get("scope")
    reason = data.get("reason")
    threat_level_str = data.get("threat_level", "medium")

    if not scope or not reason:
        return jsonify({"error": "scope and reason required"}), 400

    threat_level = ThreatLevel(threat_level_str)
    security = get_head_of_security()

    if scope == "building":
        lockdown = security.freeze_building(reason, threat_level)
    elif scope.startswith("floor:"):
        floor_id = scope.split(":", 1)[1]
        lockdown = security.trigger_floor_lockdown(floor_id, reason, threat_level)
    else:
        return jsonify({"error": f"Invalid scope: {scope}"}), 400

    return jsonify(lockdown.to_dict())


@app.route("/api/security/block", methods=["POST"])
def security_block():
    """
    Block delivery.

    Body: {
        "artifact_id": "...",
        "reason": "security concern",
        "required_mitigations": []
    }
    """
    data = request.get_json()
    artifact_id = data.get("artifact_id")
    reason = data.get("reason")
    required_mitigations = data.get("required_mitigations", [])

    if not artifact_id or not reason:
        return jsonify({"error": "artifact_id and reason required"}), 400

    security = get_head_of_security()
    block = security.block_delivery(artifact_id, reason, required_mitigations)

    return jsonify(block.to_dict())


@app.route("/api/security/lockdowns", methods=["GET"])
def get_active_lockdowns():
    """Get active lockdowns"""
    security = get_head_of_security()
    return jsonify({"lockdowns": security.get_active_lockdowns()})


@app.route("/api/security/blocked", methods=["GET"])
def get_blocked_deliveries():
    """Get blocked deliveries"""
    security = get_head_of_security()
    return jsonify({"blocked_deliveries": security.get_blocked_deliveries()})


@app.route("/api/security/permissions", methods=["GET"])
def get_active_permissions():
    """Get active permissions"""
    entity_id = request.args.get("entity_id")
    security = get_head_of_security()
    return jsonify({"permissions": security.get_active_permissions(entity_id)})


# ===== Floor Specification Endpoints =====


@app.route("/api/floors", methods=["GET"])
def list_floors():
    """List all floor specifications"""
    floors = get_all_floors()
    return jsonify({"floors": [floor.to_dict() for floor in floors]})


@app.route("/api/floors/<language>", methods=["GET"])
def get_floor(language: str):
    """Get specific floor specification"""
    try:
        lang_enum = ProgrammingLanguage(language.lower())
        floor = get_floor_specification(lang_enum)
        return jsonify(floor.to_dict())
    except ValueError:
        return jsonify({"error": f"Unknown language: {language}"}), 404


# ===== WebSocket Events =====


@socketio.on("connect")
def handle_connect():
    """Handle client connection"""
    emit("connected", {"message": "Connected to Miniature Office simulation"})


@socketio.on("request_state")
def handle_request_state():
    """Handle state request via WebSocket"""
    if simulation:
        emit("state_update", simulation.get_state())


# ============================================================================
# CANONICAL BUNDLE API ENDPOINTS
# ============================================================================


@app.route("/api/canonical-bundle", methods=["GET"])
def get_bundle_status():
    """Get canonical bundle status and report."""
    try:
        bundle = get_canonical_bundle()
        is_complete, missing = bundle.verify_bundle_completeness()

        return jsonify(
            {
                "bundle_id": bundle.bundle_id,
                "version": bundle.version,
                "created_at": bundle.created_at.isoformat(),
                "is_complete": is_complete,
                "missing_artifacts": missing,
                "report": bundle.generate_bundle_report(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/charter", methods=["GET"])
def get_charter():
    """Get the Civilization Charter."""
    try:
        bundle = get_canonical_bundle()
        charter = bundle.charter

        return jsonify(
            {
                "charter_id": charter.charter_id,
                "version": charter.version,
                "issued_date": charter.issued_date.isoformat(),
                "axioms": charter.axioms,
                "is_immutable": charter.is_immutable,
                "human_readable": charter.to_human_readable(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/authority-ledger", methods=["GET"])
def get_authority_ledger():
    """Get the Authority & Role Ledger."""
    try:
        bundle = get_canonical_bundle()
        ledger = bundle.authority_ledger

        return jsonify(
            {
                "ledger_id": ledger.ledger_id,
                "created_at": ledger.created_at.isoformat(),
                "total_grants": len(ledger.grants),
                "active_grants": len([g for g in ledger.grants if not g.revoked]),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/purpose-lock", methods=["GET"])
def get_purpose_lock():
    """Get the Purpose Lock Attestation."""
    try:
        bundle = get_canonical_bundle()
        purpose_lock = bundle.purpose_lock

        return jsonify(
            {
                "attestation_id": purpose_lock.attestation_id,
                "version": purpose_lock.version,
                "timestamp": purpose_lock.timestamp.isoformat(),
                "overall_locked": purpose_lock.overall_locked,
                "subsystems_checked": len(purpose_lock.subsystems_checked),
                "report": purpose_lock.generate_attestation_report(),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/board-resolutions", methods=["GET"])
def get_board_resolutions():
    """Get the Board Resolution Archive."""
    try:
        bundle = get_canonical_bundle()
        archive = bundle.board_resolutions

        return jsonify(
            {
                "archive_id": archive.archive_id,
                "created_at": archive.created_at.isoformat(),
                "total_resolutions": len(archive.resolutions),
                "resolutions": [
                    {
                        "resolution_id": r.resolution_id,
                        "directive_id": r.directive_id,
                        "decision": r.decision,
                        "timestamp": r.timestamp.isoformat(),
                    }
                    for r in archive.resolutions[:10]  # Latest 10
                ],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/precedents", methods=["GET"])
def get_precedents():
    """Get the Directive Precedent Corpus."""
    try:
        bundle = get_canonical_bundle()
        corpus = bundle.precedent_corpus

        return jsonify(
            {
                "corpus_id": corpus.corpus_id,
                "total_precedents": len(corpus.precedents),
                "indexed_tags": len(corpus.index),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/meta-office-rulings", methods=["GET"])
def get_meta_rulings():
    """Get the Meta-Office Rulings Ledger."""
    try:
        bundle = get_canonical_bundle()
        ledger = bundle.meta_office_rulings

        return jsonify(
            {
                "ledger_id": ledger.ledger_id,
                "total_rulings": len(ledger.rulings),
                "rulings": [
                    {
                        "ruling_id": r.ruling_id,
                        "ruling_type": r.ruling_type,
                        "timestamp": r.timestamp.isoformat(),
                    }
                    for r in ledger.rulings[:10]
                ],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/law-failure-matrix", methods=["GET"])
def get_law_failure_matrix():
    """Get the Law × Failure × Response Matrix."""
    try:
        bundle = get_canonical_bundle()
        matrix = bundle.law_failure_matrix

        return jsonify(
            {
                "matrix_id": matrix.matrix_id,
                "version": matrix.version,
                "total_mappings": len(matrix.responses),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/formal-verification", methods=["GET"])
def get_formal_verification():
    """Get the Formal Law Verification Models."""
    try:
        bundle = get_canonical_bundle()
        models = bundle.formal_verification

        return jsonify(
            {
                "model_id": models.model_id,
                "version": models.version,
                "total_invariants": len(models.invariants),
                "verified_invariants": len(
                    [i for i in models.invariants if i.verified]
                ),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/violation-playbooks", methods=["GET"])
def get_violation_playbooks():
    """Get the Invariant Violation Playbooks."""
    try:
        bundle = get_canonical_bundle()
        playbooks = bundle.violation_playbooks

        return jsonify(
            {
                "playbooks_id": playbooks.playbooks_id,
                "total_playbooks": len(playbooks.playbooks),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/execution-kernel", methods=["GET"])
def get_execution_kernel():
    """Get the Canonical Execution Kernel."""
    try:
        bundle = get_canonical_bundle()
        kernel = bundle.execution_kernel

        return jsonify(
            {
                "kernel_id": kernel.kernel_id,
                "version": kernel.version,
                "conformance_criteria": kernel.conformance_criteria,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/simulation-traces", methods=["GET"])
def get_simulation_traces():
    """Get the Simulation Trace Corpus."""
    try:
        bundle = get_canonical_bundle()
        corpus = bundle.simulation_traces

        return jsonify(
            {"corpus_id": corpus.corpus_id, "total_traces": len(corpus.traces)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/reproducibility-packets", methods=["GET"])
def get_reproducibility_packets():
    """Get the Reproducibility Packets."""
    try:
        bundle = get_canonical_bundle()
        packets = bundle.reproducibility_packets

        return jsonify(
            {"packets_id": packets.packets_id, "total_packets": len(packets.packets)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/floor-profiles", methods=["GET"])
def get_floor_profiles():
    """Get the Floor Runtime Profiles."""
    try:
        bundle = get_canonical_bundle()
        profiles = bundle.floor_profiles

        return jsonify(
            {
                "profiles_id": profiles.profiles_id,
                "total_profiles": len(profiles.profiles),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/contract-registry", methods=["GET"])
def get_contract_registry():
    """Get the Cross-Floor Contract Registry."""
    try:
        bundle = get_canonical_bundle()
        registry = bundle.contract_registry

        return jsonify(
            {
                "registry_id": registry.registry_id,
                "total_contracts": len(registry.contracts),
                "active_contracts": len([c for c in registry.contracts if c.is_active]),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/contract-drift", methods=["GET"])
def get_contract_drift():
    """Get the Contract Drift Reports."""
    try:
        bundle = get_canonical_bundle()
        drift = bundle.contract_drift

        return jsonify(
            {"reports_id": drift.reports_id, "total_reports": len(drift.reports)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/tool-provenance", methods=["GET"])
def get_tool_provenance():
    """Get the Tool Provenance & Trust Ledger."""
    try:
        bundle = get_canonical_bundle()
        ledger = bundle.tool_provenance

        return jsonify(
            {"ledger_id": ledger.ledger_id, "total_tools": len(ledger.tools)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/unsafe-exceptions", methods=["GET"])
def get_unsafe_exceptions():
    """Get the Unsafe Capability Exception Records."""
    try:
        bundle = get_canonical_bundle()
        records = bundle.unsafe_exceptions

        return jsonify(
            {
                "records_id": records.records_id,
                "total_exceptions": len(records.exceptions),
                "active_exceptions": len(
                    [e for e in records.exceptions if not e.revoked]
                ),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/consigliere-logs", methods=["GET"])
def get_consigliere_logs():
    """Get the Consigliere Interaction Logs."""
    try:
        bundle = get_canonical_bundle()
        logs = bundle.consigliere_logs

        return jsonify(
            {"logs_id": logs.logs_id, "total_interactions": len(logs.interactions)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/security-dossiers", methods=["GET"])
def get_security_dossiers():
    """Get the Security Decision Dossiers."""
    try:
        bundle = get_canonical_bundle()
        dossiers = bundle.security_dossiers

        return jsonify(
            {
                "dossiers_id": dossiers.dossiers_id,
                "total_decisions": len(dossiers.decisions),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/override-ledger", methods=["GET"])
def get_override_ledger():
    """Get the Override Cost Ledger."""
    try:
        bundle = get_canonical_bundle()
        ledger = bundle.override_ledger

        return jsonify(
            {"ledger_id": ledger.ledger_id, "total_overrides": len(ledger.overrides)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/amendments", methods=["GET"])
def get_amendments():
    """Get the Constitutional Amendment Registry."""
    try:
        bundle = get_canonical_bundle()
        registry = bundle.amendment_registry

        return jsonify(
            {
                "registry_id": registry.registry_id,
                "total_amendments": len(registry.amendments),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/rejected-proposals", methods=["GET"])
def get_rejected_proposals():
    """Get the Dormant / Rejected Proposal Archive."""
    try:
        bundle = get_canonical_bundle()
        archive = bundle.rejected_proposals

        return jsonify(
            {
                "archive_id": archive.archive_id,
                "total_proposals": len(archive.proposals),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/audit-interface", methods=["GET"])
def get_audit_interface():
    """Get the Independent Audit Interface."""
    try:
        bundle = get_canonical_bundle()
        interface = bundle.audit_interface

        return jsonify(
            {
                "interface_id": interface.interface_id,
                "accessible_artifacts": interface.accessible_artifacts,
                "total_access_grants": len(interface.access_log),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/compliance-reports", methods=["GET"])
def get_compliance_reports():
    """Get the Compliance & Certification Reports."""
    try:
        bundle = get_canonical_bundle()
        reports = bundle.compliance_reports

        return jsonify(
            {"reports_id": reports.reports_id, "total_reports": len(reports.reports)}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/freeze-protocol", methods=["GET"])
def get_freeze_protocol():
    """Get the Civilization Freeze Protocol."""
    try:
        bundle = get_canonical_bundle()
        protocol = bundle.freeze_protocol

        return jsonify(
            {
                "protocol_id": protocol.protocol_id,
                "is_frozen": protocol.is_frozen,
                "frozen_at": (
                    protocol.frozen_at.isoformat() if protocol.frozen_at else None
                ),
                "access_locked": protocol.access_locked,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/shutdown-protocol", methods=["GET"])
def get_shutdown_protocol():
    """Get the Civilization Shutdown & Succession Protocol."""
    try:
        bundle = get_canonical_bundle()
        protocol = bundle.shutdown_protocol

        return jsonify(
            {
                "protocol_id": protocol.protocol_id,
                "is_shutdown": protocol.is_shutdown,
                "shutdown_at": (
                    protocol.shutdown_at.isoformat() if protocol.shutdown_at else None
                ),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/canonical-bundle/metrics-canon", methods=["GET"])
def get_metrics_canon():
    """Get the Success & Failure Metrics Canon."""
    try:
        bundle = get_canonical_bundle()
        canon = bundle.metrics_canon

        return jsonify(
            {
                "canon_id": canon.canon_id,
                "version": canon.version,
                "correctness_metrics": canon.correctness_metrics,
                "completeness_metrics": canon.completeness_metrics,
                "trustworthiness_metrics": canon.trustworthiness_metrics,
                "forbidden_metrics": canon.forbidden_metrics,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_server(host="0.0.0.0", port=5000, debug=False):
    """Run the API server"""
    # Initialize simulation on startup
    init_simulation()

    print(f"Starting Miniature Office API Server on {host}:{port}")
    print(f"Simulation initialized with world: {simulation.world.name}")

    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


# Initialize simulation at module level for production servers (gunicorn, etc.)
# Only initialize if explicitly in production mode
if os.getenv("FLASK_ENV") == "production":
    simulation = init_simulation()
    print(
        f"Production mode: Simulation initialized with world: {simulation.world.name if simulation else 'None'}"
    )


if __name__ == "__main__":
    run_server(debug=True)
