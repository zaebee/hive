import os
from types import SimpleNamespace
from click.testing import CliRunner
from genesis_engine.cli import genesis

def test_transform_command(mocker):
    """
    Tests the transform command, mocking the entire mistral_agent backend
    to ensure the test is fast, predictable, and makes no external calls.
    """
    # 1. Mock all the functions imported from the mistral_agent package
    mock_parse_config = mocker.patch('genesis_engine.refactoring.parse_mermaid_config')
    mock_parse_llm_config = mocker.patch('genesis_engine.refactoring.parse_llm_config')
    mock_gen_report = mocker.patch('genesis_engine.refactoring.generate_hive_state_report')
    mock_get_suggestion = mocker.patch('genesis_engine.refactoring.get_llm_suggestion')

    # 2. Configure the mocks to return predictable values
    mock_parse_config.return_value = {"model": "mock-model"}
    # The actual config object needs to have a .model attribute for the
    # print statement in the application code.
    mock_llm_config_object = SimpleNamespace(model="mock-model")
    mock_parse_llm_config.return_value = mock_llm_config_object

    mock_prompt = "This is a mock prompt."
    mock_gen_report.return_value = mock_prompt

    mock_suggestion = "<<<<<<< SEARCH\n    pass\n=======\n    # Refactored!\n    pass\n>>>>>>> REPLACE"
    mock_get_suggestion.return_value = mock_suggestion

    runner = CliRunner()

    # 3. Use an isolated filesystem to create a dummy file to transform
    with runner.isolated_filesystem():
        # The code under test expects a config file at a relative path.
        # We must create it in the isolated filesystem for the test to pass.
        os.makedirs('mistral_agent')
        with open('mistral_agent/config.md', 'w') as f:
            f.write("model: mock-model\n")

        dummy_file_name = "legacy_code.py"
        dummy_file_content = "def old_function():\n    pass\n"
        with open(dummy_file_name, "w") as f:
            f.write(dummy_file_content)

        # 4. Run the transform command on the dummy file
        result = runner.invoke(
            genesis,
            ['transform', dummy_file_name],
            catch_exceptions=False
        )

        # 5. Assert that the command ran successfully and printed the suggestion
        assert result.exit_code == 0
        assert "AI REFACTORING SUGGESTION" in result.output
        assert mock_suggestion in result.output

        # 6. Assert that our mocked functions were called correctly
        mock_parse_config.assert_called_once_with('mistral_agent/config.md')
        mock_parse_llm_config.assert_called_once_with({"model": "mock-model"})

        # Assert that the prompt generator was called with the correct arguments
        mock_gen_report.assert_called_once()
        call_args = mock_gen_report.call_args[1] # .call_args is a tuple of (args, kwargs)
        assert call_args['component_id'] == dummy_file_name
        assert call_args['component_code_path'] == dummy_file_name

        # Assert that the suggestion function was called with the mock prompt and config
        mock_get_suggestion.assert_called_once_with(
            mock_prompt,
            mock_llm_config_object
        )
