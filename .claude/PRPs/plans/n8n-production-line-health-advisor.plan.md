# Feature: n8n Production Line Health Advisor Agent

## Summary

Build a local AI-powered data analysis agent integrated with n8n that analyzes manufacturing/production data. Uses **Ollama with Llama 3.1** (free, local) for AI capabilities. The agent accepts CSV uploads via webhook, generates health reports with matplotlib visualizations, and supports conversational follow-up questions with session context. Designed as a workshop demo for ASSA ABLOY.

## User Story

As an AI consultant running workshops at ASSA ABLOY
I want to demonstrate an AI agent that analyzes production line data and answers follow-up questions
So that workshop participants can see what's achievable with AI agents and envision applications in their own domains

## Problem Statement

ASSA ABLOY leadership needs to see tangible, industry-relevant AI demos to drive adoption. Generic demos don't resonate - they need something that speaks directly to their manufacturing optimization goals.

## Solution Statement

A Docker-based solution combining n8n (visual workflow orchestration with chat UI) and a Python FastAPI backend with **Ollama-powered local LLM** agent. The agent uses tool calling to analyze uploaded CSVs, generate charts, and answer questions while maintaining conversation context. **No API keys or costs required.**

## Metadata

| Field            | Value                                                               |
| ---------------- | ------------------------------------------------------------------- |
| Type             | NEW_CAPABILITY                                                      |
| Complexity       | MEDIUM                                                              |
| Systems Affected | Docker, n8n, FastAPI, Ollama, Pandas, Matplotlib                    |
| Dependencies     | ollama>=0.4.0, fastapi>=0.115.0, pandas>=2.0.0, matplotlib>=3.8.0   |
| Estimated Tasks  | 15                                                                  |

---

## Pre-Flight Checklist (HUMAN ACTION REQUIRED)

**CRITICAL: Complete these BEFORE running ralph loop.**

### 1. Install Docker Desktop
```bash
# macOS
brew install --cask docker

# Then open Docker Desktop app and wait for it to start
# Verify:
docker --version
```

### 2. Install Ollama and Pull Model
```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve &

# Pull Llama 3.1 (supports tool calling)
ollama pull llama3.1

# Verify:
ollama list
# Should show: llama3.1:latest
```

### 3. Create Project Directory Structure
```bash
cd /Users/kylechalmers/Development/n8n-data-analysis-agent

# Create all directories
mkdir -p app/agent app/analysis app/models data/sample tests n8n/workflows

# Create all __init__.py files
touch app/__init__.py
touch app/agent/__init__.py
touch app/analysis/__init__.py
touch app/models/__init__.py
```

### 4. Create .env File
```bash
# Create .env from example (no API keys needed for Ollama!)
cat > .env << 'EOF'
OLLAMA_HOST=http://host.docker.internal:11434
DATA_DIR=/data
LOG_LEVEL=INFO
EOF
```

### Pre-Flight Verification
```bash
# Run this to verify all prerequisites:
docker --version && \
ollama list | grep llama3.1 && \
test -d app/agent && \
test -f .env && \
echo "✅ All prerequisites met - ready for ralph loop"
```

---

## UX Design

### Before State

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              BEFORE STATE                                      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   Workshop participant asks: "What can AI agents do for us?"                  ║
║                                                                               ║
║   ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐║
║   │   Consultant    │ ──────► │  Generic Slides │ ──────► │   Skepticism    │║
║   │   Presents      │         │  ChatGPT Demo   │         │   Unclear ROI   │║
║   └─────────────────┘         └─────────────────┘         └─────────────────┘║
║                                                                               ║
║   PAIN_POINT: No industry-specific context, no actionable next steps         ║
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
║   │   n8n Chat UI   │ ──────► │   FastAPI       │ ──────► │  Health Report  │║
║   │   Upload CSV    │         │   + Ollama      │         │  + Charts       │║
║   └─────────────────┘         └─────────────────┘         └─────────────────┘║
║           │                                                       │           ║
║           │ "What's causing M003 issues?"                        │           ║
║           ▼                                                       ▼           ║
║   ┌─────────────────┐                                    ┌─────────────────┐ ║
║   │  Follow-up Q&A  │ ◄────────────────────────────────► │  Drill-down     │ ║
║   │  with context   │                                    │  Analysis       │ ║
║   └─────────────────┘                                    └─────────────────┘ ║
║                                                                               ║
║   VALUE: "I can see exactly how this applies to our production lines"        ║
║   BONUS: Runs 100% locally - no API costs, no data leaves the machine        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Files to Create

| File                              | Action | Purpose                               |
| --------------------------------- | ------ | ------------------------------------- |
| `docker-compose.yml`              | CREATE | n8n + app orchestration               |
| `Dockerfile`                      | CREATE | Python app container                  |
| `.env.example`                    | CREATE | Environment template                  |
| `requirements.txt`                | CREATE | Python dependencies                   |
| `app/__init__.py`                 | CREATE | Package marker (pre-flight)           |
| `app/main.py`                     | CREATE | FastAPI app, routes                   |
| `app/config.py`                   | CREATE | Settings/env vars                     |
| `app/models/__init__.py`          | CREATE | Package marker (pre-flight)           |
| `app/models/schemas.py`           | CREATE | Pydantic request/response models      |
| `app/analysis/__init__.py`        | CREATE | Package marker (pre-flight)           |
| `app/analysis/data_loader.py`     | CREATE | CSV parsing and validation            |
| `app/analysis/production.py`      | CREATE | Production analysis logic             |
| `app/analysis/visualizations.py`  | CREATE | Matplotlib chart generation           |
| `app/agent/__init__.py`           | CREATE | Package marker (pre-flight)           |
| `app/agent/prompts.py`            | CREATE | System prompts                        |
| `app/agent/tools.py`              | CREATE | Tool definitions and execution        |
| `app/agent/core.py`               | CREATE | Agent orchestration with Ollama       |
| `data/sample/predictive_maintenance.csv` | CREATE | Synthetic demo dataset         |
| `tests/test_analysis.py`          | CREATE | Unit tests                            |

