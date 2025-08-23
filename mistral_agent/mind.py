import litellm
from typing import Dict

# Set a fallback for the logger to avoid a warning if the user hasn't configured it.
# In a real application, you would configure logging properly.
litellm.set_verbose = False

def get_llm_suggestion(prompt: str, config: Dict[str, str]) -> str:
    """
    Communicates with an LLM to get a suggestion based on a prompt.

    This function acts as the "Mind" of the Mistral Agent, taking the
    state report (senses) and using an LLM to "think" of a solution.

    Args:
        prompt: The fully-formatted prompt string from the context generator.
        config: The configuration dictionary parsed from the Mermaid diagram.
                Expected keys include 'model', 'temperature', 'api_key', etc.

    Returns:
        The string content of the LLM's response.

    Raises:
        ValueError: If the required 'model' key is not in the config.
        Exception: Propagates exceptions from the litellm API call.
    """
    if "model" not in config:
        raise ValueError("LLM 'model' not specified in configuration.")

    messages = [{"role": "user", "content": prompt}]

    # Prepare parameters for the litellm call from our config
    # This dynamically builds the keyword arguments for the completion call.
    api_params = {
        "model": config["model"],
        "messages": messages,
        "temperature": float(config.get("temperature", 0.7)),
        "max_tokens": int(config.get("max_tokens", 2048)),
        "api_key": config.get("api_key"),
        "api_base": config.get("api_base")
    }

    # Remove None values so we don't pass them to the API
    api_params = {k: v for k, v in api_params.items() if v is not None}

    print(f"--- Calling LLM (Model: {api_params['model']}) ---")

    try:
        response = litellm.completion(**api_params)

        # Extract the content from the response object
        content = response.choices[0].message.content

        if not content:
            return "Error: Received an empty response from the LLM."

        return content.strip()

    except Exception as e:
        # In a real application, you'd have more specific error handling for different
        # API exceptions (e.g., AuthenticationError, RateLimitError).
        print(f"An error occurred during the LLM API call: {e}")
        raise

if __name__ == '__main__':
    import os
    # This demonstration requires a valid API key for an LLM provider.
    # We will mock this call in the unit tests.
    print("--- Mistral Agent's Mind Demonstration ---")

    # To run this demo:
    # 1. Have an API key for a provider like OpenAI, Anthropic, or Mistral AI.
    # 2. Set it as an environment variable, e.g., `export OPENAI_API_KEY="sk-..."`
    # litellm will automatically detect and use it.

    from mistral_agent.config import parse_mermaid_config

    config_file = 'mistral_agent/config.md'

    # The parser needs the dummy env var to be set for the api_key field in the config
    os.environ['MISTRAL_API_KEY'] = os.environ.get("MISTRAL_API_KEY", "dummy_key_for_parser")

    try:
        llm_config = parse_mermaid_config(config_file)

        # For the live demo, let's override the model to one that litellm can easily access
        # if the corresponding API key is set in the environment.
        if "OPENAI_API_KEY" in os.environ:
             llm_config["model"] = "gpt-3.5-turbo"
             llm_config["api_key"] = os.environ["OPENAI_API_KEY"]
        elif "MISTRAL_API_KEY" != "dummy_key_for_parser":
             llm_config["model"] = "mistral/mistral-tiny"
        else:
            print("\nNo major LLM API key found in environment (e.g., OPENAI_API_KEY).")
            print("The API call will likely fail, which is expected.")
            # We still need a valid model name for litellm to attempt the call
            llm_config["model"] = "gpt-3.5-turbo"


        dummy_prompt = "Explain the concept of 'emergent behavior' in 50 words."

        print(f"\nSending prompt to model '{llm_config.get('model')}'...")

        suggestion = get_llm_suggestion(prompt=dummy_prompt, config=llm_config)

        print("\n--- LLM Response ---")
        print(suggestion)
        print("--------------------")

    except Exception as e:
        print(f"\nDemonstration failed as expected without a valid API key.")
        print(f"Error: {e}")

    # Clean up dummy env var
    if os.environ.get('MISTRAL_API_KEY') == "dummy_key_for_parser":
        del os.environ['MISTRAL_API_KEY']
