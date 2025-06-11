import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from cli_manager.utils.managed_completion import (
    refresh_cli_completion,
    refresh_all_completions,
    _find_completion_file
)


@pytest.fixture
def mock_completion_dir(tmp_path):
    """Setup mock completion directory"""
    completion_dir = tmp_path / ".completions"
    completion_dir.mkdir()
    return completion_dir


def test_refresh_cli_completion_cli_not_found(mock_completion_dir):
    """Test refreshing completion when CLI is not found"""
    with patch('pathlib.Path.home', return_value=mock_completion_dir.parent):
        with patch('cli_manager.utils.managed_completion.generate_completion') as mock_gen:
            mock_gen.return_value = (None, "CLI not found")
            
            success, messages = refresh_cli_completion("test-cli", "backend")
            
            assert success
            assert "No completion file found" in messages[0]


def test_refresh_cli_completion_remove_existing(mock_completion_dir):
    """Test removing existing completion when CLI is not found"""
    completion_file = mock_completion_dir / "test-cli"
    completion_file.write_text('# META: {"source_cli":"test-cli","backend":"backend"}')
    
    with patch('pathlib.Path.home', return_value=mock_completion_dir.parent):
        with patch('cli_manager.utils.managed_completion.generate_completion') as mock_gen:
            mock_gen.return_value = (None, "CLI not found")
            
            success, messages = refresh_cli_completion("test-cli", "backend")
            
            assert success
            assert "Removed completion" in messages[0]
            assert not completion_file.exists()


def test_refresh_cli_completion_success(mock_completion_dir):
    """Test successful completion refresh"""
    with patch('pathlib.Path.home', return_value=mock_completion_dir.parent):
        with patch('cli_manager.utils.managed_completion.generate_completion') as mock_gen:
            with patch('cli_manager.utils.managed_completion.install_completion') as mock_install:
                mock_gen.return_value = ("completion script", "Generated")
                mock_install.return_value = (True, ["Installed"])
                
                success, messages = refresh_cli_completion(
                    "test-cli",
                    "backend",
                    "wrapper-cli"
                )
                
                assert success
                assert "Installed" in messages[0]


def test_refresh_all_completions_no_dir():
    """Test refresh all when completion directory doesn't exist"""
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/nonexistent')
        
        success, messages = refresh_all_completions("backend")
        
        assert success
        assert "No completions directory found" in messages[0]


def test_refresh_all_completions_mixed_files(mock_completion_dir):
    """Test refresh all with mix of managed and unmanaged files"""
    # Create managed completion file
    managed_file = mock_completion_dir / "managed-cli"
    managed_file.write_text(
        '# META: {"source_cli":"managed-cli","backend":"backend","wrapper_cli":"managed-cli"}'
    )
    
    # Create unmanaged completion file
    unmanaged_file = mock_completion_dir / "unmanaged-cli"
    unmanaged_file.write_text("# Some completion")
    
    with patch('pathlib.Path.home', return_value=mock_completion_dir.parent):
        with patch('cli_manager.utils.managed_completion.refresh_cli_completion') as mock_refresh:
            mock_refresh.return_value = (True, ["Refreshed"])
            
            success, messages = refresh_all_completions("backend")
            
            assert success
            assert mock_refresh.call_count == 1  # Only managed file processed
            mock_refresh.assert_called_with("managed-cli", "backend", None)


def test_find_completion_file(mock_completion_dir):
    """Test finding completion file by CLI name"""
    # Create test completion file
    test_file = mock_completion_dir / "test-cli"
    test_file.write_text(
        '# META: {"source_cli":"test-cli","backend":"backend"}'
    )
    
    result = _find_completion_file(mock_completion_dir, "test-cli")
    
    assert result == test_file


def test_find_completion_file_not_found(mock_completion_dir):
    """Test when completion file is not found"""
    result = _find_completion_file(mock_completion_dir, "nonexistent")
    
    assert result is None 