---

## NOT Building (Scope Limits)

- **Authentication** - Demo only, no user management
- **Persistent database** - In-memory sessions only
- **Cloud deployment** - Local Docker only
- **n8n workflow JSON export** - Manual UI setup (documented)

---

## Step-by-Step Tasks

Execute in order. Each task is atomic and independently verifiable.

---

### Task 1: CREATE docker-compose.yml

- [x] **COMPLETE**

**ACTION**: Create docker-compose.yml with n8n and app services

**FILE**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_SECURE_COOKIE=false
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - agent-network
    restart: unless-stopped

  app:
    build: .
    container_name: production-analyst
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434
      - DATA_DIR=/data
      - LOG_LEVEL=INFO
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./app:/app
      - ./data:/data
    networks:
      - agent-network
    restart: unless-stopped

volumes:
  n8n_data:

networks:
  agent-network:
    driver: bridge
```

**VALIDATE**:
```bash
docker-compose config > /dev/null && echo "✅ docker-compose.yml valid"
```

---

### Task 2: CREATE Dockerfile

- [x] **COMPLETE**

**ACTION**: Create Dockerfile for Python app

**FILE**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**VALIDATE**:
```bash
test -f Dockerfile && head -1 Dockerfile | grep -q "FROM python" && echo "✅ Dockerfile valid"
```

---

### Task 3: CREATE requirements.txt

- [x] **COMPLETE**

**ACTION**: Create Python dependencies file

**FILE**: `requirements.txt`

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-multipart>=0.0.9
ollama>=0.4.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.8.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pytest>=8.0.0
httpx>=0.27.0
```

**VALIDATE**:
```bash
test -f requirements.txt && grep -q "ollama" requirements.txt && echo "✅ requirements.txt valid"
```

---

### Task 4: CREATE .env.example

- [x] **COMPLETE**

**ACTION**: Create environment template

**FILE**: `.env.example`

```bash
# Ollama Configuration (runs locally - no API key needed!)
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1

# Application Configuration
DATA_DIR=/data
LOG_LEVEL=INFO
```

**VALIDATE**:
```bash
test -f .env.example && grep -q "OLLAMA" .env.example && echo "✅ .env.example valid"
```

---

### Task 5: CREATE app/config.py

- [x] **COMPLETE**

**ACTION**: Create configuration module

**FILE**: `app/config.py`

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Ollama settings
    ollama_host: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.1"

    # Application settings
    data_dir: str = "/data"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
```

**VALIDATE**:
```bash
cd app && python -c "from config import settings; print(f'✅ config.py valid: model={settings.ollama_model}')"
```

---

### Task 6: CREATE app/models/schemas.py

- [x] **COMPLETE**

**ACTION**: Create Pydantic request/response models

**FILE**: `app/models/schemas.py`

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AnalysisResponse(BaseModel):
    """Response from CSV analysis endpoint."""
    session_id: str
    summary: str
    insights: List[str]
    charts: List[str]  # base64 encoded PNG images
    raw_stats: Dict[str, Any]


class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    session_id: str
    response: str
    charts: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Response from health check endpoint."""
    status: str
    version: str = "1.0.0"
    ollama_status: str = "unknown"
```

**VALIDATE**:
```bash
cd app && python -c "from models.schemas import AnalysisResponse, ChatRequest; print('✅ schemas.py valid')"
```

---

### Task 7: CREATE app/analysis/data_loader.py

- [x] **COMPLETE**

**ACTION**: Create CSV loading and validation module

**FILE**: `app/analysis/data_loader.py`

```python
"""Data loading and validation utilities."""
import pandas as pd
from io import StringIO
from typing import Tuple, Dict, Any


def load_csv_from_bytes(content: bytes) -> pd.DataFrame:
    """Load CSV from uploaded file bytes."""
    return pd.read_csv(StringIO(content.decode('utf-8')))


def load_csv_from_path(file_path: str) -> pd.DataFrame:
    """Load CSV from file path."""
    return pd.read_csv(file_path)


def validate_production_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate DataFrame has expected production data columns.
    Flexible - works with various column naming conventions.
    """
    required_patterns = ['target', 'failure', 'product', 'type']
    df_cols_lower = [c.lower() for c in df.columns]

    found = sum(1 for p in required_patterns if any(p in c for c in df_cols_lower))

    if found >= 2:
        return True, "Schema valid"
    return False, f"Expected production data columns. Found: {list(df.columns)}"


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names for consistent processing."""
    df = df.copy()
    # Replace spaces and special chars with underscores
    df.columns = df.columns.str.replace(r'[\[\]\(\) ]', '_', regex=True)
    df.columns = df.columns.str.replace(r'_+', '_', regex=True)
    df.columns = df.columns.str.strip('_')
    return df


def get_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Get basic summary statistics."""
    df = normalize_columns(df)

    stats = {
        "total_records": len(df),
        "columns": list(df.columns),
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
    }

    # Try to find failure/target column
    target_col = None
    for col in df.columns:
        if 'target' in col.lower() or 'failure' in col.lower():
            target_col = col
            break

    if target_col and df[target_col].dtype in ['int64', 'float64', 'bool']:
        stats["failure_rate"] = float(df[target_col].mean())
        stats["total_failures"] = int(df[target_col].sum())

    # Try to find machine/product column
    for col in df.columns:
        if 'product' in col.lower() or 'machine' in col.lower():
            stats["unique_machines"] = int(df[col].nunique())
            break

    return stats
```

**VALIDATE**:
```bash
cd app && python -c "
from analysis.data_loader import load_csv_from_bytes, get_summary_stats
import pandas as pd
df = pd.DataFrame({'Product_ID': ['M1', 'M2'], 'Target': [0, 1]})
stats = get_summary_stats(df)
assert stats['total_records'] == 2
print('✅ data_loader.py valid')
"
```

