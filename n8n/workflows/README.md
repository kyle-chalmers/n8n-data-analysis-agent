# n8n Workflows for Production Health Advisor

This directory contains n8n workflow JSON files that expose the Production Health Advisor API through n8n webhooks.

## Workflows

### 1. Production Line Analysis (`01-production-analysis.json`)

Accepts CSV file uploads and returns AI-powered health analysis reports.

- **Webhook Path**: `/webhook/production-analyze`
- **Method**: POST (multipart/form-data)
- **Input**: CSV file in `file` field
- **Output**: JSON with `session_id`, `analysis`, and `charts`

### 2. Production Line Chat (`02-production-chat.json`)

Enables follow-up questions about previously analyzed data.

- **Webhook Path**: `/webhook/production-chat`
- **Method**: POST (application/json)
- **Input**: `{"session_id": "...", "message": "..."}`
- **Output**: JSON with `session_id` and `response`

## Automated Import

### Prerequisites

1. **Generate n8n API Key**:
   - Open n8n: http://localhost:5678
   - Click your user icon (top-right) → Settings
   - Navigate to "API" section
   - Click "Create API Key"
   - Copy the generated key

2. **Add to .env**:
   ```bash
   echo "N8N_API_KEY=your-api-key-here" >> .env
   ```

3. **Verify services are running**:
   ```bash
   curl http://localhost:8000/health  # FastAPI
   curl http://localhost:5678/healthz  # n8n
   ```

### Import Workflows

```bash
./scripts/import-n8n-workflows.sh
```

This script will:
- Import both workflow JSON files to n8n
- Activate each workflow
- Display status of all workflows

## Manual Import (Fallback)

If the API import fails, you can import manually:

1. Open n8n: http://localhost:5678
2. Click "Workflows" in the left sidebar
3. Click "Add Workflow" → "Import from File"
4. Select `01-production-analysis.json`
5. Click "Save" then "Activate" (toggle in top-right)
6. Repeat for `02-production-chat.json`

## Testing

### Run End-to-End Tests

```bash
./scripts/test-n8n-workflows.sh
```

### Manual Testing

**Test Analysis Workflow:**
```bash
curl -X POST "http://localhost:5678/webhook/production-analyze" \
  -F "file=@data/sample/predictive_maintenance.csv"
```

**Test Chat Workflow:**
```bash
# Use the session_id from the analysis response
curl -X POST "http://localhost:5678/webhook/production-chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "message": "What is the failure rate?"}'
```

## Response Accuracy Validation

The AI analysis responses have been validated against the actual CSV data:

| Metric | AI Response | Actual Data | Status |
|--------|-------------|-------------|--------|
| Overall failure rate | 2.91% | 2.91% | ✅ Accurate |
| M007 failure rate | 4.65% | 4.65% | ✅ Accurate |
| M015 failure rate | 4.88% | 4.88% | ✅ Accurate |
| M042 failure rate | 4.37% | 4.37% | ✅ Accurate |
| M046 failure rate | 4.44% | 4.44% | ✅ Accurate |
| M049 failure rate | 5.78% | 5.78% | ✅ Accurate |

### Validation Script

To verify AI responses against actual data:

```bash
# Calculate actual failure rate from CSV
awk -F',' 'NR>1 {total++; if($9==1) failures++} END {
    print "Failure rate:", (failures/total)*100, "%"
}' data/sample/predictive_maintenance.csv

# Check per-machine failure rates (machines with >4% failure)
awk -F',' 'NR>1 {
    machine=$2; total[machine]++
    if($9==1) failures[machine]++
} END {
    for(m in total) {
        rate = (failures[m]/total[m])*100
        if(rate > 4) printf "%s: %.2f%%\n", m, rate
    }
}' data/sample/predictive_maintenance.csv | sort -t':' -k2 -rn
```

## Troubleshooting

### Webhook returns 404

- Ensure the workflow is activated (toggle should be ON)
- Check the workflow path matches exactly: `production-analyze` or `production-chat`

### Workflow not connecting to FastAPI

- Verify FastAPI is running: `curl http://localhost:8000/health`
- Check Docker network: n8n must reach FastAPI via `http://production-analyst:8000`
- If running outside Docker, the URL may need to be `http://localhost:8000`

### API import fails

- Verify `N8N_API_KEY` is set correctly in `.env`
- Check n8n is running: `curl http://localhost:5678/healthz`
- Use manual import as fallback (see above)

### Analysis returns error about file

- Ensure you're sending the file as multipart/form-data
- The field name must be `file`
- File must be a valid CSV

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  External       │     │  n8n            │     │  FastAPI        │
│  Client         │────►│  Webhooks       │────►│  Backend        │
│  (curl/browser) │     │  localhost:5678 │     │  :8000          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                        │
                              │ Docker Network         │
                              │ production-analyst:8000│
                              └────────────────────────┘
```
