# Pipeline Monitoring & Health Tracking

**Author**: CI/CD Architect  
**Date**: 2026-04-10  
**Purpose**: Monitor workflow health, performance, and reliability

## Overview

This document provides a comprehensive monitoring strategy for GitHub Actions workflows to ensure reliability, performance, and early detection of issues.

## Key Performance Indicators (KPIs)

### 1. Workflow Execution Metrics

| Metric | Target | Critical Threshold | Measurement |
|--------|--------|-------------------|-------------|
| Avg CI Runtime | <10 min | >15 min | Per workflow run |
| P95 CI Runtime | <12 min | >20 min | 95th percentile |
| Success Rate | >95% | <90% | Last 30 days |
| Cache Hit Rate | >80% | <60% | Per job |
| Queue Time | <30s | >2 min | Time to start |

### 2. Security Scan Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| CodeQL Runtime | <5 min | >10 min |
| Bandit Runtime | <1 min | >2 min |
| Trivy Runtime | <2 min | >5 min |
| Vulnerabilities Found | 0 HIGH | >0 CRITICAL |
| False Positive Rate | <10% | >25% |

### 3. Deployment Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Deployment Frequency | Daily | <Weekly |
| Lead Time for Changes | <1 hour | >4 hours |
| Mean Time to Recovery (MTTR) | <30 min | >2 hours |
| Change Failure Rate | <5% | >15% |
| Rollback Rate | <2% | >10% |

## Monitoring Implementation

### 1. Workflow Status Dashboard

Create a workflow that generates a status dashboard:

```yaml
name: Workflow Health Dashboard
on:
  schedule:

    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  generate-dashboard:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4
      
      - name: Fetch workflow runs
        run: |
          gh api \
            /repos/${{ github.repository }}/actions/runs \
            --paginate \
            --jq '.workflow_runs[] | select(.created_at > (now - 86400)) | {
              workflow: .name,
              status: .conclusion,
              duration: ((.updated_at | fromdateiso8601) - (.created_at | fromdateiso8601)),
              created: .created_at
            }' > workflow_runs.json
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Generate health report
        run: |
          python3 << 'EOF'
          import json
          from collections import defaultdict
          from datetime import datetime
          
          with open('workflow_runs.json') as f:
              runs = [json.loads(line) for line in f]
          
          stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failure': 0, 'durations': []})
          
          for run in runs:
              workflow = run['workflow']
              stats[workflow]['total'] += 1
              if run['status'] == 'success':
                  stats[workflow]['success'] += 1
              elif run['status'] == 'failure':
                  stats[workflow]['failure'] += 1
              stats[workflow]['durations'].append(run['duration'])
          
          print("## 📊 Workflow Health Dashboard")
          print(f"\n**Generated**: {datetime.now().isoformat()}")
          print(f"\n**Period**: Last 24 hours")
          print("\n### Workflow Statistics\n")
          print("| Workflow | Runs | Success Rate | Avg Duration | P95 Duration |")
          print("|----------|------|--------------|--------------|--------------|")
          
          for workflow, data in sorted(stats.items()):
              success_rate = (data['success'] / data['total'] * 100) if data['total'] > 0 else 0
              avg_duration = sum(data['durations']) / len(data['durations']) if data['durations'] else 0
              p95_duration = sorted(data['durations'])[int(len(data['durations']) * 0.95)] if data['durations'] else 0
              
              status_emoji = '✅' if success_rate >= 95 else '⚠️' if success_rate >= 90 else '❌'
              
              print(f"| {status_emoji} {workflow} | {data['total']} | {success_rate:.1f}% | {avg_duration/60:.1f}m | {p95_duration/60:.1f}m |")
          
          EOF
      
      - name: Create Issue if unhealthy
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Workflow Health Alert',
              body: 'Workflow health metrics have degraded. Check the latest dashboard run.',
              labels: ['ci/cd', 'urgent']
            });

```

### 2. Real-time Workflow Monitoring

Add monitoring steps to critical workflows:

