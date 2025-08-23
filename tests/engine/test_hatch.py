import os
import json
import shutil
from click.testing import CliRunner
from genesis_engine.cli import genesis

def test_hatch_aggregate():
    runner = CliRunner()
    domain = 'test_domain'
    component_name = 'test_component'
    output_path = os.path.join('hive', 'components', domain, component_name)

    # Clean up any previous test runs
    if os.path.exists(os.path.join('hive', 'components', domain)):
        shutil.rmtree(os.path.join('hive', 'components', domain))

    try:
        # Run the command
        result = runner.invoke(
            genesis,
            ['hatch', 'aggregate', component_name, '--domain', domain],
            catch_exceptions=False  # So we see the full traceback on errors
        )

        # Check command output and exit code
        assert result.exit_code == 0, result.output
        assert f"Successfully hatched aggregate '{component_name}'" in result.output

        # --- Verification ---
        # 1. Check that all expected files were created
        expected_files = [
            '__init__.py',
            'aggregate.py',
            'commands.py',
            'events.py',
            'tests/__init__.py',
            'tests/test_aggregate.py'
        ]
        for f in expected_files:
            file_path = os.path.join(output_path, f)
            assert os.path.exists(file_path), f"File not found: {file_path}"

        # 2. Check the content of a key file to verify rendering
        with open(os.path.join(output_path, 'aggregate.py'), 'r') as f:
            content = f.read()
            assert 'class TestComponent(AggregateRoot):' in content
            assert 'def _on_test_component_created(self, event: TestComponentCreated):' in content
            assert 'from .events import TestComponentCreated' in content

        # 3. Check the content of the test file
        with open(os.path.join(output_path, 'tests/test_aggregate.py'), 'r') as f:
            content = f.read()
            assert 'from ..aggregate import TestComponent' in content
            assert 'from ..events import TestComponentCreated' in content
            assert 'def test_create_test_component():' in content

        # 4. Check the metadata file
        metadata_path = os.path.join(output_path, '.genesis')
        assert os.path.exists(metadata_path)
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            assert metadata['type'] == 'aggregate'
            assert metadata['name'] == component_name
            assert metadata['domain'] == domain

    finally:
        # Clean up created files
        if os.path.exists(os.path.join('hive', 'components', domain)):
            shutil.rmtree(os.path.join('hive', 'components', domain))
