#!/usr/bin/env bash
# =============================================================================
# PETP Background Mode — CLI Integration Tests
# =============================================================================
# Run: bash testcoverage/test_cli_commands.sh
#
# Tests all CLI arguments of PETP_background.py by actually invoking them
# and checking exit codes / output patterns.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

PASS=0
FAIL=0
ERRORS=()

run_test() {
    local label="$1"
    local cmd="$2"
    local expect_exit="${3:-0}"
    local expect_output="$4"

    printf "  %-60s " "$label"
    output=$(eval "$cmd" 2>&1)
    actual_exit=$?

    if [ "$actual_exit" -ne "$expect_exit" ]; then
        echo "FAIL (exit=$actual_exit, expected=$expect_exit)"
        FAIL=$((FAIL + 1))
        ERRORS+=("$label: exit=$actual_exit expected=$expect_exit")
        return
    fi

    if [ -n "$expect_output" ]; then
        if echo "$output" | grep -q "$expect_output"; then
            echo "PASS"
            PASS=$((PASS + 1))
        else
            echo "FAIL (output missing: $expect_output)"
            FAIL=$((FAIL + 1))
            ERRORS+=("$label: missing output pattern '$expect_output'")
        fi
    else
        echo "PASS"
        PASS=$((PASS + 1))
    fi
}

echo "=============================="
echo " PETP CLI Integration Tests"
echo "=============================="
echo ""

# ---------------------------------------------------------------------------
# --run-execution (single execution, no HTTP server)
# ---------------------------------------------------------------------------
echo "▶ --run-execution"

run_test \
    "ENDECODER encode (base64)" \
    "python PETP_background.py --run-execution ENDECODER --init-data '{\"type\":\"ENCODE\",\"algorithms\":\"base64\",\"inbound\":\"hello\"}' --no-http" \
    0 \
    "\"ok\": true"

run_test \
    "ENDECODER decode (base64)" \
    "python PETP_background.py --run-execution ENDECODER --init-data '{\"type\":\"DECODE\",\"algorithms\":\"base64\",\"inbound\":\"aGVsbG8=\"}' --no-http" \
    0 \
    "\"ok\": true"

run_test \
    "Non-existent execution" \
    "python PETP_background.py --run-execution __DOES_NOT_EXIST__ --no-http" \
    0 \
    "\"ok\": false"

run_test \
    "With init-data JSON object" \
    "python PETP_background.py --run-execution ENDECODER --init-data '{\"type\":\"ENCODE\",\"algorithms\":\"base64\",\"inbound\":\"data\"}' --no-http" \
    0 \
    "\"ok\": true"

# ---------------------------------------------------------------------------
# --run-pipeline (single pipeline, no HTTP server)
# ---------------------------------------------------------------------------
echo ""
echo "▶ --run-pipeline"

run_test \
    "Non-existent pipeline" \
    "python PETP_background.py --run-pipeline __NO_SUCH_PIPELINE__ --no-http" \
    0 \
    "\"ok\": false"

run_test \
    "OOTB_TEST_PIPLINE_BG pipeline" \
    "python PETP_background.py --run-pipeline OOTB_TEST_PIPLINE_BG --no-http" \
    0 \
    "Immediate pipeline result"

# ---------------------------------------------------------------------------
# --ui-policy
# ---------------------------------------------------------------------------
echo ""
echo "▶ --ui-policy"

run_test \
    "ui-policy=skip (default)" \
    "python PETP_background.py --run-execution ENDECODER --init-data '{\"type\":\"ENCODE\",\"algorithms\":\"base64\",\"inbound\":\"x\"}' --ui-policy skip --no-http" \
    0 \
    "\"ok\": true"

run_test \
    "ui-policy=abort" \
    "python PETP_background.py --run-execution ENDECODER --init-data '{\"type\":\"ENCODE\",\"algorithms\":\"base64\",\"inbound\":\"x\"}' --ui-policy abort --no-http" \
    0 \
    "\"ok\": true"

# ---------------------------------------------------------------------------
# --headless
# ---------------------------------------------------------------------------
echo ""
echo "▶ --headless"

run_test \
    "headless flag accepted" \
    "python PETP_background.py --run-execution ENDECODER --init-data '{\"type\":\"ENCODE\",\"algorithms\":\"base64\",\"inbound\":\"h\"}' --headless --no-http" \
    0 \
    "\"ok\": true"

# ---------------------------------------------------------------------------
# --log-level
# ---------------------------------------------------------------------------
echo ""
echo "▶ --log-level"

run_test \
    "log-level=DEBUG" \
    "python PETP_background.py --run-execution ENDECODER --init-data '{\"type\":\"ENCODE\",\"algorithms\":\"base64\",\"inbound\":\"d\"}' --log-level DEBUG --no-http" \
    0 \
    "\"ok\": true"

run_test \
    "log-level=WARNING (suppresses INFO output)" \
    "python PETP_background.py --run-execution ENDECODER --init-data '{\"type\":\"ENCODE\",\"algorithms\":\"base64\",\"inbound\":\"w\"}' --log-level WARNING --no-http" \
    0 \
    ""

# ---------------------------------------------------------------------------
# --init-data validation
# ---------------------------------------------------------------------------
echo ""
echo "▶ --init-data validation"

run_test \
    "Invalid JSON init-data" \
    "python PETP_background.py --run-execution ENDECODER --init-data 'not-json' --no-http" \
    1 \
    "Invalid --init-data"

run_test \
    "Non-object init-data (array)" \
    "python PETP_background.py --run-execution ENDECODER --init-data '[1,2,3]' --no-http" \
    1 \
    "must be a JSON object"

run_test \
    "Empty init-data (default)" \
    "python PETP_background.py --run-execution ENDECODER --no-http" \
    0 \
    "\"ok\": true"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
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
