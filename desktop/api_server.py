"""
Enhanced Cognitive IDE - Backend API Server
Provides simulation state, AI analysis, and other backend services
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
from typing import Optional, List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from app.miniature_office.cognitive_ide import CognitiveIDE
    from app.miniature_office.agent_lounge import AgentLounge
    from app.miniature_office.meta_security_dept import MetaSecurityDepartment
    MINIATURE_OFFICE_AVAILABLE = True
except ImportError:
    MINIATURE_OFFICE_AVAILABLE = False
    logging.warning("Miniature Office components not available, using mock data")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Cognitive IDE API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
cognitive_ide: Optional[CognitiveIDE] = None
simulation_running = False
simulation_tick = 0


# Pydantic models
class CodeAnalysisRequest(BaseModel):
    code: str
    context: Dict[str, Any]
    position: Dict[str, int]
    language: str


class CodeSuggestion(BaseModel):
    id: str
    type: str
    severity: str
    line: int
    column: int
    message: str
    suggestion: str
    confidence: float


class SimulationState(BaseModel):
    tick: int
    totalAgents: int
    activeTasks: int
    completedTasks: int
    worldStatus: str
    floors: List[Dict[str, Any]]


# Initialize Cognitive IDE
@app.on_event("startup")
async def startup_event():
    global cognitive_ide
    
    logger.info("🚀 Starting Enhanced Cognitive IDE API Server")
    
    if MINIATURE_OFFICE_AVAILABLE:
        try:
            agent_lounge = AgentLounge()
            meta_security = MetaSecurityDepartment()
            cognitive_ide = CognitiveIDE(
                agent_lounge=agent_lounge,
                meta_security=meta_security
            )
            logger.info("✅ Cognitive IDE initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cognitive IDE: {e}")
            cognitive_ide = None
    else:
        logger.warning("⚠️ Running with mock data (Miniature Office unavailable)")


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "miniature_office_available": MINIATURE_OFFICE_AVAILABLE,
        "cognitive_ide_initialized": cognitive_ide is not None
    }


# Simulation endpoints
@app.get("/api/simulation/state")
async def get_simulation_state():
    """Get current simulation state with all floors and agents"""
    
    global simulation_tick
    
    if cognitive_ide and MINIATURE_OFFICE_AVAILABLE:
        try:
            state = cognitive_ide.get_simulation_state()
            floors = cognitive_ide.list_floors()
            
            return {
                "tick": state.tick,
                "totalAgents": state.total_agents,
                "activeTasks": state.active_tasks,
                "completedTasks": state.completed_tasks,
                "worldStatus": state.world_status,
                "floors": [
                    {
                        "id": f.floor_number,
                        "name": f.language,
                        "height": f.floor_number * 5,
                        "agents": generate_mock_agents(f.agent_count, f.floor_number),
                        "departments": generate_mock_departments(f.department_count)
                    }
                    for f in floors
                ]
            }
        except Exception as e:
            logger.error(f"Error getting simulation state: {e}")
    
    # Mock data
    return {
        "tick": simulation_tick,
        "totalAgents": 24,
        "activeTasks": 8,
        "completedTasks": 156,
        "worldStatus": "running" if simulation_running else "idle",
        "floors": [
            {
                "id": 0,
                "name": "Lobby",
                "height": 0,
                "agents": generate_mock_agents(2, 0),
                "departments": generate_mock_departments(1)
            },
            {
                "id": 1,
                "name": "Python",
                "height": 5,
                "agents": generate_mock_agents(8, 1),
                "departments": generate_mock_departments(4)
            },
            {
                "id": 2,
                "name": "JavaScript",
                "height": 10,
                "agents": generate_mock_agents(6, 2),
                "departments": generate_mock_departments(4)
            },
            {
                "id": 3,
                "name": "Rust",
                "height": 15,
                "agents": generate_mock_agents(4, 3),
                "departments": generate_mock_departments(3)
            },
        ]
    }


def generate_mock_agents(count: int, floor: int) -> List[Dict[str, Any]]:
    """Generate mock agent data"""
    import random
    statuses = ['idle', 'active', 'blocked', 'completed']
    roles = ['Developer', 'Tester', 'Architect', 'DevOps']
    
    agents = []
    for i in range(count):
        agents.append({
            "id": f"agent_{floor}_{i}",
            "position": {
                "x": random.uniform(-9, 9),
                "y": floor * 5 + 0.3,
                "z": random.uniform(-9, 9)
            },
            "role": random.choice(roles),
            "status": random.choice(statuses),
            "health": random.uniform(0.7, 1.0)
        })
    
    return agents


def generate_mock_departments(count: int) -> List[Dict[str, Any]]:
    """Generate mock department data"""
    import random
    departments = []
    
    for i in range(count):
        x_pos = -6 + (i % 2) * 12
        z_pos = -6 + (i // 2) * 12
        
        departments.append({
            "id": f"dept_{i}",
            "name": f"Department {i+1}",
            "position": {"x": x_pos, "y": 0, "z": z_pos},
            "size": {"x": 3, "y": 2, "z": 3},
            "capacity": 5,
            "occupied": random.randint(0, 5)
        })
    
    return departments


@app.post("/api/simulation/step")
async def step_simulation():
    """Advance simulation by one tick"""
    global simulation_tick
    
    if cognitive_ide and MINIATURE_OFFICE_AVAILABLE:
        try:
            state = cognitive_ide.step_simulation()
            return {"success": True, "tick_count": state.tick}
        except Exception as e:
            logger.error(f"Error stepping simulation: {e}")
    
    simulation_tick += 1
    return {"success": True, "tick_count": simulation_tick}


@app.post("/api/simulation/start")
async def start_simulation():
    """Start the simulation"""
    global simulation_running
    simulation_running = True
    logger.info("Simulation started")
    return {"success": True, "status": "running"}


@app.post("/api/simulation/stop")
async def stop_simulation():
    """Stop the simulation"""
    global simulation_running
    simulation_running = False
    logger.info("Simulation stopped")
    return {"success": True, "status": "stopped"}


# AI Analysis endpoints
@app.post("/api/ai/analyze", response_model=Dict[str, List[CodeSuggestion]])
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code and return AI suggestions"""
    
    suggestions = []
    
    # Simple pattern-based analysis (replace with actual AI model)
    lines = request.code.split('\n')
    
    for i, line in enumerate(lines):
        # Security checks
        if 'eval(' in line or 'exec(' in line:
            suggestions.append(CodeSuggestion(
                id=f"security_{i}",
                type="bug-fix",
                severity="error",
                line=i + 1,
                column=1,
                message="Avoid using eval/exec - potential security risk",
                suggestion="Use safer alternatives like ast.literal_eval",
                confidence=0.95
            ))
        
        # Performance checks
        if 'for ' in line and 'range(len(' in line:
            suggestions.append(CodeSuggestion(
                id=f"perf_{i}",
                type="optimization",
                severity="warning",
                line=i + 1,
                column=1,
                message="Use enumerate() instead of range(len())",
                suggestion=line.replace("range(len(", "enumerate("),
                confidence=0.9
            ))
        
        # Style checks
        if len(line) > 120:
            suggestions.append(CodeSuggestion(
                id=f"style_{i}",
                type="refactor",
                severity="info",
                line=i + 1,
                column=1,
                message="Line too long (>120 chars)",
                suggestion="Consider breaking into multiple lines",
                confidence=0.85
            ))
    
    return {"suggestions": suggestions}


# Agent endpoints
@app.get("/api/agents")
async def get_agents():
    """Get all active agents"""
    
    # Mock data for now
    return {
        "agents": [
            {"name": "Agent Alpha", "role": "Developer", "status": "active"},
            {"name": "Agent Beta", "role": "Tester", "status": "idle"},
            {"name": "Agent Gamma", "role": "DevOps", "status": "active"},
        ]
    }


@app.get("/api/tasks")
async def get_tasks():
    """Get all active tasks"""
    
    return {
        "tasks": [
            {"id": "task_1", "name": "Implement feature X", "status": "in_progress"},
            {"id": "task_2", "name": "Fix bug Y", "status": "pending"},
            {"id": "task_3", "name": "Deploy service Z", "status": "completed"},
        ]
    }


@app.get("/api/supply-store")
async def get_supply_store():
    """Get available tools from supply store"""
    
    return {
        "available_count": 42,
        "tools": [
            {"name": "Code Analyzer", "type": "analysis"},
            {"name": "Test Generator", "type": "testing"},
            {"name": "Deployment Tool", "type": "deployment"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("API_PORT", 8000))
    logger.info(f"Starting server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
