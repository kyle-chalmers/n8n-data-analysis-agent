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

# Check API key
if [ -z "$N8N_API_KEY" ]; then
    echo "❌ N8N_API_KEY not set. Please add it to .env file."
    echo "   See: n8n/workflows/README.md for instructions"
    exit 1
fi

N8N_URL="${N8N_URL:-http://localhost:5678}"
WORKFLOWS_DIR="$PROJECT_DIR/n8n/workflows"

echo "=== n8n Workflow Import Script ==="
echo "n8n URL: $N8N_URL"
echo ""

# Function to import a workflow
import_workflow() {
    local file="$1"
    local name=$(basename "$file" .json)
    
    echo "Importing: $name"
    
    # POST the workflow JSON to create it
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "X-N8N-API-KEY: $N8N_API_KEY" \
        -H "Content-Type: application/json" \
        -d @"$file" \
        "$N8N_URL/api/v1/workflows")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        workflow_id=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))")
        echo "  ✅ Created workflow ID: $workflow_id"
        
        # Activate the workflow
        echo "  Activating workflow..."
        activate_response=$(curl -s -X POST \
            -H "X-N8N-API-KEY: $N8N_API_KEY" \
            "$N8N_URL/api/v1/workflows/$workflow_id/activate")
        
        is_active=$(echo "$activate_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('active', False))" 2>/dev/null)
        if [ "$is_active" = "True" ]; then
            echo "  ✅ Workflow activated"
        else
            echo "  ⚠️  Activation response: $activate_response"
        fi
    else
        echo "  ❌ Failed to create workflow (HTTP $http_code)"
        echo "  Response: $body"
        return 1
    fi
}

# Import each workflow
for workflow_file in "$WORKFLOWS_DIR"/*.json; do
    if [ -f "$workflow_file" ]; then
        import_workflow "$workflow_file"
        echo ""
    fi
done

echo "=== Import Complete ==="

# List all workflows
echo ""
echo "Current workflows in n8n:"
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_URL/api/v1/workflows" | python3 -c "
import sys, json
data = json.load(sys.stdin)
workflows = data.get('data', [])
for wf in workflows:
    status = '🟢 Active' if wf.get('active') else '🔴 Inactive'
    print(f\"  {status}: {wf.get('name')} (ID: {wf.get('id')})\")
"
