import json
from typing import Dict, Any, List

from hive_physics.constants import PhysicalConstants
from hive_physics.utils.graph import build_adjacency_list, calculate_architectural_hops
from hive_physics.datasources.prometheus import PrometheusDataSource

def _get_component_data(component_id: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper function to find a component's data by its ID (for graph structure)."""
    for comp in components:
        if comp.get("id") == component_id:
            return comp
    raise ValueError(f"Component with id '{component_id}' not found in mock data.")

def predict_bond_strength(
    datasource: PrometheusDataSource,
    metrics_file: str,
    component1_id: str,
    component2_id: str
) -> float:
    """
    Predicts the bond strength (gravitational force) between two components.

    Uses a live data source for component mass and a file for the architectural graph.

    Formula: F = G_hive * (m1 * m2) / r^2
    """
    # 1. Get component mass from the live data source
    # Treat mass as 0.0 if Prometheus has no data for the component.
    m1 = datasource.get_component_mass(component1_id) or 0.0
    m2 = datasource.get_component_mass(component2_id) or 0.0

    # 2. Get architectural distance 'r' from the file-based graph
    try:
        with open(metrics_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Metrics file not found at {metrics_file}")

    components_data = data.get("hive_snapshot", {}).get("components", [])
    if not components_data:
        raise ValueError("No component data found in metrics file.")

    # These calls will raise a ValueError if a component is not in the graph file
    _get_component_data(component1_id, components_data)
    _get_component_data(component2_id, components_data)

    graph = build_adjacency_list(components_data)
    r = calculate_architectural_hops(graph, component1_id, component2_id)

    # 3. Calculate the force
    if r == -1:  # No path between components
        return 0.0
    if r == 0:  # The components are the same
        return float('inf')

    G_hive = PhysicalConstants.G_HIVE
    force = G_hive * (m1 * m2) / (r**2)
    return force

if __name__ == '__main__':
    import os

    print("--- Predicting Component Bond Strength (with Live Data Source) ---")

    # This demonstration requires a Prometheus server.
    # We will use a mock datasource for the actual unit tests.
    prometheus_url = os.environ.get("PROMETHEUS_URL")
    if not prometheus_url:
        print("\nSKIPPING DEMO: PROMETHEUS_URL environment variable is not set.")
        print("Set it to your Prometheus server's URL to run this demo (e.g., http://localhost:9090).")
    else:
        try:
            print(f"Connecting to Prometheus at {prometheus_url}...")
            live_datasource = PrometheusDataSource(api_url=prometheus_url)
            mock_file_path = 'hive_physics/data/mock_metrics.json'

            c1_id, c2_id = "comp_001", "comp_002"
            print(f"\nCalculating bond strength between '{c1_id}' and '{c2_id}'...")

            # Note: This will likely return 0 unless you have a Prometheus server
            # running that is scraped for a metric named 'hive_dna_aggregate_commands_handled_total'
            # with component_name="comp_001" or "comp_002".
            strength = predict_bond_strength(live_datasource, mock_file_path, c1_id, c2_id)
            print(f"  - Predicted Strength: {strength:.4f}")

        except Exception as e:
            print(f"  - An error occurred during the demonstration: {e}")
