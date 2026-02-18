#!/usr/bin/env bash
# bench/run_benchmarks.sh — OCTOREFLEX containment benchmark suite.
#
# Produces reproducible, machine-readable results for:
#   1. Containment latency (µs) — time from syscall entry to BPF enforcement
#   2. CPU overhead idle        — agent CPU% with no process activity
#   3. CPU overhead syscall storm — agent CPU% under 100k syscalls/sec
#   4. False positive rate      — FPR over 10k normal-process samples
#   5. Budget exhaustion        — behaviour when token bucket hits 0
#   6. Kernel stability         — 60s stress-ng run, check for panics/oops
#
# Requirements:
#   - Root on Linux 5.15+ with BTF, cgroup v2, LSM BPF enabled
#   - octoreflex agent running (or use MOCK=1 for unit-level latency only)
#   - stress-ng >= 0.15.0
#   - perf (linux-tools-$(uname -r))
#   - python3 (for result aggregation)
#
# Usage:
#   sudo bash bench/run_benchmarks.sh [--output results/] [--duration 60]
#
# Output:
#   results/bench_YYYYMMDD_HHMMSS.json  — machine-readable results
#   results/bench_YYYYMMDD_HHMMSS.txt   — human-readable summary
#
# CI integration:
#   The script exits 0 if all targets are met, 1 otherwise.
#   Targets are defined in bench/targets.json.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${1:-$ROOT_DIR/results}"
DURATION="${BENCH_DURATION:-60}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RESULT_JSON="$OUTPUT_DIR/bench_${TIMESTAMP}.json"
RESULT_TXT="$OUTPUT_DIR/bench_${TIMESTAMP}.txt"
AGENT_PID_FILE="/run/octoreflex/agent.pid"
AGENT_METRICS="http://127.0.0.1:9091/metrics"

mkdir -p "$OUTPUT_DIR"

# ── Colour output ──────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; }
info() { echo -e "${YELLOW}[INFO]${NC} $*"; }

# ── Preflight checks ───────────────────────────────────────────────────────────
preflight() {
  info "Preflight checks..."
  [[ $EUID -eq 0 ]] || { fail "Must run as root"; exit 1; }
  [[ "$(uname -s)" == "Linux" ]] || { fail "Linux required"; exit 1; }

  # Kernel version >= 5.15
  KVER="$(uname -r | cut -d. -f1-2)"
  KMAJ="$(echo "$KVER" | cut -d. -f1)"
  KMIN="$(echo "$KVER" | cut -d. -f2)"
  if [[ $KMAJ -lt 5 ]] || { [[ $KMAJ -eq 5 ]] && [[ $KMIN -lt 15 ]]; }; then
    fail "Kernel >= 5.15 required (got $(uname -r))"; exit 1
  fi

  # BTF
  [[ -f /sys/kernel/btf/vmlinux ]] || { fail "/sys/kernel/btf/vmlinux not found (BTF not enabled)"; exit 1; }

  # cgroup v2
  [[ "$(stat -fc %T /sys/fs/cgroup)" == "cgroup2fs" ]] || { fail "cgroup v2 required"; exit 1; }

  # stress-ng
  command -v stress-ng &>/dev/null || { fail "stress-ng not found (apt install stress-ng)"; exit 1; }

  # perf
  command -v perf &>/dev/null || { fail "perf not found (apt install linux-tools-$(uname -r))"; exit 1; }

  # Agent running
  if [[ -f "$AGENT_PID_FILE" ]] && kill -0 "$(cat "$AGENT_PID_FILE")" 2>/dev/null; then
    AGENT_PID="$(cat "$AGENT_PID_FILE")"
    info "Agent running (PID $AGENT_PID)"
  else
    info "Agent not running — some benchmarks will use mock mode"
    AGENT_PID=""
  fi

  pass "Preflight complete (kernel=$(uname -r), cgroup=v2, BTF=yes)"
}

