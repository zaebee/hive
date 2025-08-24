import os
from mistral_agent.config import parse_mermaid_config
from mistral_agent.context import generate_hive_state_report
from mistral_agent.mind import parse_llm_config, get_llm_suggestion

def transform_component(target_file: str):
    """
    Uses the Mistral Agent to suggest a refactoring for a given file.

    :param target_file: The path to the source code file to be transformed.
    """
    print("Loading Mistral Agent configuration...")
    try:
        # 1. Load configuration from the mistral_agent package
        config_file = 'mistral_agent/config.md'
        if not os.path.exists(config_file):
            print(f"Error: Agent configuration file not found at '{config_file}'")
            return

        raw_config = parse_mermaid_config(config_file)
        llm_config = parse_llm_config(raw_config)
        print(f"Configuration loaded. Using model: {llm_config.model}")

    except Exception as e:
        print(f"Error loading agent configuration: {e}")
        return

    # 2. Prepare arguments for the prompt generator
    component_id = os.path.basename(target_file)
    problem_description = "Refactor the following code for clarity, efficiency, and adherence to Hive best practices. The goal is to improve the code's structure and maintainability."
    # For now, we pass empty physics results as this is a general refactoring task.
    mock_physics_result = {}

    print("Generating state report for LLM...")
    # 3. Generate the prompt
    prompt = generate_hive_state_report(
        component_id=component_id,
        problem_description=problem_description,
        component_code_path=target_file,
        mock_physics_result=mock_physics_result
    )

    print("Sending prompt to the LLM for a refactoring suggestion...")
    # 4. Get the suggestion from the LLM
    try:
        suggestion = get_llm_suggestion(prompt, llm_config)

        print("\n--- AI REFACTORING SUGGESTION ---")
        print(suggestion)
        print("---------------------------------")
        print("\nReview the suggestion above. You can manually apply it to your code.")

    except Exception as e:
        print(f"\nAn error occurred while communicating with the LLM: {e}")
        print("Please check your API keys (e.g., OPENAI_API_KEY) and network connection.")
