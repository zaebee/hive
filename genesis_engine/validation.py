import os
import json
from hive_physics.validation.rules import check_valency_conservation

def validate_component(target_path: str, ruleset: str):
    """
    Validates a component based on a specified ruleset.

    :param target_path: The path to the component's directory.
    :param ruleset: The ruleset to apply (e.g., 'valency').
    """
    if ruleset != 'valency':
        print(f"Error: Unknown ruleset '{ruleset}'. Only 'valency' is currently supported.")
        return

    workflow_file = os.path.join(target_path, 'workflow.json')
    if not os.path.isfile(workflow_file):
        print(f"Error: No 'workflow.json' found in '{target_path}'. Cannot perform validation.")
        return

    try:
        with open(workflow_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading or parsing '{workflow_file}': {e}")
        return

    workflows = data.get("sample_workflows", {})
    if not workflows:
        print("No workflows found in 'workflow.json'.")
        return

    print(f"--- Validating Valency Conservation in '{os.path.basename(target_path)}' ---")
    all_valid = True
    for name in workflows.keys():
        is_conserved, in_val, out_val = check_valency_conservation(workflow_file, name)

        status = "✅ CONSERVED" if is_conserved else "❌ NOT CONSERVED"
        print(f"\nWorkflow: '{name}'")
        print(f"  - Status: {status}")
        print(f"  - Input Valency: {in_val}")
        print(f"  - Output Valency: {out_val}")
        if not is_conserved:
            all_valid = False
            print(f"  - Imbalance: {abs(in_val - out_val)}")

    print("\n--- Validation Summary ---")
    if all_valid:
        print("✅ All workflows passed validation.")
    else:
        print("❌ Some workflows failed validation.")
