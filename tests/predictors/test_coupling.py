import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.predictors.coupling import predict_bond_strength
from hive_physics.datasources.prometheus import PrometheusDataSource
from hive_physics.datasources.kubernetes import KubernetesDataSource

@pytest.fixture
def mock_datasources(mocker):
    """Provides mock Prometheus and Kubernetes datasources."""
    mock_prom_ds = mocker.Mock(spec=PrometheusDataSource)
    mock_k8s_ds = mocker.Mock(spec=KubernetesDataSource)
    return mock_prom_ds, mock_k8s_ds

def test_predict_bond_strength(mock_datasources):
    """
    Tests the main bond strength prediction logic.
    """
    mock_prom_ds, mock_k8s_ds = mock_datasources

    # Mock the data returned by the datasources
    mock_k8s_ds.get_architectural_graph.return_value = {
        "comp_001": ["comp_002"],
        "comp_002": ["comp_001", "comp_003"],
        "comp_003": ["comp_002"],
    }

    # Define a mapping for mass lookup
    mass_map = {"comp_001": 200.0, "comp_002": 1500.0, "comp_003": 800.0}
    mock_prom_ds.get_component_mass.side_effect = lambda name: mass_map.get(name)

    # Call the function to be tested
    strengths = predict_bond_strength(mock_prom_ds, mock_k8s_ds)

    # Assertions
    # r=1 between comp_001 and comp_002. F = 0.01 * (200*1500)/1^2 = 3000
    assert strengths["comp_001 <-> comp_002"] == pytest.approx(3000.0)

    # r=1 between comp_002 and comp_003. F = 0.01 * (1500*800)/1^2 = 12000
    assert strengths["comp_002 <-> comp_003"] == pytest.approx(12000.0)

    # r=2 between comp_001 and comp_003.
    assert "comp_001 <-> comp_003" not in strengths # They are not directly connected in this test graph

def test_predict_with_no_graph(mock_datasources):
    """
    Tests that the function returns an empty dict if the graph is empty.
    """
    mock_prom_ds, mock_k8s_ds = mock_datasources
    mock_k8s_ds.get_architectural_graph.return_value = {}

    strengths = predict_bond_strength(mock_prom_ds, mock_k8s_ds)
    assert strengths == {}

def test_predict_with_missing_mass(mock_datasources):
    """
    Tests that if a component's mass is None (not in Prometheus), it is
    treated as 0, resulting in a bond strength of 0.
    """
    mock_prom_ds, mock_k8s_ds = mock_datasources

    mock_k8s_ds.get_architectural_graph.return_value = {"comp_001": ["comp_002"], "comp_002": ["comp_001"]}

    # comp_002's mass is missing from the map
    mass_map = {"comp_001": 200.0}
    mock_prom_ds.get_component_mass.side_effect = lambda name: mass_map.get(name)

    strengths = predict_bond_strength(mock_prom_ds, mock_k8s_ds)

    # The force should be 0 because m2 is 0
    assert strengths["comp_001 <-> comp_002"] == 0.0
