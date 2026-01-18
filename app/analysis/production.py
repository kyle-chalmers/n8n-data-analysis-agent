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
