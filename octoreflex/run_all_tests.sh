#!/usr/bin/env bash
#
# run_all_tests.sh - OCTOREFLEX Master Test Runner
#
# Executes the complete test suite with proper ordering and reporting.
# Designed for CI/CD pipelines and pre-release validation.
#
# Usage:
#   ./run_all_tests.sh [OPTIONS]
#
# Options:
#   --quick         Run unit tests only (fast pre-commit check)
#   --integration   Include integration tests (requires root)
#   --full          Run complete test suite including chaos and fuzzing
#   --coverage      Generate HTML coverage report
#   --benchmark     Run performance benchmarks
#   --verbose       Enable verbose output
#   --help          Show this help message
#
# Exit codes:
#   0 - All tests passed
#   1 - Test failures detected
#   2 - Missing dependencies or prerequisites

set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default options
RUN_UNIT=1
RUN_INTEGRATION=0
RUN_ADVERSARIAL=0
RUN_FUZZ=0
RUN_PERFORMANCE=0
RUN_CHAOS=0
GENERATE_COVERAGE=0
VERBOSE=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ── Functions ────────────────────────────────────────────────────────────────

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $*"
}

log_error() {
    echo -e "${RED}[✗]${NC} $*"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Go
    if ! command -v go &> /dev/null; then
        log_error "Go not found. Install Go 1.22+"
        exit 2
    fi

    GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
    log_info "Go version: $GO_VERSION"

    # Check for BPF requirements (integration tests)
    if [ $RUN_INTEGRATION -eq 1 ]; then
        if [ ! -f /sys/kernel/btf/vmlinux ]; then
            log_warning "BTF not available. Integration tests will be skipped."
            RUN_INTEGRATION=0
        fi

        if [ "$(id -u)" -ne 0 ]; then
            log_warning "Not running as root. Integration tests require sudo."
            RUN_INTEGRATION=0
        fi

        if [ ! -f bpf/octoreflex.bpf.o ]; then
            log_info "Building eBPF programs..."
            make bpf
        fi
    fi

    log_success "Prerequisites check passed"
}

run_unit_tests() {
    log_info "Running unit tests..."
    
    local flags="-v -race -count=1"
    if [ $GENERATE_COVERAGE -eq 1 ]; then
        flags="$flags -coverprofile=coverage.out"
    fi

    if go test $flags ./internal/...; then
        log_success "Unit tests PASSED"
        
        if [ $GENERATE_COVERAGE -eq 1 ]; then
            local coverage=$(go tool cover -func=coverage.out | grep total | awk '{print $3}')
            log_info "Coverage: $coverage"
            
            go tool cover -html=coverage.out -o coverage.html
            log_success "Coverage report: coverage.html"
        fi
        return 0
    else
        log_error "Unit tests FAILED"
        return 1
    fi
}

run_integration_tests() {
    log_info "Running integration tests..."
    
    if sudo go test -v -count=1 ./test/integration/...; then
        log_success "Integration tests PASSED"
        return 0
    else
        log_error "Integration tests FAILED"
        return 1
    fi
}

run_adversarial_tests() {
    log_info "Running adversarial attack simulations..."
    
    if go test -v -count=1 ./test/adversarial/...; then
        log_success "Adversarial tests PASSED"
        return 0
    else
        log_error "Adversarial tests FAILED"
        return 1
    fi
}

run_fuzz_tests() {
    log_info "Running fuzz tests (10s per target)..."
    
    local targets=("FuzzEventParser" "FuzzConfigParser" "FuzzAnomalyScore")
    local all_passed=1
    
    for target in "${targets[@]}"; do
        log_info "Fuzzing $target..."
        if go test -fuzz="$target" -fuzztime=10s ./test/fuzz 2>&1 | grep -q "FAIL"; then
            log_error "Fuzzing $target FAILED"
            all_passed=0
        else
            log_success "Fuzzing $target PASSED"
        fi
    done
    
    return $all_passed
}

run_performance_tests() {
    log_info "Running performance benchmarks..."
    
    if go test -bench=. -benchtime=10s -benchmem ./test/performance | tee bench.txt; then
        log_success "Performance tests PASSED"
        
        # Parse results
        if grep -q "BenchmarkContainmentLatency" bench.txt; then
            local latency=$(grep "BenchmarkContainmentLatency" bench.txt | awk '{print $3}')
            log_info "Containment latency: $latency"
        fi
        
        return 0
    else
        log_error "Performance tests FAILED"
        return 1
    fi
}

run_chaos_tests() {
    log_info "Running chaos engineering tests..."
    
    if go test -v -timeout=30m ./test/chaos; then
        log_success "Chaos tests PASSED"
        return 0
    else
        log_error "Chaos tests FAILED"
        return 1
    fi
}

# ── Argument Parsing ─────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            # Only unit tests
            ;;
        --integration)
            RUN_INTEGRATION=1
            ;;
        --full)
            RUN_INTEGRATION=1
            RUN_ADVERSARIAL=1
            RUN_FUZZ=1
            RUN_PERFORMANCE=1
            RUN_CHAOS=1
            ;;
        --coverage)
            GENERATE_COVERAGE=1
            ;;
        --benchmark)
            RUN_PERFORMANCE=1
            ;;
        --verbose)
            VERBOSE=1
            set -x
            ;;
        --help)
            head -n 20 "$0" | tail -n +3 | sed 's/^# //'
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 2
            ;;
    esac
    shift
done

# ── Main Execution ───────────────────────────────────────────────────────────

main() {
    local start_time=$(date +%s)
    local failed_tests=()
    
    echo "=================================================="
    echo "   OCTOREFLEX Test Suite"
    echo "=================================================="
    echo ""
    
    check_prerequisites
    echo ""
    
    # Run tests in dependency order
    if [ $RUN_UNIT -eq 1 ]; then
        if ! run_unit_tests; then
            failed_tests+=("unit")
        fi
        echo ""
    fi
    
    if [ $RUN_INTEGRATION -eq 1 ]; then
        if ! run_integration_tests; then
            failed_tests+=("integration")
        fi
        echo ""
    fi
    
    if [ $RUN_ADVERSARIAL -eq 1 ]; then
        if ! run_adversarial_tests; then
            failed_tests+=("adversarial")
        fi
        echo ""
    fi
    
    if [ $RUN_PERFORMANCE -eq 1 ]; then
        if ! run_performance_tests; then
            failed_tests+=("performance")
        fi
        echo ""
    fi
    
    if [ $RUN_FUZZ -eq 1 ]; then
        if ! run_fuzz_tests; then
            failed_tests+=("fuzz")
        fi
        echo ""
    fi
    
    if [ $RUN_CHAOS -eq 1 ]; then
        if ! run_chaos_tests; then
            failed_tests+=("chaos")
        fi
        echo ""
    fi
    
    # Summary
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "=================================================="
    echo "   Test Summary"
    echo "=================================================="
    echo "Duration: ${duration}s"
    echo ""
    
    if [ ${#failed_tests[@]} -eq 0 ]; then
        log_success "ALL TESTS PASSED ✓"
        echo ""
        echo "🎉 Test suite completed successfully!"
        return 0
    else
        log_error "FAILED TEST SUITES:"
        for suite in "${failed_tests[@]}"; do
            echo "  - $suite"
        done
        echo ""
        echo "💥 Test suite failed. See logs above for details."
        return 1
    fi
}

# Run main and exit with its return code
main
exit $?
