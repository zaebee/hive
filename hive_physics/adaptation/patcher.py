"""
The Patcher module for the Adaptation Engine.

This module uses the `git` command-line tool to apply patches.
"""
import subprocess
import tempfile
from pathlib import Path

def apply_patch_with_git(patch_content: str) -> bool:
    """
    Applies a patch using the `git apply` command.

    Args:
        patch_content: A string containing the patch.

    Returns:
        True if the patch was applied successfully, False otherwise.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.patch') as temp_patch_file:
        temp_patch_file.write(patch_content)
        patch_path = temp_patch_file.name

    try:
        # Use git apply with --check to see if the patch is valid
        check_process = subprocess.run(
            ['git', 'apply', '--check', patch_path],
            capture_output=True, text=True
        )
        if check_process.returncode != 0:
            print(f"Patch is not valid:\n{check_process.stderr}")
            return False

        # If the check passes, apply the patch for real
        apply_process = subprocess.run(
            ['git', 'apply', patch_path],
            capture_output=True, text=True
        )
        if apply_process.returncode != 0:
            print(f"Failed to apply patch:\n{apply_process.stderr}")
            return False

        return True
    finally:
        # Clean up the temporary patch file
        Path(patch_path).unlink()
