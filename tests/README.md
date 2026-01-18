# Tests Documentation

## Overview

Unit tests for the Production Line Health Advisor agent. Tests cover data loading, production analysis, and visualization generation modules.

## Running Tests

```bash
# From project root
cd /Users/kylechalmers/Development/n8n-data-analysis-agent

# Install dependencies (if not using Docker)
pip install pytest pandas numpy matplotlib pydantic pydantic-settings

# Run all tests
PYTHONPATH=app pytest tests/ -v

# Run specific test class
PYTHONPATH=app pytest tests/test_analysis.py::TestDataLoader -v

# Run with coverage (requires pytest-cov)
PYTHONPATH=app pytest tests/ -v --cov=app --cov-report=term-missing
```

## Test Results (2026-01-18)

**Status: ALL PASSING (12/12)**

```
tests/test_analysis.py::TestDataLoader::test_load_csv_from_bytes PASSED
tests/test_analysis.py::TestDataLoader::test_validate_production_data_valid PASSED
tests/test_analysis.py::TestDataLoader::test_validate_production_data_invalid PASSED
tests/test_analysis.py::TestDataLoader::test_get_summary_stats PASSED
tests/test_analysis.py::TestDataLoader::test_normalize_columns PASSED
tests/test_analysis.py::TestProduction::test_analyze_failure_rates PASSED
tests/test_analysis.py::TestProduction::test_identify_risk_factors PASSED
tests/test_analysis.py::TestProduction::test_get_high_risk_machines PASSED
tests/test_analysis.py::TestVisualizations::test_create_failure_rate_by_type_chart PASSED
tests/test_analysis.py::TestVisualizations::test_create_risk_factors_chart PASSED
tests/test_analysis.py::TestVisualizations::test_create_machine_comparison_chart PASSED
tests/test_analysis.py::TestVisualizations::test_chart_with_missing_columns PASSED
```

## Test Classes

### TestDataLoader

Tests for `app/analysis/data_loader.py` - CSV parsing and validation.

| Test | Description | Validates |
|------|-------------|-----------|
| `test_load_csv_from_bytes` | Load CSV from byte content | File upload parsing works correctly |
| `test_validate_production_data_valid` | Validate schema with correct columns | Accepts valid production data |
| `test_validate_production_data_invalid` | Validate schema with missing columns | Rejects invalid data gracefully |
| `test_get_summary_stats` | Generate summary statistics | Returns record count, failure rate, column info |
| `test_normalize_columns` | Normalize column names | Handles special characters, spaces, brackets |

### TestProduction

Tests for `app/analysis/production.py` - Production data analysis logic.

| Test | Description | Validates |
|------|-------------|-----------|
| `test_analyze_failure_rates` | Calculate failure rates | Overall rate, by type, by machine |
| `test_identify_risk_factors` | Find correlations with failures | Returns sorted list with correlation strength |
| `test_get_high_risk_machines` | Identify machines above threshold | Returns machines sorted by risk |

### TestVisualizations

Tests for `app/analysis/visualizations.py` - Chart generation.

| Test | Description | Validates |
|------|-------------|-----------|
| `test_create_failure_rate_by_type_chart` | Bar chart by product type | Returns valid base64 PNG |
| `test_create_risk_factors_chart` | Horizontal bar chart of correlations | Returns valid base64 PNG |
| `test_create_machine_comparison_chart` | Top machines comparison | Returns valid base64 PNG |
| `test_chart_with_missing_columns` | Handle missing data gracefully | Returns None instead of crashing |

## Test Fixtures

### `sample_df`

A pytest fixture that generates a 100-record sample DataFrame with:

- `UDI`: Unique identifier (1-100)
- `Product_ID`: Machine IDs (M001-M010)
- `Type`: Product types (L, M, H)
- `Air_temperature_K`: Temperature readings (~300K)
- `Process_temperature_K`: Process temperature (~310K)
- `Rotational_speed_rpm`: RPM values (1200-2000)
- `Torque_Nm`: Torque values (~40 Nm)
- `Tool_wear_min`: Tool wear (0-250 min)
- `Target`: Failure indicator (0/1, ~5% failure rate)
- `Failure_Type`: Failure category

Uses `np.random.seed(42)` for reproducibility.

## Integration Tests

Integration tests are run manually via curl commands after `docker compose up`:

```bash
# Health check (validates Ollama connection)
curl -s http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0","ollama_status":"connected"}

# CSV analysis endpoint
curl -s -X POST http://localhost:8000/webhook/analyze \
  -F "file=@data/sample/predictive_maintenance.csv"
# Expected: JSON with session_id, summary, charts (base64), raw_stats

# Chat endpoint (use session_id from above)
curl -s -X POST http://localhost:8000/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "<SESSION_ID>", "message": "Which machines have highest failure risk?"}'
# Expected: JSON with response and optional charts
```

### Integration Test Results (2026-01-18)

| Endpoint | Status | Response |
|----------|--------|----------|
| `GET /health` | PASS | Ollama connected |
| `POST /webhook/analyze` | PASS | Returns session_id, summary, charts |
| `POST /webhook/chat` | PASS | Maintains context, returns machine-specific insights |
| n8n UI (port 5678) | PASS | HTTP 200, accessible |

## Not Tested (Out of Scope)

- n8n workflow integration (manual UI configuration)
- Load testing / performance benchmarks
- Edge cases: very large files, malformed CSV, concurrent sessions
- Ollama model switching