---

### Task 8: CREATE app/analysis/production.py

- [x] **COMPLETE**

**ACTION**: Create production data analysis module

**FILE**: `app/analysis/production.py`

```python
"""Production data analysis functions."""
import pandas as pd
from typing import Dict, List, Any
from analysis.data_loader import normalize_columns


def _find_column(df: pd.DataFrame, patterns: List[str]) -> str | None:
    """Find column matching any of the patterns."""
    for col in df.columns:
        col_lower = col.lower()
        if any(p in col_lower for p in patterns):
            return col
    return None


def analyze_failure_rates(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze failure rates overall and by machine/type."""
    df = normalize_columns(df)

    target_col = _find_column(df, ['target', 'failure'])
    product_col = _find_column(df, ['product', 'machine'])
    type_col = _find_column(df, ['type', 'category'])

    result = {
        "total_records": len(df),
        "analysis_available": False
    }

    if not target_col:
        result["error"] = "No target/failure column found"
        return result

    result["analysis_available"] = True
    result["overall_failure_rate"] = float(df[target_col].mean())
    result["total_failures"] = int(df[target_col].sum())

    if type_col:
        result["by_product_type"] = df.groupby(type_col)[target_col].mean().to_dict()

    if product_col:
        machine_rates = df.groupby(product_col)[target_col].agg(['mean', 'count', 'sum'])
        machine_rates.columns = ['failure_rate', 'sample_count', 'failures']
        # Get high risk machines (above average)
        avg_rate = result["overall_failure_rate"]
        high_risk = machine_rates[machine_rates['failure_rate'] > avg_rate * 1.5]
        result["high_risk_machines"] = high_risk.head(10).to_dict('index')
        result["total_machines"] = len(machine_rates)

    return result


def identify_risk_factors(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Identify correlations between numeric features and failures."""
    df = normalize_columns(df)

    target_col = _find_column(df, ['target', 'failure'])
    if not target_col:
        return [{"error": "No target column found"}]

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)

    correlations = []
    for col in numeric_cols:
        try:
            corr = df[col].corr(df[target_col])
            if pd.notna(corr):
                correlations.append({
                    "factor": col,
                    "correlation": round(float(corr), 4),
                    "strength": "strong" if abs(corr) > 0.3 else "moderate" if abs(corr) > 0.1 else "weak",
                    "direction": "positive" if corr > 0 else "negative"
                })
        except Exception:
            continue

    return sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)


def get_high_risk_machines(df: pd.DataFrame, threshold: float = 0.05) -> List[Dict[str, Any]]:
    """Get machines with failure rate above threshold."""
    df = normalize_columns(df)

    target_col = _find_column(df, ['target', 'failure'])
    product_col = _find_column(df, ['product', 'machine'])

    if not target_col or not product_col:
        return []

    machine_stats = df.groupby(product_col).agg({
        target_col: ['mean', 'sum', 'count']
    }).reset_index()
    machine_stats.columns = ['machine_id', 'failure_rate', 'total_failures', 'sample_count']

    high_risk = machine_stats[machine_stats['failure_rate'] > threshold]
    high_risk = high_risk.sort_values('failure_rate', ascending=False)

    return high_risk.head(10).to_dict('records')


def analyze_failure_types(df: pd.DataFrame) -> Dict[str, int]:
    """Analyze distribution of failure types."""
    df = normalize_columns(df)

    failure_type_col = _find_column(df, ['failure_type', 'failure_mode', 'defect'])
    if not failure_type_col:
        return {"error": "No failure type column found"}

    return df[failure_type_col].value_counts().to_dict()
```

**VALIDATE**:
```bash
cd app && python -c "
from analysis.production import analyze_failure_rates, identify_risk_factors
import pandas as pd
import numpy as np
np.random.seed(42)
df = pd.DataFrame({
    'Product_ID': ['M1']*50 + ['M2']*50,
    'Type': ['A']*50 + ['B']*50,
    'Temperature': np.random.normal(100, 10, 100),
    'Target': [0]*90 + [1]*10
})
result = analyze_failure_rates(df)
assert result['analysis_available'] == True
assert result['overall_failure_rate'] == 0.1
print('✅ production.py valid')
"
```

---

### Task 9: CREATE app/analysis/visualizations.py

- [x] **COMPLETE**

**ACTION**: Create matplotlib chart generation module

**FILE**: `app/analysis/visualizations.py`

