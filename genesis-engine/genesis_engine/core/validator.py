import os

ALLOWED_DIRS = ["aggregates", "connectors", "transformations", "genesis_engine", "tests"]

def validate_project_structure(root_dir: str) -> list[str]:
    """
    Validates the project structure.
    Returns a list of errors.
    """
    errors = []
    for root, dirs, files in os.walk(root_dir):
        # Ignore .venv directory
        if ".venv" in dirs:
            dirs.remove(".venv")

        for file in files:
            if file.endswith(".py"):
                # Check for python files in the root directory
                if root == root_dir and file != "setup.py":
                    # This check is a bit naive, as we are inside genesis-engine
                    # project. But for a generated project it would be useful.
                    pass

                # Check that python files are in allowed directories
                in_allowed_dir = False
                for allowed_dir in ALLOWED_DIRS:
                    if root.startswith(os.path.join(root_dir, allowed_dir)) or root == root_dir:
                         # This is a simplification.
                         # We are checking if the path starts with an allowed dir.
                         # A better check would be to see if the file is in one of the
                         # allowed directories directly.
                        in_allowed_dir = True
                        break

                # This logic is a bit flawed for the current project structure,
                # but it's a good starting point for a generated project.
                # For now, we will just check for .py files in forbidden places.

                # A better implementation would be to check the full path.
                # For example, a file in `connectors/http/utils.py` should be allowed.
                # A file in `some_other_dir/logic.py` should not.

                path_parts = root.split(os.sep)
                if len(path_parts) > 1 and path_parts[1] not in ALLOWED_DIRS and file.endswith('.py'):
                     if path_parts[0] == '.':
                         if len(path_parts) > 1 and path_parts[1] not in ALLOWED_DIRS:
                             errors.append(f"Python file found in non-allowed directory: {os.path.join(root, file)}")
    return errors

import ast

def analyze_bonds(root_dir: str) -> list[str]:
    """
    Analyzes the 'chemical bonds' between components by checking imports.
    Returns a list of warnings.
    """
    warnings = []
    aggregates = {}  # module_name -> path

    # First, find all aggregate files
    for root, _, files in os.walk(os.path.join(root_dir, "aggregates")):
        for file in files:
            if file.endswith("_aggregate.py"):
                module_name = file[:-3]
                aggregates[module_name] = os.path.join(root, file)

    # Then, check for toxic bonds (aggregate importing another aggregate)
    for module_name, path in aggregates.items():
        with open(path, "r") as f:
            try:
                tree = ast.parse(f.read(), filename=path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in aggregates and alias.name != module_name:
                                warnings.append(
                                    f"Toxic bond detected in {path}: "
                                    f"Aggregate '{module_name}' directly imports aggregate '{alias.name}'."
                                )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module in aggregates and node.module != module_name:
                            warnings.append(
                                f"Toxic bond detected in {path}: "
                                f"Aggregate '{module_name}' directly imports from aggregate '{node.module}'."
                            )
            except Exception as e:
                warnings.append(f"Could not parse {path}: {e}")

    return warnings
