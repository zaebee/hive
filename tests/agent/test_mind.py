import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mistral_agent.mind import get_llm_suggestion

@pytest.fixture
def sample_config():
    """Provides a sample agent configuration dictionary."""
    return {
        "model": "test-model",
        "temperature": "0.8",
        "max_tokens": "1024",
        "api_key": "test-key",
        "api_base": "https://test.api.base"
    }

def test_get_llm_suggestion_success(mocker, sample_config):
    """Tests a successful LLM call with proper parameter passing."""
    # 1. Setup the mock for litellm.completion within the 'mind' module
    mock_completion = mocker.patch('mistral_agent.mind.litellm.completion')

    # Create a mock response object that mimics the structure of litellm's response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a test suggestion."
    mock_completion.return_value = mock_response

    # 2. Call the function
    prompt = "Test prompt"
    result = get_llm_suggestion(prompt, sample_config)

    # 3. Assert the result
    assert result == "This is a test suggestion."

    # 4. Assert that litellm was called correctly
    mock_completion.assert_called_once()
    call_args = mock_completion.call_args.kwargs
    assert call_args['model'] == 'test-model'
    assert call_args['messages'] == [{"role": "user", "content": prompt}]
    assert call_args['temperature'] == 0.8
    assert call_args['max_tokens'] == 1024
    assert call_args['api_key'] == 'test-key'
    assert call_args['api_base'] == 'https://test.api.base'

def test_llm_api_error(mocker, sample_config):
    """Tests that an exception from the LLM API is propagated."""
    # Setup the mock to raise a generic exception
    mocker.patch('mistral_agent.mind.litellm.completion', side_effect=Exception("Test API Error"))

    with pytest.raises(Exception, match="Test API Error"):
        get_llm_suggestion("prompt", sample_config)

def test_missing_model_in_config():
    """Tests that a ValueError is raised if the model is not in the config."""
    bad_config = {"temperature": "0.5"} # Missing 'model' key
    with pytest.raises(ValueError, match="LLM 'model' not specified in configuration."):
        get_llm_suggestion("prompt", bad_config)

def test_empty_response_from_llm(mocker, sample_config):
    """Tests handling of an empty but successful response from the LLM."""
    mock_completion = mocker.patch('mistral_agent.mind.litellm.completion')

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "" # Empty content
    mock_completion.return_value = mock_response

    result = get_llm_suggestion("prompt", sample_config)
    assert "Error: Received an empty response" in result
