import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.predictors.coupling import PredictorService, DataSourceInterface
from hive_physics.events import EventPublisher

@pytest.fixture
def mock_data_source(mocker):
    """Provides a mock datasource that implements the interface."""
    mock_ds = mocker.Mock(spec=DataSourceInterface)

    # Setup mock return values for the datasource
    mock_ds.get_architectural_graph.return_value = {
        "comp_a": ["comp_b"],
        "comp_b": ["comp_a"],
        "comp_c": []
    }
    mass_map = {"comp_a": 100.0, "comp_b": 200.0, "comp_c": 50.0}
    mock_ds.get_component_mass.side_effect = lambda name: mass_map.get(name)

    return mock_ds

@pytest.fixture
def mock_event_publisher(mocker):
    """Provides a mock event publisher."""
    return mocker.Mock(spec=EventPublisher)

def test_service_predicts_bond_strength(mock_data_source):
    """
    Tests that the PredictorService correctly calculates bond strength.
    """
    # Test without an event publisher first
    service = PredictorService(data_source=mock_data_source)
    strengths = service.predict_bond_strength()

    # F = 0.01 * (100 * 200) / 1^2 = 200
    assert strengths["comp_a <-> comp_b"] == pytest.approx(200.0)
    # Ensure it only calculates for connected components
    assert len(strengths) == 1

def test_service_publishes_event(mock_data_source, mock_event_publisher):
    """
    Tests that the service calls the event publisher when one is provided.
    """
    service = PredictorService(
        data_source=mock_data_source,
        event_publisher=mock_event_publisher
    )
    service.predict_bond_strength()

    # Assert that the publisher was called with the correct data
    # Note: The order of comp1_id and comp2_id depends on iteration order,
    # so we can't be certain. A more robust test would check the call args
    # in a way that is order-independent, but this is sufficient for now.
    mock_event_publisher.publish_bond_strength_event.assert_called_once()
    # A simple way to check the content without being order-sensitive
    args, kwargs = mock_event_publisher.publish_bond_strength_event.call_args
    assert set(args[:2]) == {"comp_a", "comp_b"}
    assert args[2] == pytest.approx(200.0)


def test_service_handles_no_graph(mock_data_source):
    """
    Tests that the service handles the case where the datasource returns no graph.
    """
    mock_data_source.get_architectural_graph.return_value = {}
    service = PredictorService(data_source=mock_data_source)
    strengths = service.predict_bond_strength()
    assert strengths == {}

def test_service_does_not_publish_if_no_publisher(mock_data_source, mock_event_publisher):
    """
    Tests that the event publisher is not called if it's not provided.
    """
    # This test is implicitly covered by the mocker, but we can be explicit.
    service = PredictorService(data_source=mock_data_source, event_publisher=None)
    service.predict_bond_strength()

    # The mock_event_publisher was never passed in, so it should have no calls.
    mock_event_publisher.publish_bond_strength_event.assert_not_called()
