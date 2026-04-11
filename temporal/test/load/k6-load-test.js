// k6 Load Testing Script for Temporal Workflows
// Simulates 1000+ concurrent agents executing workflows

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const workflowStarts = new Counter('workflow_starts');
const workflowCompletions = new Counter('workflow_completions');
const workflowFailures = new Counter('workflow_failures');
const workflowDuration = new Trend('workflow_duration_ms');
const workflowSuccessRate = new Rate('workflow_success_rate');

// Test configuration
export const options = {
  scenarios: {
    // Ramp-up scenario: gradually increase load
    ramp_up: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },   // Ramp to 100 agents
        { duration: '3m', target: 500 },   // Ramp to 500 agents
        { duration: '5m', target: 1000 },  // Ramp to 1000 agents
        { duration: '10m', target: 1000 }, // Hold at 1000 agents
        { duration: '5m', target: 0 },     // Ramp down
      ],
      gracefulRampDown: '30s',
    },
    
    // Spike test: sudden burst of traffic
    spike_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 100 },   // Normal load
        { duration: '30s', target: 2000 },  // Spike!
        { duration: '1m', target: 2000 },   // Hold spike
        { duration: '30s', target: 100 },   // Return to normal
        { duration: '30s', target: 0 },     // Ramp down
      ],
      startTime: '30m', // Run after ramp-up test
      gracefulRampDown: '30s',
    },
    
    // Sustained load: constant high load
    sustained_load: {
      executor: 'constant-vus',
      vus: 800,
      duration: '15m',
      startTime: '60m', // Run after spike test
    },
  },
  
  thresholds: {
    // Performance requirements
    'http_req_duration': ['p(95)<2000', 'p(99)<5000'], // 95th percentile < 2s, 99th < 5s
    'workflow_success_rate': ['rate>0.95'],             // >95% success rate
    'workflow_duration_ms': ['p(95)<3000', 'p(99)<8000'],
    'http_req_failed': ['rate<0.05'],                   // <5% HTTP failures
  },
};

// Environment configuration
const TEMPORAL_API_URL = __ENV.TEMPORAL_API_URL || 'http://localhost:8080';
const TEMPORAL_NAMESPACE = __ENV.TEMPORAL_NAMESPACE || 'default';

export default function () {
  const agentId = `agent-${__VU}-${randomString(8)}`;
  const workflowId = `workflow-${agentId}-${Date.now()}`;
  
  group('Temporal Workflow Execution', function () {
    // Step 1: Start workflow
    const startTime = Date.now();
    
    const workflowPayload = JSON.stringify({
      workflowId: workflowId,
      taskQueue: 'load-test-queue',
      namespace: TEMPORAL_NAMESPACE,
      request: {
        input_data: {
          agent_id: agentId,
          operation: 'load_test',
          iteration: __ITER,
          vu: __VU,
        },
        context: {
          test_run: 'k6_load_test',
          correlation_id: workflowId,
        },
        timeout_seconds: 30,
        max_retries: 3,
      },
    });
    
    const startResponse = http.post(
      `${TEMPORAL_API_URL}/api/v1/workflows/start`,
      workflowPayload,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        tags: { operation: 'start_workflow' },
      }
    );
    
    const startSuccess = check(startResponse, {
      'workflow started': (r) => r.status === 200 || r.status === 201,
      'workflow id returned': (r) => r.json('workflowId') !== undefined,
    });
    
    if (startSuccess) {
      workflowStarts.add(1);
      
      // Step 2: Poll for workflow completion
      let completed = false;
      let attempts = 0;
      const maxAttempts = 60; // 60 attempts * 500ms = 30s timeout
      
      while (!completed && attempts < maxAttempts) {
        sleep(0.5);
        
        const statusResponse = http.get(
          `${TEMPORAL_API_URL}/api/v1/workflows/${workflowId}/status`,
          {
            tags: { operation: 'check_status' },
          }
        );
        
        if (statusResponse.status === 200) {
          const status = statusResponse.json('status');
          
          if (status === 'COMPLETED') {
            completed = true;
            const duration = Date.now() - startTime;
            workflowDuration.add(duration);
            workflowCompletions.add(1);
            workflowSuccessRate.add(1);
            
            check(statusResponse, {
              'workflow completed successfully': (r) => r.json('result.success') === true,
            });
          } else if (status === 'FAILED' || status === 'TERMINATED') {
            workflowFailures.add(1);
            workflowSuccessRate.add(0);
            completed = true;
          }
        }
        
        attempts++;
      }
      
      if (!completed) {
        console.log(`Workflow ${workflowId} timed out after ${maxAttempts * 0.5}s`);
        workflowFailures.add(1);
        workflowSuccessRate.add(0);
      }
    } else {
      workflowFailures.add(1);
      workflowSuccessRate.add(0);
    }
  });
  
  // Think time between iterations
  sleep(1);
}

export function handleSummary(data) {
  return {
    'load-test-summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options) {
  const { indent = '', enableColors = false } = options || {};
  
  let summary = '\n' + indent + '=== k6 Load Test Summary ===\n\n';
  
  summary += indent + `Total Duration: ${data.state.testRunDurationMs / 1000}s\n`;
  summary += indent + `Workflows Started: ${data.metrics.workflow_starts.values.count}\n`;
  summary += indent + `Workflows Completed: ${data.metrics.workflow_completions.values.count}\n`;
  summary += indent + `Workflows Failed: ${data.metrics.workflow_failures.values.count}\n`;
  summary += indent + `Success Rate: ${(data.metrics.workflow_success_rate.values.rate * 100).toFixed(2)}%\n\n`;
  
  summary += indent + 'Workflow Duration:\n';
  summary += indent + `  P50: ${data.metrics.workflow_duration_ms.values['p(50)']}ms\n`;
  summary += indent + `  P95: ${data.metrics.workflow_duration_ms.values['p(95)']}ms\n`;
  summary += indent + `  P99: ${data.metrics.workflow_duration_ms.values['p(99)']}ms\n\n`;
  
  summary += indent + 'HTTP Request Duration:\n';
  summary += indent + `  P50: ${data.metrics.http_req_duration.values['p(50)']}ms\n`;
  summary += indent + `  P95: ${data.metrics.http_req_duration.values['p(95)']}ms\n`;
  summary += indent + `  P99: ${data.metrics.http_req_duration.values['p(99)']}ms\n\n`;
  
  return summary;
}
