import json
from typing import Dict, Any, List

from hive_physics.constants import PhysicalConstants
from hive_physics.utils.graph import calculate_architectural_hops
from hive_physics.datasources.prometheus import PrometheusDataSource
from hive_physics.datasources.kubernetes import KubernetesDataSource

def predict_bond_strength(
    prom_datasource: PrometheusDataSource,
    k8s_datasource: KubernetesDataSource
) -> Dict[str, float]:
    """
    Predicts the bond strength for all connected components in the graph.

    Uses live data sources for both the architectural graph and component mass.

    Returns:
        A dictionary where keys are component pairs and values are bond strengths.
    """
    print("Predicting bond strengths for all components...")

    # 1. Get live architectural graph from Kubernetes
    graph = k8s_datasource.get_architectural_graph()
    if not graph:
        print("Could not discover architectural graph. No bonds to predict.")
        return {}

    # 2. Get live mass for all components in the graph
    all_component_ids = list(graph.keys())
    masses = {comp_id: prom_datasource.get_component_mass(comp_id) or 0.0 for comp_id in all_component_ids}

    bond_strengths = {}

    # Use a set to avoid calculating the same bond twice (A->B and B->A)
    calculated_pairs = set()

    for comp1_id, connections in graph.items():
        for comp2_id in connections:
            pair = tuple(sorted((comp1_id, comp2_id)))
            if pair in calculated_pairs:
                continue

            # 3. Get mass and calculate distance for each pair
            m1 = masses.get(comp1_id, 0.0)
            m2 = masses.get(comp2_id, 0.0)

            r = calculate_architectural_hops(graph, comp1_id, comp2_id)

            # 4. Calculate force
            if r > 0:
                G_hive = PhysicalConstants.G_HIVE
                force = G_hive * (m1 * m2) / (r**2)
                bond_strengths[f"{comp1_id} <-> {comp2_id}"] = force

            calculated_pairs.add(pair)

    return bond_strengths

if __name__ == '__main__':
    import os

    print("--- Predicting All Component Bond Strengths (with Live Data Sources) ---")

    prometheus_url = os.environ.get("PROMETHEUS_URL")

    if not prometheus_url:
        print("\nSKIPPING DEMO: PROMETHEUS_URL environment variable is not set.")
    else:
        try:
            print(f"Connecting to Prometheus at {prometheus_url}...")
            prom_ds = PrometheusDataSource(api_url=prometheus_url)

            print("Connecting to Kubernetes...")
            k8s_ds = KubernetesDataSource()

            strengths = predict_bond_strength(prom_ds, k8s_ds)

            print("\n--- Bond Strength Report ---")
            if not strengths:
                print("No bonds found or data available.")
            else:
                for pair, force in strengths.items():
                    print(f"  - {pair}: {force:.4f}")

        except Exception as e:
            print(f"\nAn error occurred during the demonstration: {e}")
