"""
Unit tests for the adaptation aggregate.
"""
import pytest
import os
import subprocess
from pathlib import Path
from hive_physics.adaptation.aggregate import AdaptationAggregate, ApplyPatchCommand

@pytest.fixture
def temp_git_repo_for_aggregate(tmp_path):
    """Creates a temporary git repository for aggregate tests."""
    repo_path = tmp_path / "agg_repo"
    repo_path.mkdir()
    subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
    original_cwd = Path.cwd()
    os.chdir(repo_path)
    yield repo_path
    os.chdir(original_cwd)

def test_honey_patch_is_applied(temp_git_repo_for_aggregate):
    """Tests that a beneficial ('honey') patch is applied successfully."""
    file_path = temp_git_repo_for_aggregate / "healthy_code.py"
    # This code has a complexity of 1
    file_path.write_text("def f(a, b):\n    return a + b\n")

    # This patch reduces complexity to 1 (from 2 if it was more complex)
    # But more importantly, it's a valid change.
    patch_content = """\
--- a/healthy_code.py
+++ b/healthy_code.py
@@ -1,2 +1,2 @@
 def f(a, b):
-    return a + b
+    return a * b # A change that doesn't increase toxicity
"""
    aggregate = AdaptationAggregate("test_agg")
    command = ApplyPatchCommand(patch=patch_content)
    events = aggregate._execute_immune_logic(command)

    assert events[0].payload["status"] == "applied"
    assert "return a * b" in file_path.read_text()

def test_poison_patch_is_rejected_and_rolled_back(temp_git_repo_for_aggregate):
    """Tests that a harmful ('poison') patch is rejected and rolled back."""
    file_path = temp_git_repo_for_aggregate / "simple_code.py"
    original_content = "a = 1\n"
    file_path.write_text(original_content)

    # This patch adds a very complex function, increasing toxicity
    patch_content = """\
--- a/simple_code.py
+++ b/simple_code.py
@@ -1 +1,5 @@
-a = 1
+def complex_func(a,b,c,d):
+    if a:
+        if b:
+            if c:
+                if d:
+                    return 1
"""
    aggregate = AdaptationAggregate("test_agg")
    command = ApplyPatchCommand(patch=patch_content)
    events = aggregate._execute_immune_logic(command)

    assert events[0].payload["status"] == "rejected_by_toxicity"
    assert file_path.read_text() == original_content

def test_invalid_patch_is_rejected(temp_git_repo_for_aggregate):
    """Tests that a patch that fails to apply is rejected."""
    file_path = temp_git_repo_for_aggregate / "code.py"
    original_content = "a = 1\n"
    file_path.write_text(original_content)

    patch_content = "this is not a valid patch"
    aggregate = AdaptationAggregate("test_agg")
    command = ApplyPatchCommand(patch=patch_content)
    events = aggregate._execute_immune_logic(command)

    assert events[0].payload["status"] == "rejected_by_git"
    assert file_path.read_text() == original_content

def test_creation_patch_is_applied(temp_git_repo_for_aggregate):
    """Tests that a patch that creates a file is applied."""
    new_file_path = temp_git_repo_for_aggregate / "new_file.py"
    patch_content = """\
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1 @@
+print("hello")
"""
    aggregate = AdaptationAggregate("test_agg")
    command = ApplyPatchCommand(patch=patch_content)
    events = aggregate._execute_immune_logic(command)

    assert events[0].payload["status"] == "applied"
    assert new_file_path.exists()
    assert new_file_path.read_text().strip() == 'print("hello")'

def test_deletion_patch_is_applied(temp_git_repo_for_aggregate):
    """Tests that a patch that deletes a file is applied."""
    file_to_delete = temp_git_repo_for_aggregate / "old_file.py"
    file_to_delete.write_text("to be deleted\n")
    subprocess.run(['git', 'add', file_to_delete])

    patch_content = """\
--- a/old_file.py
+++ /dev/null
@@ -1 +0,0 @@
-to be deleted
"""
    aggregate = AdaptationAggregate("test_agg")
    command = ApplyPatchCommand(patch=patch_content)
    events = aggregate._execute_immune_logic(command)

    assert events[0].payload["status"] == "applied"
    assert not file_to_delete.exists()