```python
"""Visualization generation functions."""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server

import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from typing import List, Dict, Any

from analysis.data_loader import normalize_columns


def _fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"


def _find_column(df: pd.DataFrame, patterns: List[str]) -> str | None:
    """Find column matching any of the patterns."""
    for col in df.columns:
        col_lower = col.lower()
        if any(p in col_lower for p in patterns):
            return col
    return None


def create_failure_rate_by_type_chart(df: pd.DataFrame) -> str | None:
    """Create bar chart of failure rates by product type."""
    df = normalize_columns(df)

    target_col = _find_column(df, ['target', 'failure'])
    type_col = _find_column(df, ['type', 'category'])

    if not target_col or not type_col:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    rates = df.groupby(type_col)[target_col].mean() * 100
    colors = ['#2ecc71' if r < 3 else '#f39c12' if r < 5 else '#e74c3c' for r in rates]

    bars = ax.bar(rates.index, rates.values, color=colors, edgecolor='black')
    ax.set_ylabel('Failure Rate (%)', fontsize=12)
    ax.set_xlabel('Product Type', fontsize=12)
    ax.set_title('Failure Rate by Product Type', fontsize=14, fontweight='bold')

    # Add value labels
    for bar, val in zip(bars, rates.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f'{val:.1f}%', ha='center', fontweight='bold')

    ax.set_ylim(0, max(rates.values) * 1.2)

    return _fig_to_base64(fig)


def create_risk_factors_chart(risk_factors: List[Dict[str, Any]]) -> str | None:
    """Create horizontal bar chart of risk factor correlations."""
    if not risk_factors or 'error' in risk_factors[0]:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    # Take top 8 factors
    factors = [f['factor'].replace('_', ' ')[:20] for f in risk_factors[:8]]
    correlations = [f['correlation'] for f in risk_factors[:8]]
    colors = ['#e74c3c' if c > 0 else '#3498db' for c in correlations]

    ax.barh(factors, correlations, color=colors, edgecolor='black')
    ax.set_xlabel('Correlation with Failure', fontsize=12)
    ax.set_title('Risk Factors: Correlation with Machine Failure', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='black', linewidth=0.5)

    # Add value labels
    for i, (factor, corr) in enumerate(zip(factors, correlations)):
        ax.text(corr + 0.01 if corr >= 0 else corr - 0.01,
                i, f'{corr:.3f}',
                va='center', ha='left' if corr >= 0 else 'right',
                fontsize=10)

    plt.tight_layout()
    return _fig_to_base64(fig)


def create_failure_distribution_chart(df: pd.DataFrame) -> str | None:
    """Create pie chart of failure type distribution."""
    df = normalize_columns(df)

    failure_type_col = _find_column(df, ['failure_type', 'failure_mode', 'defect'])
    target_col = _find_column(df, ['target', 'failure'])

    if not failure_type_col:
        return None

    # Filter to only failures if we have a target column
    if target_col:
        failure_df = df[df[target_col] == 1]
    else:
        failure_df = df

    if len(failure_df) == 0:
        return None

    fig, ax = plt.subplots(figsize=(10, 8))

    failure_counts = failure_df[failure_type_col].value_counts()
    colors = plt.cm.Set3(range(len(failure_counts)))

    wedges, texts, autotexts = ax.pie(
        failure_counts.values,
        labels=failure_counts.index,
        autopct='%1.1f%%',
        colors=colors,
        explode=[0.03] * len(failure_counts),
        shadow=True
    )
    ax.set_title('Distribution of Failure Types', fontsize=14, fontweight='bold')

    return _fig_to_base64(fig)


def create_machine_comparison_chart(df: pd.DataFrame, top_n: int = 10) -> str | None:
    """Create bar chart comparing top machines by failure rate."""
    df = normalize_columns(df)

    target_col = _find_column(df, ['target', 'failure'])
    product_col = _find_column(df, ['product', 'machine'])

    if not target_col or not product_col:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))

    machine_rates = df.groupby(product_col)[target_col].mean().nlargest(top_n) * 100
    overall_avg = df[target_col].mean() * 100

    colors = ['#e74c3c' if r > overall_avg * 1.5 else '#f39c12' if r > overall_avg else '#2ecc71'
              for r in machine_rates]

    bars = ax.bar(range(len(machine_rates)), machine_rates.values, color=colors, edgecolor='black')
    ax.set_xticks(range(len(machine_rates)))
    ax.set_xticklabels(machine_rates.index, rotation=45, ha='right')
    ax.set_ylabel('Failure Rate (%)', fontsize=12)
    ax.set_xlabel('Machine ID', fontsize=12)
    ax.set_title(f'Top {top_n} Machines by Failure Rate', fontsize=14, fontweight='bold')
    ax.axhline(y=overall_avg, color='red', linestyle='--', linewidth=2, label=f'Overall Avg: {overall_avg:.1f}%')
    ax.legend()

    plt.tight_layout()
    return _fig_to_base64(fig)
```

**VALIDATE**:
```bash
cd app && python -c "
from analysis.visualizations import create_failure_rate_by_type_chart
import pandas as pd
import numpy as np
np.random.seed(42)
df = pd.DataFrame({
    'Type': ['A']*50 + ['B']*50,
    'Target': [0]*45 + [1]*5 + [0]*40 + [1]*10
})
img = create_failure_rate_by_type_chart(df)
assert img is not None
assert img.startswith('data:image/png;base64,')
print('✅ visualizations.py valid')
"
```

---

### Task 10: CREATE app/agent/prompts.py

- [x] **COMPLETE**

**ACTION**: Create system prompts for the agent

**FILE**: `app/agent/prompts.py`

```python
"""System prompts for the Production Line Health Advisor agent."""

SYSTEM_PROMPT = """You are a Production Line Health Advisor AI agent specialized in analyzing manufacturing data to identify failure risks, quality issues, and optimization opportunities.

CONTEXT: You're helping ASSA ABLOY (global leader in access solutions) analyze their production line data. They have a Manufacturing Footprint Program targeting significant cost savings through optimization.

COMMUNICATION STYLE:
- Be direct and concise - manufacturing teams value efficiency
- Lead with the most critical findings
- Quantify everything with specific numbers from the data
- Provide actionable recommendations, not just observations

WHEN ANALYZING DATA:
1. Start with overall health metrics (failure rate, high-risk machines)
2. Identify the most significant risk factors
3. Highlight machines requiring immediate attention
4. Suggest specific preventive actions

WHEN ANSWERING FOLLOW-UP QUESTIONS:
- Reference the data you've already analyzed
- If asked about something not in the data, say so clearly
- Offer to generate relevant visualizations when helpful

You have access to these tools:
- analyze_data: Run statistical analysis (failure_rates, risk_factors, machine_comparison, failure_types)
- create_chart: Generate visualizations (failure_by_type, risk_factors, failure_distribution, machine_comparison)

Always be specific and reference actual values from the data. Never make up numbers."""

INITIAL_ANALYSIS_PROMPT = """Analyze this production dataset and provide a comprehensive health report.

Start by running a full analysis using the analyze_data tool with analysis_type="all", then create the most relevant charts.

Structure your response as:
1. **Executive Summary** (2-3 sentences on overall health)
2. **Key Metrics** (failure rate, records analyzed, machines monitored)
3. **Critical Findings** (top 3 issues requiring attention)
4. **Recommendations** (specific actions to reduce failures)

Include at least 2 charts that support your findings."""
```