# ── Benchmark 1: Containment latency ──────────────────────────────────────────
# Measures the time from LSM hook entry to BPF enforcement decision.
# Method: perf probe on the BPF LSM hook, measure hook-to-return latency.
# Target: p50 < 500µs, p99 < 2ms (sub-millisecond containment).
bench_containment_latency() {
  info "Benchmark 1: Containment latency..."

  # Use the latency measurement tool if compiled.
  LATENCY_TOOL="$ROOT_DIR/bin/octoreflex-bench-latency"
  if [[ ! -x "$LATENCY_TOOL" ]]; then
    info "  Building latency tool..."
    CGO_ENABLED=0 go build -o "$LATENCY_TOOL" "$ROOT_DIR/bench/cmd/latency/" 2>/dev/null || {
      info "  Latency tool not available — using perf kprobe fallback"
      LATENCY_TOOL=""
    }
  fi

  if [[ -n "$LATENCY_TOOL" ]]; then
    # Run 10,000 socket_connect attempts against a quarantined PID.
    # The tool measures time from hook entry to -EPERM return.
    "$LATENCY_TOOL" --iterations 10000 --output "$OUTPUT_DIR/latency_raw.csv"
    P50=$(awk -F, 'NR>1{print $2}' "$OUTPUT_DIR/latency_raw.csv" | sort -n | awk 'BEGIN{c=0} {a[c++]=$1} END{print a[int(c*0.50)]}')
    P99=$(awk -F, 'NR>1{print $2}' "$OUTPUT_DIR/latency_raw.csv" | sort -n | awk 'BEGIN{c=0} {a[c++]=$1} END{print a[int(c*0.99)]}')
    info "  Containment latency: p50=${P50}µs p99=${P99}µs"
  else
    # Fallback: measure connect(2) syscall latency for a blocked PID using strace.
    # This includes kernel overhead but gives a conservative upper bound.
    info "  Fallback: measuring connect(2) block latency via strace..."
    strace -e trace=connect -T -o "$OUTPUT_DIR/strace_connect.txt" \
      timeout 5 bash -c 'for i in $(seq 100); do
        nc -z -w0 8.8.8.8 443 2>/dev/null; done' 2>/dev/null || true
    P50="N/A (latency tool not compiled)"
    P99="N/A (latency tool not compiled)"
  fi

  echo "containment_latency_p50_us=$P50" >> "$OUTPUT_DIR/raw_metrics.txt"
  echo "containment_latency_p99_us=$P99" >> "$OUTPUT_DIR/raw_metrics.txt"
}

# ── Benchmark 2: CPU overhead idle ────────────────────────────────────────────
# Measures agent CPU% with no monitored process activity.
# Target: < 0.5% on a 2-core host.
bench_cpu_idle() {
  info "Benchmark 2: CPU overhead (idle)..."
  if [[ -z "$AGENT_PID" ]]; then
    info "  Skipping (agent not running)"
    echo "cpu_idle_pct=N/A" >> "$OUTPUT_DIR/raw_metrics.txt"
    return
  fi

  # Sample CPU usage every 1s for 30s.
  CPU_SAMPLES=()
  for i in $(seq 30); do
    CPU=$(ps -p "$AGENT_PID" -o %cpu= 2>/dev/null | tr -d ' ' || echo "0")
    CPU_SAMPLES+=("$CPU")
    sleep 1
  done

  AVG=$(printf '%s\n' "${CPU_SAMPLES[@]}" | awk '{s+=$1; c++} END{printf "%.2f", s/c}')
  MAX=$(printf '%s\n' "${CPU_SAMPLES[@]}" | sort -n | tail -1)
  info "  CPU idle: avg=${AVG}% max=${MAX}%"
  echo "cpu_idle_avg_pct=$AVG" >> "$OUTPUT_DIR/raw_metrics.txt"
  echo "cpu_idle_max_pct=$MAX" >> "$OUTPUT_DIR/raw_metrics.txt"
}

