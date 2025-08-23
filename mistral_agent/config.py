import re
import os
from typing import Dict

def parse_mermaid_config(file_path: str) -> Dict[str, str]:
    """
    Parses a Markdown file to extract configuration from Mermaid classDef styles.

    This unique configuration loader treats the style definitions in a Mermaid
    diagram as a source of key-value pairs.

    Example `classDef` line:
    `classDef agent-secrets api_key:env_MISTRAL_API_KEY,model:gpt-4`

    This would be parsed into:
    { "api_key": "value_of_MISTRAL_API_KEY_env_var", "model": "gpt-4" }

    Args:
        file_path: The path to the markdown file containing the Mermaid diagram.

    Returns:
        A dictionary containing all parsed configuration values.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If an environment variable specified with 'env_' is not set.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found at: {file_path}")

    with open(file_path, 'r') as f:
        content = f.read()

    config_dict = {}

    # Regex to find all `classDef` lines and capture the style definition part
    pattern = re.compile(r'^\s*classDef\s+[\w-]+\s+(.*)$', re.MULTILINE)
    matches = pattern.findall(content)

    for style_string in matches:
        # Split by comma to get key-value pairs
        pairs = style_string.strip().split(',')
        for pair in pairs:
            if ':' not in pair:
                continue

            key, value = pair.split(':', 1)
            key = key.strip()
            value = value.strip()

            # Check for environment variable substitution
            if value.startswith('env_'):
                env_var_name = value[4:]
                env_value = os.environ.get(env_var_name)
                if env_value is None:
                    raise ValueError(f"Required environment variable '{env_var_name}' is not set.")
                config_dict[key] = env_value
            else:
                config_dict[key] = value

    return config_dict

if __name__ == '__main__':
    # Demonstrate the parser with the sample config file.
    # We need to set a dummy environment variable for the test to pass.
    print("--- Mermaid Config Parser Demonstration ---")

    config_file = 'mistral_agent/config.md'

    # Set a dummy API key for the demonstration
    dummy_key = "sk-1234567890abcdef"
    os.environ['MISTRAL_API_KEY'] = dummy_key
    print(f"Set dummy environment variable MISTRAL_API_KEY='{dummy_key}'")

    try:
        print(f"\nParsing config file: '{config_file}'...")
        config = parse_mermaid_config(config_file)

        print("\nSuccessfully parsed configuration:")
        for key, val in config.items():
            # Censor the API key for printing
            printable_val = '********' if 'key' in key else val
            print(f"  - {key}: {printable_val}")

        # Example assertion
        assert config['model'] == 'gpt-4-turbo'
        assert config['api_key'] == dummy_key
        print("\nAssertions passed.")

    except (FileNotFoundError, ValueError) as e:
        print(f"\nAn error occurred: {e}")

    # Clean up the environment variable
    del os.environ['MISTRAL_API_KEY']
