from typing import List, Dict, Any

from hive_physics.constants import PhysicalConstants
from hive_physics.utils.graph import calculate_architectural_hops
from hive_physics.datasources.prometheus import PrometheusDataSource
from hive_physics.datasources.kubernetes import KubernetesDataSource

def _calculate_em_force(
    graph: Dict[str, List[str]],
    comp1_id: str,
    comp2_id: str,
    charges: Dict[str, int]
) -> float:
    """Calculates the electromagnetic force between two components."""
    k_hive = PhysicalConstants.K_HIVE_ELECTRO

    q1 = charges.get(comp1_id, 0)
    q2 = charges.get(comp2_id, 0)

    if q1 == 0 or q2 == 0:
        return 0.0

    r = calculate_architectural_hops(graph, comp1_id, comp2_id)

    if r <= 0:
        return 0.0

    force = k_hive * (q1 * q2) / (r**2)
    return force

def find_most_stable_path(
    prom_datasource: PrometheusDataSource,
    k8s_datasource: KubernetesDataSource,
    start_component_id: str,
    max_steps: int = 5
) -> List[str]:
    """
    Finds the most stable workflow using live data for graph and charge.
    """
    print("Discovering most stable path with live data...")

    # 1. Get live architectural graph from Kubernetes
    graph = k8s_datasource.get_architectural_graph()
    if start_component_id not in graph:
        raise ValueError(f"Start component '{start_component_id}' not found in K8s graph.")

    # 2. Get live charge for all components in the graph
    all_component_ids = list(graph.keys())
    charges = {comp_id: prom_datasource.get_component_charge(comp_id) or 0 for comp_id in all_component_ids}

    # 3. Find the path of maximum attraction
    path = [start_component_id]
    current_comp_id = start_component_id

    for _ in range(max_steps - 1):
        neighbors = graph.get(current_comp_id, [])
        best_neighbor = None
        max_attraction = 0

        for neighbor_id in neighbors:
            if neighbor_id in path:
                continue

            force = _calculate_em_force(graph, current_comp_id, neighbor_id, charges)

            if force < max_attraction:
                max_attraction = force
                best_neighbor = neighbor_id

        if best_neighbor:
            path.append(best_neighbor)
            current_comp_id = best_neighbor
        else:
            break

    return path

if __name__ == '__main__':
    import os

    print("--- Simulating Stable Workflow Discovery (with Live Data Sources) ---")

    prometheus_url = os.environ.get("PROMETHEUS_URL")

    if not prometheus_url:
        print("\nSKIPPING DEMO: PROMETHEUS_URL environment variable is not set.")
    else:
        try:
            print(f"Connecting to Prometheus at {prometheus_url}...")
            prom_ds = PrometheusDataSource(api_url=prometheus_url)

            print("Connecting to Kubernetes...")
            k8s_ds = KubernetesDataSource()

            start_id = "rest-connector" # Assume a service named this exists
            print(f"\nDiscovering stable path starting from '{start_id}'...")

            stable_path = find_most_stable_path(prom_ds, k8s_ds, start_id)

            path_str = " -> ".join(stable_path)
            print(f"  - Discovered Stable Path: {path_str}")

        except Exception as e:
            print(f"\nAn error occurred during the demonstration: {e}")
