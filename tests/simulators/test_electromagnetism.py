import pytest
import sys
import os

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.simulators.electromagnetism import find_most_stable_path

@pytest.fixture
def mock_metrics_file_path():
    """Provides the path to the main mock data file."""
    return 'hive_physics/data/mock_metrics.json'

def test_path_discovery_from_positive_charge(mock_metrics_file_path):
    """
    Tests that the simulation correctly finds the path of maximum attraction
    starting from a positively charged component.
    Path should be comp_001 (+1) -> comp_002 (-1).
    """
    path = find_most_stable_path(mock_metrics_file_path, "comp_001")
    assert path == ['RestConnector', 'OrderAggregate']

def test_path_from_neutral_charge(mock_metrics_file_path):
    """
    Tests that a simulation starting from a neutral component results in a
    path containing only that component, as there are no attractive forces
    to follow.
    """
    path = find_most_stable_path(mock_metrics_file_path, "comp_003")
    assert path == ['PaymentTransform']

def test_error_on_bad_start_node(mock_metrics_file_path):
    """
    Tests that a ValueError is raised for a non-existent start component ID.
    """
    with pytest.raises(ValueError, match="Start component 'comp_999' not found."):
        find_most_stable_path(mock_metrics_file_path, "comp_999")
