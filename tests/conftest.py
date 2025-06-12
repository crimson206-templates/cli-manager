import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_home(monkeypatch):
    """Create a temporary home directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        monkeypatch.setenv("HOME", str(temp_path))
        yield temp_path


@pytest.fixture
def temp_path():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        yield temp_path


@pytest.fixture
def mock_completion_dir(temp_home):
    """Create a temporary completion directory"""
    completion_dir = temp_home / ".completions"
    completion_dir.mkdir(parents=True)
    return completion_dir


@pytest.fixture
def mock_wrapper_dir(temp_home):
    """Create a temporary directory for wrapper script"""
    wrapper_dir = temp_home / ".local" / "bin"
    wrapper_dir.mkdir(parents=True)
    return wrapper_dir 