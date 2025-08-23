import pytest
import sys
import os

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from mistral_agent.context import generate_hive_state_report

def test_report_generation(tmp_path):
    """
    Tests that the state report is generated correctly and contains all
    the necessary components.
    """
    # 1. Setup mock inputs
    component_id = "test_component_001"
    problem = "This is a test problem description."

    source_code_content = "def hello_hive():\n    print('Hello from the Hive!')"
    code_file = tmp_path / "test_component.py"
    code_file.write_text(source_code_content)

    mock_physics = {"Bond Strength": 999.9, "Toxicity Score": 15}

    # 2. Generate the report
    report = generate_hive_state_report(
        component_id=component_id,
        problem_description=problem,
        component_code_path=str(code_file),
        mock_physics_result=mock_physics
    )

    # 3. Assert that all key pieces of information are in the report
    assert isinstance(report, str)
    assert component_id in report
    assert problem in report
    assert source_code_content in report
    assert "Bond Strength: 999.9" in report
    assert "Toxicity Score: 15" in report
    assert "MISTRAL AGENT STATE REPORT" in report # Check for template structure
    assert "MISSION: AI-Powered Refactoring" in report

def test_report_generation_with_missing_file():
    """
    Tests that the report generator handles a missing source code file gracefully.
    """
    report = generate_hive_state_report(
        component_id="test_component_002",
        problem_description="File not found test.",
        component_code_path="non/existent/file.py",
        mock_physics_result={"metric": 1}
    )

    assert "Error: Source code file not found" in report
