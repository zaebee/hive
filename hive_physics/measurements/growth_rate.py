import git
from datetime import datetime, timedelta, timezone
import sys
import os

# Add the repository root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.datasources.git_history import count_components_at_commit

def measure_growth_rate(repo_path: str, days_ago: int = 7) -> float:
    """
    Measures the Hive Growth Rate (Λ_hive) over a given period.

    Formula: Λ_hive = (new_count - old_count) / days

    Args:
        repo_path: The file path to the git repository.
        days_ago: The number of days in the past to compare against.

    Returns:
        The Hive Growth Rate in components per day.
    """
    if days_ago <= 0:
        raise ValueError("days_ago must be a positive integer.")

    repo = git.Repo(repo_path, search_parent_directories=True)

    # 1. Get the current component count
    head_commit = repo.head.commit
    new_count = count_components_at_commit(repo_path, head_commit.hexsha)

    # 2. Find the commit from N days ago
    target_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
    old_commit = None

    # Iterate through commits from HEAD backwards
    for commit in repo.iter_commits(repo.head.commit):
        commit_date = commit.authored_datetime
        if commit_date <= target_date:
            old_commit = commit
            break

    if old_commit is None:
        # If no commit is old enough, we can't measure growth.
        # This might happen in a very new repository.
        # Fallback to the very first commit of the repo.
        old_commit = next(repo.iter_commits(reverse=True))

    # 3. Get the old component count
    old_count = count_components_at_commit(repo_path, old_commit.hexsha)

    # 4. Calculate Lambda_hive
    growth_rate = (new_count - old_count) / days_ago

    return growth_rate

if __name__ == '__main__':
    print("--- Measuring Hive Growth Rate (Λ_hive) ---")

    try:
        repo_dir = '.'
        days = 7

        print(f"Calculating growth rate over the last {days} days...")

        lambda_hive = measure_growth_rate(repo_dir, days)

        print(f"\nCalculated Λ_hive: {lambda_hive:.4f} components/day")

        if lambda_hive > 0.1:
            print("Interpretation: The Hive is in a period of rapid growth.")
        elif lambda_hive > 0:
            print("Interpretation: The Hive is growing slowly and steadily.")
        elif lambda_hive == 0:
            print("Interpretation: The Hive is stable.")
        else:
            print("Interpretation: The Hive is shrinking (refactoring or decommissioning).")

    except Exception as e:
        print(f"An error occurred: {e}")
