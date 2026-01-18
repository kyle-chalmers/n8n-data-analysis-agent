# Feature: n8n Workflow Creation for Production Line Health Advisor

## Summary

Create and deploy two n8n workflows that connect to the existing FastAPI backend: (1) CSV Analysis workflow that accepts file uploads and returns AI-powered health reports with charts, and (2) Chat workflow for follow-up questions. Workflows will be created as JSON files and imported via n8n's REST API using an API key.

## User Story

As a workshop facilitator demonstrating AI capabilities
I want n8n workflows that accept CSV uploads and enable follow-up chat
So that participants can interact with the Production Health Advisor through n8n's visual interface

## Problem Statement

The FastAPI backend is fully functional (`/webhook/analyze` and `/webhook/chat` endpoints work), but there are no n8n workflows to expose these capabilities through n8n's user-friendly interface. Without workflows, users must interact directly with the API via curl.

## Solution Statement

Create two n8n workflow JSON files, import them via the n8n REST API (authenticated with API key), activate them, and verify end-to-end functionality. The workflows will use Webhook triggers to receive requests and HTTP Request nodes to forward to FastAPI.

## Metadata

| Field            | Value                                              |
| ---------------- | -------------------------------------------------- |
| Type             | NEW_CAPABILITY                                     |
| Complexity       | MEDIUM                                             |
| Systems Affected | n8n, FastAPI (existing)                            |
| Dependencies     | n8n REST API, N8N_API_KEY environment variable     |
| Estimated Tasks  | 8                                                  |

---

## Pre-Flight Checklist (HUMAN ACTION REQUIRED)

**CRITICAL: Complete these BEFORE running ralph loop.**

### 1. Generate n8n API Key

```
1. Open n8n: http://localhost:5678
2. Click your user icon (top-right) → Settings
3. Navigate to "API" section
4. Click "Create API Key"
5. Copy the generated key
```

### 2. Add API Key to .env

```bash
cd /Users/kylechalmers/Development/n8n-data-analysis-agent

# Add to .env file
echo "N8N_API_KEY=your-api-key-here" >> .env
```

### 3. Verify Prerequisites

```bash
# Run this to verify all prerequisites:
source .env && \
curl -s http://localhost:8000/health | grep -q "healthy" && \
curl -s http://localhost:5678/healthz && \
test -n "$N8N_API_KEY" && \
echo "✅ All prerequisites met - ready for ralph loop"
```

**IMPORTANT**: Do NOT proceed until you have completed the API key setup.

### 4. API Permissions Verified ✅

The following API permissions have been tested and confirmed working:
- ✅ `GET /api/v1/workflows` - List workflows
- ✅ `POST /api/v1/workflows` - Create workflow (note: `active` field is read-only)
- ✅ `POST /api/v1/workflows/{id}/activate` - Activate workflow
- ✅ `DELETE /api/v1/workflows/{id}` - Delete workflow

---

## UX Design

### Before State

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              BEFORE STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐║
║   │   User has      │         │   Must use      │         │   JSON output   │║
║   │   CSV file      │ ──────► │   curl command  │ ──────► │   in terminal   │║
║   └─────────────────┘         └─────────────────┘         └─────────────────┘║
║                                                                               ║
║   USER_FLOW: User must know API endpoint, use curl, parse JSON manually       ║
║   PAIN_POINT: Technical barrier, no visual interface, poor demo experience    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### After State

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                               AFTER STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐║
║   │   n8n Webhook   │         │   n8n HTTP      │         │   Formatted     │║
║   │   receives CSV  │ ──────► │   Request to    │ ──────► │   JSON + Charts │║
║   │   via POST      │         │   FastAPI       │         │   returned      │║
║   └─────────────────┘         └─────────────────┘         └─────────────────┘║
║           │                                                       │           ║
║           │                                                       │           ║
║           ▼                                                       ▼           ║
║   ┌─────────────────┐                                    ┌─────────────────┐ ║
║   │  Chat Webhook   │ ──── session_id + message ────────►│  Follow-up      │ ║
║   │  for questions  │                                    │  Analysis       │ ║
║   └─────────────────┘                                    └─────────────────┘ ║
║                                                                               ║
║   USER_FLOW: Upload CSV → Get report → Ask follow-up questions                ║
║   VALUE_ADD: Visual workflow, easy demo, professional interface               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Mandatory Reading

