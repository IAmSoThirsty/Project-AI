"""
Control Plane API Server

FastAPI-based RESTful server for control plane operations.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from .deployment import DeploymentAPI
from .scaling import ScalingAPI
from .monitoring import MonitoringAPI
from .lifecycle import LifecycleAPI


# Request/Response Models
class DeploymentRequest(BaseModel):
    name: str = Field(..., description="Deployment name")
    deployment_type: str = Field(..., description="Type: agent, workflow, service")
    image: str = Field(..., description="Container image")
    replicas: int = Field(1, ge=1, description="Number of replicas")
    strategy: str = Field("rolling_update", description="Deployment strategy")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    resources: Optional[Dict[str, Any]] = Field(None, description="Resource requirements")
    labels: Optional[Dict[str, str]] = Field(None, description="Labels")


class DeploymentUpdateRequest(BaseModel):
    image: Optional[str] = None
    replicas: Optional[int] = Field(None, ge=1)
    environment: Optional[Dict[str, str]] = None
    resources: Optional[Dict[str, Any]] = None


class ScalingRequest(BaseModel):
    replicas: int = Field(..., ge=1, description="Target replica count")


class VerticalScalingRequest(BaseModel):
    cpu: Optional[str] = Field(None, description="CPU limit (e.g., '500m')")
    memory: Optional[str] = Field(None, description="Memory limit (e.g., '1Gi')")


class AutoscalingPolicyRequest(BaseModel):
    name: str = Field(..., description="Policy name")
    target_id: str = Field(..., description="Target deployment ID")
    scaling_type: str = Field("horizontal", description="Horizontal or vertical")
    min_replicas: int = Field(1, ge=1)
    max_replicas: int = Field(10, ge=1)
    target_metric: str = Field("cpu", description="Metric to track")
    target_value: float = Field(80.0, gt=0)


class AgentRequest(BaseModel):
    name: str = Field(..., description="Agent name")
    agent_type: str = Field(..., description="Agent type")
    version: str = Field("1.0.0", description="Agent version")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    auto_start: bool = Field(False, description="Start immediately")


class AgentUpdateRequest(BaseModel):
    version: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    restart: bool = Field(True, description="Restart after update")


# Initialize FastAPI app
app = FastAPI(
    title="Temporal Control Plane API",
    description="RESTful API for deploying, scaling, monitoring, and managing cloud infrastructure",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API instances
deployment_api = DeploymentAPI()
scaling_api = ScalingAPI()
monitoring_api = MonitoringAPI()
lifecycle_api = LifecycleAPI()


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


# Deployment endpoints
@app.post("/api/v1/deployments", tags=["Deployment"])
async def create_deployment(request: DeploymentRequest):
    """Create a new deployment"""
    try:
        result = deployment_api.create_deployment(
            name=request.name,
            deployment_type=request.deployment_type,
            image=request.image,
            replicas=request.replicas,
            strategy=request.strategy,
            environment=request.environment,
            resources=request.resources,
            labels=request.labels,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/deployments", tags=["Deployment"])
async def list_deployments(
    deployment_type: Optional[str] = None,
    status: Optional[str] = None,
):
    """List deployments with optional filters"""
    return deployment_api.list_deployments(
        deployment_type=deployment_type,
        status=status,
    )


@app.get("/api/v1/deployments/{deployment_id}", tags=["Deployment"])
async def get_deployment(deployment_id: str):
    """Get deployment by ID"""
    result = deployment_api.get_deployment(deployment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return result


@app.put("/api/v1/deployments/{deployment_id}", tags=["Deployment"])
async def update_deployment(deployment_id: str, request: DeploymentUpdateRequest):
    """Update a deployment"""
    result = deployment_api.update_deployment(
        deployment_id=deployment_id,
        image=request.image,
        replicas=request.replicas,
        environment=request.environment,
        resources=request.resources,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return result


@app.delete("/api/v1/deployments/{deployment_id}", tags=["Deployment"])
async def delete_deployment(deployment_id: str):
    """Delete a deployment"""
    success = deployment_api.delete_deployment(deployment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return {"success": True}


@app.post("/api/v1/deployments/{deployment_id}/rollback", tags=["Deployment"])
async def rollback_deployment(deployment_id: str, revision: Optional[int] = None):
    """Rollback deployment to previous revision"""
    result = deployment_api.rollback_deployment(deployment_id, revision)
    if not result:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return result


# Scaling endpoints
@app.post("/api/v1/scaling/{deployment_id}/horizontal", tags=["Scaling"])
async def scale_horizontal(deployment_id: str, request: ScalingRequest):
    """Scale deployment horizontally"""
    return scaling_api.scale_horizontal(deployment_id, request.replicas)


@app.post("/api/v1/scaling/{deployment_id}/vertical", tags=["Scaling"])
async def scale_vertical(deployment_id: str, request: VerticalScalingRequest):
    """Scale deployment vertically"""
    return scaling_api.scale_vertical(
        deployment_id,
        cpu=request.cpu,
        memory=request.memory,
    )


@app.post("/api/v1/scaling/policies", tags=["Scaling"])
async def create_autoscaling_policy(request: AutoscalingPolicyRequest):
    """Create autoscaling policy"""
    try:
        return scaling_api.create_autoscaling_policy(
            name=request.name,
            target_id=request.target_id,
            scaling_type=request.scaling_type,
            min_replicas=request.min_replicas,
            max_replicas=request.max_replicas,
            target_metric=request.target_metric,
            target_value=request.target_value,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/scaling/policies", tags=["Scaling"])
async def list_autoscaling_policies(
    target_id: Optional[str] = None,
    enabled: Optional[bool] = None,
):
    """List autoscaling policies"""
    return scaling_api.list_autoscaling_policies(target_id, enabled)


@app.get("/api/v1/scaling/policies/{policy_id}", tags=["Scaling"])
async def get_autoscaling_policy(policy_id: str):
    """Get autoscaling policy"""
    result = scaling_api.get_autoscaling_policy(policy_id)
    if not result:
        raise HTTPException(status_code=404, detail="Policy not found")
    return result


@app.delete("/api/v1/scaling/policies/{policy_id}", tags=["Scaling"])
async def delete_autoscaling_policy(policy_id: str):
    """Delete autoscaling policy"""
    success = scaling_api.delete_autoscaling_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"success": True}


@app.get("/api/v1/scaling/history", tags=["Scaling"])
async def get_scaling_history(
    deployment_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """Get scaling operation history"""
    return scaling_api.get_scaling_history(deployment_id, limit)


# Monitoring endpoints
@app.get("/api/v1/monitoring/metrics", tags=["Monitoring"])
async def query_metrics(
    metric_name: str,
    deployment_id: Optional[str] = None,
    aggregation: str = "avg",
):
    """Query metrics"""
    return monitoring_api.query_metrics(
        metric_name=metric_name,
        deployment_id=deployment_id,
        aggregation=aggregation,
    )


@app.get("/api/v1/monitoring/metrics/available", tags=["Monitoring"])
async def get_available_metrics(deployment_id: Optional[str] = None):
    """Get available metrics"""
    return monitoring_api.get_available_metrics(deployment_id)


@app.get("/api/v1/monitoring/logs", tags=["Monitoring"])
async def query_logs(
    deployment_id: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """Query logs"""
    return monitoring_api.query_logs(
        deployment_id=deployment_id,
        level=level,
        search=search,
        limit=limit,
    )


@app.get("/api/v1/monitoring/traces", tags=["Monitoring"])
async def query_traces(
    deployment_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    min_duration: Optional[float] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """Query distributed traces"""
    return monitoring_api.query_traces(
        deployment_id=deployment_id,
        trace_id=trace_id,
        min_duration=min_duration,
        limit=limit,
    )


@app.get("/api/v1/monitoring/health/{deployment_id}", tags=["Monitoring"])
async def get_health_status(deployment_id: str):
    """Get health status"""
    return monitoring_api.get_health_status(deployment_id)


@app.get("/api/v1/monitoring/dashboard", tags=["Monitoring"])
async def get_dashboard_data(deployment_id: Optional[str] = None):
    """Get dashboard data"""
    return monitoring_api.get_dashboard_data(deployment_id)


# Lifecycle endpoints
@app.post("/api/v1/agents", tags=["Lifecycle"])
async def create_agent(request: AgentRequest):
    """Create a new agent"""
    try:
        return lifecycle_api.create_agent(
            name=request.name,
            agent_type=request.agent_type,
            version=request.version,
            config=request.config,
            auto_start=request.auto_start,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/agents", tags=["Lifecycle"])
async def list_agents(
    agent_type: Optional[str] = None,
    state: Optional[str] = None,
):
    """List agents"""
    return lifecycle_api.list_agents(agent_type, state)


@app.get("/api/v1/agents/{agent_id}", tags=["Lifecycle"])
async def get_agent(agent_id: str):
    """Get agent by ID"""
    result = lifecycle_api.get_agent(agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.post("/api/v1/agents/{agent_id}/start", tags=["Lifecycle"])
async def start_agent(agent_id: str):
    """Start an agent"""
    result = lifecycle_api.start_agent(agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.post("/api/v1/agents/{agent_id}/stop", tags=["Lifecycle"])
async def stop_agent(agent_id: str, graceful: bool = True):
    """Stop an agent"""
    result = lifecycle_api.stop_agent(agent_id, graceful)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.post("/api/v1/agents/{agent_id}/restart", tags=["Lifecycle"])
async def restart_agent(agent_id: str):
    """Restart an agent"""
    result = lifecycle_api.restart_agent(agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.put("/api/v1/agents/{agent_id}", tags=["Lifecycle"])
async def update_agent(agent_id: str, request: AgentUpdateRequest):
    """Update agent configuration"""
    result = lifecycle_api.update_agent(
        agent_id=agent_id,
        version=request.version,
        config=request.config,
        restart=request.restart,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.post("/api/v1/agents/{agent_id}/pause", tags=["Lifecycle"])
async def pause_agent(agent_id: str):
    """Pause agent"""
    result = lifecycle_api.pause_agent(agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.post("/api/v1/agents/{agent_id}/resume", tags=["Lifecycle"])
async def resume_agent(agent_id: str):
    """Resume agent"""
    result = lifecycle_api.resume_agent(agent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.delete("/api/v1/agents/{agent_id}", tags=["Lifecycle"])
async def delete_agent(agent_id: str, force: bool = False):
    """Delete an agent"""
    result = lifecycle_api.delete_agent(agent_id, force)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found")
    return result


@app.get("/api/v1/agents/operations/history", tags=["Lifecycle"])
async def get_operation_history(
    agent_id: Optional[str] = None,
    operation: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """Get operation history"""
    return lifecycle_api.get_operation_history(agent_id, operation, limit)


class ControlPlaneServer:
    """Control Plane Server wrapper"""
    
    def __init__(self):
        self.app = app
        
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the server"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    server = ControlPlaneServer()
    server.run()
