import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.simulators.electromagnetism import find_most_stable_path
from hive_physics.datasources.prometheus import PrometheusDataSource
from hive_physics.datasources.kubernetes import KubernetesDataSource

@pytest.fixture
def mock_datasources(mocker):
    """Provides mock Prometheus and Kubernetes datasources."""
    mock_prom_ds = mocker.Mock(spec=PrometheusDataSource)
    mock_k8s_ds = mocker.Mock(spec=KubernetesDataSource)
    return mock_prom_ds, mock_k8s_ds

def test_path_discovery_from_positive_charge(mock_datasources):
    """
    Tests that the simulation correctly finds the path of maximum attraction.
    """
    mock_prom_ds, mock_k8s_ds = mock_datasources

    # Mock the data returned by the datasources
    mock_k8s_ds.get_architectural_graph.return_value = {
        "comp_001": ["comp_002"],
        "comp_002": ["comp_001", "comp_003"],
        "comp_003": ["comp_002"],
    }

    charge_map = {"comp_001": 1, "comp_002": -1, "comp_003": 0}
    mock_prom_ds.get_component_charge.side_effect = lambda name: charge_map.get(name)

    # Test
    path = find_most_stable_path(mock_prom_ds, mock_k8s_ds, "comp_001")

    # Assert
    # Path should be comp_001 (+1) -> comp_002 (-1). It stops at comp_002
    # because its other neighbor, comp_003, has a charge of 0.
    assert path == ['comp_001', 'comp_002']

def test_path_from_neutral_charge(mock_datasources):
    """
    Tests that a simulation starting from a neutral component results in a
    path containing only that component.
    """
    mock_prom_ds, mock_k8s_ds = mock_datasources

    mock_k8s_ds.get_architectural_graph.return_value = {
        "comp_001": ["comp_003"],
        "comp_003": ["comp_001"],
    }
    charge_map = {"comp_001": 1, "comp_003": 0}
    mock_prom_ds.get_component_charge.side_effect = lambda name: charge_map.get(name)

    # Test
    path = find_most_stable_path(mock_prom_ds, mock_k8s_ds, "comp_003")

    # Assert
    assert path == ['comp_003']

def test_error_on_bad_start_node(mock_datasources):
    """
    Tests that a ValueError is raised for a non-existent start component ID.
    """
    mock_prom_ds, mock_k8s_ds = mock_datasources

    mock_k8s_ds.get_architectural_graph.return_value = {"comp_001": []}

    with pytest.raises(ValueError, match="Start component 'comp_999' not found in K8s graph."):
        find_most_stable_path(mock_prom_ds, mock_k8s_ds, "comp_999")
