import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import List, Tuple

from cli_manager.utils.completion_utils import (
    update_cli_completion,
    update_wrapper_completion,
    get_completion_dir,
    remove_cli_completion
)

class TestCompletionUtils:
    @pytest.fixture
    def mock_completion_dir(self, tmp_path: Path) -> Path:
        """Create a temporary completion directory for testing"""
        with patch('cli_manager.utils.completion_utils.get_completion_dir') as mock_dir:
            mock_dir.return_value = tmp_path
            yield tmp_path

    @patch('cli_manager.utils.completion_utils.generate_completion')
    @patch('cli_manager.utils.completion_utils.install_completion')
    def test_update_cli_completion_success(
        self,
        mock_install: MagicMock,
        mock_generate: MagicMock
    ) -> None:
        """Test successful CLI completion update"""
        # Arrange
        mock_generate.return_value = ("test_script", "Generated script")
        mock_install.return_value = (True, ["Installation successful"])
        
        # Act
        success, messages = update_cli_completion("test_cli")
        
        # Assert
        assert success is True
        assert messages == ["Installation successful"]
        mock_generate.assert_called_once_with("test_cli")
        mock_install.assert_called_once_with("test_cli", "test_script")

    @patch('cli_manager.utils.completion_utils.generate_completion')
    def test_update_cli_completion_generation_failure(
        self,
        mock_generate: MagicMock
    ) -> None:
        """Test CLI completion update when generation fails"""
        # Arrange
        mock_generate.return_value = (None, "Generation failed")
        
        # Act
        success, messages = update_cli_completion("test_cli")
        
        # Assert
        assert success is False
        assert messages == ["Generation failed"]

    @patch('cli_manager.utils.completion_utils.add_wrapper_completion')
    @patch('cli_manager.utils.completion_utils.add_meta_to_completion')
    @patch('cli_manager.utils.completion_utils.install_completion')
    def test_update_wrapper_completion_success(
        self,
        mock_install: MagicMock,
        mock_add_meta: MagicMock,
        mock_add_wrapper: MagicMock
    ) -> None:
        """Test successful wrapper completion update"""
        # Arrange
        registered_clis = ["cli1", "cli2"]
        mock_add_wrapper.return_value = "wrapper_script"
        mock_add_meta.return_value = "meta_script"
        mock_install.return_value = (True, ["Wrapper installation successful"])
        
        # Act
        success, messages = update_wrapper_completion(registered_clis)
        
        # Assert
        assert success is True
        assert messages == ["Wrapper installation successful"]
        mock_add_wrapper.assert_called_once_with("superclisubs", "supercli", registered_clis)
        mock_add_meta.assert_called_once_with(
            "supercli",
            "supercli",
            "superclisubs",
            "wrapper_script"
        )
        mock_install.assert_called_once_with("superclisubs", "meta_script")

    def test_get_completion_dir(self) -> None:
        """Test getting completion directory path"""
        # Act
        completion_dir = get_completion_dir()
        
        # Assert
        assert completion_dir == Path.home() / ".completions"
        assert isinstance(completion_dir, Path)

    def test_remove_cli_completion_existing_file(
        self,
        mock_completion_dir: Path
    ) -> None:
        """Test removing existing completion file"""
        # Arrange
        cli_name = "test_cli"
        completion_file = mock_completion_dir / cli_name
        completion_file.touch()
        
        # Act
        success, message = remove_cli_completion(cli_name)
        
        # Assert
        assert success is True
        assert message == f"Removed completion for {cli_name}"
        assert not completion_file.exists()

    def test_remove_cli_completion_non_existing_file(
        self,
        mock_completion_dir: Path
    ) -> None:
        """Test removing non-existing completion file"""
        # Arrange
        cli_name = "non_existing_cli"
        
        # Act
        success, message = remove_cli_completion(cli_name)
        
        # Assert
        assert success is True
        assert message == f"No completion file found for {cli_name}"

    def test_remove_cli_completion_error(
        self,
        mock_completion_dir: Path
    ) -> None:
        """Test error handling when removing completion file"""
        # Arrange
        cli_name = "test_cli"
        completion_file = mock_completion_dir / cli_name
        completion_file.touch()
        
        with patch('pathlib.Path.unlink') as mock_unlink:
            mock_unlink.side_effect = Exception("Test error")
            
            # Act
            success, message = remove_cli_completion(cli_name)
            
            # Assert
            assert success is False
            assert message.startswith(f"Failed to remove completion for {cli_name}")
            assert "Test error" in message 