**VALIDATE**:
```bash
cd app && python -c "from agent.prompts import SYSTEM_PROMPT, INITIAL_ANALYSIS_PROMPT; print('✅ prompts.py valid')"
```

---

### Task 11: CREATE app/agent/tools.py

- [x] **COMPLETE**

**ACTION**: Create tool definitions and execution logic

**FILE**: `app/agent/tools.py`

```python
"""Tool definitions and execution for the Production Analyst agent."""
from typing import Any, Dict
import pandas as pd
import json

from analysis.production import (
    analyze_failure_rates,
    identify_risk_factors,
    get_high_risk_machines,
    analyze_failure_types
)
from analysis.visualizations import (
    create_failure_rate_by_type_chart,
    create_risk_factors_chart,
    create_failure_distribution_chart,
    create_machine_comparison_chart
)


# Tool definitions for Ollama function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": "Run statistical analysis on the production dataset. Use this to get failure rates, identify risk factors, find high-risk machines, or analyze failure types.",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["failure_rates", "risk_factors", "high_risk_machines", "failure_types", "all"],
                        "description": "Type of analysis to run. Use 'all' for comprehensive analysis."
                    }
                },
                "required": ["analysis_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": "Generate a visualization chart. Use this to create visual representations of the data analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": ["failure_by_type", "risk_factors", "failure_distribution", "machine_comparison"],
                        "description": "Type of chart to generate"
                    }
                },
                "required": ["chart_type"]
            }
        }
    }
]


def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    df: pd.DataFrame,
    analysis_cache: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a tool and return the result.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        df: The DataFrame to analyze
        analysis_cache: Cache for storing analysis results

    Returns:
        Dict with 'type' and either 'data', 'image', or 'error'
    """
    try:
        if tool_name == "analyze_data":
            analysis_type = tool_args.get("analysis_type", "all")

            if analysis_type == "all":
                result = {
                    "failure_rates": analyze_failure_rates(df),
                    "risk_factors": identify_risk_factors(df),
                    "high_risk_machines": get_high_risk_machines(df),
                    "failure_types": analyze_failure_types(df)
                }
                # Cache all results
                analysis_cache.update(result)
            elif analysis_type == "failure_rates":
                result = analyze_failure_rates(df)
                analysis_cache["failure_rates"] = result
            elif analysis_type == "risk_factors":
                result = identify_risk_factors(df)
                analysis_cache["risk_factors"] = result
            elif analysis_type == "high_risk_machines":
                result = get_high_risk_machines(df)
                analysis_cache["high_risk_machines"] = result
            elif analysis_type == "failure_types":
                result = analyze_failure_types(df)
                analysis_cache["failure_types"] = result
            else:
                return {"type": "error", "message": f"Unknown analysis type: {analysis_type}"}

            return {"type": "analysis", "data": result}

        elif tool_name == "create_chart":
            chart_type = tool_args.get("chart_type")
            chart = None

            if chart_type == "failure_by_type":
                chart = create_failure_rate_by_type_chart(df)
            elif chart_type == "risk_factors":
                # Use cached risk factors if available
                risk_factors = analysis_cache.get("risk_factors") or identify_risk_factors(df)
                chart = create_risk_factors_chart(risk_factors)
            elif chart_type == "failure_distribution":
                chart = create_failure_distribution_chart(df)
            elif chart_type == "machine_comparison":
                chart = create_machine_comparison_chart(df)
            else:
                return {"type": "error", "message": f"Unknown chart type: {chart_type}"}

            if chart is None:
                return {"type": "error", "message": f"Could not generate {chart_type} chart - required columns not found"}

            return {"type": "chart", "image": chart, "chart_type": chart_type}

        else:
            return {"type": "error", "message": f"Unknown tool: {tool_name}"}

    except Exception as e:
        return {"type": "error", "message": f"Tool execution error: {str(e)}"}
```

**VALIDATE**:
```bash
cd app && python -c "
from agent.tools import TOOLS, execute_tool
import pandas as pd
import numpy as np
np.random.seed(42)
df = pd.DataFrame({
    'Product_ID': ['M1']*50 + ['M2']*50,
    'Type': ['A']*50 + ['B']*50,
    'Target': [0]*90 + [1]*10
})
cache = {}
result = execute_tool('analyze_data', {'analysis_type': 'failure_rates'}, df, cache)
assert result['type'] == 'analysis'
assert 'failure_rates' in cache
print('✅ tools.py valid')
"
```

---

### Task 12: CREATE app/agent/core.py

- [x] **COMPLETE**

**ACTION**: Create agent orchestration with Ollama

**FILE**: `app/agent/core.py`

