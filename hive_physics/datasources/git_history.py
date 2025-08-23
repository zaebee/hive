import git
import os

def count_components_at_commit(repo_path: str, commit_hash: str) -> int:
    """
    Scans a repository at a specific commit and counts the "components".

    For this PoC, a "component" is defined as any .py file within the
    'hive_physics' directory, excluding __init__.py files and the CLI example.
    This is a simple heuristic that can be made more sophisticated later.

    Args:
        repo_path: The file path to the git repository.
        commit_hash: The hash of the commit to inspect.

    Returns:
        The number of components found at that commit.
    """
    try:
        # search_parent_directories=True is important for finding .git in parent dirs
        repo = git.Repo(repo_path, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        raise ValueError(f"Path '{repo_path}' is not a valid git repository.")

    commit = repo.commit(commit_hash)
    tree = commit.tree

    component_count = 0

    # We need to recursively traverse the tree to check all files
    for blob in tree.traverse():
        # Heuristic for identifying a component file
        if (
            blob.type == 'blob' and
            blob.path.startswith('hive_physics/') and
            blob.path.endswith('.py') and
            not os.path.basename(blob.path).startswith('__init__') and
            'genesis-cli-integration-example.py' not in blob.path and
            'datasources' not in blob.path
        ):
            component_count += 1

    return component_count

if __name__ == '__main__':
    # This block demonstrates the usage of the function.
    # It inspects the current repository's latest commit.
    print("--- Analyzing Component Count in Current Git Commit ---")

    try:
        # Assumes the script is run from somewhere inside the git repo
        repo_dir = '.'
        repo = git.Repo(repo_dir, search_parent_directories=True)
        latest_commit_hash = repo.head.commit.hexsha

        print(f"Analyzing commit: {latest_commit_hash[:7]}...")

        count = count_components_at_commit(repo_dir, latest_commit_hash)

        print(f"\nFound {count} components in the current HEAD.")
        print("Note: A 'component' is currently defined as a non-__init__ .py file in the 'hive_physics' directory.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure you are running this from within the git repository.")
