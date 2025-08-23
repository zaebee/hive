import os
from genesis_engine.utils import find_component_path
from hive_physics.predictors.coupling import PredictorService
from hive_physics.datasources.kubernetes import KubernetesDataSource

def analyze_component(analysis_type: str, component_name: str, domain: str | None):
    """
    Performs analysis on a component.

    :param analysis_type: The type of analysis to perform (e.g., 'bonds').
    :param component_name: The name of the component.
    :param domain: The domain of the component.
    """
    if analysis_type == 'bonds':
        analyze_bonds(component_name, domain)
    else:
        print(f"Error: Unknown analysis type '{analysis_type}'.")

def analyze_bonds(component_name: str, domain: str | None):
    """
    Analyzes the bond strengths of a component by integrating with Hive Physics.
    """
    print(f"Locating component '{component_name}'...")
    try:
        # Although we find the component path, the physics engine currently
        # derives its graph from live data sources, not local files.
        # This check still serves as a validation that the component exists.
        component_path = find_component_path(component_name, domain)
        if not component_path:
            print(f"Error: Component '{component_name}' not found in the project structure.")
            return
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(f"Found component at: {component_path}")
    print("Initializing Hive Physics data sources (requires live Kubernetes connection)...")

    # As discovered during exploration, the physics engine requires this env var.
    if not os.environ.get("PROMETHEUS_URL"):
        print("\nERROR: PROMETHEUS_URL environment variable is not set.")
        print("This is required by the physics engine to calculate component mass.")
        return

    try:
        # The physics engine is designed to work with live data sources.
        k8s_ds = KubernetesDataSource()

        predictor = PredictorService(data_source=k8s_ds)
        all_strengths = predictor.predict_bond_strength()

        if not all_strengths:
            print("No bond strengths could be calculated. Check connection to data sources.")
            return

        # Filter the results to show only bonds related to the specified component.
        component_bonds = {
            pair: force for pair, force in all_strengths.items() if component_name in pair
        }

        print("\n--- Bond Strength Report ---")
        if not component_bonds:
            print(f"No bonds found for component '{component_name}'.")
        else:
            for pair, force in component_bonds.items():
                print(f"  - {pair}: {force:.4f}")

    except Exception as e:
        print(f"\nAn error occurred during analysis: {e}")
        print("Please ensure you are connected to the Kubernetes cluster and that Prometheus is accessible.")
