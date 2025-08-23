import pytest
import sys
import os

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.predictors.coupling import predict_bond_strength
from hive_physics.datasources.prometheus import PrometheusDataSource

@pytest.fixture
def mock_metrics_file_path():
    """Provides the path to the main mock data file for graph structure."""
    return 'hive_physics/data/mock_metrics.json'

def test_predict_strong_bond_one_hop(mock_metrics_file_path, mocker):
    """
    Tests bond between comp_001 and comp_002 at r=1.
    We mock the masses returned from the datasource.
    F = 0.01 * (200 * 1500) / 1^2 = 3000
    """
    mock_datasource = mocker.Mock(spec=PrometheusDataSource)
    # Simulate the datasource returning mass 200.0 for comp_001 and 1500.0 for comp_002
    mock_datasource.get_component_mass.side_effect = [200.0, 1500.0]

    strength = predict_bond_strength(mock_datasource, mock_metrics_file_path, "comp_001", "comp_002")

    assert mock_datasource.get_component_mass.call_count == 2
    assert strength == pytest.approx(3000.0)

def test_predict_weaker_bond_two_hops(mock_metrics_file_path, mocker):
    """
    Tests bond between comp_001 and comp_003 at r=2.
    F = 0.01 * (200 * 800) / 2^2 = 400
    """
    mock_datasource = mocker.Mock(spec=PrometheusDataSource)
    mock_datasource.get_component_mass.side_effect = [200.0, 800.0]

    strength = predict_bond_strength(mock_datasource, mock_metrics_file_path, "comp_001", "comp_003")
    assert strength == pytest.approx(400.0)

def test_predict_zero_distance(mock_metrics_file_path, mocker):
    """
    Tests the case where the components are the same, r=0. Should return infinity.
    """
    mock_datasource = mocker.Mock(spec=PrometheusDataSource)
    # The mass is fetched but doesn't matter for the r=0 case.
    mock_datasource.get_component_mass.return_value = 100.0

    strength = predict_bond_strength(mock_datasource, mock_metrics_file_path, "comp_001", "comp_001")
    assert strength == float('inf')
    # Ensure mass was not fetched, as the r=0 check happens first.
    # Let's re-read the source. The mass is fetched first. So the mock should be called.
    # The test is correct as is, but the implementation could be optimized.
    assert mock_datasource.get_component_mass.call_count == 2


def test_error_on_missing_component_in_graph(mock_metrics_file_path, mocker):
    """
    Tests that a ValueError is raised for a component not in the graph file.
    """
    mock_datasource = mocker.Mock(spec=PrometheusDataSource)
    mock_datasource.get_component_mass.return_value = 100.0 # Datasource might find it

    with pytest.raises(ValueError, match="Component with id 'comp_999' not found in mock data."):
        predict_bond_strength(mock_datasource, mock_metrics_file_path, "comp_001", "comp_999")

def test_mass_is_none(mock_metrics_file_path, mocker):
    """
    Tests that if a component's mass is None (not found in Prometheus), it is
    treated as 0, resulting in a bond strength of 0.
    """
    mock_datasource = mocker.Mock(spec=PrometheusDataSource)
    # One component is found, the other is not.
    mock_datasource.get_component_mass.side_effect = [200.0, None]

    strength = predict_bond_strength(mock_datasource, mock_metrics_file_path, "comp_001", "comp_002")
    assert strength == 0.0
