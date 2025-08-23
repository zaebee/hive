import pytest

from hive_physics.utils.graph import calculate_architectural_hops

@pytest.fixture
def sample_graph():
    """Provides a sample component graph for testing."""
    return {
        "comp_001": ["comp_002"],
        "comp_002": ["comp_001", "comp_003"],
        "comp_003": ["comp_002", "comp_004"],
        "comp_004": ["comp_003"],
        "comp_005": [] # An isolated component
    }

def test_single_hop_distance(sample_graph):
    """Tests a direct connection."""
    assert calculate_architectural_hops(sample_graph, "comp_001", "comp_002") == 1

def test_multi_hop_distance(sample_graph):
    """Tests a path that requires multiple hops."""
    assert calculate_architectural_hops(sample_graph, "comp_001", "comp_004") == 3

def test_zero_hop_distance(sample_graph):
    """Tests the distance from a node to itself."""
    assert calculate_architectural_hops(sample_graph, "comp_001", "comp_001") == 0

def test_no_path(sample_graph):
    """Tests for when no path exists between two nodes."""
    assert calculate_architectural_hops(sample_graph, "comp_001", "comp_005") == -1

def test_node_not_in_graph(sample_graph):
    """Tests that a ValueError is raised for a non-existent node."""
    with pytest.raises(ValueError, match="Node 'comp_999' not found in the graph."):
        calculate_architectural_hops(sample_graph, "comp_001", "comp_999")

def test_symmetric_path(sample_graph):
    """Tests that the path distance is the same in both directions."""
    assert calculate_architectural_hops(sample_graph, "comp_004", "comp_001") == 3
