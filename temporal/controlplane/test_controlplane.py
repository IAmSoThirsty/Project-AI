"""
Test suite for Control Plane API
"""

import pytest
from temporal.controlplane.api.deployment import DeploymentAPI
from temporal.controlplane.api.scaling import ScalingAPI
from temporal.controlplane.api.monitoring import MonitoringAPI
from temporal.controlplane.api.lifecycle import LifecycleAPI


class TestDeploymentAPI:
    """Test Deployment API"""
    
    def setup_method(self):
        self.api = DeploymentAPI()
    
    def test_create_deployment(self):
        result = self.api.create_deployment(
            name="test-deployment",
            deployment_type="agent",
            image="test:latest",
            replicas=3,
        )
        
        assert result["name"] == "test-deployment"
        assert result["type"] == "agent"
        assert result["replicas"] == 3
        assert result["status"] == "deployed"
    
    def test_list_deployments(self):
        self.api.create_deployment("test-1", "agent", "test:1")
        self.api.create_deployment("test-2", "workflow", "test:2")
        
        all_deployments = self.api.list_deployments()
        assert len(all_deployments) == 2
        
        agents = self.api.list_deployments(deployment_type="agent")
        assert len(agents) == 1
    
    def test_get_deployment(self):
        created = self.api.create_deployment("test", "agent", "test:latest")
        deployment_id = created["id"]
        
        result = self.api.get_deployment(deployment_id)
        assert result is not None
        assert result["id"] == deployment_id
    
    def test_update_deployment(self):
        created = self.api.create_deployment("test", "agent", "test:v1")
        deployment_id = created["id"]
        
        updated = self.api.update_deployment(
            deployment_id,
            image="test:v2",
            replicas=5,
        )
        
        assert updated["image"] == "test:v2"
        assert updated["replicas"] == 5
        assert updated["revision"] == 2
    
    def test_delete_deployment(self):
        created = self.api.create_deployment("test", "agent", "test:latest")
        deployment_id = created["id"]
        
        success = self.api.delete_deployment(deployment_id)
        assert success is True
        
        result = self.api.get_deployment(deployment_id)
        assert result is None
    
    def test_rollback_deployment(self):
        created = self.api.create_deployment("test", "agent", "test:v1")
        deployment_id = created["id"]
        
        self.api.update_deployment(deployment_id, image="test:v2")
        
        rolled_back = self.api.rollback_deployment(deployment_id)
        assert rolled_back["revision"] == 1


class TestScalingAPI:
    """Test Scaling API"""
    
    def setup_method(self):
        self.api = ScalingAPI()
    
    def test_scale_horizontal(self):
        result = self.api.scale_horizontal("deploy-123", 5)
        
        assert result["type"] == "horizontal"
        assert result["target_replicas"] == 5
        assert result["status"] == "completed"
    
    def test_scale_vertical(self):
        result = self.api.scale_vertical(
            "deploy-123",
            cpu="1000m",
            memory="2Gi",
        )
        
        assert result["type"] == "vertical"
        assert result["resources"]["cpu"] == "1000m"
        assert result["resources"]["memory"] == "2Gi"
    
    def test_create_autoscaling_policy(self):
        result = self.api.create_autoscaling_policy(
            name="test-policy",
            target_id="deploy-123",
            min_replicas=2,
            max_replicas=10,
        )
        
        assert result["name"] == "test-policy"
        assert result["min_replicas"] == 2
        assert result["max_replicas"] == 10
        assert result["enabled"] is True
    
    def test_list_autoscaling_policies(self):
        self.api.create_autoscaling_policy("policy-1", "deploy-1")
        self.api.create_autoscaling_policy("policy-2", "deploy-2")
        
        all_policies = self.api.list_autoscaling_policies()
        assert len(all_policies) == 2
        
        filtered = self.api.list_autoscaling_policies(target_id="deploy-1")
        assert len(filtered) == 1
    
    def test_update_autoscaling_policy(self):
        created = self.api.create_autoscaling_policy("test", "deploy-123")
        policy_id = created["id"]
        
        updated = self.api.update_autoscaling_policy(
            policy_id,
            max_replicas=20,
            enabled=False,
        )
        
        assert updated["max_replicas"] == 20
        assert updated["enabled"] is False
    
    def test_get_scaling_history(self):
        self.api.scale_horizontal("deploy-123", 3)
        self.api.scale_horizontal("deploy-123", 5)
        
        history = self.api.get_scaling_history()
        assert len(history) >= 2


