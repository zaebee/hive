import litellm
from typing import Dict, Optional, Protocol
import logging
from dataclasses import dataclass

# Configure proper logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMClientProtocol(Protocol):
    def completion(self, **kwargs) -> dict:
        ...

@dataclass
class LLMConfig:
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    api_key: Optional[str] = None
    api_base: Optional[str] = None

def get_llm_suggestion(
    prompt: str,
    config: LLMConfig,
    llm_client: LLMClientProtocol = litellm
) -> str:
    """
    Communicates with an LLM to get a suggestion based on a prompt.

    Args:
        prompt: The fully-formatted prompt string from the context generator.
        config: The configuration object for the LLM call.
        llm_client: The LLM client implementation (default: litellm)

    Returns:
        The string content of the LLM's response.

    Raises:
        ValueError: If the required 'model' is not specified.
        Exception: Propagates exceptions from the LLM API call.
    """
    if not config.model:
        raise ValueError("LLM 'model' not specified in configuration.")

    messages = [{"role": "user", "content": prompt}]

    # Prepare parameters for the LLM call
    api_params = {
        "model": config.model,
        "messages": messages,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "api_key": config.api_key,
        "api_base": config.api_base
    }

    # Remove None values so we don't pass them to the API
    api_params = {k: v for k, v in api_params.items() if v is not None}

    logger.info(f"Calling LLM (Model: {api_params['model']})")

    try:
        response = llm_client.completion(**api_params)

        # Extract the content from the response object
        content = response.choices[0].message.content

        if not content:
            logger.warning("Received an empty response from the LLM")
            return "Error: Received an empty response from the LLM."

        return content.strip()

    except Exception as e:
        logger.error(f"An error occurred during the LLM API call: {e}")
        raise

def parse_llm_config(config_dict: Dict[str, str]) -> LLMConfig:
    """Helper function to parse a dictionary into an LLMConfig object."""
    if "model" not in config_dict:
        raise ValueError("LLM 'model' not specified in configuration dictionary.")
    return LLMConfig(
        model=config_dict.get("model"),
        temperature=float(config_dict.get("temperature", 0.7)),
        max_tokens=int(config_dict.get("max_tokens", 2048)),
        api_key=config_dict.get("api_key"),
        api_base=config_dict.get("api_base")
    )

if __name__ == '__main__':
    import os
    from mistral_agent.config import parse_mermaid_config

    print("--- Mistral Agent's Mind Demonstration (Refactored) ---")

    config_file = 'mistral_agent/config.md'
    os.environ['MISTRAL_API_KEY'] = os.environ.get("MISTRAL_API_KEY", "dummy_key_for_parser")

    try:
        raw_config = parse_mermaid_config(config_file)
        llm_config = parse_llm_config(raw_config)

        if "OPENAI_API_KEY" in os.environ:
             llm_config.model = "gpt-3.5-turbo"
             llm_config.api_key = os.environ["OPENAI_API_KEY"]

        dummy_prompt = "Explain 'autopoiesis' in the context of software in 50 words."

        print(f"\nSending prompt to model '{llm_config.model}'...")

        suggestion = get_llm_suggestion(prompt=dummy_prompt, config=llm_config)

        print("\n--- LLM Response ---")
        print(suggestion)
        print("--------------------")

    except Exception as e:
        print(f"\nDemonstration failed. This is expected without a valid API key.")
        print(f"Error: {e}")

    if os.environ.get('MISTRAL_API_KEY') == "dummy_key_for_parser":
        del os.environ['MISTRAL_API_KEY']
