import pytest

from hive_physics.predictors.coupling import predict_bond_strength

@pytest.fixture
def mock_metrics_file_path():
    """Provides the path to the main mock data file."""
    # This assumes pytest is run from the repository root.
    return 'hive_physics/data/mock_metrics.json'

def test_predict_strong_bond_one_hop(mock_metrics_file_path):
    """
    Tests bond between comp_001 (mass 200) and comp_002 (mass 1500) at r=1.
    F = 0.01 * (200 * 1500) / 1^2 = 3000
    """
    strength = predict_bond_strength(mock_metrics_file_path, "comp_001", "comp_002")
    assert strength == pytest.approx(3000.0)

def test_predict_weaker_bond_two_hops(mock_metrics_file_path):
    """
    Tests bond between comp_001 (mass 200) and comp_003 (mass 800) at r=2.
    F = 0.01 * (200 * 800) / 2^2 = 400
    """
    strength = predict_bond_strength(mock_metrics_file_path, "comp_001", "comp_003")
    assert strength == pytest.approx(400.0)

def test_predict_zero_distance(mock_metrics_file_path):
    """
    Tests the case where the components are the same, r=0. Should return infinity.
    """
    strength = predict_bond_strength(mock_metrics_file_path, "comp_001", "comp_001")
    assert strength == float('inf')

def test_error_on_missing_component(mock_metrics_file_path):
    """
    Tests that a ValueError is raised for a non-existent component ID.
    """
    with pytest.raises(ValueError, match="Component with id 'comp_999' not found in mock data."):
        predict_bond_strength(mock_metrics_file_path, "comp_001", "comp_999")

def test_error_on_missing_file():
    """
    Tests that a ValueError is raised for a non-existent metrics file.
    """
    with pytest.raises(ValueError, match="Metrics file not found"):
        predict_bond_strength("non_existent_file.json", "comp_001", "comp_002")
