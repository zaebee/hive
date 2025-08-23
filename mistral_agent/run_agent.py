import os
import sys

# Add the repository root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mistral_agent.config import parse_mermaid_config
from mistral_agent.context import generate_hive_state_report
from mistral_agent.mind import get_llm_suggestion

def run_ai_refactoring_task():
    """
    Orchestrates the full "Sense -> Think -> Respond" workflow for the Mistral Agent.
    """
    print("--- 🐝 Initializing Mistral Agent for a 'Guided Evolution' Task 🐝 ---")

    # --- Define Inputs ---
    config_file = 'mistral_agent/config.md'
    target_component_id = "comp_002_OrderAggregate"
    problem = f"High bond strength detected between component '{target_component_id}' and its neighbors. This suggests tight coupling that should be reduced by refactoring."
    # Use a real file from our project as the code to be "refactored"
    code_file = "hive_physics/predictors/coupling.py"
    mock_physics = {
        "Bond Strength (comp_001 <-> comp_002)": 3000.0,
        "Bond Strength (comp_002 <-> comp_003)": 12000.0,
        "Component Type": "Predictor",
        "Recommendation": "Consider introducing an intermediary component or using an event-driven pattern to decouple."
    }

    # --- SENSE PHASE ---
    print("\n[1. SENSE] Parsing configuration and assessing Hive state...")

    # Set dummy env var for parser, in case a real key isn't set for the demo
    # This allows the config parser to succeed even if the key isn't needed for a local model
    os.environ['MISTRAL_API_KEY'] = os.environ.get("MISTRAL_API_KEY", "dummy_key_for_parser")

    try:
        config = parse_mermaid_config(config_file)

        # For a live demo, we can check for a real key and set the model accordingly
        # litellm automatically detects keys from env vars like OPENAI_API_KEY, ANTHROPIC_API_KEY etc.
        if "OPENAI_API_KEY" in os.environ:
             config["model"] = "gpt-4-turbo"

        report = generate_hive_state_report(
            component_id=target_component_id,
            problem_description=problem,
            component_code_path=code_file,
            mock_physics_result=mock_physics
        )
        print("✅ State report generated successfully.")
        # To see the full prompt, uncomment the line below
        # print(report)

    except Exception as e:
        print(f"❌ Error in SENSE phase: {e}")
        return

    # --- THINK PHASE ---
    print("\n[2. THINK] Sending state report to LLM for analysis...")

    try:
        suggestion = get_llm_suggestion(prompt=report, config=config)
        print("✅ AI suggestion received.")
    except Exception as e:
        print(f"❌ Error in THINK phase: {e}")
        print("This is expected if a valid LLM API key is not configured or available.")
        return

    # --- RESPOND PHASE ---
    print("\n[3. RESPOND] Presenting the AI-generated suggestion.")
    print("\n--- AI REFACTORING SUGGESTION ---")
    print(suggestion)
    print("---------------------------------")


if __name__ == '__main__':
    run_ai_refactoring_task()

    # Clean up the dummy environment variable if it was set by this script
    if os.environ.get('MISTRAL_API_KEY') == "dummy_key_for_parser":
        del os.environ['MISTRAL_API_KEY']