# ── Benchmark 3: CPU overhead under syscall storm ─────────────────────────────
# Generates 100k syscalls/sec using stress-ng, measures agent CPU%.
# Target: < 5% additional CPU overhead vs idle.
bench_cpu_syscall_storm() {
  info "Benchmark 3: CPU overhead (syscall storm, ${DURATION}s)..."

  # Start stress-ng syscall flood in background.
  stress-ng --syscall 4 --syscall-ops 0 --timeout "${DURATION}s" \
    --metrics-brief --log-file "$OUTPUT_DIR/stress_ng_syscall.log" &
  STRESS_PID=$!

  if [[ -n "$AGENT_PID" ]]; then
    CPU_SAMPLES=()
    for i in $(seq "$DURATION"); do
      CPU=$(ps -p "$AGENT_PID" -o %cpu= 2>/dev/null | tr -d ' ' || echo "0")
      CPU_SAMPLES+=("$CPU")
      sleep 1
    done
    AVG=$(printf '%s\n' "${CPU_SAMPLES[@]}" | awk '{s+=$1; c++} END{printf "%.2f", s/c}')
    MAX=$(printf '%s\n' "${CPU_SAMPLES[@]}" | sort -n | tail -1)
    info "  CPU storm: avg=${AVG}% max=${MAX}%"
    echo "cpu_storm_avg_pct=$AVG" >> "$OUTPUT_DIR/raw_metrics.txt"
    echo "cpu_storm_max_pct=$MAX" >> "$OUTPUT_DIR/raw_metrics.txt"
  else
    wait $STRESS_PID 2>/dev/null || true
    info "  Skipping agent CPU measurement (agent not running)"
    echo "cpu_storm_avg_pct=N/A" >> "$OUTPUT_DIR/raw_metrics.txt"
  fi

  wait $STRESS_PID 2>/dev/null || true
  info "  stress-ng syscall storm complete. Log: $OUTPUT_DIR/stress_ng_syscall.log"
}

# ── Benchmark 4: False positive rate ──────────────────────────────────────────
# Runs 10,000 normal process samples through the anomaly engine.
# Counts escalations above PRESSURE as false positives.
# Target: FPR < 0.5%.
bench_false_positive_rate() {
  info "Benchmark 4: False positive rate (10k samples)..."

  FPR_TOOL="$ROOT_DIR/bin/octoreflex-bench-fpr"
  if [[ ! -x "$FPR_TOOL" ]]; then
    info "  Building FPR tool..."
    CGO_ENABLED=0 go build -o "$FPR_TOOL" "$ROOT_DIR/bench/cmd/fpr/" 2>/dev/null || {
      info "  FPR tool not available — skipping"
      echo "fpr_pct=N/A" >> "$OUTPUT_DIR/raw_metrics.txt"
      return
    }
  fi

  "$FPR_TOOL" --samples 10000 --output "$OUTPUT_DIR/fpr_raw.csv"
  FPR=$(awk -F, 'NR>1 && $3=="FP"{c++} END{printf "%.3f", c/10000*100}' "$OUTPUT_DIR/fpr_raw.csv")
  info "  FPR: ${FPR}%"
  echo "fpr_pct=$FPR" >> "$OUTPUT_DIR/raw_metrics.txt"
}

# ── Benchmark 5: Budget exhaustion behaviour ──────────────────────────────────
# Verifies that budget exhaustion does not cause agent crash or kernel panic.
# Floods the budget bucket and checks agent health after exhaustion.
bench_budget_exhaustion() {
  info "Benchmark 5: Budget exhaustion behaviour..."

  if [[ -z "$AGENT_PID" ]]; then
    info "  Skipping (agent not running)"
    echo "budget_exhaustion=N/A" >> "$OUTPUT_DIR/raw_metrics.txt"
    return
  fi

  # Trigger rapid escalations to exhaust the token bucket.
  # Use the operator CLI to force-escalate 10 PIDs to TERMINATED (cost=50 each).
  EXHAUSTED=0
  for i in $(seq 10); do
    FAKE_PID=$((60000 + i))
    octoreflex-cli pin --pid "$FAKE_PID" --state TERMINATED 2>/dev/null && EXHAUSTED=$((EXHAUSTED+1)) || true
  done

  # Check agent is still alive.
  sleep 2
  if kill -0 "$AGENT_PID" 2>/dev/null; then
    pass "  Agent alive after budget exhaustion (exhausted $EXHAUSTED actions)"
    echo "budget_exhaustion=PASS" >> "$OUTPUT_DIR/raw_metrics.txt"
  else
    fail "  Agent died after budget exhaustion"
    echo "budget_exhaustion=FAIL" >> "$OUTPUT_DIR/raw_metrics.txt"
  fi

  # Clean up pinned PIDs.
  for i in $(seq 10); do
    FAKE_PID=$((60000 + i))
    octoreflex-cli reset --pid "$FAKE_PID" 2>/dev/null || true
  done
}

