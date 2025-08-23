import pytest
import sys
import os

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mistral_agent.config import parse_mermaid_config

@pytest.fixture
def temp_config_file(tmp_path):
    """A fixture to create a temporary markdown config file."""
    def _create_file(content):
        config_path = tmp_path / "config.md"
        config_path.write_text(content)
        return str(config_path)
    return _create_file

def test_parsing_success(temp_config_file):
    """Tests successful parsing of a valid config file."""
    content = """
    # Sample Config
    ```mermaid
    graph TD
        A --> B
        classDef style1 model:gpt-4,temperature:0.7
        classDef style2 api_base:https://example.com
    ```
    """
    config_file = temp_config_file(content)
    config = parse_mermaid_config(config_file)
    assert config == {
        "model": "gpt-4",
        "temperature": "0.7",
        "api_base": "https://example.com"
    }

def test_env_var_substitution(temp_config_file, mocker):
    """Tests that environment variables are correctly substituted."""
    # Use mocker to temporarily set an environment variable
    mocker.patch.dict(os.environ, {"MY_API_KEY": "secret-key"})
    content = "classDef secrets api_key:env_MY_API_KEY"
    config_file = temp_config_file(content)
    config = parse_mermaid_config(config_file)
    assert config["api_key"] == "secret-key"

def test_env_var_missing(temp_config_file):
    """Tests that an error is raised for a missing environment variable."""
    content = "classDef secrets api_key:env_MISSING_KEY"
    config_file = temp_config_file(content)
    with pytest.raises(ValueError, match="Required environment variable 'MISSING_KEY' is not set."):
        parse_mermaid_config(config_file)

def test_file_not_found():
    """Tests that an error is raised for a non-existent file."""
    with pytest.raises(FileNotFoundError):
        parse_mermaid_config("non_existent_file.md")

def test_malformed_pairs_are_ignored(temp_config_file):
    """Tests that malformed key-value pairs without a colon are ignored."""
    content = "classDef style key1:val1,malformed-pair,key2:val2"
    config_file = temp_config_file(content)
    config = parse_mermaid_config(config_file)
    assert config == {"key1": "val1", "key2": "val2"}
    assert "malformed-pair" not in config

def test_empty_style_string(temp_config_file):
    """Tests that an empty style string produces an empty dict."""
    content = "classDef empty_style "
    config_file = temp_config_file(content)
    config = parse_mermaid_config(config_file)
    assert config == {}
