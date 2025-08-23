import requests
import os
from typing import Optional

class PrometheusDataSource:
    """
    A data source for fetching Hive metrics from a Prometheus server.
    """
    def __init__(self, api_url: str):
        """
        Initializes the data source and tests the connection to Prometheus.

        Args:
            api_url: The base URL of the Prometheus server (e.g., http://localhost:9090)
        """
        if not api_url:
            raise ValueError("Prometheus API URL cannot be empty.")

        if not api_url.endswith('/api/v1'):
            self.api_url = api_url.rstrip('/') + '/api/v1'
        else:
            self.api_url = api_url

        try:
            # Test connection on initialization by checking the build info
            response = requests.get(f"{self.api_url}/status/buildinfo", timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Could not connect to Prometheus at {api_url}. Error: {e}")

    def get_component_mass(self, component_name: str) -> Optional[float]:
        """
        Fetches the 'mass' of a component from Prometheus.

        'Mass' is defined as the 5-minute rate of commands handled by the component.
        This uses the DNA-Matched Metric: `hive_dna_aggregate_commands_handled_total`.

        Args:
            component_name: The name of the component (e.g., "OrderAggregate").

        Returns:
            The calculated mass (float) or None if no data is found.
        """
        # The PromQL query is based on the dna_matched_metrics_spec.md
        query = f'rate(hive_dna_aggregate_commands_handled_total{{component_name="{component_name}"}}[5m])'

        print(f"Executing PromQL query: {query}")

        try:
            response = requests.get(
                f"{self.api_url}/query",
                params={'query': query},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get('status') == 'success' and result.get('data', {}).get('result'):
                # Get the value from the first (and should be only) result vector
                mass_str = result['data']['result'][0]['value'][1]
                return float(mass_str)
            else:
                # No data found for this component, which is a valid state.
                return None
        except requests.RequestException as e:
            print(f"Error querying Prometheus: {e}")
            return None
        except (KeyError, IndexError, TypeError):
            # Handle cases where the JSON response format is unexpected
            print(f"Unexpected or malformed response from Prometheus for query: {query}")
            return None

if __name__ == '__main__':
    print("--- Prometheus Data Source Demonstration ---")

    # This example requires a running Prometheus instance.
    # We will use mocking to test this properly in the unit tests.
    prometheus_url = os.environ.get("PROMETHEUS_URL", "http://localhost:9090")

    print(f"Attempting to connect to Prometheus at: {prometheus_url}")

    try:
        datasource = PrometheusDataSource(api_url=prometheus_url)
        print("Connection successful.")

        component_to_query = "OrderAggregate"
        print(f"\nQuerying mass for component: '{component_to_query}'...")

        mass = datasource.get_component_mass(component_to_query)

        if mass is not None:
            print(f"  - Successfully retrieved mass: {mass:.4f}")
        else:
            print("  - No data found for this component. This is expected if the component hasn't emitted metrics.")

    except (ValueError, ConnectionError) as e:
        print(f"\nCould not run demonstration: {e}")
        print("Please ensure Prometheus is running and the PROMETHEUS_URL environment variable is set if needed.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
