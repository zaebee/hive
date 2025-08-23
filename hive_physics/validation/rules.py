import json
from typing import Tuple

def check_valency_conservation(metrics_file: str, workflow_name: str) -> Tuple[bool, int, int]:
    """
    Checks if a workflow conserves valency.

    According to the Hive's physical laws, in a closed system, the total
    input valency must equal the total output valency. This function
    validates this rule for a given workflow definition.

    Args:
        metrics_file: Path to the JSON file with sample workflow data.
        workflow_name: The name of the workflow to validate.

    Returns:
        A tuple containing:
        - bool: True if valency is conserved, False otherwise.
        - int: The total input valency.
        - int: The total output valency.
    """
    try:
        with open(metrics_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Metrics file not found at {metrics_file}")
        return False, 0, 0

    workflow = data.get("sample_workflows", {}).get(workflow_name)
    if not workflow:
        raise ValueError(f"Workflow '{workflow_name}' not found in mock data.")

    steps = workflow.get("steps", [])
    total_in_valency = 0
    total_out_valency = 0

    for step in steps:
        valency = step.get("valency", [0, 0])
        if isinstance(valency, list) and len(valency) == 2:
            total_in_valency += valency[0]
            total_out_valency += valency[1]

    is_conserved = total_in_valency == total_out_valency
    return is_conserved, total_in_valency, total_out_valency

if __name__ == '__main__':
    mock_file_path = 'hive_physics/data/mock_metrics.json'

    print("--- Validating Valency Conservation in Workflows ---")

    # Test case 1: A balanced workflow
    wf1_name = "OrderPlacement"
    print(f"\nValidating workflow: '{wf1_name}'...")
    conserved1, in1, out1 = check_valency_conservation(mock_file_path, wf1_name)
    print(f"  - Is Conserved: {conserved1}")
    print(f"  - Total Input Valency: {in1}")
    print(f"  - Total Output Valency: {out1}")
    if not conserved1:
        print(f"  - Imbalance: {abs(in1 - out1)}")

    # Test case 2: An unbalanced workflow
    wf2_name = "UnbalancedWorkflow"
    print(f"\nValidating workflow: '{wf2_name}'...")
    conserved2, in2, out2 = check_valency_conservation(mock_file_path, wf2_name)
    print(f"  - Is Conserved: {conserved2}")
    print(f"  - Total Input Valency: {in2}")
    print(f"  - Total Output Valency: {out2}")
    if not conserved2:
        print(f"  - Imbalance: {abs(in2 - out2)}")
