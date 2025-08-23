from typing import Dict, List
from kubernetes import client, config

class KubernetesDataSource:
    """
    A data source for discovering the Hive's architectural graph from
    a live Kubernetes cluster.
    """
    def __init__(self):
        """
        Initializes the Kubernetes client. It automatically handles configuration
        for in-cluster or local (kubeconfig) environments.
        """
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException as e:
                raise ConnectionError(f"Could not configure Kubernetes client: {e}")

        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    def get_architectural_graph(self) -> Dict[str, List[str]]:
        """
        Discovers the Hive architectural graph from Kubernetes resources.

        - Nodes: K8s Services with the label 'hive-component=true'. The service
          name is treated as the component ID.
        - Edges: Discovered by inspecting environment variables in the corresponding
          Deployments. If an env var's value contains the name of another Hive
          service, a connection is inferred.

        Returns:
            An adjacency list representation of the graph.
        """
        graph: Dict[str, List[str]] = {}

        # 1. Find all Hive services (nodes)
        services = self.core_v1.list_service_for_all_namespaces(label_selector='hive-component=true').items
        hive_service_names = {s.metadata.name for s in services}

        if not hive_service_names:
            return {}

        for service in services:
            service_name = service.metadata.name
            namespace = service.metadata.namespace

            # Initialize node in graph
            if service_name not in graph:
                graph[service_name] = []

            # 2. Find the corresponding deployment to inspect env vars
            # Heuristic: Assume deployment name matches service name.
            try:
                deployment = self.apps_v1.read_namespaced_deployment(name=service_name, namespace=namespace)

                # 3. Discover connections from environment variables
                for container in deployment.spec.template.spec.containers:
                    if not container.env:
                        continue
                    for env_var in container.env:
                        if env_var.value:
                            # Check if the env var value contains the name of another hive service
                            for other_service in hive_service_names:
                                if other_service != service_name and other_service in env_var.value:
                                    graph[service_name].append(other_service)
            except client.ApiException as e:
                if e.status == 404:
                    print(f"Warning: Deployment for service '{service_name}' not found in namespace '{namespace}'. Cannot scan for connections.")
                else:
                    # Re-raise other API errors
                    raise e

        # Clean up connections (remove duplicates and sort)
        for service_name, connections in graph.items():
            graph[service_name] = sorted(list(set(connections)))

        return graph

if __name__ == '__main__':
    print("--- Kubernetes Data Source Demonstration ---")
    print("This script attempts to connect to a Kubernetes cluster.")
    print("It will use your local kubeconfig or in-cluster service account.")

    try:
        datasource = KubernetesDataSource()
        print("\nSuccessfully connected to Kubernetes.")

        print("\nDiscovering Hive architectural graph...")
        discovered_graph = datasource.get_architectural_graph()

        if not discovered_graph:
            print("\nNo Hive components found (services with label 'hive-component=true').")
        else:
            print("\nDiscovered Graph (Adjacency List):")
            for node, connections in discovered_graph.items():
                print(f"  - {node}: {connections}")

    except (ConnectionError, client.ApiException) as e:
        print(f"\nCould not run demonstration: {e}")
        print("Please ensure you have a valid Kubernetes configuration.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
