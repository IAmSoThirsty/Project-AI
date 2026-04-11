#!/usr/bin/env python3
"""
Control Plane Integration Test

Demonstrates complete workflow using all APIs.
"""

import sys
import time
from temporal.controlplane.api.deployment import DeploymentAPI
from temporal.controlplane.api.scaling import ScalingAPI
from temporal.controlplane.api.monitoring import MonitoringAPI
from temporal.controlplane.api.lifecycle import LifecycleAPI


def print_section(title):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_deployment_workflow():
    """Demonstrate deployment workflow"""
    print_section("DEPLOYMENT WORKFLOW")
    
    api = DeploymentAPI()
    
    # Create deployment
    print("1. Creating deployment...")
    deployment = api.create_deployment(
        name="demo-app",
        deployment_type="agent",
        image="demo:v1.0.0",
        replicas=3,
        strategy="rolling_update",
        environment={"ENV": "production"},
        resources={"cpu": "500m", "memory": "1Gi"},
    )
    deployment_id = deployment["id"]
    print(f"   ✓ Created deployment: {deployment_id}")
    print(f"   Status: {deployment['status']}")
    
    # List deployments
    print("\n2. Listing all deployments...")
    deployments = api.list_deployments()
    print(f"   ✓ Found {len(deployments)} deployment(s)")
    
    # Update deployment
    print("\n3. Updating deployment to v2.0.0...")
    updated = api.update_deployment(
        deployment_id,
        image="demo:v2.0.0",
        replicas=5,
    )
    print(f"   ✓ Updated to revision {updated['revision']}")
    print(f"   Image: {updated['image']}")
    print(f"   Replicas: {updated['replicas']}")
    
    # Rollback
    print("\n4. Rolling back deployment...")
    rolled_back = api.rollback_deployment(deployment_id)
    print(f"   ✓ Rolled back to revision {rolled_back['revision']}")
    
    return deployment_id


def demo_scaling_workflow(deployment_id):
    """Demonstrate scaling workflow"""
    print_section("SCALING WORKFLOW")
    
    api = ScalingAPI()
    
    # Horizontal scaling
    print("1. Scaling horizontally to 10 replicas...")
    result = api.scale_horizontal(deployment_id, 10)
    print(f"   ✓ Scaled to {result['target_replicas']} replicas")
    
    # Vertical scaling
    print("\n2. Scaling vertically...")
    result = api.scale_vertical(
        deployment_id,
        cpu="2000m",
        memory="4Gi",
    )
    print(f"   ✓ Resources: CPU={result['resources']['cpu']}, Memory={result['resources']['memory']}")
    
    # Create autoscaling policy
    print("\n3. Creating autoscaling policy...")
    policy = api.create_autoscaling_policy(
        name="demo-autoscale",
        target_id=deployment_id,
        min_replicas=2,
        max_replicas=20,
        target_metric="cpu",
        target_value=75.0,
    )
    print(f"   ✓ Policy created: {policy['id']}")
    print(f"   Range: {policy['min_replicas']} - {policy['max_replicas']} replicas")
    print(f"   Target: {policy['target_metric']} @ {policy['target_value']}%")
    
    # List policies
    print("\n4. Listing autoscaling policies...")
    policies = api.list_autoscaling_policies()
    print(f"   ✓ Found {len(policies)} policy(ies)")
    
    return policy["id"]


def demo_monitoring_workflow(deployment_id):
    """Demonstrate monitoring workflow"""
    print_section("MONITORING WORKFLOW")
    
    api = MonitoringAPI()
    
    # Query metrics
    print("1. Querying CPU metrics...")
    metrics = api.query_metrics("cpu_usage", deployment_id=deployment_id)
    print(f"   ✓ Metric: {metrics['metric']}")
    print(f"   Data points: {len(metrics['data_points'])}")
    print(f"   Average: {metrics['summary']['avg']:.2f}%")
    print(f"   Min/Max: {metrics['summary']['min']:.2f}% / {metrics['summary']['max']:.2f}%")
    
    # List available metrics
    print("\n2. Available metrics...")
    available = api.get_available_metrics()
    print(f"   ✓ {len(available)} metrics available:")
    for metric in available[:5]:
        print(f"      - {metric['name']} ({metric['type']}) [{metric['unit']}]")
    
    # Query logs
    print("\n3. Querying logs...")
    logs = api.query_logs(deployment_id=deployment_id, limit=10)
    print(f"   ✓ Total logs: {logs['total']}")
    print(f"   Showing: {len(logs['logs'])} entries")
    
    # Query traces
    print("\n4. Querying traces...")
    traces = api.query_traces(deployment_id=deployment_id, limit=5)
    print(f"   ✓ Total traces: {traces['total']}")
    print(f"   Showing: {len(traces['traces'])} traces")
    
    # Health status
    print("\n5. Checking health status...")
    health = api.get_health_status(deployment_id)
    print(f"   ✓ Status: {health['status']}")
    print(f"   Liveness: {health['checks']['liveness']}")
    print(f"   Readiness: {health['checks']['readiness']}")
    
    # Dashboard
    print("\n6. Getting dashboard data...")
    dashboard = api.get_dashboard_data()
    print(f"   ✓ Total deployments: {dashboard['summary']['total_deployments']}")
    print(f"   Healthy: {dashboard['summary']['healthy_deployments']}")
    print(f"   Avg CPU: {dashboard['metrics']['avg_cpu_usage']:.2f}%")
    print(f"   Avg Memory: {dashboard['metrics']['avg_memory_usage']:.2f}%")


