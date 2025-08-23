import pytest
import sys
import os
import git

# Add the repository root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from hive_physics.datasources.git_history import count_components_at_commit

@pytest.fixture
def git_repo(tmp_path):
    """Creates a temporary git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    repo = git.Repo.init(repo_path)

    # Create the hive_physics directory
    (repo_path / "hive_physics").mkdir()

    # We need to configure a user for the commits
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test User").release()
        cw.set_value("user", "email", "test@example.com").release()

    return repo, repo_path

def test_count_initial_commit(git_repo):
    """Tests counting components in the first commit."""
    repo, repo_path = git_repo

    # Create and commit two component files
    (repo_path / "hive_physics" / "comp1.py").touch()
    (repo_path / "hive_physics" / "comp2.py").touch()
    repo.index.add(["hive_physics/comp1.py", "hive_physics/comp2.py"])
    commit1 = repo.index.commit("Initial commit with 2 components")

    assert count_components_at_commit(str(repo_path), commit1.hexsha) == 2

def test_count_after_adding_components(git_repo):
    """Tests the count after adding more components in a second commit."""
    repo, repo_path = git_repo

    (repo_path / "hive_physics" / "comp1.py").touch()
    repo.index.add(["hive_physics/comp1.py"])
    commit1 = repo.index.commit("Initial commit")

    # Add a new component
    (repo_path / "hive_physics" / "comp3.py").touch()
    repo.index.add(["hive_physics/comp3.py"])
    commit2 = repo.index.commit("Add a third component")

    # The latest commit should have 2 components (comp1.py and comp3.py)
    assert count_components_at_commit(str(repo_path), commit2.hexsha) == 2

def test_count_ignores_non_component_files(git_repo):
    """Tests that non-component files are correctly ignored."""
    repo, repo_path = git_repo

    (repo_path / "hive_physics" / "comp1.py").touch()
    (repo_path / "hive_physics" / "__init__.py").touch() # Should be ignored
    (repo_path / "README.md").touch() # Should be ignored (not in hive_physics)

    # Test that the datasources directory is ignored
    (repo_path / "hive_physics" / "datasources").mkdir()
    (repo_path / "hive_physics" / "datasources" / "helper.py").touch()

    repo.index.add([
        "hive_physics/comp1.py",
        "hive_physics/__init__.py",
        "README.md",
        "hive_physics/datasources/helper.py"
    ])
    commit = repo.index.commit("Add various files")

    assert count_components_at_commit(str(repo_path), commit.hexsha) == 1

def test_count_on_previous_commit(git_repo):
    """Tests that the function correctly inspects the state of a past commit."""
    repo, repo_path = git_repo

    # Commit 1
    (repo_path / "hive_physics" / "comp1.py").touch()
    repo.index.add(["hive_physics/comp1.py"])
    commit1 = repo.index.commit("Initial commit with 1 component")

    # Commit 2
    (repo_path / "hive_physics" / "comp2.py").touch()
    repo.index.add(["hive_physics/comp2.py"])
    commit2 = repo.index.commit("Second commit with 2 components")

    # Check counts at different commits
    assert count_components_at_commit(str(repo_path), commit2.hexsha) == 2
    assert count_components_at_commit(str(repo_path), commit1.hexsha) == 1