```yaml
jobs:
  monitor:
    runs-on: ubuntu-latest
    if: always()
    needs: [lint, test, security, build]
    steps:

      - name: Calculate workflow duration
        run: |
          START_TIME="${{ github.event.workflow_run.created_at }}"
          END_TIME="$(date -u +%s)"
          DURATION=$((END_TIME - $(date -d "$START_TIME" +%s)))
          
          echo "Workflow duration: ${DURATION}s"
          echo "WORKFLOW_DURATION=${DURATION}" >> $GITHUB_ENV
          
          # Alert if over threshold

          if [ $DURATION -gt 600 ]; then
            echo "::warning::Workflow exceeded 10-minute target (${DURATION}s)"
          fi
      
      - name: Check job statuses
        run: |
          LINT_STATUS="${{ needs.lint.result }}"
          TEST_STATUS="${{ needs.test.result }}"
          SECURITY_STATUS="${{ needs.security.result }}"
          BUILD_STATUS="${{ needs.build.result }}"
          
          echo "## Workflow Summary" >> $GITHUB_STEP_SUMMARY
          echo "| Job | Status |" >> $GITHUB_STEP_SUMMARY
          echo "|-----|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| Lint | $LINT_STATUS |" >> $GITHUB_STEP_SUMMARY
          echo "| Test | $TEST_STATUS |" >> $GITHUB_STEP_SUMMARY
          echo "| Security | $SECURITY_STATUS |" >> $GITHUB_STEP_SUMMARY
          echo "| Build | $BUILD_STATUS |" >> $GITHUB_STEP_SUMMARY
      
      - name: Record metrics
        run: |
          # Send to monitoring system (e.g., DataDog, New Relic, CloudWatch)
          curl -X POST https://api.monitoring.example.com/metrics \
            -H "Authorization: Bearer ${{ secrets.MONITORING_TOKEN }}" \
            -d '{
              "workflow": "${{ github.workflow }}",
              "duration": ${{ env.WORKFLOW_DURATION }},
              "success": "${{ job.status == 'success' }}",
              "timestamp": "$(date -u +%s)"
            }' || true

```

### 3. Cache Performance Monitoring

Track cache hit rates:

```yaml

- name: Monitor cache performance
  run: |
    # Check if cache was restored
    if [ -d "$HOME/.cache/pip" ]; then
      CACHE_SIZE=$(du -sh "$HOME/.cache/pip" | cut -f1)
      echo "✅ Cache hit (size: $CACHE_SIZE)"
      echo "CACHE_HIT=true" >> $GITHUB_ENV
    else
      echo "❌ Cache miss"
      echo "CACHE_HIT=false" >> $GITHUB_ENV
    fi
    
    # Log cache statistics

    echo "## Cache Performance" >> $GITHUB_STEP_SUMMARY
    echo "- Hit: ${{ env.CACHE_HIT }}" >> $GITHUB_STEP_SUMMARY
    echo "- Size: $CACHE_SIZE" >> $GITHUB_STEP_SUMMARY
```

### 4. Security Scan Monitoring

Track security findings over time:

```yaml

- name: Track security metrics
  if: always()
  run: |
    python3 << 'EOF'
    import json
    import os
    
    # Load Bandit results

    with open('bandit-report.json') as f:
        report = json.load(f)
    
    results = report.get('results', [])
    high_sev = len([r for r in results if r['issue_severity'] == 'HIGH'])
    med_sev = len([r for r in results if r['issue_severity'] == 'MEDIUM'])
    low_sev = len([r for r in results if r['issue_severity'] == 'LOW'])
    
    print(f"Security findings: HIGH={high_sev}, MED={med_sev}, LOW={low_sev}")
    
    # Write to step summary

    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
        f.write("## 🔒 Security Scan Results\n\n")
        f.write(f"- **HIGH**: {high_sev}\n")
        f.write(f"- **MEDIUM**: {med_sev}\n")
        f.write(f"- **LOW**: {low_sev}\n")
    
    # Fail if high severity issues

    if high_sev > 0:
        print("::error::High severity security issues found")
        exit(1)
    EOF
```

## Alerting Strategy

### 1. Slack/Teams Notifications

```yaml

- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: |
      🔴 Workflow Failed: ${{ github.workflow }}
      Branch: ${{ github.ref }}
      Commit: ${{ github.sha }}
      Author: ${{ github.actor }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}

```

### 2. Email Alerts

```yaml

- name: Send email alert
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: '🚨 CI Failure: ${{ github.workflow }}'
    body: |
      Workflow ${{ github.workflow }} failed.
      
      Details:

      - Repository: ${{ github.repository }}
      - Branch: ${{ github.ref }}
      - Commit: ${{ github.sha }}
      - Author: ${{ github.actor }}
      - Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
    to: devops@example.com

```

### 3. GitHub Issue Creation

