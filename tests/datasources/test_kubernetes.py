import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# It's better to import the modules to be mocked, and then patch them.
from kubernetes import client, config
from hive_physics.datasources.kubernetes import KubernetesDataSource

# Helper functions to create mock Kubernetes API objects
def _create_mock_service(name, namespace, labels):
    """Creates a mock V1Service object with a proper string name."""
    service = MagicMock()
    service.metadata = MagicMock()
    service.metadata.name = name # This is the critical fix
    service.metadata.namespace = namespace
    service.metadata.labels = labels
    return service

def _create_mock_env_var(name, value):
    env_var = MagicMock()
    env_var.name = name
    env_var.value = value
    return env_var

def _create_mock_deployment(env_vars):
    deployment = MagicMock()
    container = MagicMock(env=env_vars)
    deployment.spec = MagicMock()
    deployment.spec.template = MagicMock()
    deployment.spec.template.spec = MagicMock(containers=[container])
    return deployment

@pytest.fixture
def mock_k8s_client(mocker):
    """Mocks the Kubernetes client and its API calls."""
    mocker.patch('kubernetes.config.load_incluster_config', side_effect=config.ConfigException)
    mocker.patch('kubernetes.config.load_kube_config')

    mock_core_v1 = mocker.patch('kubernetes.client.CoreV1Api', autospec=True).return_value
    mock_apps_v1 = mocker.patch('kubernetes.client.AppsV1Api', autospec=True).return_value

    return mock_core_v1, mock_apps_v1

def test_graph_discovery_success(mock_k8s_client):
    """Tests that the graph is correctly discovered from mock K8s resources."""
    mock_core_v1, mock_apps_v1 = mock_k8s_client

    # 1. Setup mock API responses
    mock_core_v1.list_service_for_all_namespaces.return_value.items = [
        _create_mock_service("service-a", "ns1", {"hive-component": "true"}),
        _create_mock_service("service-b", "ns1", {"hive-component": "true"}),
        _create_mock_service("service-c", "ns2", {"hive-component": "true"}),
    ]

    deployment_a = _create_mock_deployment([_create_mock_env_var("B_HOST", "http://service-b:8080")])
    deployment_b = _create_mock_deployment([_create_mock_env_var("C_HOST", "service-c.ns2.svc.cluster.local")])
    deployment_c = _create_mock_deployment([])

    mock_apps_v1.read_namespaced_deployment.side_effect = [deployment_a, deployment_b, deployment_c]

    # 2. Test
    datasource = KubernetesDataSource()
    graph = datasource.get_architectural_graph()

    # 3. Assert
    expected_graph = {
        "service-a": ["service-b"],
        "service-b": ["service-c"],
        "service-c": []
    }
    assert graph == expected_graph

def test_no_hive_services_found(mock_k8s_client):
    """Tests that an empty graph is returned if no services have the hive label."""
    mock_core_v1, _ = mock_k8s_client
    mock_core_v1.list_service_for_all_namespaces.return_value.items = []

    datasource = KubernetesDataSource()
    graph = datasource.get_architectural_graph()

    assert graph == {}

def test_deployment_not_found_is_handled(mock_k8s_client, capsys):
    """Tests that a missing deployment for a service is handled gracefully."""
    mock_core_v1, mock_apps_v1 = mock_k8s_client

    mock_core_v1.list_service_for_all_namespaces.return_value.items = [
        _create_mock_service("service-a", "ns1", {"hive-component": "true"})
    ]
    mock_apps_v1.read_namespaced_deployment.side_effect = client.ApiException(status=404)

    datasource = KubernetesDataSource()
    graph = datasource.get_architectural_graph()

    assert graph == {"service-a": []}
    captured = capsys.readouterr()
    assert "Warning: Deployment for service 'service-a' not found" in captured.out