```python
"""Agent core orchestration using Ollama."""
import ollama
from typing import Dict, List, Any, Optional
import pandas as pd
import json
import logging

from config import settings
from agent.tools import TOOLS, execute_tool
from agent.prompts import SYSTEM_PROMPT, INITIAL_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class ProductionAnalystAgent:
    """AI agent for analyzing production line data using Ollama."""

    def __init__(self):
        self.model = settings.ollama_model
        self.sessions: Dict[str, Dict] = {}
        self._client = None

    @property
    def client(self):
        """Lazy initialization of Ollama client."""
        if self._client is None:
            self._client = ollama.Client(host=settings.ollama_host)
        return self._client

    def check_ollama_connection(self) -> bool:
        """Check if Ollama is reachable."""
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return False

    def get_or_create_session(self, session_id: str) -> Dict:
        """Get existing session or create new one."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "df": None,
                "messages": [],
                "analysis_cache": {},
                "charts": []
            }
        return self.sessions[session_id]

    def load_data(self, session_id: str, df: pd.DataFrame) -> None:
        """Load DataFrame into session."""
        session = self.get_or_create_session(session_id)
        session["df"] = df
        session["analysis_cache"] = {}
        session["charts"] = []
        session["messages"] = []  # Reset conversation for new data

    def run_initial_analysis(self, session_id: str) -> Dict[str, Any]:
        """Run initial analysis when data is first uploaded."""
        session = self.get_or_create_session(session_id)

        if session["df"] is None:
            return {"error": "No data loaded for this session"}

        # Add data context to the prompt
        df = session["df"]
        data_context = f"""
The uploaded dataset contains:
- {len(df)} records
- Columns: {', '.join(df.columns.tolist())}
- Numeric columns: {', '.join(df.select_dtypes(include=['number']).columns.tolist())}
"""

        session["messages"] = [
            {"role": "user", "content": data_context + "\n\n" + INITIAL_ANALYSIS_PROMPT}
        ]

        return self._run_agent_loop(session_id)

    def chat(self, session_id: str, message: str) -> Dict[str, Any]:
        """Process a follow-up chat message."""
        session = self.get_or_create_session(session_id)

        if session["df"] is None:
            return {"error": "No data loaded. Please upload a CSV file first."}

        session["messages"].append({"role": "user", "content": message})

        return self._run_agent_loop(session_id)

    def _run_agent_loop(self, session_id: str, max_iterations: int = 10) -> Dict[str, Any]:
        """Run the agent loop until completion or max iterations."""
        session = self.sessions[session_id]
        charts_generated = []
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            try:
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *session["messages"]
                    ],
                    tools=TOOLS,
                    options={"temperature": 0.7}
                )
            except Exception as e:
                logger.error(f"Ollama API error: {e}")
                return {"error": f"LLM API error: {str(e)}"}

            message = response.get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            # Add assistant response to history
            session["messages"].append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls if tool_calls else None
            })

            # If no tool calls, we're done
            if not tool_calls:
                break

            # Process tool calls
            for tool_call in tool_calls:
                func = tool_call.get("function", {})
                tool_name = func.get("name")
                tool_args = func.get("arguments", {})

                # Handle string arguments (some models return JSON string)
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError:
                        tool_args = {}

                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                # Execute the tool
                result = execute_tool(
                    tool_name,
                    tool_args,
                    session["df"],
                    session["analysis_cache"]
                )

                # Track charts
                if result.get("type") == "chart" and result.get("image"):
                    charts_generated.append(result["image"])

                # Add tool result to messages
                session["messages"].append({
                    "role": "tool",
                    "content": json.dumps(result, default=str)
                })

        # Store charts in session
        session["charts"].extend(charts_generated)

        # Get final text response
        final_response = ""
        for msg in reversed(session["messages"]):
            if msg["role"] == "assistant" and msg.get("content"):
                final_response = msg["content"]
                break

        return {
            "response": final_response,
            "charts": charts_generated,
            "session_id": session_id
        }


# Global agent instance
agent = ProductionAnalystAgent()
```

**VALIDATE**:
```bash
cd app && python -c "
from agent.core import agent
print(f'Agent model: {agent.model}')
print('✅ core.py valid (agent created)')
"
```

---

### Task 13: CREATE app/main.py

- [x] **COMPLETE**

**ACTION**: Create FastAPI application with all endpoints

**FILE**: `app/main.py`

```python
"""FastAPI application for Production Line Health Advisor."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging

from models.schemas import AnalysisResponse, ChatRequest, ChatResponse, HealthResponse
from analysis.data_loader import load_csv_from_bytes, validate_production_data, get_summary_stats
from agent.core import agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Production Line Health Advisor",
    description="AI-powered analysis agent for manufacturing data. Uses Ollama (local LLM) - no API keys needed!",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    ollama_ok = agent.check_ollama_connection()
    return HealthResponse(
        status="healthy",
        ollama_status="connected" if ollama_ok else "disconnected"
    )


@app.post("/webhook/analyze", response_model=AnalysisResponse)
async def analyze_csv(file: UploadFile = File(...)):
    """
    Analyze an uploaded CSV file.

    Upload a production/manufacturing CSV and get an AI-powered health report
    with visualizations and actionable insights.
    """
    logger.info(f"Received file: {file.filename}")

    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")

    try:
        # Read and parse CSV
        contents = await file.read()
        df = load_csv_from_bytes(contents)
        logger.info(f"Loaded CSV with {len(df)} rows, {len(df.columns)} columns")

        # Validate schema (warning only)
        valid, message = validate_production_data(df)
        if not valid:
            logger.warning(f"Schema validation warning: {message}")

        # Create session and load data
        session_id = str(uuid.uuid4())
        agent.load_data(session_id, df)
        logger.info(f"Created session: {session_id}")

        # Run initial analysis
        result = agent.run_initial_analysis(session_id)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        # Get summary stats
        stats = get_summary_stats(df)

        return AnalysisResponse(
            session_id=session_id,
            summary=result.get("response", "Analysis complete"),
            insights=[],  # Could parse from response if needed
            charts=result.get("charts", []),
            raw_stats=stats
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/webhook/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the agent about previously uploaded data.

    Ask follow-up questions about your production data. The agent remembers
    the context from your uploaded CSV.
    """
    logger.info(f"Chat request for session: {request.session_id}")

    try:
        result = agent.chat(request.session_id, request.message)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return ChatResponse(
            session_id=request.session_id,
            response=result.get("response", ""),
            charts=result.get("charts")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**VALIDATE**:
```bash
cd app && python -c "
from main import app
print(f'App title: {app.title}')
print(f'Routes: {[r.path for r in app.routes]}')
print('✅ main.py valid')
"
```

---

### Task 14: CREATE data/sample/predictive_maintenance.csv

- [x] **COMPLETE**

**ACTION**: Generate synthetic production dataset

**FILE**: `data/sample/predictive_maintenance.csv`

```python
# Run this Python script to generate the dataset
import pandas as pd
import numpy as np

np.random.seed(42)
n = 10000

