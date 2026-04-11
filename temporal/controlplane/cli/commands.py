"""
Control Plane CLI

Command-line interface for control plane operations.
"""

import click
import requests
import json
from typing import Optional
from datetime import datetime


class ControlPlaneClient:
    """Client for control plane API"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        
    def _request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.text else {}
    
    def get(self, endpoint: str, **kwargs):
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs):
        return self._request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs):
        return self._request("PUT", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)


@click.group()
@click.option('--api-url', default='http://localhost:8000/api/v1', help='Control plane API URL')
@click.pass_context
def cli(ctx, api_url):
    """Control Plane CLI - Manage deployments, scaling, and monitoring"""
    ctx.ensure_object(dict)
    ctx.obj['client'] = ControlPlaneClient(api_url)


# Deployment commands
@cli.group()
def deployment():
    """Deployment management commands"""
    pass


@deployment.command('create')
@click.option('--name', required=True, help='Deployment name')
@click.option('--type', 'deployment_type', required=True, type=click.Choice(['agent', 'workflow', 'service']))
@click.option('--image', required=True, help='Container image')
@click.option('--replicas', default=1, help='Number of replicas')
@click.option('--strategy', default='rolling_update', type=click.Choice(['recreate', 'rolling_update', 'blue_green', 'canary']))
@click.pass_context
def create_deployment(ctx, name, deployment_type, image, replicas, strategy):
    """Create a new deployment"""
    client = ctx.obj['client']
    
    data = {
        "name": name,
        "deployment_type": deployment_type,
        "image": image,
        "replicas": replicas,
        "strategy": strategy,
    }
    
    try:
        result = client.post("deployments", json=data)
        click.echo(f"✓ Deployment created: {result['id']}")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@deployment.command('list')
@click.option('--type', 'deployment_type', help='Filter by type')
@click.option('--status', help='Filter by status')
@click.pass_context
def list_deployments(ctx, deployment_type, status):
    """List deployments"""
    client = ctx.obj['client']
    
    params = {}
    if deployment_type:
        params['deployment_type'] = deployment_type
    if status:
        params['status'] = status
    
    try:
        result = client.get("deployments", params=params)
        click.echo(f"Found {len(result)} deployment(s):\n")
        
        for dep in result:
            click.echo(f"  {dep['id']}: {dep['name']} ({dep['type']}) - {dep['status']}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@deployment.command('get')
@click.argument('deployment_id')
@click.pass_context
def get_deployment(ctx, deployment_id):
    """Get deployment details"""
    client = ctx.obj['client']
    
    try:
        result = client.get(f"deployments/{deployment_id}")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@deployment.command('delete')
@click.argument('deployment_id')
@click.confirmation_option(prompt='Are you sure you want to delete this deployment?')
@click.pass_context
def delete_deployment(ctx, deployment_id):
    """Delete a deployment"""
    client = ctx.obj['client']
    
    try:
        client.delete(f"deployments/{deployment_id}")
        click.echo(f"✓ Deployment deleted: {deployment_id}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@deployment.command('rollback')
@click.argument('deployment_id')
@click.option('--revision', type=int, help='Target revision')
@click.pass_context
def rollback_deployment(ctx, deployment_id, revision):
    """Rollback deployment"""
    client = ctx.obj['client']
    
    params = {}
    if revision:
        params['revision'] = revision
    
    try:
        result = client.post(f"deployments/{deployment_id}/rollback", params=params)
        click.echo(f"✓ Deployment rolled back to revision {result['revision']}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


# Scaling commands
@cli.group()
def scaling():
    """Scaling management commands"""
    pass


@scaling.command('horizontal')
@click.argument('deployment_id')
@click.option('--replicas', required=True, type=int, help='Target replica count')
@click.pass_context
def scale_horizontal(ctx, deployment_id, replicas):
    """Scale deployment horizontally"""
    client = ctx.obj['client']
    
    try:
        result = client.post(f"scaling/{deployment_id}/horizontal", json={"replicas": replicas})
        click.echo(f"✓ Scaled to {replicas} replicas")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@scaling.command('vertical')
@click.argument('deployment_id')
@click.option('--cpu', help='CPU limit (e.g., 500m)')
@click.option('--memory', help='Memory limit (e.g., 1Gi)')
@click.pass_context
def scale_vertical(ctx, deployment_id, cpu, memory):
    """Scale deployment vertically"""
    client = ctx.obj['client']
    
    data = {}
    if cpu:
        data['cpu'] = cpu
    if memory:
        data['memory'] = memory
    
    try:
        result = client.post(f"scaling/{deployment_id}/vertical", json=data)
        click.echo("✓ Vertical scaling completed")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@scaling.command('autoscale')
@click.option('--name', required=True, help='Policy name')
@click.option('--target', required=True, help='Target deployment ID')
@click.option('--min', 'min_replicas', default=1, help='Minimum replicas')
@click.option('--max', 'max_replicas', default=10, help='Maximum replicas')
@click.option('--metric', default='cpu', type=click.Choice(['cpu', 'memory', 'requests']))
@click.option('--value', 'target_value', default=80.0, help='Target metric value')
@click.pass_context
def create_autoscale_policy(ctx, name, target, min_replicas, max_replicas, metric, target_value):
    """Create autoscaling policy"""
    client = ctx.obj['client']
    
    data = {
        "name": name,
        "target_id": target,
        "min_replicas": min_replicas,
        "max_replicas": max_replicas,
        "target_metric": metric,
        "target_value": target_value,
    }
    
    try:
        result = client.post("scaling/policies", json=data)
        click.echo(f"✓ Autoscaling policy created: {result['id']}")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


# Monitoring commands
@cli.group()
def monitoring():
    """Monitoring commands"""
    pass


@monitoring.command('metrics')
@click.option('--metric', required=True, help='Metric name')
@click.option('--deployment', help='Deployment ID')
@click.pass_context
def query_metrics(ctx, metric, deployment):
    """Query metrics"""
    client = ctx.obj['client']
    
    params = {"metric_name": metric}
    if deployment:
        params['deployment_id'] = deployment
    
    try:
        result = client.get("monitoring/metrics", params=params)
        click.echo(f"Metric: {result['metric']}")
        click.echo(f"Summary: avg={result['summary']['avg']:.2f}, min={result['summary']['min']:.2f}, max={result['summary']['max']:.2f}")
        click.echo(f"\nData points: {len(result['data_points'])}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@monitoring.command('logs')
@click.option('--deployment', help='Deployment ID')
@click.option('--level', type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']))
@click.option('--search', help='Search term')
@click.option('--limit', default=100, help='Result limit')
@click.pass_context
def query_logs(ctx, deployment, level, search, limit):
    """Query logs"""
    client = ctx.obj['client']
    
    params = {"limit": limit}
    if deployment:
        params['deployment_id'] = deployment
    if level:
        params['level'] = level
    if search:
        params['search'] = search
    
    try:
        result = client.get("monitoring/logs", params=params)
        click.echo(f"Total logs: {result['total']}\n")
        
        for log in result['logs']:
            click.echo(f"[{log['timestamp']}] {log['level'].upper()}: {log['message']}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@monitoring.command('health')
@click.argument('deployment_id')
@click.pass_context
def get_health(ctx, deployment_id):
    """Get health status"""
    client = ctx.obj['client']
    
    try:
        result = client.get(f"monitoring/health/{deployment_id}")
        click.echo(f"Status: {result['status']}")
        click.echo(f"Checks: {json.dumps(result['checks'], indent=2)}")
        click.echo(f"Metrics: {json.dumps(result['metrics'], indent=2)}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@monitoring.command('dashboard')
@click.pass_context
def get_dashboard(ctx):
    """Get dashboard data"""
    client = ctx.obj['client']
    
    try:
        result = client.get("monitoring/dashboard")
        click.echo("Dashboard Summary:")
        click.echo(json.dumps(result['summary'], indent=2))
        click.echo("\nMetrics:")
        click.echo(json.dumps(result['metrics'], indent=2))
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


# Agent lifecycle commands
@cli.group()
def agent():
    """Agent lifecycle management commands"""
    pass


@agent.command('create')
@click.option('--name', required=True, help='Agent name')
@click.option('--type', 'agent_type', required=True, help='Agent type')
@click.option('--version', default='1.0.0', help='Agent version')
@click.option('--start', is_flag=True, help='Start immediately')
@click.pass_context
def create_agent(ctx, name, agent_type, version, start):
    """Create a new agent"""
    client = ctx.obj['client']
    
    data = {
        "name": name,
        "agent_type": agent_type,
        "version": version,
        "auto_start": start,
    }
    
    try:
        result = client.post("agents", json=data)
        click.echo(f"✓ Agent created: {result['id']}")
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@agent.command('list')
@click.option('--type', 'agent_type', help='Filter by type')
@click.option('--state', help='Filter by state')
@click.pass_context
def list_agents(ctx, agent_type, state):
    """List agents"""
    client = ctx.obj['client']
    
    params = {}
    if agent_type:
        params['agent_type'] = agent_type
    if state:
        params['state'] = state
    
    try:
        result = client.get("agents", params=params)
        click.echo(f"Found {len(result)} agent(s):\n")
        
        for agent in result:
            click.echo(f"  {agent['id']}: {agent['name']} ({agent['type']}) - {agent['state']}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@agent.command('start')
@click.argument('agent_id')
@click.pass_context
def start_agent(ctx, agent_id):
    """Start an agent"""
    client = ctx.obj['client']
    
    try:
        result = client.post(f"agents/{agent_id}/start")
        click.echo(f"✓ Agent started: {agent_id}")
        click.echo(f"State: {result['agent']['state']}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@agent.command('stop')
@click.argument('agent_id')
@click.option('--force', is_flag=True, help='Force stop')
@click.pass_context
def stop_agent(ctx, agent_id, force):
    """Stop an agent"""
    client = ctx.obj['client']
    
    params = {"graceful": not force}
    
    try:
        result = client.post(f"agents/{agent_id}/stop", params=params)
        click.echo(f"✓ Agent stopped: {agent_id}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@agent.command('restart')
@click.argument('agent_id')
@click.pass_context
def restart_agent(ctx, agent_id):
    """Restart an agent"""
    client = ctx.obj['client']
    
    try:
        result = client.post(f"agents/{agent_id}/restart")
        click.echo(f"✓ Agent restarted: {agent_id}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@agent.command('delete')
@click.argument('agent_id')
@click.option('--force', is_flag=True, help='Force delete')
@click.confirmation_option(prompt='Are you sure you want to delete this agent?')
@click.pass_context
def delete_agent(ctx, agent_id, force):
    """Delete an agent"""
    client = ctx.obj['client']
    
    params = {"force": force}
    
    try:
        client.delete(f"agents/{agent_id}", params=params)
        click.echo(f"✓ Agent deleted: {agent_id}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


class ControlPlaneCLI:
    """Control Plane CLI wrapper"""
    
    @staticmethod
    def run():
        """Run the CLI"""
        cli(obj={})


if __name__ == '__main__':
    ControlPlaneCLI.run()
