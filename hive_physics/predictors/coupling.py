import json
import math
import sys
import os
from typing import Dict, Any

# Add the repository root to the Python path to allow the relative import to work.
# This is necessary for running the script directly for demonstration purposes.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.constants import PhysicalConstants

def _get_component_data(component_id: str, components: list) -> Dict[str, Any]:
    """Helper function to find a component's data by its ID."""
    for comp in components:
        if comp.get("id") == component_id:
            return comp
    raise ValueError(f"Component with id '{component_id}' not found in mock data.")

def _calculate_distance(pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
    """Calculates the Euclidean distance between two points in 3D space."""
    return math.sqrt(
        (pos2.get('x', 0) - pos1.get('x', 0))**2 +
        (pos2.get('y', 0) - pos1.get('y', 0))**2 +
        (pos2.get('z', 0) - pos1.get('z', 0))**2
    )

def predict_bond_strength(metrics_file: str, component1_id: str, component2_id: str) -> float:
    """
    Predicts the bond strength (gravitational force) between two components.

    Formula: F = G_hive * (m1 * m2) / r^2
    - F: Bond strength (this function's output)
    - G_hive: The Hive's gravitational constant.
    - m1, m2: "Mass" of the components (e.g., event throughput).
    - r: Distance between the components.

    Args:
        metrics_file: Path to the JSON file with mock component data.
        component1_id: The ID of the first component.
        component2_id: The ID of the second component.

    Returns:
        The predicted bond strength.
    """
    try:
        with open(metrics_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Metrics file not found at {metrics_file}")
        return 0.0

    components_data = data.get("hive_snapshot", {}).get("components", [])
    if not components_data:
        print("Error: No component data found in metrics file.")
        return 0.0

    try:
        comp1 = _get_component_data(component1_id, components_data)
        comp2 = _get_component_data(component2_id, components_data)
    except ValueError as e:
        print(f"Error: {e}")
        return 0.0

    m1 = comp1.get("mass", 0.0)
    m2 = comp2.get("mass", 0.0)

    pos1 = comp1.get("position")
    pos2 = comp2.get("position")

    if not pos1 or not pos2:
        print("Error: Component position data is missing.")
        return 0.0

    r = _calculate_distance(pos1, pos2)

    if r == 0:
        # Avoid division by zero. In physics, this would be a singularity.
        # In the Hive, it represents two components being the same entity
        # or occupying the same "space", implying infinite coupling.
        return float('inf')

    # Get the gravitational constant from our constants file
    G_hive = PhysicalConstants.G_HIVE

    force = G_hive * (m1 * m2) / (r**2)
    return force

if __name__ == '__main__':
    import sys
    import os
    # Add the repository root to the Python path to allow the relative import to work.
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from hive_physics.constants import PhysicalConstants

    mock_file_path = 'hive_physics/data/mock_metrics.json'

    print("--- Predicting Component Bond Strength (Gravitational Force) ---")

    # Test case 1: Two components close to each other
    c1_id, c2_id = "comp_001", "comp_002"
    print(f"\nCalculating bond strength between '{c1_id}' and '{c2_id}'...")
    strength1 = predict_bond_strength(mock_file_path, c1_id, c2_id)
    print(f"Predicted Strength: {strength1:.4f}")

    # Test case 2: Two components far from each other
    c1_id, c3_id = "comp_001", "comp_003"
    print(f"\nCalculating bond strength between '{c1_id}' and '{c3_id}'...")
    strength2 = predict_bond_strength(mock_file_path, c1_id, c3_id)
    print(f"Predicted Strength: {strength2:.4f}")

    # Test case 3: Component with itself (r=0)
    print(f"\nCalculating bond strength between '{c1_id}' and '{c1_id}'...")
    strength3 = predict_bond_strength(mock_file_path, c1_id, c1_id)
    print(f"Predicted Strength: {strength3}")
