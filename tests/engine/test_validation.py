import os
import shutil
from click.testing import CliRunner
from genesis_engine.cli import genesis

def test_validate_command_success():
    """
    Tests the validate command on a component that should pass validation.
    """
    runner = CliRunner()
    domain = 'validation_domain'
    component_name = 'valid_component'
    component_path = os.path.join('hive', 'components', domain, component_name)

    # Clean up from previous runs
    if os.path.exists(os.path.join('hive', 'components', domain)):
        shutil.rmtree(os.path.join('hive', 'components', domain))

    try:
        # 1. Hatch a component that we know has a valid workflow.json
        hatch_result = runner.invoke(
            genesis,
            ['hatch', 'aggregate', component_name, '--domain', domain],
            catch_exceptions=False
        )
        assert hatch_result.exit_code == 0

        # 2. Run the validate command on the new component
        validate_result = runner.invoke(
            genesis,
            ['validate', component_path],
            catch_exceptions=False
        )

        # 3. Assert the validation was successful
        assert validate_result.exit_code == 0
        assert "✅ CONSERVED" in validate_result.output
        assert "✅ All workflows passed validation." in validate_result.output
        assert "❌" not in validate_result.output

    finally:
        # Cleanup
        if os.path.exists(os.path.join('hive', 'components', domain)):
            shutil.rmtree(os.path.join('hive', 'components', domain))

def test_validate_command_failure():
    """
    Tests the validate command on a component with an invalid workflow.
    """
    runner = CliRunner()
    domain = 'validation_domain'
    component_name = 'invalid_component'
    component_path = os.path.join('hive', 'components', domain, component_name)

    # Clean up from previous runs
    if os.path.exists(os.path.join('hive', 'components', domain)):
        shutil.rmtree(os.path.join('hive', 'components', domain))

    try:
        # 1. Hatch a component
        hatch_result = runner.invoke(
            genesis,
            ['hatch', 'aggregate', component_name, '--domain', domain],
            catch_exceptions=False
        )
        assert hatch_result.exit_code == 0

        # 2. Manually overwrite the workflow.json with an invalid one
        invalid_workflow_content = """
        {
            "sample_workflows": {
                "invalid_workflow": {
                    "steps": [{"primitive": "A", "valency": [1, 2]}]
                }
            }
        }
        """
        workflow_path = os.path.join(component_path, 'workflow.json')
        with open(workflow_path, 'w') as f:
            f.write(invalid_workflow_content)

        # 3. Run the validate command
        validate_result = runner.invoke(
            genesis,
            ['validate', component_path],
            catch_exceptions=False
        )

        # 4. Assert the validation failed as expected
        assert validate_result.exit_code == 0
        assert "❌ NOT CONSERVED" in validate_result.output
        assert "❌ Some workflows failed validation." in validate_result.output
        assert "✅ CONSERVED" not in validate_result.output

    finally:
        # Cleanup
        if os.path.exists(os.path.join('hive', 'components', domain)):
            shutil.rmtree(os.path.join('hive', 'components', domain))
