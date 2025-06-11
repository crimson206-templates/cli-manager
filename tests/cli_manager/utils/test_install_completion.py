import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from cli_manager.utils.install_completion import (
    generate_completion,
    add_wrapper_completion,
    install_completion,
    add_bashrc_loader
)


def test_generate_completion_success():
    """Test successful completion generation"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = "some completion script"
        mock_run.return_value.returncode = 0
        
        script, message = generate_completion("test-cli")
        
        assert script == "some completion script"
        assert "Generated completion for test-cli" in message
        mock_run.assert_called_once_with(
            ["test-cli", "completions", "bash"],
            capture_output=True,
            text=True,
            check=True
        )


def test_generate_completion_command_error():
    """Test completion generation with command error"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "test-cli")
        
        script, message = generate_completion("test-cli")
        
        assert script is None
        assert "Failed to generate completion for test-cli" in message


def test_generate_completion_not_found():
    """Test completion generation with CLI not found"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        
        script, message = generate_completion("test-cli")
        
        assert script is None
        assert "test-cli not found in PATH" in message


def test_add_wrapper_completion():
    """Test adding wrapper completion script"""
    base_completion = "# Original completion"
    wrapper_name = "wrapper-cli"
    cli_name = "original-cli"
    
    result = add_wrapper_completion(base_completion, wrapper_name, cli_name)
    
    assert base_completion in result
    assert wrapper_name in result
    assert cli_name in result
    assert "complete -F" in result


@pytest.fixture
def mock_path(tmp_path):
    """Setup mock paths for testing"""
    completion_dir = tmp_path / ".completions"
    completion_dir.mkdir()
    return tmp_path


def test_install_completion_success(mock_path):
    """Test successful completion installation"""
    with patch('pathlib.Path.home', return_value=mock_path):
        success, messages = install_completion(
            "test-cli",
            "test completion script"
        )
        
        assert success
        assert any("Completion installed" in msg for msg in messages)
        assert (mock_path / ".completions" / "test-cli").exists()


def test_install_completion_with_wrapper(mock_path):
    """Test completion installation with wrapper"""
    with patch('pathlib.Path.home', return_value=mock_path):
        success, messages = install_completion(
            "test-cli",
            "test completion script",
            wrapper_name="wrapper-cli"
        )
        
        assert success
        assert any("Wrapper completion added" in msg for msg in messages)


def test_install_completion_failure():
    """Test completion installation failure"""
    with patch('pathlib.Path.home', side_effect=Exception("Test error")):
        success, messages = install_completion(
            "test-cli",
            "test completion script"
        )
        
        assert not success
        assert "Failed to install completion" in messages[0]


def test_install_completion_existing_dir(mock_path):
    """Test completion installation with existing completion directory"""
    completion_dir = mock_path / ".completions"
    # Directory already exists from fixture
    
    with patch('pathlib.Path.home', return_value=mock_path):
        success, messages = install_completion(
            "test-cli",
            "test completion script"
        )
        
        assert success
        assert any("Completion installed" in msg for msg in messages)
        assert (completion_dir / "test-cli").exists()


def test_add_bashrc_loader_already_exists():
    """Test when loader already exists in .bashrc"""
    mock_content = "existing content\n~/.completions\nmore content"
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/mock/home')
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=mock_content):
                result = add_bashrc_loader()
                assert result is None


def test_add_bashrc_loader_success():
    """Test successful loader addition to .bashrc"""
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/mock/home')
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=""):
                with patch('builtins.open', mock_open()) as mock_file:
                    result = add_bashrc_loader()
                    assert "Added completion loader" in result
                    mock_file.assert_called_once()


def test_add_bashrc_loader_failure():
    """Test loader addition failure"""
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/mock/home')
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=""):
                with patch('builtins.open', side_effect=Exception("Test error")):
                    result = add_bashrc_loader()
                    assert "Failed to add loader to .bashrc" in result 