#!/bin/bash
set -e

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

N8N_URL="${N8N_URL:-http://localhost:5678}"
FASTAPI_URL="${FASTAPI_URL:-http://localhost:8000}"
SAMPLE_CSV="$PROJECT_DIR/data/sample/predictive_maintenance.csv"

echo "=== n8n Workflow End-to-End Tests ==="
echo ""

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

test_pass() {
    echo "✅ $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo "❌ $1"
    echo "   $2"
    ((TESTS_FAILED++))
}

# Test 1: FastAPI is running
echo "Test 1: FastAPI health check"
if curl -s "$FASTAPI_URL/health" | grep -q "healthy"; then
    test_pass "FastAPI is healthy"
else
    test_fail "FastAPI not responding" "URL: $FASTAPI_URL/health"
fi

# Test 2: n8n is running
echo ""
echo "Test 2: n8n health check"
if curl -s "$N8N_URL/healthz" > /dev/null 2>&1; then
    test_pass "n8n is healthy"
else
    test_fail "n8n not responding" "URL: $N8N_URL/healthz"
fi

# Test 3: Workflows are active
echo ""
echo "Test 3: Workflows are active"
if [ -n "$N8N_API_KEY" ]; then
    ACTIVE_COUNT=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_URL/api/v1/workflows" | \
        python3 -c "import sys,json; print(len([w for w in json.load(sys.stdin).get('data',[]) if w.get('active')]))" 2>/dev/null || echo "0")
    
    if [ "$ACTIVE_COUNT" -ge 2 ]; then
        test_pass "$ACTIVE_COUNT workflows active"
    else
        test_fail "Expected 2 active workflows" "Found: $ACTIVE_COUNT"
    fi
else
    echo "⚠️  Skipping (N8N_API_KEY not set)"
fi

# Test 4: Analysis webhook
echo ""
echo "Test 4: Analysis webhook (CSV upload)"
if [ -f "$SAMPLE_CSV" ]; then
    ANALYSIS_RESPONSE=$(curl -s -X POST "$N8N_URL/webhook/production-analyze" \
        -F "file=@$SAMPLE_CSV" 2>/dev/null)
    
    SESSION_ID=$(echo "$ANALYSIS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)
    
    if [ -n "$SESSION_ID" ]; then
        test_pass "Analysis returned session_id: ${SESSION_ID:0:20}..."
        
        # Test 5: Chat webhook
        echo ""
        echo "Test 5: Chat webhook (follow-up question)"
        CHAT_RESPONSE=$(curl -s -X POST "$N8N_URL/webhook/production-chat" \
            -H "Content-Type: application/json" \
            -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"What is the overall failure rate?\"}" 2>/dev/null)
        
        if echo "$CHAT_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'response' in d or 'session_id' in d else 1)" 2>/dev/null; then
            test_pass "Chat returned valid response"
        else
            test_fail "Chat webhook failed" "Response: $CHAT_RESPONSE"
        fi
    else
        test_fail "Analysis webhook failed" "Response: $ANALYSIS_RESPONSE"
        echo ""
        echo "Test 5: Chat webhook"
        echo "⚠️  Skipping (no session_id from analysis)"
    fi
else
    test_fail "Sample CSV not found" "Expected: $SAMPLE_CSV"
    echo ""
    echo "Test 5: Chat webhook"
    echo "⚠️  Skipping (no CSV for analysis)"
fi

# Summary
echo ""
echo "════════════════════════════════════════"
echo "Test Results: $TESTS_PASSED passed, $TESTS_FAILED failed"
echo "════════════════════════════════════════"

if [ "$TESTS_FAILED" -gt 0 ]; then
    exit 1
fi
