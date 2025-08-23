import os
import sys
import re
from pathlib import Path
from typing import Optional

# Add the repository root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mistral_agent.config import parse_mermaid_config
from mistral_agent.context import generate_hive_state_report
from mistral_agent.mind import get_llm_suggestion, parse_llm_config
from mistral_agent.hands import apply_code_patch

def extract_diff_from_suggestion(suggestion: str) -> Optional[str]:
    """
    Extracts a git merge-diff block from the LLM's suggestion text.
    Handles markdown code blocks.
    """
    # Regex to find the diff block, including the markdown ```diff wrapper
    diff_pattern = re.compile(r"```diff\n(<<<<<<< SEARCH.*>>>>>>> REPLACE)```", re.DOTALL)
    match = diff_pattern.search(suggestion)
    if match:
        return match.group(1).strip()

    # Fallback for plain diff without markdown wrapper
    diff_pattern_plain = re.compile(r"(<<<<<<< SEARCH.*>>>>>>> REPLACE)", re.DOTALL)
    match_plain = diff_pattern_plain.search(suggestion)
    if match_plain:
        return match_plain.group(1).strip()

    return None


def run_self_reflection_task():
    """
    Orchestrates the agent's full Sense-Think-Act loop.
    """
    print("--- 🐝 Initializing Mistral Agent for a 'Self-Healing' Task (v3) 🐝 ---")

    # --- Define Inputs for Self-Reflection ---
    config_file = 'mistral_agent/config.md'
    target_component_id = "mistral_agent/mind"
    code_file = Path("mistral_agent/mind.py")
    problem = f"""
You are the Mistral Agent, a core component of the Hive.
Your task is to perform an act of self-reflection and "Guided Evolution".
Analyze your own source code, provided below, which represents your "Mind".
Based on the core principles of the Hive (modularity, clarity, dependency injection, testability),
propose a refactoring of your own code to improve it.
The output must be a code patch in the git merge-diff format, inside a markdown block.
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
        llm_config = parse_llm_config(raw_config)

        report = generate_hive_state_report(
            component_id=target_component_id,
            problem_description=problem,
            component_code_path=str(code_file),
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
        print("\n--- AGENT'S PROPOSED EVOLUTION ---")
        print(suggestion)
        print("------------------------------------")
    except Exception as e:
        print(f"❌ Error in THINK phase: {e}")
        return

    # --- ACT PHASE ---
    print("\n[3. ACT] Applying the AI-generated patch...")

    diff_block = extract_diff_from_suggestion(suggestion)

    if not diff_block:
        print("❌ Could not find a valid diff block in the LLM's suggestion.")
        return

    try:
        if apply_code_patch(code_file, diff_block):
            print(f"✅ Patch successfully applied to '{code_file}'.")
        else:
            print("❌ Patch application failed. The 'SEARCH' block was likely not found.")

    except Exception as e:
        print(f"❌ Error in ACT phase: {e}")


if __name__ == '__main__':
    run_self_reflection_task()

    if "dummy_key_for_parser" in os.environ.get('MISTRAL_API_KEY', ''):
        del os.environ['MISTRAL_API_KEY']