**External Documentation:**

| Source | Section | Why Needed |
|--------|---------|------------|
| [n8n Export/Import Docs](https://docs.n8n.io/workflows/export-import/) | Workflow JSON format | Understand required JSON structure |
| [n8n API Reference](https://docs.n8n.io/api/api-reference/) | Workflow endpoints | POST/PATCH workflow API calls |
| [n8n API Authentication](https://docs.n8n.io/api/authentication/) | X-N8N-API-KEY header | Authentication for API calls |

---

## Files to Create

| File                                              | Action | Purpose                                    |
| ------------------------------------------------- | ------ | ------------------------------------------ |
| `n8n/workflows/01-production-analysis.json`       | CREATE | CSV upload → analysis workflow             |
| `n8n/workflows/02-production-chat.json`           | CREATE | Chat follow-up workflow                    |
| `scripts/import-n8n-workflows.sh`                 | CREATE | Script to import and activate workflows    |
| `scripts/test-n8n-workflows.sh`                   | CREATE | End-to-end test script                     |
| `n8n/workflows/README.md`                         | CREATE | Documentation for manual import            |

---

## NOT Building (Scope Limits)

- **n8n credentials management** - Using direct API calls, no stored credentials
- **Error retry logic in n8n** - Simple pass-through, errors handled by FastAPI
- **Response transformation** - Return FastAPI response as-is
- **UI customization** - Default n8n webhook response format

---

## Step-by-Step Tasks

Execute in order. Each task is atomic and independently verifiable.

---

### Task 1: CREATE `n8n/workflows/01-production-analysis.json`

- [x] **COMPLETED**

**ACTION**: Create the CSV analysis workflow JSON

**FILE**: `n8n/workflows/01-production-analysis.json`

**IMPLEMENT**: n8n workflow with these nodes:
1. **Webhook** node (trigger)
   - Name: "CSV Upload Webhook"
   - HTTP Method: POST
   - Path: `production-analyze`
   - Response Mode: "Response Node"
   - Binary Data: true (to accept file uploads)

2. **HTTP Request** node
   - Name: "Call FastAPI Analysis"
   - Method: POST
   - URL: `http://production-analyst:8000/webhook/analyze`
   - Content Type: Multipart Form Data
   - Body Parameters: `file` = binary data from webhook

3. **Respond to Webhook** node
   - Name: "Return Analysis"
   - Respond With: JSON
   - Response Body: `{{ $json }}`

**NODE POSITIONS** (for visual layout):
- Webhook: [250, 300]
- HTTP Request: [500, 300]
- Respond to Webhook: [750, 300]

**CONNECTIONS**:
- Webhook → HTTP Request (main output)
- HTTP Request → Respond to Webhook (main output)

**VALIDATE**:
```bash
cat n8n/workflows/01-production-analysis.json | python3 -m json.tool > /dev/null && echo "✅ Valid JSON"

python3 << 'EOF'
import json
with open('n8n/workflows/01-production-analysis.json') as f:
    wf = json.load(f)

# Check required fields
assert 'name' in wf, "Missing 'name' field"
assert 'nodes' in wf, "Missing 'nodes' field"
assert 'connections' in wf, "Missing 'connections' field"

# Check node types
node_types = {n['type'] for n in wf['nodes']}
required = {'n8n-nodes-base.webhook', 'n8n-nodes-base.httpRequest', 'n8n-nodes-base.respondToWebhook'}
missing = required - node_types
assert not missing, f"Missing nodes: {missing}"

# Check connections exist
assert wf['connections'], "No connections defined"

print("✅ 01-production-analysis.json structure valid")
EOF
```

---

### Task 2: CREATE `n8n/workflows/02-production-chat.json`

- [x] **COMPLETED**

**ACTION**: Create the chat follow-up workflow JSON

**FILE**: `n8n/workflows/02-production-chat.json`

**IMPLEMENT**: n8n workflow with these nodes:
1. **Webhook** node (trigger)
   - Name: "Chat Webhook"
   - HTTP Method: POST
   - Path: `production-chat`
   - Response Mode: "Response Node"
   - Authentication: None

2. **HTTP Request** node
   - Name: "Call FastAPI Chat"
   - Method: POST
   - URL: `http://production-analyst:8000/webhook/chat`
   - Content Type: JSON
   - Body: `{"session_id": "{{ $json.session_id }}", "message": "{{ $json.message }}"}`

3. **Respond to Webhook** node
   - Name: "Return Chat Response"
   - Respond With: JSON
   - Response Body: `{{ $json }}`

**VALIDATE**:
```bash
cat n8n/workflows/02-production-chat.json | python3 -m json.tool > /dev/null && echo "✅ Valid JSON"

python3 << 'EOF'
import json
with open('n8n/workflows/02-production-chat.json') as f:
    wf = json.load(f)

assert 'name' in wf, "Missing 'name' field"
assert 'nodes' in wf, "Missing 'nodes' field"
assert len(wf['nodes']) >= 3, "Expected at least 3 nodes"

# Check webhook path is different from analysis workflow
webhook_node = next((n for n in wf['nodes'] if n['type'] == 'n8n-nodes-base.webhook'), None)
assert webhook_node, "No webhook node found"
assert 'chat' in webhook_node['parameters'].get('path', '').lower(), "Webhook path should contain 'chat'"

print("✅ 02-production-chat.json structure valid")
EOF
```

---

### Task 3: CREATE `scripts/import-n8n-workflows.sh`

- [x] **COMPLETED**

**ACTION**: Create script to import workflows via n8n API

**FILE**: `scripts/import-n8n-workflows.sh`

**IMPLEMENT**: Bash script that:
1. Loads N8N_API_KEY from .env
2. POSTs each workflow JSON to n8n API
3. Activates each imported workflow
4. Reports success/failure

**API DETAILS** (verified working):
- Create workflow: `POST http://localhost:5678/api/v1/workflows`
  - NOTE: `active` field is READ-ONLY - do NOT include in request body
- Activate workflow: `POST http://localhost:5678/api/v1/workflows/{id}/activate`
- List workflows: `GET http://localhost:5678/api/v1/workflows`
- Auth header: `X-N8N-API-KEY: {key}`

**VALIDATE**:
```bash
test -f scripts/import-n8n-workflows.sh && echo "✅ Script exists"
test -x scripts/import-n8n-workflows.sh || chmod +x scripts/import-n8n-workflows.sh
head -1 scripts/import-n8n-workflows.sh | grep -q "#!/bin/bash" && echo "✅ Has shebang"
grep -q "N8N_API_KEY" scripts/import-n8n-workflows.sh && echo "✅ Uses API key"
grep -q "api/v1/workflows" scripts/import-n8n-workflows.sh && echo "✅ Calls workflow API"
```

---

### Task 4: CREATE `scripts/test-n8n-workflows.sh`

- [x] **COMPLETED**

**ACTION**: Create end-to-end test script

**FILE**: `scripts/test-n8n-workflows.sh`

**IMPLEMENT**: Bash script that:
1. Tests services are running (FastAPI, n8n)
2. Tests workflow is active via API
3. POSTs CSV to analysis webhook, validates response
4. POSTs chat message with session_id, validates response
5. Reports pass/fail for each test

**VALIDATE**:
```bash
test -f scripts/test-n8n-workflows.sh && echo "✅ Script exists"
chmod +x scripts/test-n8n-workflows.sh
grep -q "webhook/production-analyze" scripts/test-n8n-workflows.sh && echo "✅ Tests analysis webhook"
grep -q "webhook/production-chat" scripts/test-n8n-workflows.sh && echo "✅ Tests chat webhook"
```

---

### Task 5: CREATE `n8n/workflows/README.md`

- [x] **COMPLETED**

**ACTION**: Create documentation for manual import fallback

**FILE**: `n8n/workflows/README.md`

**IMPLEMENT**: Markdown documentation with:
1. Overview of both workflows
2. Manual import instructions (UI-based)
3. How to activate workflows
4. Testing instructions
5. Troubleshooting common issues

**VALIDATE**:
```bash
test -f n8n/workflows/README.md && echo "✅ README exists"
grep -q "production-analyze" n8n/workflows/README.md && echo "✅ Documents analysis workflow"
grep -q "production-chat" n8n/workflows/README.md && echo "✅ Documents chat workflow"
```

---

### Task 6: EXECUTE workflow import

- [x] **COMPLETED**

**ACTION**: Run the import script to deploy workflows to n8n

**EXECUTE**:
```bash
cd /Users/kylechalmers/Development/n8n-data-analysis-agent
./scripts/import-n8n-workflows.sh
```

**VALIDATE**:
```bash
# Check workflows exist via API
source .env
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" http://localhost:5678/api/v1/workflows | python3 -c "
import sys, json
data = json.load(sys.stdin)
workflows = data.get('data', [])
if len(workflows) < 2:
    print(f'❌ Expected 2 workflows, found {len(workflows)}')
    sys.exit(1)
for wf in workflows:
    status = '🟢 Active' if wf.get('active') else '🔴 Inactive'
    print(f\"{status}: {wf.get('name')} (ID: {wf.get('id')})\")
print('✅ Workflows imported')
"
```

---

### Task 7: ACTIVATE workflows

- [x] **COMPLETED**

**ACTION**: Ensure both workflows are activated (webhooks listening)

**EXECUTE** (if not already active from import):
```bash
source .env

# Get workflow IDs and activate each
WORKFLOW_IDS=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" http://localhost:5678/api/v1/workflows | \
  python3 -c "import sys,json; print(' '.join(str(w['id']) for w in json.load(sys.stdin).get('data',[])))")

for ID in $WORKFLOW_IDS; do
  echo "Activating workflow $ID..."
  curl -s -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
    "http://localhost:5678/api/v1/workflows/$ID/activate"
done
```

**VALIDATE**:
```bash
source .env
ACTIVE_COUNT=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" http://localhost:5678/api/v1/workflows | \
  python3 -c "import sys,json; print(len([w for w in json.load(sys.stdin).get('data',[]) if w.get('active')]))")

if [ "$ACTIVE_COUNT" -ge 2 ]; then
  echo "✅ $ACTIVE_COUNT workflows active"
else
  echo "❌ Only $ACTIVE_COUNT workflows active, expected 2"
  exit 1
fi
```

---

### Task 8: END-TO-END validation

- [x] **COMPLETED**

**ACTION**: Run complete end-to-end test

**EXECUTE**:
```bash
cd /Users/kylechalmers/Development/n8n-data-analysis-agent
./scripts/test-n8n-workflows.sh
```

**VALIDATE** (manual verification if script fails):
```bash
# Test 1: Analysis webhook
echo "Testing analysis webhook..."
ANALYSIS_RESPONSE=$(curl -s -X POST "http://localhost:5678/webhook/production-analyze" \
  -F "file=@data/sample/predictive_maintenance.csv")

SESSION_ID=$(echo "$ANALYSIS_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null)

if [ -n "$SESSION_ID" ]; then
  echo "✅ Analysis webhook returned session_id: ${SESSION_ID:0:20}..."
else
  echo "❌ Analysis webhook failed"
  echo "$ANALYSIS_RESPONSE"
  exit 1
fi

# Test 2: Chat webhook
echo "Testing chat webhook..."
CHAT_RESPONSE=$(curl -s -X POST "http://localhost:5678/webhook/production-chat" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"What is the overall failure rate?\"}")

if echo "$CHAT_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'response' in d or 'session_id' in d else 1)" 2>/dev/null; then
  echo "✅ Chat webhook returned valid response"
else
  echo "❌ Chat webhook failed"
  echo "$CHAT_RESPONSE"
  exit 1
fi

echo ""
echo "════════════════════════════════════════"
echo "✅ ALL END-TO-END TESTS PASSED"
echo "════════════════════════════════════════"
```

---

## Validation Commands (All Levels)

### Level 1: Files Created

```bash
test -f n8n/workflows/01-production-analysis.json && echo "✅ Analysis workflow JSON"
test -f n8n/workflows/02-production-chat.json && echo "✅ Chat workflow JSON"
test -f scripts/import-n8n-workflows.sh && echo "✅ Import script"
test -f scripts/test-n8n-workflows.sh && echo "✅ Test script"
test -f n8n/workflows/README.md && echo "✅ README"
```

### Level 2: JSON Valid

```bash
python3 -m json.tool n8n/workflows/01-production-analysis.json > /dev/null && echo "✅ Analysis JSON valid"
python3 -m json.tool n8n/workflows/02-production-chat.json > /dev/null && echo "✅ Chat JSON valid"
```

### Level 3: Workflows Imported & Active

```bash
source .env
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" http://localhost:5678/api/v1/workflows | python3 -c "
import sys, json
data = json.load(sys.stdin)
workflows = data.get('data', [])
active = [w for w in workflows if w.get('active')]
print(f'Workflows: {len(workflows)}, Active: {len(active)}')
if len(active) >= 2:
    print('✅ Level 3 PASSED')
else:
    print('❌ Level 3 FAILED')
    sys.exit(1)
"
```

### Level 4: End-to-End Test

```bash
./scripts/test-n8n-workflows.sh
```

---

## Acceptance Criteria

- [ ] `n8n/workflows/01-production-analysis.json` exists and is valid n8n workflow JSON
- [ ] `n8n/workflows/02-production-chat.json` exists and is valid n8n workflow JSON
- [ ] Both workflows imported into n8n (visible in n8n UI)
- [ ] Both workflows are ACTIVE (webhooks listening)
- [ ] `POST /webhook/production-analyze` with CSV returns analysis with session_id
- [ ] `POST /webhook/production-chat` with session_id and message returns response
- [ ] `scripts/test-n8n-workflows.sh` passes all checks

---

## Completion Checklist

- [x] Pre-flight: N8N_API_KEY configured in .env
- [x] Task 1: Analysis workflow JSON created
- [x] Task 2: Chat workflow JSON created
- [x] Task 3: Import script created
- [x] Task 4: Test script created
- [x] Task 5: README documentation created
- [x] Task 6: Workflows imported to n8n
- [x] Task 7: Workflows activated
- [x] Task 8: End-to-end tests pass
- [x] Level 1-4 validation commands all pass

---

## Risks and Mitigations

| Risk                          | Likelihood | Impact | Mitigation                                         |
| ----------------------------- | ---------- | ------ | -------------------------------------------------- |
| n8n API auth fails            | Medium     | High   | README includes manual import fallback instructions |
| Webhook path conflicts        | Low        | Medium | Use unique paths: production-analyze, production-chat |
| Binary file handling in n8n   | Medium     | High   | Test with actual CSV, verify multipart form config |
| Docker network connectivity   | Low        | High   | Use container name (production-analyst) not localhost |

---

## Notes

**n8n Workflow JSON Format:**
- Must include: `name`, `nodes`, `connections`, `settings`
- Each node needs: `id`, `name`, `type`, `typeVersion`, `position`, `parameters`
- Connections are keyed by source node name

**API Endpoints** (verified 2026-01-18):
- Create: `POST /api/v1/workflows` with workflow JSON body
  - IMPORTANT: `active` field is READ-ONLY, do not include in body
- Activate: `POST /api/v1/workflows/{id}/activate` (not PATCH!)
- List: `GET /api/v1/workflows`
- Auth: `X-N8N-API-KEY` header

**Container Networking:**
- n8n container reaches FastAPI via `http://production-analyst:8000` (Docker network)
- External clients reach n8n webhooks via `http://localhost:5678/webhook/{path}`

**Sources:**
- [n8n Export/Import Docs](https://docs.n8n.io/workflows/export-import/)
- [n8n API Reference](https://docs.n8n.io/api/api-reference/)
- [n8n API Authentication](https://docs.n8n.io/api/authentication/)
