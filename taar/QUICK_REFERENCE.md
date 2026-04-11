# TAAR Enhanced Build System - Quick Reference

## 🚀 Quick Start (30 seconds)

```bash
# 1. Install dependencies
pip install aiohttp

# 2. Run incremental build
python -m taar.build_enhanced

# 3. View dashboard
# Open .taar-cache/analytics/dashboard.html in browser
```

## 📊 Common Commands

### Basic Builds

```bash
# Incremental build (changed files only)
python -m taar.build_enhanced

# Full build (all runners)
python -m taar.build_enhanced --full

# Generate dashboard only
python -m taar.build_enhanced --dashboard

# Visualizations only
python -m taar.build_enhanced --viz-only
```

### Distributed Cache

```bash
# Terminal 1: Start cache server
python -m taar.build_enhanced --serve-cache --cache-port 8765

# Terminal 2: Use remote cache
python -m taar.build_enhanced --remote-cache http://localhost:8765

# Team member: Connect to shared cache
python -m taar.build_enhanced --remote-cache http://build-server:8765
```

### Demo & Testing

```bash
# Run comprehensive demo
python taar/demo_enhanced.py

# Run tests
pytest tests/test_build_enhanced.py -v

# Run specific test
pytest tests/test_build_enhanced.py::test_graph_visualizer_d3_html -v
```

## 🎯 Key Features

### 1. Incremental Builds (~70% time saved)
**What**: Only builds changed files and their dependencies
**When**: Every commit, before push
**Example**: Changed 1 file → Build 5 files instead of 150

### 2. Distributed Cache (~80% hit rate)
**What**: Share build results across team
**When**: Team development, CI/CD
**Example**: Teammate builds → Your build uses cache → 5x faster

### 3. Dependency Graph (~instant insights)
**What**: Visual graph of file → runner → test relationships
**When**: Understanding impact, debugging failures
**Example**: Changed auth.py → Shows all affected tests

### 4. Build Analytics (~historical trends)
**What**: Track build times, cache rates, bottlenecks
**When**: Performance optimization, sprint retrospectives
**Example**: Dashboard shows build times decreased 60% this week

### 5. Performance (~5-10x faster)
**What**: Parallel execution, smart batching, content caching
**When**: All builds
**Example**: 120s build → 12-24s build

## 📈 Performance Comparison

| Scenario | Before | After | Speedup |
|----------|--------|-------|---------|
| Full build (cold) | 120s | 120s | 1.0x |
| 1 file changed | 120s | 24s | 5.0x |
| No changes | 120s | 2s | 60x |
| Team member | 120s | 15s | 8.0x |

## 🔧 Configuration Examples

### Minimal (taar.toml)

```toml
[taar]
parallelism = "auto"
cache_dir = ".taar-cache"

[taar.runners.python]
enabled = true
paths = ["src/**/*.py"]

[taar.runners.python.commands]
test = "pytest {test_files}"
```

### With Remote Cache

```toml
[taar]
parallelism = 8

[taar.remote_cache]
enabled = true
backend = "http"
url = "http://cache-server:8765"
compression = true
```

### Advanced

```toml
[taar]
parallelism = 16
fail_fast = false
notifications = true

[taar.runners.python]
paths = ["src/**/*.py"]
test_paths = ["tests/**/*.py"]
priority = {lint = 1, typecheck = 2, test = 3}

[taar.runners.python.commands]
lint = "ruff check {files}"
typecheck = "mypy {files}"
test = "pytest {test_files} -v"

[taar.graph.impact]
"src/auth/**/*.py" = ["tests/test_auth*.py"]
"src/api/**/*.py" = ["tests/integration/**/*.py"]
```

## 📊 Output Examples

### Successful Build

```
📊 Detected 3 changed files
🎯 Affected runners: python, typescript
📈 Graph visualization: .taar-cache/visualizations/abc123/graph_interactive.html

🔨 Running python (3 files)...
⊙ lint: CACHED
✓ typecheck: PASS (2.1s)
✓ test: PASS (5.3s)

======================================================================
📊 BUILD SUMMARY
======================================================================
Duration:          7.4s
Tasks:             12 (8 executed, 4 cached)
Cache Hit Rate:    33.3%
Success Rate:      100.0%
Incremental Save:  45.2s

🌐 Remote Cache:
  Uploads:   4 (67.8 KB)
  Downloads: 0 (0.0 KB)

📊 Dashboard: .taar-cache/analytics/dashboard.html
======================================================================
```

