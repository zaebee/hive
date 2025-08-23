import os
from typing import Dict, Any

def generate_hive_state_report(
    component_id: str,
    problem_description: str,
    component_code_path: str,
    mock_physics_result: Dict[str, Any]
) -> str:
    """
    Assembles a comprehensive state report for the Mistral Agent.

    This function gathers all necessary context (source code, physics metrics)
    into a single, formatted prompt suitable for an LLM. This forms the
    "Senses" of the agent.

    Args:
        component_id: The ID of the component to focus on.
        problem_description: A natural language description of the problem.
        component_code_path: The file path to the component's source code.
        mock_physics_result: A mock dictionary of physics metrics for this component.

    Returns:
        A formatted string containing the full context report.
    """
    # 1. Read the component's source code
    try:
        with open(component_code_path, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        source_code = f"# Error: Source code file not found at {component_code_path}"

    # 2. Format the physics data into a readable string
    physics_report_lines = [f"- {key}: {value}" for key, value in mock_physics_result.items()]
    physics_report = "\n".join(physics_report_lines)

    # 3. Assemble the final prompt using a clear, structured template
    report = f"""
# MISTRAL AGENT STATE REPORT

## MISSION: AI-Powered Refactoring (Guided Evolution)

An issue has been detected in the Hive. Your task is to analyze the following context and propose a code modification to resolve the issue. The output should be a code block in the git merge-diff format (`<<<<<<< SEARCH`, `=======`, `>>>>>>> REPLACE`).

---

## 1. PROBLEM DESCRIPTION

{problem_description}

---

## 2. TARGET COMPONENT

- **Component ID:** `{component_id}`
- **Source Code Path:** `{component_code_path}`

```python
{source_code}
```

---

## 3. RELEVANT HIVE PHYSICS METRICS

{physics_report}

---

## 4. TASK

Based on all the provided context, generate a code patch in the git merge-diff format to resolve the stated problem.
"""
    return report.strip()

if __name__ == '__main__':
    print("--- Hive State Report Generator Demonstration ---")

    # Define mock inputs for the demonstration
    target_component_id = "comp_002"
    problem = f"High bond strength detected between '{target_component_id}' and its neighbors. This suggests tight coupling that should be reduced."

    # We'll use the coupling predictor's code as an example component to be "refactored"
    code_file = "hive_physics/predictors/coupling.py"

    mock_physics = {
        "Bond Strength (comp_001 <-> comp_002)": 3000.0,
        "Bond Strength (comp_002 <-> comp_003)": 12000.0,
        "Component Type": "Predictor"
    }

    print(f"\nGenerating report for component '{target_component_id}'...")

    # Generate the report
    state_report = generate_hive_state_report(
        component_id=target_component_id,
        problem_description=problem,
        component_code_path=code_file,
        mock_physics_result=mock_physics
    )

    print("\n--- GENERATED STATE REPORT (PROMPT) ---")
    print(state_report)
    print("--------------------------------------")
    print("\nThis report is now ready to be sent to an LLM for 'Guided Evolution'.")