# Generate realistic production data
df = pd.DataFrame({
    'UDI': range(1, n + 1),
    'Product_ID': [f'M{i:03d}' for i in np.random.randint(1, 51, n)],
    'Type': np.random.choice(['L', 'M', 'H'], n, p=[0.5, 0.3, 0.2]),
    'Air_temperature_K': np.round(np.random.normal(300, 2, n), 1),
    'Process_temperature_K': np.round(np.random.normal(310, 2, n), 1),
    'Rotational_speed_rpm': np.random.randint(1200, 2000, n),
    'Torque_Nm': np.round(np.random.normal(40, 10, n), 1),
    'Tool_wear_min': np.random.randint(0, 250, n),
})

# Generate correlated failures (higher temp, torque, wear = more failures)
failure_prob = (
    0.01 +  # base rate
    0.02 * (df['Process_temperature_K'] > 312) +
    0.02 * (df['Torque_Nm'] > 50) +
    0.03 * (df['Tool_wear_min'] > 200) +
    0.01 * (df['Type'] == 'L')  # Low quality type has more failures
)
df['Target'] = (np.random.random(n) < failure_prob).astype(int)

# Generate failure types for failed items
failure_types = ['No Failure', 'Heat Dissipation Failure', 'Power Failure',
                 'Overstrain Failure', 'Tool Wear Failure']
df['Failure_Type'] = 'No Failure'
failures_mask = df['Target'] == 1
n_failures = failures_mask.sum()
df.loc[failures_mask, 'Failure_Type'] = np.random.choice(
    failure_types[1:], n_failures, p=[0.3, 0.2, 0.25, 0.25]
)

# Save to CSV
df.to_csv('/Users/kylechalmers/Development/n8n-data-analysis-agent/data/sample/predictive_maintenance.csv', index=False)
print(f"Generated {n} records with {df['Target'].sum()} failures ({df['Target'].mean()*100:.1f}% failure rate)")
```

**VALIDATE**:
```bash
test -f data/sample/predictive_maintenance.csv && \
head -1 data/sample/predictive_maintenance.csv | grep -q "Product_ID" && \
wc -l data/sample/predictive_maintenance.csv | grep -q "10001" && \
echo "✅ predictive_maintenance.csv valid (10000 records + header)"
```

---

### Task 15: CREATE tests/test_analysis.py

- [x] **COMPLETE**

**ACTION**: Create unit tests

**FILE**: `tests/test_analysis.py`

```python
"""Unit tests for analysis modules."""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

from analysis.data_loader import (
    load_csv_from_bytes,
    validate_production_data,
    get_summary_stats,
    normalize_columns
)
from analysis.production import (
    analyze_failure_rates,
    identify_risk_factors,
    get_high_risk_machines
)
from analysis.visualizations import (
    create_failure_rate_by_type_chart,
    create_risk_factors_chart,
    create_machine_comparison_chart
)


@pytest.fixture
def sample_df():
    """Create sample production DataFrame for testing."""
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        'UDI': range(1, n + 1),
        'Product_ID': [f'M{i:03d}' for i in np.random.randint(1, 11, n)],
        'Type': np.random.choice(['L', 'M', 'H'], n, p=[0.5, 0.3, 0.2]),
        'Air_temperature_K': np.random.normal(300, 2, n),
        'Process_temperature_K': np.random.normal(310, 2, n),
        'Rotational_speed_rpm': np.random.randint(1200, 2000, n),
        'Torque_Nm': np.random.normal(40, 10, n),
        'Tool_wear_min': np.random.randint(0, 250, n),
        'Target': np.random.choice([0, 1], n, p=[0.95, 0.05]),
        'Failure_Type': np.random.choice(
            ['No Failure', 'Heat Dissipation', 'Tool Wear'], n, p=[0.9, 0.05, 0.05]
        )
    })


class TestDataLoader:
    """Tests for data_loader module."""

    def test_load_csv_from_bytes(self, sample_df):
        """Test loading CSV from bytes."""
        csv_bytes = sample_df.to_csv(index=False).encode('utf-8')
        loaded_df = load_csv_from_bytes(csv_bytes)
        assert len(loaded_df) == len(sample_df)
        assert list(loaded_df.columns) == list(sample_df.columns)

    def test_validate_production_data_valid(self, sample_df):
        """Test validation with valid production data."""
        valid, message = validate_production_data(sample_df)
        assert valid is True

    def test_validate_production_data_invalid(self):
        """Test validation with invalid data."""
        invalid_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        valid, message = validate_production_data(invalid_df)
        assert valid is False

    def test_get_summary_stats(self, sample_df):
        """Test summary statistics generation."""
        stats = get_summary_stats(sample_df)
        assert stats['total_records'] == 100
        assert 'failure_rate' in stats
        assert 0 <= stats['failure_rate'] <= 1

    def test_normalize_columns(self):
        """Test column normalization."""
        df = pd.DataFrame({'Air temperature [K]': [1, 2], 'Process (temp)': [3, 4]})
        normalized = normalize_columns(df)
        assert 'Air_temperature_K' in normalized.columns
        assert 'Process_temp' in normalized.columns


class TestProduction:
    """Tests for production analysis module."""

    def test_analyze_failure_rates(self, sample_df):
        """Test failure rate analysis."""
        result = analyze_failure_rates(sample_df)
        assert result['analysis_available'] is True
        assert 'overall_failure_rate' in result
        assert 0 <= result['overall_failure_rate'] <= 1
        assert result['total_records'] == 100

    def test_identify_risk_factors(self, sample_df):
        """Test risk factor identification."""
        factors = identify_risk_factors(sample_df)
        assert isinstance(factors, list)
        assert len(factors) > 0
        assert 'factor' in factors[0]
        assert 'correlation' in factors[0]
        assert 'strength' in factors[0]

    def test_get_high_risk_machines(self, sample_df):
        """Test high risk machine identification."""
        machines = get_high_risk_machines(sample_df, threshold=0.0)
        assert isinstance(machines, list)
        # With threshold=0, should return machines with any failures