```yaml

- name: Create issue on repeated failures
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      // Check if workflow has failed 3 times in a row
      const runs = await github.rest.actions.listWorkflowRuns({
        owner: context.repo.owner,
        repo: context.repo.repo,
        workflow_id: context.workflow,
        per_page: 3
      });
      
      const failures = runs.data.workflow_runs.filter(r => r.conclusion === 'failure').length;
      
      if (failures >= 3) {
        await github.rest.issues.create({
          owner: context.repo.owner,
          repo: context.repo.repo,
          title: `🚨 CI Workflow Failing Repeatedly: ${context.workflow}`,
          body: `The workflow has failed ${failures} times in a row. Investigation required.`,
          labels: ['ci/cd', 'urgent', 'bug']
        });
      }
```

## Metrics Collection

### 1. Custom Metrics Script

Create `.github/scripts/collect-metrics.py`:

```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timedelta
import subprocess

def get_workflow_runs(days=30):
    """Fetch workflow runs from last N days"""
    since = (datetime.now() - timedelta(days=days)).isoformat()
    
    cmd = [
        'gh', 'api',
        '/repos/{owner}/{repo}/actions/runs',
        '--paginate',
        '-f', f'created=>={since}',
        '--jq', '.workflow_runs[]'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return [json.loads(line) for line in result.stdout.strip().split('\n') if line]

def calculate_metrics(runs):
    """Calculate key metrics from workflow runs"""
    total_runs = len(runs)
    successful_runs = len([r for r in runs if r['conclusion'] == 'success'])
    failed_runs = len([r for r in runs if r['conclusion'] == 'failure'])
    
    durations = []
    for run in runs:
        if run['updated_at'] and run['created_at']:
            start = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(run['updated_at'].replace('Z', '+00:00'))
            durations.append((end - start).total_seconds())
    
    avg_duration = sum(durations) / len(durations) if durations else 0
    p95_duration = sorted(durations)[int(len(durations) * 0.95)] if durations else 0
    
    return {
        'total_runs': total_runs,
        'successful_runs': successful_runs,
        'failed_runs': failed_runs,
        'success_rate': (successful_runs / total_runs * 100) if total_runs > 0 else 0,
        'avg_duration_minutes': avg_duration / 60,
        'p95_duration_minutes': p95_duration / 60
    }

def main():
    runs = get_workflow_runs(days=30)
    metrics = calculate_metrics(runs)
    
    print(f"## 📊 CI/CD Metrics (Last 30 Days)\n")
    print(f"- **Total Runs**: {metrics['total_runs']}")
    print(f"- **Success Rate**: {metrics['success_rate']:.1f}%")
    print(f"- **Avg Duration**: {metrics['avg_duration_minutes']:.1f} minutes")
    print(f"- **P95 Duration**: {metrics['p95_duration_minutes']:.1f} minutes")
    
    # Check thresholds

    if metrics['success_rate'] < 90:
        print("\n⚠️  **WARNING**: Success rate below 90%")
        sys.exit(1)
    
    if metrics['p95_duration_minutes'] > 15:
        print("\n⚠️  **WARNING**: P95 duration exceeds 15 minutes")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### 2. Automated Metrics Collection Workflow

```yaml
name: Collect CI Metrics
on:
  schedule:

    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4
      
      - name: Install dependencies
        run: pip install pandas matplotlib
      
      - name: Collect metrics
        run: python .github/scripts/collect-metrics.py
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Generate trend charts
        run: |
          python << 'EOF'
          import pandas as pd
          import matplotlib.pyplot as plt
          from datetime import datetime, timedelta
          
          # Generate sample trend data (replace with actual data)

          dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
          durations = [8 + (i % 5) for i in range(30)]
          success_rates = [95 + (i % 10) for i in range(30)]
          
          # Plot duration trend

          plt.figure(figsize=(12, 6))
          plt.subplot(1, 2, 1)
          plt.plot(dates, durations)
          plt.axhline(y=10, color='r', linestyle='--', label='Target')
          plt.title('CI Duration Trend')
          plt.ylabel('Minutes')
          plt.legend()
          
          # Plot success rate trend

          plt.subplot(1, 2, 2)
          plt.plot(dates, success_rates)
          plt.axhline(y=95, color='g', linestyle='--', label='Target')
          plt.title('Success Rate Trend')
          plt.ylabel('Percentage')
          plt.legend()
          
          plt.tight_layout()
          plt.savefig('ci_metrics_trend.png')
          EOF
      
      - name: Upload metrics report
        uses: actions/upload-artifact@v4
        with:
          name: ci-metrics-report
          path: |
            ci_metrics_trend.png
            metrics.json

