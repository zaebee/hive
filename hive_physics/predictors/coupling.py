import json
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from hive_physics.constants import PhysicalConstants
from hive_physics.utils.graph import calculate_architectural_hops
from hive_physics.events import EventPublisher, EventSubscriber
from hive_physics.models import ArchitecturalGraph, ComponentMass

class DataSourceInterface(ABC):
    @abstractmethod
    def get_architectural_graph(self) -> Optional[ArchitecturalGraph]:
        pass

    @abstractmethod
    def get_component_mass(self, component_id: str) -> Optional[float]:
        pass

class PredictorService:
    def __init__(
        self,
        data_source: DataSourceInterface,
        event_publisher: Optional[EventPublisher] = None
    ):
        self.data_source = data_source
        self.event_publisher = event_publisher

    def predict_bond_strength(self) -> Dict[str, float]:
        """
        Predicts the bond strength for all connected components in the graph.
        Uses data sources for architectural graph and component mass.
        Publishes bond strength events if event publisher is configured.
        """
        print("Predicting bond strengths for all components...")

        graph = self.data_source.get_architectural_graph()
        if not graph:
            print("Could not discover architectural graph. No bonds to predict.")
            return {}

        all_component_ids = list(graph.keys())
        masses = {comp_id: self.data_source.get_component_mass(comp_id) or 0.0 for comp_id in all_component_ids}

        bond_strengths = {}
        calculated_pairs = set()

        for comp1_id, connections in graph.items():
            for comp2_id in connections:
                pair = tuple(sorted((comp1_id, comp2_id)))
                if pair in calculated_pairs:
                    continue

                m1 = masses.get(comp1_id, 0.0)
                m2 = masses.get(comp2_id, 0.0)
                r = calculate_architectural_hops(graph, comp1_id, comp2_id)

                if r > 0:
                    G_hive = PhysicalConstants.G_HIVE
                    force = G_hive * (m1 * m2) / (r**2)
                    bond_strengths[f"{comp1_id} <-> {comp2_id}"] = force

                    # Publish event if event publisher is configured
                    if self.event_publisher:
                        self.event_publisher.publish_bond_strength_event(
                            comp1_id, comp2_id, force
                        )

                calculated_pairs.add(pair)

        return bond_strengths

if __name__ == '__main__':
    import os
    from hive_physics.datasources.prometheus import PrometheusDataSource
    from hive_physics.datasources.kubernetes import KubernetesDataSource
    from hive_physics.events import KafkaEventPublisher

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

            # Create event publisher if needed
            event_publisher = KafkaEventPublisher() if os.environ.get("EVENT_BROKER_ENABLED") else None

            # Use the new service with dependency injection
            predictor = PredictorService(data_source=k8s_ds, event_publisher=event_publisher)
            strengths = predictor.predict_bond_strength()

            print("\n--- Bond Strength Report ---")
            if not strengths:
                print("No bonds found or data available.")
            else:
                for pair, force in strengths.items():
                    print(f"  - {pair}: {force:.4f}")

        except Exception as e:
            print(f"\nAn error occurred during the demonstration: {e}")
