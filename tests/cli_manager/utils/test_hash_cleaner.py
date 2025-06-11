import pytest
from cli_manager.utils.hash_cleaner import (
    extract_completion_function,
    clean_function_name,
    clean_content
)

def test_extract_completion_function():
    # Test with simple completion function
    content = """
_cli_complete() {
    echo "test"
}
"""
    assert extract_completion_function(content, "cli") == "_cli_complete"

    # Test with hashed completion function
    content = """
_cli_dd335f68b4aa246c_complete() {
    echo "test"
}
"""
    assert extract_completion_function(content, "cli") == "_cli_dd335f68b4aa246c_complete"

    # Test with multiple completion functions
    content = """
_other_complete() {
    echo "other"
}
_cli_complete() {
    echo "test"
}
"""
    assert extract_completion_function(content, "cli") == "_cli_complete"

    # Test with no matching function
    content = """
_other_complete() {
    echo "other"
}
"""
    assert extract_completion_function(content, "cli") is None

    # Test with empty content
    assert extract_completion_function("", "cli") is None

def test_clean_function_name():
    # Test with simple function name
    assert clean_function_name("_cli_complete", "cli") == "_cli_complete"

    # Test with hashed function name
    assert clean_function_name("_cli_dd335f68b4aa246c_complete", "cli") == "_cli_complete"

    # Test with None input
    assert clean_function_name(None, "cli") is None

    # Test with partial CLI name match
    assert clean_function_name("_mycli_dd335f68b4aa246c_complete", "mycli") == "_mycli_complete"


def test_clean_content():
    # Test with simple content
    content = """
_cli_complete() {
    echo "test"
}
"""
    cleaned = clean_content(content, "cli")
    assert cleaned == content

    # Test with hashed content
    content = """
_cli_dd335f68b4aa246c_complete() {
    echo "test"
}
"""
    expected = """
_cli_complete() {
    echo "test"
}
"""
    cleaned = clean_content(content, "cli")
    assert cleaned == expected
    # Test with no completion function
    content = "echo 'no completion here'"
    cleaned = clean_content(content, "cli")
    assert cleaned == content

    # Test with empty content
    cleaned = clean_content("", "cli")
    assert cleaned == ""
