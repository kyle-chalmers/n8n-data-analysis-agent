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