class TestVisualizations:
    """Tests for visualization module."""

    def test_create_failure_rate_by_type_chart(self, sample_df):
        """Test failure rate chart generation."""
        chart = create_failure_rate_by_type_chart(sample_df)
        assert chart is not None
        assert chart.startswith('data:image/png;base64,')
        assert len(chart) > 1000  # Should have substantial content

    def test_create_risk_factors_chart(self, sample_df):
        """Test risk factors chart generation."""
        factors = identify_risk_factors(sample_df)
        chart = create_risk_factors_chart(factors)
        assert chart is not None
        assert chart.startswith('data:image/png;base64,')

    def test_create_machine_comparison_chart(self, sample_df):
        """Test machine comparison chart generation."""
        chart = create_machine_comparison_chart(sample_df)
        assert chart is not None
        assert chart.startswith('data:image/png;base64,')

    def test_chart_with_missing_columns(self):
        """Test chart generation with missing columns returns None."""
        incomplete_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        chart = create_failure_rate_by_type_chart(incomplete_df)
        assert chart is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

**VALIDATE**:
```bash
cd /Users/kylechalmers/Development/n8n-data-analysis-agent && \
pip install pytest pandas numpy matplotlib -q && \
PYTHONPATH=app pytest tests/test_analysis.py -v --tb=short
```

---

## Post-Task: n8n Workflow Setup (HUMAN ACTION)

After all code tasks complete, manually set up n8n workflow:

1. **Open n8n**: http://localhost:5678
2. **Create new workflow**
3. **Add Webhook node**:
   - HTTP Method: POST
   - Path: `analyze`
4. **Add HTTP Request node**:
   - Method: POST
   - URL: `http://app:8000/webhook/analyze`
   - Send Body: Form-Data
   - Specify Body: Form Fields
   - Field Name: `file`, Type: Binary
5. **Add Respond to Webhook node**
6. **Connect**: Webhook → HTTP Request → Respond
7. **Activate workflow**
8. **Test with**: `curl -X POST http://localhost:5678/webhook/analyze -F "file=@data/sample/predictive_maintenance.csv"`

---

## Validation Commands

### Level 1: Static Validation (No Docker needed)

```bash
cd /Users/kylechalmers/Development/n8n-data-analysis-agent

# Check all files exist
for f in docker-compose.yml Dockerfile requirements.txt .env.example \
         app/config.py app/main.py app/models/schemas.py \
         app/analysis/data_loader.py app/analysis/production.py app/analysis/visualizations.py \
         app/agent/prompts.py app/agent/tools.py app/agent/core.py \
         data/sample/predictive_maintenance.csv tests/test_analysis.py; do
    test -f "$f" && echo "✅ $f" || echo "❌ $f missing"
done

# Python syntax check
python -m py_compile app/main.py app/config.py app/agent/core.py
echo "✅ Python syntax valid"
```

### Level 2: Unit Tests (No Docker needed)

```bash
cd /Users/kylechalmers/Development/n8n-data-analysis-agent
pip install -q pytest pandas numpy matplotlib pydantic pydantic-settings
PYTHONPATH=app pytest tests/ -v
```

### Level 3: Docker Build

```bash
cd /Users/kylechalmers/Development/n8n-data-analysis-agent
docker-compose build --no-cache
echo "✅ Docker build successful"
```

### Level 4: Integration Test

```bash
# Start services
docker-compose up -d

# Wait for startup
sleep 15

# Test health (should show ollama connected)
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✅ Health check passed"

# Test CSV analysis
curl -s -X POST http://localhost:8000/webhook/analyze \
  -F "file=@data/sample/predictive_maintenance.csv" | \
  grep -q "session_id" && echo "✅ Analysis endpoint working"

# Test n8n is running
curl -s http://localhost:5678/healthz | grep -q "ok" && echo "✅ n8n running"

docker-compose logs --tail=20
```

---

## Acceptance Criteria

- [ ] All 15 tasks marked complete with checkboxes
- [ ] `docker-compose build` succeeds without errors
- [ ] `docker-compose up` starts both n8n and FastAPI
- [ ] `/health` endpoint shows `ollama_status: connected`
- [ ] CSV upload to `/webhook/analyze` returns analysis with charts
- [ ] Unit tests pass: `pytest tests/ -v`
- [ ] No API keys required - runs 100% locally

---

## Completion Checklist

- [ ] Pre-flight: Docker installed and running
- [ ] Pre-flight: Ollama installed with llama3.1 model
- [ ] Pre-flight: Directory structure created with `__init__.py` files
- [ ] Pre-flight: `.env` file created
- [ ] All 15 tasks completed in order
- [ ] Level 1: Static validation passes
- [ ] Level 2: Unit tests pass
- [ ] Level 3: Docker build succeeds
- [ ] Level 4: Integration tests pass
- [ ] Post-task: n8n workflow configured (manual)

---

## Risks and Mitigations

| Risk                     | Likelihood | Impact | Mitigation                                        |
| ------------------------ | ---------- | ------ | ------------------------------------------------- |
| Ollama not running       | Medium     | High   | Pre-flight check, clear error message             |
| Docker networking issues | Medium     | Medium | Use `host.docker.internal`, explicit network      |
| Model not pulled         | Low        | High   | Pre-flight: `ollama pull llama3.1`                |
| Tool calling issues      | Medium     | Medium | Fallback to non-tool response, retry logic        |

---

## Notes

**Why Ollama over paid APIs:**
- Zero cost - important for workshop demos you run repeatedly
- No API keys to manage or expose
- Data stays local - important for ASSA ABLOY data sensitivity
- Llama 3.1 has good tool calling support

**Performance expectations:**
- First response: 10-30 seconds (model loading)
- Subsequent responses: 5-15 seconds
- Chart generation: 1-2 seconds

**Future enhancements:**
- Add streaming responses for better UX
- Add session persistence with Redis
- Add more analysis scenarios (Sales, Supply Chain)
