import os
import pytest
import shutil
from genesis_engine.core.validator import validate_project_structure, analyze_bonds

@pytest.fixture(autouse=True)
def cleanup_generated_files():
    """
    This fixture will run after each test function, and it will
    clean up any generated directories.
    """
    yield
    if os.path.exists("forbidden"):
        shutil.rmtree("forbidden")
    if os.path.exists("aggregates"):
        shutil.rmtree("aggregates")

def test_validate_project_structure():
    # Test with no errors
    errors = validate_project_structure(".")
    assert len(errors) == 0

    # Test with an error
    os.makedirs("forbidden", exist_ok=True)
    with open("forbidden/logic.py", "w") as f:
        f.write("print('hello')")

    errors = validate_project_structure(".")
    assert len(errors) > 0
    assert "forbidden/logic.py" in errors[0]

def test_analyze_bonds():
    # Test with no toxic bonds
    warnings = analyze_bonds(".")
    assert len(warnings) == 0

    # Test with a toxic bond
    os.makedirs("aggregates", exist_ok=True)
    with open("aggregates/agg1_aggregate.py", "w") as f:
        f.write("import agg2_aggregate")
    with open("aggregates/agg2_aggregate.py", "w") as f:
        f.write("# empty")

    warnings = analyze_bonds(".")
    assert len(warnings) > 0
    assert "Toxic bond detected" in warnings[0]