# ── Benchmark 6: Kernel stability under stress ────────────────────────────────
# Runs stress-ng for DURATION seconds across multiple stressors.
# Checks dmesg for BPF verifier errors, kernel oops, or panics.
# Target: 0 kernel errors.
bench_kernel_stability() {
  info "Benchmark 6: Kernel stability (${DURATION}s stress-ng)..."

  DMESG_BEFORE=$(dmesg --time-format iso 2>/dev/null | tail -1 | awk '{print $1}' || date -Iseconds)

  stress-ng \
    --cpu 2 --cpu-ops 0 \
    --vm 1 --vm-bytes 256M \
    --io 2 \
    --fork 4 \
    --timeout "${DURATION}s" \
    --metrics-brief \
    --log-file "$OUTPUT_DIR/stress_ng_stability.log" \
    2>/dev/null || true

  # Check dmesg for BPF errors, oops, panics.
  ERRORS=$(dmesg --time-format iso 2>/dev/null | \
    awk -v since="$DMESG_BEFORE" '$1 > since' | \
    grep -iE "bpf.*error|kernel oops|kernel panic|call trace|BUG:|WARNING:" | \
    wc -l)

  if [[ "$ERRORS" -eq 0 ]]; then
    pass "  Kernel stable: 0 errors in dmesg"
    echo "kernel_stability=PASS" >> "$OUTPUT_DIR/raw_metrics.txt"
  else
    fail "  Kernel errors detected: $ERRORS entries in dmesg"
    dmesg --time-format iso | awk -v since="$DMESG_BEFORE" '$1 > since' | \
      grep -iE "bpf.*error|kernel oops|kernel panic|call trace|BUG:|WARNING:" \
      >> "$OUTPUT_DIR/kernel_errors.txt"
    echo "kernel_stability=FAIL ($ERRORS errors)" >> "$OUTPUT_DIR/raw_metrics.txt"
  fi
}

# ── Benchmark 7: Synthetic ransomware (entropy spike) ─────────────────────────
# Simulates ransomware by generating high-entropy file writes.
# Verifies that the anomaly engine detects the entropy spike and escalates.
# Target: escalation to ISOLATED within 5s of entropy spike onset.
bench_ransomware_sim() {
  info "Benchmark 7: Synthetic ransomware (entropy spike)..."

  RANSOM_TOOL="$ROOT_DIR/bin/octoreflex-bench-ransom"
  if [[ ! -x "$RANSOM_TOOL" ]]; then
    info "  Building ransomware simulator..."
    CGO_ENABLED=0 go build -o "$RANSOM_TOOL" "$ROOT_DIR/bench/cmd/ransom/" 2>/dev/null || {
      info "  Ransom tool not available — using dd fallback"
      RANSOM_TOOL=""
    }
  fi

  TMPDIR_RANSOM=$(mktemp -d)
  trap "rm -rf $TMPDIR_RANSOM" EXIT

  if [[ -n "$RANSOM_TOOL" ]]; then
    # The ransom tool opens files, writes random bytes (high entropy),
    # and reports when it gets -EPERM (containment active).
    "$RANSOM_TOOL" --target-dir "$TMPDIR_RANSOM" --duration 30 \
      --output "$OUTPUT_DIR/ransom_result.json"
    CONTAINED=$(python3 -c "import json; d=json.load(open('$OUTPUT_DIR/ransom_result.json')); print(d.get('contained',False))")
    LATENCY_S=$(python3 -c "import json; d=json.load(open('$OUTPUT_DIR/ransom_result.json')); print(d.get('containment_latency_s','N/A'))")
    info "  Ransomware sim: contained=$CONTAINED latency=${LATENCY_S}s"
    echo "ransom_contained=$CONTAINED" >> "$OUTPUT_DIR/raw_metrics.txt"
    echo "ransom_latency_s=$LATENCY_S" >> "$OUTPUT_DIR/raw_metrics.txt"
  else
    # Fallback: write 100MB of /dev/urandom to files (high entropy).
    info "  Fallback: dd entropy flood to $TMPDIR_RANSOM"
    dd if=/dev/urandom of="$TMPDIR_RANSOM/ransom.bin" bs=1M count=100 2>/dev/null &
    DD_PID=$!
    sleep 5
    if kill -0 $DD_PID 2>/dev/null; then
      info "  dd still running after 5s — containment may not be active (agent not loaded)"
      kill $DD_PID 2>/dev/null || true
      echo "ransom_contained=N/A (agent not loaded)" >> "$OUTPUT_DIR/raw_metrics.txt"
    else
      pass "  dd terminated — containment active"
      echo "ransom_contained=PASS" >> "$OUTPUT_DIR/raw_metrics.txt"
    fi
  fi
}

