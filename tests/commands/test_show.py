import pytest
from pathlib import Path
from cli_manager.commands.show import ShowCommand
from cleo.testers.command_tester import CommandTester


@pytest.fixture
def command():
    return ShowCommand()


@pytest.fixture
def command_tester(command):
    return CommandTester(command)


def test_show_no_clis(command_tester, mock_wrapper_dir):
    """Test show command when no CLIs are registered"""
    # Act
    exit_code = command_tester.execute([])
    
    # Assert
    assert exit_code == 0
    assert "No CLIs are registered" in command_tester.io.fetch_output()


def test_show_with_registered_clis(
    command_tester, mock_wrapper_dir, mock_completion_dir
):
    """Test show command with registered CLIs"""
    # Arrange
    wrapper_script = mock_wrapper_dir / "superclisubs"
    wrapper_script.write_text('registered_clis="cli1 cli2"')
    wrapper_script.chmod(0o755)
    
    # Create completion file for cli1
    (mock_completion_dir / "cli1").touch()
    
    # Act
    exit_code = command_tester.execute([])
    output = command_tester.io.fetch_output()
    
    # Assert
    assert exit_code == 0
    assert "cli1" in output
    assert "cli2" in output
    assert "✓ Installed" in output  # cli1 has completion
    assert "✗ Missing" in output    # cli2 has no completion


def test_show_with_check_option(
    command_tester, mock_wrapper_dir, mock_completion_dir, monkeypatch
):
    """Test show command with --check option"""
    # Arrange
    wrapper_script = mock_wrapper_dir / "superclisubs"
    wrapper_script.write_text('registered_clis="cli1 cli2"')
    wrapper_script.chmod(0o755)
    
    # Mock shutil.which to simulate cli1 being available
    def mock_which(cmd):
        return "/usr/bin/cli1" if cmd == "cli1" else None
    monkeypatch.setattr("shutil.which", mock_which)
    
    # Act
    exit_code = command_tester.execute(["--check"])
    output = command_tester.io.fetch_output()
    
    # Assert
    assert exit_code == 0
    assert "Available in PATH" in output
    assert "✓ Available" in output      # cli1 is available
    assert "✗ Not found" in output      # cli2 is not available


def test_show_with_invalid_wrapper(command_tester, mock_wrapper_dir):
    """Test show command with invalid wrapper script"""
    # Arrange
    wrapper_script = mock_wrapper_dir / "superclisubs"
    wrapper_script.write_text('invalid_content')
    
    # Act
    exit_code = command_tester.execute([])
    
    # Assert
    assert exit_code == 0
    assert "No CLIs are registered" in command_tester.io.fetch_output() 