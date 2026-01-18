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