class TestMonitoringAPI:
    """Test Monitoring API"""
    
    def setup_method(self):
        self.api = MonitoringAPI()
    
    def test_query_metrics(self):
        result = self.api.query_metrics("cpu_usage")
        
        assert result["metric"] == "cpu_usage"
        assert "data_points" in result
        assert "summary" in result
        assert "avg" in result["summary"]
    
    def test_get_available_metrics(self):
        metrics = self.api.get_available_metrics()
        
        assert len(metrics) > 0
        assert any(m["name"] == "cpu_usage" for m in metrics)
        assert any(m["name"] == "memory_usage" for m in metrics)
    
    def test_query_logs(self):
        result = self.api.query_logs(level="error", limit=50)
        
        assert "total" in result
        assert "logs" in result
        assert len(result["logs"]) <= 50
    
    def test_query_traces(self):
        result = self.api.query_traces(min_duration=100.0)
        
        assert "total" in result
        assert "traces" in result
    
    def test_get_health_status(self):
        result = self.api.get_health_status("deploy-123")
        
        assert result["deployment_id"] == "deploy-123"
        assert "status" in result
        assert "checks" in result
        assert "metrics" in result
    
    def test_get_dashboard_data(self):
        result = self.api.get_dashboard_data()
        
        assert "summary" in result
        assert "metrics" in result
        assert "alerts" in result


class TestLifecycleAPI:
    """Test Lifecycle API"""
    
    def setup_method(self):
        self.api = LifecycleAPI()
    
    def test_create_agent(self):
        result = self.api.create_agent(
            name="test-agent",
            agent_type="worker",
            version="1.0.0",
        )
        
        assert result["name"] == "test-agent"
        assert result["type"] == "worker"
        assert result["version"] == "1.0.0"
        assert result["state"] == "stopped"
    
    def test_list_agents(self):
        self.api.create_agent("agent-1", "worker", "1.0.0")
        self.api.create_agent("agent-2", "processor", "1.0.0")
        
        all_agents = self.api.list_agents()
        assert len(all_agents) == 2
        
        workers = self.api.list_agents(agent_type="worker")
        assert len(workers) == 1
    
    def test_start_agent(self):
        created = self.api.create_agent("test", "worker", "1.0.0")
        agent_id = created["id"]
        
        result = self.api.start_agent(agent_id)
        assert result["agent"]["state"] == "running"
    
    def test_stop_agent(self):
        created = self.api.create_agent("test", "worker", "1.0.0", auto_start=True)
        agent_id = created["id"]
        
        result = self.api.stop_agent(agent_id)
        assert result["agent"]["state"] == "stopped"
    
    def test_restart_agent(self):
        created = self.api.create_agent("test", "worker", "1.0.0", auto_start=True)
        agent_id = created["id"]
        
        result = self.api.restart_agent(agent_id)
        assert result["agent"]["state"] == "running"
        assert result["agent"]["restarts"] == 1
    
    def test_update_agent(self):
        created = self.api.create_agent("test", "worker", "1.0.0")
        agent_id = created["id"]
        
        result = self.api.update_agent(
            agent_id,
            version="2.0.0",
            config={"max_tasks": 20},
        )
        
        assert result["agent"]["version"] == "2.0.0"
        assert result["agent"]["config"]["max_tasks"] == 20
    
    def test_delete_agent(self):
        created = self.api.create_agent("test", "worker", "1.0.0")
        agent_id = created["id"]
        
        result = self.api.delete_agent(agent_id)
        assert result["success"] is True
    
    def test_get_operation_history(self):
        created = self.api.create_agent("test", "worker", "1.0.0")
        agent_id = created["id"]
        
        self.api.start_agent(agent_id)
        self.api.stop_agent(agent_id)
        
        history = self.api.get_operation_history(agent_id=agent_id)
        assert len(history) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
