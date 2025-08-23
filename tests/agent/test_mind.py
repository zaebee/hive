import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mistral_agent.mind import get_llm_suggestion, parse_llm_config, LLMConfig

@pytest.fixture
def sample_config_dict():
    """Provides a sample agent configuration as a dictionary."""
    return {
        "model": "test-model",
        "temperature": "0.8",
        "max_tokens": "1024",
        "api_key": "test-key",
        "api_base": "https://test.api.base"
    }

@pytest.fixture
def sample_llm_config(sample_config_dict):
    """Provides a sample agent configuration as an LLMConfig object."""
    return parse_llm_config(sample_config_dict)

def test_parse_llm_config(sample_config_dict):
    """Tests the parsing helper function."""
    config = parse_llm_config(sample_config_dict)
    assert isinstance(config, LLMConfig)
    assert config.model == "test-model"
    assert config.temperature == 0.8
    assert config.max_tokens == 1024

def test_parse_llm_config_missing_model():
    """Tests that the parser raises an error if the model is missing."""
    with pytest.raises(ValueError, match="LLM 'model' not specified"):
        parse_llm_config({"temp": "0.5"})

def test_get_llm_suggestion_success(mocker, sample_llm_config):
    """Tests a successful LLM call with the refactored service."""
    # 1. Setup the mock for the llm_client
    mock_llm_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a refactored suggestion."
    mock_llm_client.completion.return_value = mock_response

    # 2. Call the function with the injected mock client
    prompt = "Test prompt"
    result = get_llm_suggestion(prompt, sample_llm_config, llm_client=mock_llm_client)

    # 3. Assert the result
    assert result == "This is a refactored suggestion."

    # 4. Assert that the client was called correctly
    mock_llm_client.completion.assert_called_once()
    call_args = mock_llm_client.completion.call_args.kwargs
    assert call_args['model'] == sample_llm_config.model
    assert call_args['temperature'] == sample_llm_config.temperature
    assert call_args['api_key'] == sample_llm_config.api_key

def test_llm_api_error(mocker, sample_llm_config):
    """Tests that an exception from the LLM API is propagated."""
    mock_llm_client = MagicMock()
    mock_llm_client.completion.side_effect = Exception("Test API Error")

    with pytest.raises(Exception, match="Test API Error"):
        get_llm_suggestion("prompt", sample_llm_config, llm_client=mock_llm_client)
