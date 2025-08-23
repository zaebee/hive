import os
import sys

# Add the repository root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mistral_agent.config import parse_mermaid_config
from mistral_agent.context import generate_hive_state_report
from mistral_agent.mind import get_llm_suggestion, parse_llm_config

def run_self_reflection_task():
    """
    Orchestrates the agent's self-reflection task using the refactored 'Mind'.
    """
    print("--- 🐝 Initializing Mistral Agent for a 'Self-Healing' Task (v2) 🐝 ---")

    # --- Define Inputs for Self-Reflection ---
    config_file = 'mistral_agent/config.md'
    target_component_id = "mistral_agent/mind"
    code_file = "mistral_agent/mind.py"
    problem = f"""
You are the Mistral Agent, a core component of the Hive.
Your task is to perform an act of self-reflection and "Guided Evolution".
Analyze your own source code, provided below, which represents your "Mind".
Based on the core principles of the Hive (modularity, clarity, dependency injection, testability),
propose a refactoring of your own code to improve it.
The output must be a code patch in the git merge-diff format.
"""
    mock_physics = {
        "Task": "Self-Reflection",
        "Target": "mistral_agent/mind.py"
    }

    # --- SENSE PHASE ---
    print("\n[1. SENSE] Parsing configuration and assessing own source code...")

    os.environ['MISTRAL_API_KEY'] = os.environ.get("MISTRAL_API_KEY", "dummy_key_for_parser")

    try:
        raw_config = parse_mermaid_config(config_file)
        # Convert the raw dictionary to the structured LLMConfig object
        llm_config = parse_llm_config(raw_config)

        report = generate_hive_state_report(
            component_id=target_component_id,
            problem_description=problem,
            component_code_path=code_file,
            mock_physics_result=mock_physics
        )
        print("✅ State report generated successfully.")

    except Exception as e:
        print(f"❌ Error in SENSE phase: {e}")
        return

    # --- THINK PHASE ---
    print("\n[2. THINK] Sending self-analysis prompt to LLM...")

    try:
        suggestion = get_llm_suggestion(prompt=report, config=llm_config)
        print("✅ AI self-healing suggestion received.")
    except Exception as e:
        print(f"❌ Error in THINK phase: {e}")
        return

    # --- RESPOND PHASE ---
    print("\n[3. RESPOND] Presenting the AI-generated self-improvement suggestion.")
    print("\n--- AGENT'S PROPOSED EVOLUTION (v2) ---")
    print(suggestion)
    print("--------------------------------------")


if __name__ == '__main__':
    run_self_reflection_task()

    if os.environ.get('MISTRAL_API_KEY') == "dummy_key_for_parser":
        del os.environ['MISTRAL_API_KEY']