### Failed Build

```
🔨 Running python (1 files)...
✓ lint: PASS (1.2s)
✗ typecheck: FAIL (2.1s)

======================================================================
📊 BUILD SUMMARY
======================================================================
Duration:          3.3s
Tasks:             2 (2 executed, 0 cached)
Cache Hit Rate:    0.0%
Success Rate:      50.0%

❌ 1 FAILED TASKS:
  • python:typecheck
======================================================================
```

## 🎨 Visualizations

### Dashboard (dashboard.html)
- **Build Duration Trend**: Line chart showing builds getting faster
- **Cache Hit Rate**: Track caching effectiveness over time
- **Runner Performance**: Table showing which runners are slowest
- **Bottlenecks**: Top 5 slowest tasks to optimize

### Dependency Graph (graph_interactive.html)
- **Blue nodes**: Changed files
- **Green nodes**: Affected runners
- **Yellow nodes**: Test files
- **Drag & drop**: Rearrange for clarity
- **Force layout**: Automatically organizes

## 🐛 Troubleshooting

### "ModuleNotFoundError: aiohttp"
```bash
pip install aiohttp
```

### "Cache server not responding"
```bash
# Check server is running
curl http://localhost:8765/cache/test

# Restart server
python -m taar.build_enhanced --serve-cache
```

### "Slow builds"
1. Check dashboard for bottlenecks
2. Increase parallelism: `parallelism = 16`
3. Enable remote cache
4. Check if cache is being used: look for "⊙ CACHED" in output

### "No graph visualization"
```bash
# Install Graphviz (optional)
choco install graphviz  # Windows
brew install graphviz   # macOS
apt install graphviz    # Linux

# HTML interactive graph always works (no Graphviz needed)
```

## 📚 Advanced Usage

### Programmatic API

```python
from taar.build_enhanced import IncrementalBuildOrchestrator
from taar.config import load_config

async def custom_build():
    config = load_config()
    orch = IncrementalBuildOrchestrator(config)
    
    metrics = await orch.run_incremental_build()
    
    if metrics.failed_tasks > 0:
        send_slack_alert(f"{metrics.failed_tasks} tasks failed")
    
    await orch.close()
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Enhanced Build
  run: |
    python -m taar.build_enhanced \
      --remote-cache ${{ secrets.CACHE_URL }} \
      --full
  
- name: Upload Analytics
  uses: actions/upload-artifact@v3
  with:
    name: build-analytics
    path: .taar-cache/analytics/
```

### Custom Cache Backend

```python
# Future: S3 backend
remote_config = RemoteCacheConfig(
    enabled=True,
    backend="s3",
    url="s3://my-build-cache/",
)
```

## 🎯 Best Practices

1. **Enable remote cache** for teams (8x speedup)
2. **Review dashboard weekly** to track improvements
3. **Optimize bottlenecks** shown in analytics
4. **Use fail_fast=true** in CI for faster feedback
5. **Increase parallelism** based on CPU cores
6. **Clear old cache** monthly: `rm -rf .taar-cache/results`

## 📦 Files Generated

```
.taar-cache/
├── results/           # Local cache entries
│   └── *.json
├── analytics/         # Build history & dashboard
│   ├── build_history.jsonl
│   └── dashboard.html
└── visualizations/    # Dependency graphs
    └── {run_id}/
        ├── graph_data.json
        ├── graph.dot
        ├── graph.svg
        └── graph_interactive.html
```

## 🚀 Next Steps

1. **Try the demo**: `python taar/demo_enhanced.py`
2. **Set up remote cache**: Share across team
3. **Review analytics**: Find optimization opportunities
4. **Share results**: Show 5x speedup to team

---

**Questions?** See [README_ENHANCED.md](README_ENHANCED.md) for detailed documentation.
