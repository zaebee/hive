"""
Unit tests for the 'hands' module of the Mistral Agent.
"""
import pytest
from pathlib import Path
from mistral_agent.hands import apply_code_patch

@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    """Creates a temporary file with some content."""
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Hello, world!\nThis is a test file.\nIt has multiple lines.\n")
    return p

def test_apply_valid_patch(temp_file: Path):
    """Tests that a valid patch is applied correctly."""
    diff = """\
<<<<<<< SEARCH
This is a test file.
It has multiple lines.
=======
This is a modified file.
It has new content.
>>>>>>> REPLACE
"""
    assert apply_code_patch(temp_file, diff) is True
    expected_content = "Hello, world!\nThis is a modified file.\nIt has new content.\n"
    assert temp_file.read_text() == expected_content

def test_search_block_not_found(temp_file: Path):
    """Tests that the function returns False if the SEARCH block is not found."""
    original_content = temp_file.read_text()
    diff = """\
<<<<<<< SEARCH
This content does not exist.
=======
This should not be applied.
>>>>>>> REPLACE
"""
    assert apply_code_patch(temp_file, diff) is False
    assert temp_file.read_text() == original_content

def test_empty_file(tmp_path: Path):
    """Tests that the function handles an empty file correctly."""
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()
    diff = """\
<<<<<<< SEARCH

=======
Some new content.
>>>>>>> REPLACE
"""
    # In this case, the search block is empty, representing an insertion.
    assert apply_code_patch(empty_file, diff) is True
    assert empty_file.read_text() == "Some new content."

def test_empty_diff_string(temp_file: Path):
    """Tests that the function returns False for an empty diff string."""
    original_content = temp_file.read_text()
    assert apply_code_patch(temp_file, "") is False
    assert temp_file.read_text() == original_content

def test_malformed_diff_no_separator(temp_file: Path):
    """Tests that the function handles a diff with no separator."""
    original_content = temp_file.read_text()
    diff = """\
<<<<<<< SEARCH
This is a test file.
It has multiple lines.
>>>>>>> REPLACE
"""
    with pytest.raises(ValueError, match="Separator '=======' not found"):
        apply_code_patch(temp_file, diff)
    assert temp_file.read_text() == original_content

def test_malformed_diff_no_search_header(temp_file: Path):
    """Tests that the function handles a diff with no SEARCH header."""
    original_content = temp_file.read_text()
    diff = """\
This is a test file.
It has multiple lines.
=======
This should not be applied.
>>>>>>> REPLACE
"""
    with pytest.raises(ValueError, match="Header '<<<<<<< SEARCH' not found"):
        apply_code_patch(temp_file, diff)
    assert temp_file.read_text() == original_content

def test_insertion_patch(temp_file: Path):
    """Tests that a patch with an empty SEARCH block inserts content."""
    diff = """\
<<<<<<< SEARCH

=======
This is an insertion.
>>>>>>> REPLACE
"""
    # This is not a valid operation on a non-empty file, should fail.
    assert apply_code_patch(temp_file, diff) is False

def test_deletion_patch(temp_file: Path):
    """Tests that a patch with an empty REPLACE block deletes content."""
    diff = """\
<<<<<<< SEARCH
This is a test file.
It has multiple lines.
=======

>>>>>>> REPLACE
"""
    assert apply_code_patch(temp_file, diff) is True
    assert "This is a test file" not in temp_file.read_text()
    assert temp_file.read_text() == "Hello, world!\n\n"
