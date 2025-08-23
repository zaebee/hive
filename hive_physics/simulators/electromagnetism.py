import json
from typing import List, Dict, Any

from hive_physics.constants import PhysicalConstants
from hive_physics.utils.graph import build_adjacency_list, calculate_architectural_hops

def _get_component_data(component_id: str, components: list) -> Dict[str, Any]:
    """Helper to find a component's data by ID."""
    for comp in components:
        if comp.get("id") == component_id:
            return comp
    raise ValueError(f"Component with id '{component_id}' not found.")

def _calculate_em_force(graph: Dict[str, List[str]], comp1: Dict[str, Any], comp2: Dict[str, Any]) -> float:
    """Calculates the electromagnetic force between two components."""
    k_hive = PhysicalConstants.K_HIVE_ELECTRO

    q1 = comp1.get("charge", 0)
    q2 = comp2.get("charge", 0)

    # No force if either component is neutral
    if q1 == 0 or q2 == 0:
        return 0.0

    r = calculate_architectural_hops(graph, comp1["id"], comp2["id"])

    if r == -1:  # No path
        return 0.0
    if r == 0:  # Same component, this shouldn't happen if we check neighbors
        return 0.0

    # Force = k * (q1 * q2) / r^2
    # Negative result = attraction, Positive result = repulsion
    force = k_hive * (q1 * q2) / (r**2)
    return force

def find_most_stable_path(metrics_file: str, start_component_id: str, max_steps: int = 5) -> List[str]:
    """
    Finds the most stable workflow (chain of primitives) starting from a component.

    This simulation works by iteratively finding the next component in a chain
    that has the strongest attractive electromagnetic force.

    Args:
        metrics_file: Path to the JSON file with component and graph data.
        start_component_id: The ID of the component to start the chain from.
        max_steps: The maximum length of the chain to discover.

    Returns:
        A list of component names representing the most stable path.
    """
    with open(metrics_file, 'r') as f:
        data = json.load(f)

    all_components_data = data.get("hive_snapshot", {}).get("components", [])
    graph = build_adjacency_list(all_components_data)

    if start_component_id not in graph:
        raise ValueError(f"Start component '{start_component_id}' not found.")

    path = [start_component_id]
    current_comp_id = start_component_id

    for _ in range(max_steps - 1):
        current_comp_data = _get_component_data(current_comp_id, all_components_data)
        neighbors = graph.get(current_comp_id, [])

        best_neighbor = None
        # We are looking for the most negative force (strongest attraction)
        max_attraction = 0

        for neighbor_id in neighbors:
            if neighbor_id in path:  # Avoid cycles
                continue

            neighbor_data = _get_component_data(neighbor_id, all_components_data)
            force = _calculate_em_force(graph, current_comp_data, neighbor_data)

            if force < max_attraction:
                max_attraction = force
                best_neighbor = neighbor_id

        if best_neighbor:
            path.append(best_neighbor)
            current_comp_id = best_neighbor
        else:
            # No attractive neighbors found, the stable path ends here.
            break

    # Return the names of the components in the path
    path_names = [_get_component_data(comp_id, all_components_data).get("name", "Unknown") for comp_id in path]
    return path_names

if __name__ == '__main__':
    mock_file_path = 'hive_physics/data/mock_metrics.json'
    print("--- Simulating Stable Workflow Discovery via Electromagnetism ---")

    start_id = "comp_001"
    print(f"\nDiscovering stable path starting from '{start_id}' (RestConnector)...")

    try:
        stable_path = find_most_stable_path(mock_file_path, start_id)

        print(f"  - Discovered Path: {' -> '.join(stable_path)}")
        print("  - Interpretation: The simulation follows the path of maximum attraction, deriving a stable workflow from physical first principles.")
    except Exception as e:
        print(f"An error occurred during simulation: {e}")