```

## Dashboard Setup

### GitHub Actions Dashboard (Using GitHub Pages)

Create `.github/workflows/publish-dashboard.yml`:

```yaml
name: Publish CI Dashboard
on:
  schedule:

    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  generate-dashboard:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4
        with:
          ref: gh-pages
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Generate HTML dashboard
        run: |
          cat > index.html << 'HTML'
          <!DOCTYPE html>
          <html>
          <head>
            <title>CI/CD Dashboard</title>
            <meta http-equiv="refresh" content="300">
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              .metric { display: inline-block; margin: 10px; padding: 20px; border: 1px solid #ddd; }
              .good { background-color: #d4edda; }
              .warning { background-color: #fff3cd; }
              .bad { background-color: #f8d7da; }
            </style>
          </head>
          <body>
            <h1>🚀 CI/CD Dashboard</h1>
            <p>Last updated: <span id="timestamp"></span></p>
            
            <div id="metrics"></div>
            
            <script>
              document.getElementById('timestamp').textContent = new Date().toLocaleString();
              
              // Fetch metrics from GitHub API
              fetch('https://api.github.com/repos/OWNER/REPO/actions/runs?per_page=30')
                .then(r => r.json())
                .then(data => {
                  const runs = data.workflow_runs;
                  const total = runs.length;
                  const success = runs.filter(r => r.conclusion === 'success').length;
                  const successRate = (success / total * 100).toFixed(1);
                  
                  let html = '<div class="metric ' + (successRate >= 95 ? 'good' : successRate >= 90 ? 'warning' : 'bad') + '">';
                  html += '<h3>Success Rate</h3>';
                  html += '<p style="font-size: 2em;">' + successRate + '%</p>';
                  html += '</div>';
                  
                  document.getElementById('metrics').innerHTML = html;
                });
            </script>
          </body>
          </html>
          HTML
      
      - name: Commit dashboard
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add index.html
          git commit -m "Update dashboard" || exit 0
          git push

```

## Troubleshooting Guide

### High Failure Rate (>10%)

**Investigation Steps**:

1. Check recent failed runs: `gh run list --status failure`
2. Review error patterns in logs
3. Check for infrastructure issues (GitHub status)
4. Review recent code changes (breaking changes?)

**Common Causes**:

- Flaky tests (intermittent failures)
- External dependency failures (network, APIs)
- Environment changes (runner updates)
- Resource constraints (timeout, memory)

### Slow CI Runs (>15 minutes)

**Investigation Steps**:

1. Identify slowest job: Check workflow run logs
2. Check cache hit rate: Look for "Cache restored" messages
3. Review test execution time: `pytest --durations=10`
4. Check for sequential jobs: Review workflow dependencies

**Common Causes**:

- Cache misses (dependencies reinstalled)
- Sequential job execution (should be parallel)
- Slow tests (database, integration tests)
- Large artifact uploads

### Low Cache Hit Rate (<60%)

**Investigation Steps**:

1. Check cache keys: Ensure consistent naming
2. Review dependency files: Frequent changes?
3. Check cache size: Hitting 10GB limit?
4. Verify cache-dependency-path: Correct files listed?

**Solutions**:

- Use composite cache keys (OS, Python version, hash)
- Separate production and dev dependencies
- Clean up old caches: `gh cache delete --all`

## Best Practices

1. **Set up automated monitoring** (don't rely on manual checks)
2. **Track trends, not just point-in-time metrics**
3. **Alert on degradation, not just failures**
4. **Document runbooks for common issues**
5. **Review metrics weekly** (don't set and forget)
6. **Correlate CI metrics with deployment metrics**
7. **Use visualization** (charts better than numbers)

## Conclusion

Effective pipeline monitoring requires:

- ✅ Automated metrics collection
- ✅ Real-time alerting
- ✅ Trend analysis
- ✅ Clear thresholds and targets
- ✅ Regular review and optimization

**Status**: ✅ **MONITORING FRAMEWORK READY**

Next steps:

1. Implement workflow health dashboard
2. Set up Slack/Teams notifications
3. Create metrics collection automation
4. Establish weekly review cadence
5. Document incident response procedures
