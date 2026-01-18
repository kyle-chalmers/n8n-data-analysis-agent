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
