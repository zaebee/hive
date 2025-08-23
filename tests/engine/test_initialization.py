import os
import shutil
from click.testing import CliRunner
from genesis_engine.cli import genesis

def test_init_command():
    """
    Tests the init command to ensure it creates a new project directory
    with the correct files and rendered content.
    """
    runner = CliRunner()
    project_name = "my_test_hive"

    # Ensure the test area is clean before running
    if os.path.exists(project_name):
        shutil.rmtree(project_name)

    try:
        # 1. Run the init command
        result = runner.invoke(
            genesis,
            ['init', project_name],
            catch_exceptions=False
        )

        # 2. Assert the command was successful
        assert result.exit_code == 0
        assert f"Project '{project_name}' initialized successfully" in result.output

        # 3. Verify that the project directory and key files were created
        assert os.path.isdir(project_name)

        expected_files = [
            '.gitignore',
            'pyproject.toml',
            os.path.join('hive', '.gitkeep')
        ]
        for f in expected_files:
            file_path = os.path.join(project_name, f)
            assert os.path.exists(file_path), f"File not found: {file_path}"

        # 4. Verify the content of the rendered pyproject.toml
        with open(os.path.join(project_name, 'pyproject.toml'), 'r') as f:
            content = f.read()
            assert f'name = "{project_name}"' in content

    finally:
        # Cleanup the created project directory
        if os.path.exists(project_name):
            shutil.rmtree(project_name)
