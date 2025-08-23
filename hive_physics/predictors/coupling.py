import json
from typing import Dict, Any, List

from hive_physics.constants import PhysicalConstants
from hive_physics.utils.graph import build_adjacency_list, calculate_architectural_hops

def _get_component_data(component_id: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper function to find a component's data by its ID."""
    for comp in components:
        if comp.get("id") == component_id:
            return comp
    raise ValueError(f"Component with id '{component_id}' not found in mock data.")

def predict_bond_strength(metrics_file: str, component1_id: str, component2_id: str) -> float:
    """
    Predicts the bond strength (gravitational force) between two components.
    Uses architectural hops for distance 'r'.

    Formula: F = G_hive * (m1 * m2) / r^2
    """
    try:
        with open(metrics_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Metrics file not found at {metrics_file}")

    components_data = data.get("hive_snapshot", {}).get("components", [])
    if not components_data:
        raise ValueError("No component data found in metrics file.")

    # These calls will now raise a ValueError if a component is not found
    comp1 = _get_component_data(component1_id, components_data)
    comp2 = _get_component_data(component2_id, components_data)

    m1 = comp1.get("mass", 0.0)
    m2 = comp2.get("mass", 0.0)

    # Build the graph and calculate architectural distance 'r'
    graph = build_adjacency_list(components_data)
    r = calculate_architectural_hops(graph, component1_id, component2_id)

    if r == -1:  # No path between components
        return 0.0
    if r == 0:  # The components are the same
        return float('inf')

    G_hive = PhysicalConstants.G_HIVE
    force = G_hive * (m1 * m2) / (r**2)
    return force

if __name__ == '__main__':
    mock_file_path = 'hive_physics/data/mock_metrics.json'

    print("--- Predicting Component Bond Strength (Gravitational Force) ---")

    # Test cases
    test_pairs = [
        ("comp_001", "comp_002"), # r=1
        ("comp_001", "comp_003"), # r=2
        ("comp_001", "comp_004"), # r=3
        ("comp_001", "comp_001"), # r=0
        ("comp_001", "comp_999")  # non-existent
    ]

    for c1_id, c2_id in test_pairs:
        try:
            print(f"\nCalculating bond strength between '{c1_id}' and '{c2_id}'...")
            strength = predict_bond_strength(mock_file_path, c1_id, c2_id)
            print(f"  - Predicted Strength: {strength:.4f}")
        except ValueError as e:
            print(f"  - Caught expected error: {e}")
        except Exception as e:
            print(f"  - Caught unexpected error: {e}")
