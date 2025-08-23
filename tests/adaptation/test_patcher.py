"""
Unit tests for the patcher module.
"""
import pytest
import os
import subprocess
from pathlib import Path
from hive_physics.adaptation.patcher import apply_patch_with_git

@pytest.fixture
def temp_git_repo(tmp_path):
    """Creates a temporary git repository."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    # Initialize a real git repository
    subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)

    # Change CWD to the repo path for the duration of the test
    original_cwd = Path.cwd()
    os.chdir(repo_path)
    yield repo_path
    os.chdir(original_cwd)


def test_apply_valid_patch(temp_git_repo):
    """Tests that a valid patch is applied correctly."""
    file_to_patch = temp_git_repo / "file1.txt"
    file_to_patch.write_text("hello\n") # Add newline to match git diff behavior

    subprocess.run(['git', 'add', file_to_patch])

    patch_content = """\
--- a/file1.txt
+++ b/file1.txt
@@ -1 +1 @@
-hello
+world
"""
    assert apply_patch_with_git(patch_content) is True
    assert file_to_patch.read_text().strip() == "world"

def test_apply_invalid_patch(temp_git_repo):
    """Tests that an invalid patch fails gracefully."""
    file_to_patch = temp_git_repo / "file1.txt"
    file_to_patch.write_text("hello")

    patch_content = "this is not a valid patch"
    assert apply_patch_with_git(patch_content) is False
    assert file_to_patch.read_text() == "hello"

def test_apply_creation_patch(temp_git_repo):
    """Tests that a patch can create a new file."""
    patch_content = """\
--- /dev/null
+++ b/new_file.txt
@@ -0,0 +1 @@
+new content
"""
    new_file = temp_git_repo / "new_file.txt"
    assert not new_file.exists()
    assert apply_patch_with_git(patch_content) is True
    assert new_file.exists()
    assert new_file.read_text().strip() == "new content"

def test_apply_deletion_patch(temp_git_repo):
    """Tests that a patch can delete a file."""
    file_to_delete = temp_git_repo / "file_to_delete.txt"
    file_to_delete.write_text("to be deleted\n")
    subprocess.run(['git', 'add', file_to_delete])

    patch_content = """\
--- a/file_to_delete.txt
+++ /dev/null
@@ -1 +0,0 @@
-to be deleted
"""
    assert file_to_delete.exists()
    assert apply_patch_with_git(patch_content) is True
    assert not file_to_delete.exists()