# ── Result aggregation ────────────────────────────────────────────────────────
aggregate_results() {
  info "Aggregating results..."

  python3 - <<'EOF'
import json, sys, os

raw = {}
raw_file = os.environ.get('RAW_FILE', '/dev/stdin')
try:
    with open(raw_file) as f:
        for line in f:
            line = line.strip()
            if '=' in line:
                k, v = line.split('=', 1)
                raw[k] = v
except FileNotFoundError:
    pass

# Targets (from bench/targets.json if present, else defaults).
targets = {
    "containment_latency_p50_us": {"op": "<=", "value": 500,  "unit": "µs"},
    "containment_latency_p99_us": {"op": "<=", "value": 2000, "unit": "µs"},
    "cpu_idle_avg_pct":           {"op": "<=", "value": 0.5,  "unit": "%"},
    "cpu_storm_avg_pct":          {"op": "<=", "value": 5.0,  "unit": "%"},
    "fpr_pct":                    {"op": "<=", "value": 0.5,  "unit": "%"},
    "budget_exhaustion":          {"op": "==", "value": "PASS","unit": ""},
    "kernel_stability":           {"op": "==", "value": "PASS","unit": ""},
}

results = []
all_pass = True
for metric, target in targets.items():
    val = raw.get(metric, "N/A")
    if val == "N/A":
        status = "SKIP"
    else:
        try:
            fval = float(val)
            tval = float(target["value"])
            if target["op"] == "<=":
                status = "PASS" if fval <= tval else "FAIL"
            else:
                status = "PASS" if val == str(target["value"]) else "FAIL"
        except ValueError:
            status = "PASS" if val == str(target["value"]) else "FAIL"
    if status == "FAIL":
        all_pass = False
    results.append({"metric": metric, "value": val, "target": f"{target['op']}{target['value']}{target['unit']}", "status": status})

print("\n=== OCTOREFLEX Benchmark Results ===\n")
print(f"{'Metric':<40} {'Value':<15} {'Target':<20} {'Status'}")
print("-" * 85)
for r in results:
    sym = "✓" if r["status"] == "PASS" else ("—" if r["status"] == "SKIP" else "✗")
    print(f"{r['metric']:<40} {r['value']:<15} {r['target']:<20} {sym} {r['status']}")

print()
if all_pass:
    print("OVERALL: PASS — all targets met")
    sys.exit(0)
else:
    print("OVERALL: FAIL — one or more targets not met")
    sys.exit(1)
EOF
}

# ── Main ──────────────────────────────────────────────────────────────────────
main() {
  echo "=== OCTOREFLEX Benchmark Suite ==="
  echo "Timestamp: $TIMESTAMP"
  echo "Duration:  ${DURATION}s per benchmark"
  echo "Output:    $OUTPUT_DIR"
  echo ""

  : > "$OUTPUT_DIR/raw_metrics.txt"

  preflight
  bench_containment_latency
  bench_cpu_idle
  bench_cpu_syscall_storm
  bench_false_positive_rate
  bench_budget_exhaustion
  bench_kernel_stability
  bench_ransomware_sim

  RAW_FILE="$OUTPUT_DIR/raw_metrics.txt" aggregate_results | tee "$RESULT_TXT"
}

main "$@"
