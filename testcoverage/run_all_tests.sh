#!/usr/bin/env bash
# Run all PETP test cases and report pass/fail summary.
# Usage: bash testcoverage/run_all_tests.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

PASS=0
FAIL=0
ERRORS=()

run_standalone() {
    local label="$1"
    shift
    echo "▶ $label"
    if "$@"; then
        echo "  ✓ PASS"
        PASS=$((PASS + 1))
    else
        echo "  ✗ FAIL"
        FAIL=$((FAIL + 1))
        ERRORS+=("$label")
    fi
}

run_pytest() {
    local label="$1"
    shift
    echo "▶ $label"
    if python -m pytest "$@" -q --tb=short; then
        echo "  ✓ PASS"
        PASS=$((PASS + 1))
    else
        echo "  ✗ FAIL"
        FAIL=$((FAIL + 1))
        ERRORS+=("$label")
    fi
}

echo "=============================="
echo " PETP Test Suite"
echo "=============================="

# Standalone scripts (have their own __main__ entry point)
run_standalone "nogui_smoke"         python testcoverage/nogui_smoke.py
run_standalone "test_bg_runtime"     python testcoverage/test_bg_runtime.py
run_standalone "test_cli_commands"   bash testcoverage/test_cli_commands.sh

# Pytest suites (collected and run together in one invocation)
run_pytest "pytest suites" \
    testcoverage/test_cron_history.py \
    testcoverage/test_data_chain.py \
    testcoverage/test_execution_integration.py \
    testcoverage/test_expression2str.py \
    testcoverage/test_if_else.py \
    testcoverage/test_loop_state.py \
    testcoverage/test_processors.py \
    testcoverage/test_progress_and_warmup.py \
    testcoverage/test_mcp_batch.py

echo ""
echo "=============================="
echo " Results: ${PASS} passed, ${FAIL} failed"
echo "=============================="

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo " Failed:"
    for e in "${ERRORS[@]}"; do
        echo "   - $e"
    done
    exit 1
fi

exit 0
