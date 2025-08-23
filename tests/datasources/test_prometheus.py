import pytest
import requests
import sys
import os

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.datasources.prometheus import PrometheusDataSource

PROMETHEUS_URL = "http://fake-prometheus:9090"

def test_init_success(mocker):
    """Tests successful initialization and connection check."""
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.get", return_value=mock_response)

    datasource = PrometheusDataSource(api_url=PROMETHEUS_URL)
    assert datasource.api_url == f"{PROMETHEUS_URL}/api/v1"
    requests.get.assert_called_once_with(f"{PROMETHEUS_URL}/api/v1/status/buildinfo", timeout=5)

def test_init_connection_error(mocker):
    """Tests that a ConnectionError is raised if Prometheus is unreachable."""
    mocker.patch("requests.get", side_effect=requests.RequestException("Test connection error"))

    with pytest.raises(ConnectionError, match="Could not connect to Prometheus"):
        PrometheusDataSource(api_url=PROMETHEUS_URL)

def test_get_component_mass_success(mocker):
    """Tests successfully fetching and parsing a component's mass."""
    # This mock is for the __init__ call
    init_mock_response = mocker.Mock()
    init_mock_response.raise_for_status.return_value = None

    # This mock is for the query call
    query_mock_response = mocker.Mock()
    query_mock_response.raise_for_status.return_value = None
    query_mock_response.json.return_value = {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": [{"metric": {}, "value": [1672531200, "123.45"]}]
        }
    }
    mocker.patch("requests.get", side_effect=[init_mock_response, query_mock_response])

    datasource = PrometheusDataSource(api_url=PROMETHEUS_URL)
    mass = datasource.get_component_mass("OrderAggregate")

    assert mass == 123.45

    # Check that the query call was made correctly
    expected_query = 'rate(hive_dna_aggregate_commands_handled_total{component_name="OrderAggregate"}[5m])'
    # The last call to requests.get should be the query
    requests.get.assert_called_with(f"{datasource.api_url}/query", params={'query': expected_query}, timeout=10)

def test_get_component_mass_no_data(mocker):
    """Tests the case where Prometheus has no data for the component."""
    init_mock_response = mocker.Mock()
    init_mock_response.raise_for_status.return_value = None

    query_mock_response = mocker.Mock()
    query_mock_response.raise_for_status.return_value = None
    query_mock_response.json.return_value = {
        "status": "success",
        "data": {"resultType": "vector", "result": []} # Empty result
    }
    mocker.patch("requests.get", side_effect=[init_mock_response, query_mock_response])

    datasource = PrometheusDataSource(api_url=PROMETHEUS_URL)
    mass = datasource.get_component_mass("NonExistentComponent")

    assert mass is None

def test_get_component_mass_query_error(mocker):
    """Tests that a network error during query returns None."""
    init_mock_response = mocker.Mock()
    init_mock_response.raise_for_status.return_value = None

    # The second call (the query) will raise an exception
    mocker.patch("requests.get", side_effect=[
        init_mock_response,
        requests.RequestException("Query failed")
    ])

    datasource = PrometheusDataSource(api_url=PROMETHEUS_URL)
    mass = datasource.get_component_mass("AnyComponent")

    assert mass is None