def demo_lifecycle_workflow():
    """Demonstrate lifecycle workflow"""
    print_section("LIFECYCLE WORKFLOW")
    
    api = LifecycleAPI()
    
    # Create agent
    print("1. Creating agent...")
    agent = api.create_agent(
        name="demo-worker",
        agent_type="worker",
        version="1.0.0",
        config={"max_tasks": 10},
        auto_start=False,
    )
    agent_id = agent["id"]
    print(f"   ✓ Created agent: {agent_id}")
    print(f"   State: {agent['state']}")
    
    # Start agent
    print("\n2. Starting agent...")
    result = api.start_agent(agent_id)
    print(f"   ✓ Agent started")
    print(f"   State: {result['agent']['state']}")
    
    # List agents
    print("\n3. Listing agents...")
    agents = api.list_agents()
    print(f"   ✓ Found {len(agents)} agent(s)")
    
    # Update agent
    print("\n4. Updating agent to v2.0.0...")
    updated = api.update_agent(
        agent_id,
        version="2.0.0",
        config={"max_tasks": 20},
        restart=True,
    )
    print(f"   ✓ Updated to version {updated['agent']['version']}")
    print(f"   Restarts: {updated['agent']['restarts']}")
    
    # Restart agent
    print("\n5. Restarting agent...")
    restarted = api.restart_agent(agent_id)
    print(f"   ✓ Agent restarted")
    print(f"   Total restarts: {restarted['agent']['restarts']}")
    
    # Pause agent
    print("\n6. Pausing agent...")
    paused = api.pause_agent(agent_id)
    print(f"   ✓ Agent paused")
    
    # Resume agent
    print("\n7. Resuming agent...")
    resumed = api.resume_agent(agent_id)
    print(f"   ✓ Agent resumed")
    
    # Operation history
    print("\n8. Getting operation history...")
    history = api.get_operation_history(agent_id=agent_id)
    print(f"   ✓ Found {len(history)} operation(s):")
    for op in history[-5:]:
        print(f"      - {op['operation']} @ {op['timestamp']}")
    
    # Stop agent
    print("\n9. Stopping agent...")
    stopped = api.stop_agent(agent_id)
    print(f"   ✓ Agent stopped")
    
    return agent_id


def main():
    """Run integration test"""
    print("\n" + "="*60)
    print("  CONTROL PLANE INTEGRATION TEST")
    print("="*60)
    print("\nThis test demonstrates all Control Plane APIs working together.\n")
    
    try:
        # Run workflows
        deployment_id = demo_deployment_workflow()
        policy_id = demo_scaling_workflow(deployment_id)
        demo_monitoring_workflow(deployment_id)
        agent_id = demo_lifecycle_workflow()
        
        # Summary
        print_section("TEST SUMMARY")
        print("✓ All workflows completed successfully!\n")
        print("Resources created:")
        print(f"  - Deployment: {deployment_id}")
        print(f"  - Autoscaling Policy: {policy_id}")
        print(f"  - Agent: {agent_id}")
        print("\nAll Control Plane APIs are functioning correctly.")
        print("\nNext steps:")
        print("  1. Start the API server: uvicorn temporal.controlplane.api.server:app")
        print("  2. Open the dashboard: temporal/controlplane/web/dashboard.html")
        print("  3. Use the CLI: python -m temporal.controlplane.cli.commands")
        print("\n" + "="*60 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
