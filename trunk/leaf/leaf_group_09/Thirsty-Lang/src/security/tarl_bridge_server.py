# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / tarl_bridge_server.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / tarl_bridge_server.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
#!/usr/bin/env python3
"""
T.A.R.L. Bridge Server - Python side of JS <-> Python bridge
Provides policy enforcement services to JavaScript runtime
"""

import sys
import json
import os
import traceback
from pathlib import Path

# Add tarl to path
tarl_path = Path(__file__).parent.parent.parent / 'tarl'
sys.path.insert(0, str(tarl_path.parent))

from tarl import TarlRuntime, TarlPolicy, TarlDecision, TarlVerdict


class TarlBridgeServer:
    """Bridge server handling requests from JavaScript"""
    
    def __init__(self):
        self.runtime = None
        self.policies = []
        self.policy_path = None
        self.metrics = {
            'requests': 0,
            'errors': 0
        }
    
    def initialize(self):
        """Initialize with default policies"""
        # Default allow-all policy
        default_policy = TarlPolicy(
            "default_allow",
            lambda ctx: TarlDecision(TarlVerdict.ALLOW, "Default policy")
        )
        self.policies = [default_policy]
        self.runtime = TarlRuntime(self.policies)
        self.send_response({'type': 'ready', 'status': 'initialized'})
    
    def handle_request(self, request):
        """Handle incoming request"""
        self.metrics['requests'] += 1
        
        try:
            method = request.get('method')
            params = request.get('params', {})
            req_id = request.get('id')
            
            if method == 'evaluate_policy':
                result = self.evaluate_policy(params.get('context', {}))
            elif method == 'load_policies':
                result = self.load_policies(params.get('path'))
            elif method == 'reload_policies':
                result = self.reload_policies()
            elif method == 'get_metrics':
                result = self.get_metrics()
            elif method == 'shutdown':
                result = {'status': 'shutdown'}
                self.send_response({'type': 'response', 'id': req_id, 'result': result})
                sys.exit(0)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            self.send_response({'type': 'response', 'id': req_id, 'result': result})
            
        except Exception as e:
            self.metrics['errors'] += 1
            self.send_response({
                'type': 'response', 
                'id': request.get('id'), 
                'error': str(e),
                'traceback': traceback.format_exc()
            })
    
    def evaluate_policy(self, context):
        """Evaluate policy against context"""
        if not self.runtime:
            raise RuntimeError("Runtime not initialized")
        
        decision = self.runtime.evaluate(context)
        
        return {
            'verdict': decision.verdict.value,
            'reason': decision.reason,
            'metadata': decision.metadata
        }
    
    def load_policies(self, policy_path):
        """Load policies from file"""
        self.policy_path = policy_path
        
        if not os.path.exists(policy_path):
            raise FileNotFoundError(f"Policy file not found: {policy_path}")
        
        # Load policies from JSON/YAML
        with open(policy_path, 'r') as f:
            if policy_path.endswith('.json'):
                policy_data = json.load(f)
            elif policy_path.endswith('.yaml') or policy_path.endswith('.yml'):
                import yaml
                policy_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported policy file format: {policy_path}")
        
        # Convert to TarlPolicy objects
        policies = self._parse_policies(policy_data)
        self.policies = policies
        self.runtime = TarlRuntime(self.policies)
        
        return {
            'status': 'loaded',
            'policy_count': len(policies),
            'path': policy_path
        }
    
    def reload_policies(self):
        """Reload policies from previously loaded path"""
        if not self.policy_path:
            raise RuntimeError("No policy file loaded")
        
        return self.load_policies(self.policy_path)
    
    def _parse_policies(self, policy_data):
        """Parse policy data into TarlPolicy objects"""
        policies = []
        
        for policy_def in policy_data.get('policies', []):
            name = policy_def.get('name', 'unnamed')
            rules = policy_def.get('rules', [])
            
            # Create policy function
            def make_policy_fn(rules_list):
                def policy_fn(context):
                    for rule in rules_list:
                        condition = rule.get('condition', {})
                        if self._evaluate_condition(condition, context):
                            verdict = TarlVerdict[rule.get('verdict', 'ALLOW').upper()]
                            reason = rule.get('reason', 'Policy rule matched')
                            return TarlDecision(verdict, reason)
                    return TarlDecision(TarlVerdict.ALLOW, "No rules matched")
                return policy_fn
            
            policy = TarlPolicy(name, make_policy_fn(rules))
            policies.append(policy)
        
        return policies
    
    def _evaluate_condition(self, condition, context):
        """Evaluate a condition against context"""
        if not condition:
            return True
        
        # Simple condition evaluation
        for key, expected in condition.items():
            if key not in context:
                return False
            if context[key] != expected:
                return False
        
        return True
    
    def get_metrics(self):
        """Get runtime and bridge metrics"""
        runtime_metrics = self.runtime.get_performance_metrics() if self.runtime else {}
        
        return {
            'bridge': self.metrics,
            'runtime': runtime_metrics
        }
    
    def send_response(self, response):
        """Send response to stdout"""
        sys.stdout.write(json.dumps(response) + '\n')
        sys.stdout.flush()
    
    def run(self):
        """Main server loop"""
        self.initialize()
        
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                self.handle_request(request)
            except json.JSONDecodeError as e:
                self.send_response({
                    'type': 'error',
                    'error': f"Invalid JSON: {e}"
                })
            except Exception as e:
                self.send_response({
                    'type': 'error',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })


if __name__ == '__main__':
    server = TarlBridgeServer()
    server.run()
