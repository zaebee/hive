import os
import shutil
from click.testing import CliRunner
from genesis_engine.cli import genesis

def test_analyze_bonds_command(mocker):
    """
    Tests the analyze bonds command, mocking the physics engine to avoid
    the need for live service connections in a unit test.
    """
    # Mock the hive-physics services to isolate our CLI logic
    mocker.patch('genesis_engine.analysis.KubernetesDataSource')
    mock_predictor_service = mocker.patch('genesis_engine.analysis.PredictorService')

    # Configure the mock to return predictable bond strength data
    mock_predictor_instance = mock_predictor_service.return_value
    mock_predictor_instance.predict_bond_strength.return_value = {
        "component_a <-> component_b": 123.456,
        "component_b <-> component_c": 789.012,
        "component_d <-> component_e": 555.555, # This bond should be filtered out
    }

    # Set the required environment variable for the check in the command
    mocker.patch.dict(os.environ, {"PROMETHEUS_URL": "http://fake-prometheus:9090"})

    runner = CliRunner()
    domain = 'analysis_domain'
    component_name = 'component_b'

    # Use a try/finally block to ensure component cleanup
    try:
        # 1. Hatch a component to ensure it can be found by the resolver logic
        hatch_result = runner.invoke(
            genesis,
            ['hatch', 'aggregate', component_name, '--domain', domain],
            catch_exceptions=False
        )
        assert hatch_result.exit_code == 0

        # 2. Run the analyze command on the component
        analyze_result = runner.invoke(
            genesis,
            ['analyze', 'bonds', '--component', component_name, '--domain', domain],
            catch_exceptions=False
        )

        # 3. Assert the command ran successfully and printed the correct, filtered output
        assert analyze_result.exit_code == 0
        assert "Bond Strength Report" in analyze_result.output
        # Check that the bonds including our target component are present
        assert "component_a <-> component_b" in analyze_result.output
        assert "component_b <-> component_c" in analyze_result.output
        # Check that the bond NOT including our component is filtered out
        assert "component_d <-> component_e" not in analyze_result.output
        # Check that the values are formatted correctly
        assert "123.4560" in analyze_result.output
        assert "789.0120" in analyze_result.output

        # 4. Verify that the underlying physics services were called
        mock_predictor_service.assert_called_once()
        mock_predictor_instance.predict_bond_strength.assert_called_once()

    finally:
        # Cleanup
        domain_path = os.path.join('hive', 'components', domain)
        if os.path.exists(domain_path):
            shutil.rmtree(domain_path)
