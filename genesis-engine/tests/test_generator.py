import os
import pytest
from typer.testing import CliRunner
from genesis_engine.main import app
import shutil

runner = CliRunner()

@pytest.fixture(autouse=True)
def cleanup_generated_files():
    """
    This fixture will run after each test function, and it will
    clean up any generated directories.
    """
    yield
    if os.path.exists("aggregates"):
        shutil.rmtree("aggregates")
    if os.path.exists("connectors"):
        shutil.rmtree("connectors")
    if os.path.exists("transformations"):
        shutil.rmtree("transformations")


def test_generate_aggregate():
    result = runner.invoke(
        app,
        [
            "generate",
            "aggregate",
            "test_order",
            "--commands=create,update",
            "--events=created,updated",
        ],
    )
    assert result.exit_code == 0
    assert "Generated aggregates/test_order_aggregate.py" in result.stdout

    filepath = "aggregates/test_order_aggregate.py"
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        content = f.read()
        assert "class TestOrderAggregate" in content
        assert '"create"' in content
        assert '"update"' in content
        assert 'return [self._create_event("created", event_payload)]' in content
        assert 'return [self._create_event("updated", event_payload)]' in content


def test_generate_connector():
    result = runner.invoke(
        app,
        [
            "generate",
            "connector",
            "test_db",
            "--type=secondary",
            "--protocol=db",
        ],
    )
    assert result.exit_code == 0
    assert "Generated connectors/test_db_connector.py" in result.stdout

    filepath = "connectors/test_db_connector.py"
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        content = f.read()
        assert "class TestDbConnector" in content
        assert "secondary" in content
        assert "db" in content


def test_generate_transformation():
    result = runner.invoke(
        app,
        [
            "generate",
            "transformation",
            "test_report",
        ],
    )
    assert result.exit_code == 0
    assert "Generated transformations/test_report_transformation.py" in result.stdout

    filepath = "transformations/test_report_transformation.py"
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        content = f.read()
        assert "class TestReportTransformation" in content
