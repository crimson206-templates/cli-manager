import pytest
from pathlib import Path
from cli_manager.commands.add import AddCommand
from cleo.testers.command_tester import CommandTester


@pytest.fixture
def command():
    return AddCommand()


@pytest.fixture
def command_tester(command):
    return CommandTester(command)


@pytest.fixture
def mock_cli(tmp_path):
    """Create a mock CLI executable"""
    cli_path = tmp_path / "mock_cli"
    cli_path.write_text("#!/bin/bash\necho 'some completion'")
    cli_path.chmod(0o755)
    return cli_path


def test_add_single_cli(
    command_tester, mock_wrapper_dir, mock_completion_dir, monkeypatch, mock_cli
):
    """Test adding a single CLI"""
    # Arrange
    monkeypatch.setenv("PATH", str(mock_cli.parent))
    cli_name = mock_cli.name

    # Act
    exit_code = command_tester.execute([cli_name])
    output = command_tester.io.fetch_output()

    # Assert
    assert exit_code == 0
    assert "Successfully" in output
    assert cli_name in output

    # Check wrapper script
    wrapper_script = mock_wrapper_dir / "superclisubs"
    assert wrapper_script.exists()
    assert cli_name in wrapper_script.read_text()


def test_add_multiple_clis(
    command_tester, mock_wrapper_dir, mock_completion_dir, monkeypatch, tmp_path
):
    """Test adding multiple CLIs at once"""
    # Arrange
    cli_names = ["cli1", "cli2"]
    for cli in cli_names:
        cli_path = tmp_path / cli
        cli_path.write_text("#!/bin/bash\necho 'some completion'")
        cli_path.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))

    # Act
    exit_code = command_tester.execute(cli_names)
    output = command_tester.io.fetch_output()

    # Assert
    assert exit_code == 0
    for cli in cli_names:
        assert cli in output
    assert "Successfully" in output

    # Check wrapper script
    wrapper_script = mock_wrapper_dir / "superclisubs"
    content = wrapper_script.read_text()
    for cli in cli_names:
        assert cli in content


def test_add_nonexistent_cli(command_tester, mock_wrapper_dir):
    """Test adding a CLI that doesn't exist. It doesn't raise an error. User can check them instead."""
    # Act
    exit_code = command_tester.execute(["nonexistent_cli"])
    output = command_tester.io.fetch_output()

    # Assert
    assert exit_code == 0
    assert "added" in output


def test_add_existing_cli_without_force(
    command_tester, mock_wrapper_dir, mock_completion_dir, monkeypatch, mock_cli
):
    """Test adding an already registered CLI without --force"""
    # Arrange
    monkeypatch.setenv("PATH", str(mock_cli.parent))
    cli_name = mock_cli.name

    # Add CLI first time
    command_tester.execute([cli_name])

    # Act - try to add again
    exit_code = command_tester.execute([cli_name])
    output = command_tester.io.fetch_output()

    # Assert
    assert exit_code == 1
    assert "already registered" in output


def test_add_existing_cli_with_force(
    command_tester, mock_wrapper_dir, mock_completion_dir, monkeypatch, mock_cli
):
    """Test adding an already registered CLI with --force"""
    # Arrange
    monkeypatch.setenv("PATH", str(mock_cli.parent))
    cli_name = mock_cli.name

    # Add CLI first time
    command_tester.execute([cli_name])

    # Act - add again with force
    exit_code = command_tester.execute([cli_name, "--force"])
    output = command_tester.io.fetch_output()

    # Assert
    assert exit_code == 0
    assert "Successfully" in output
    assert cli_name in output


def test_add_mixed_success_failure(
    command_tester, mock_wrapper_dir, mock_completion_dir, monkeypatch, mock_cli
):
    """Test adding mixed existing and non-existing CLIs. No error should be raised."""
    # Arrange
    monkeypatch.setenv("PATH", str(mock_cli.parent))
    cli_name = mock_cli.name

    # First add cli1 to make it fail on second try
    command_tester.execute([cli_name])

    # Act - try to add both (one exists, one doesn't)
    exit_code = command_tester.execute([cli_name, "nonexistent_cli"])
    output = command_tester.io.fetch_output()

    # Assert
    assert exit_code == 0
    assert "Failed" in output
    assert cli_name in output
    assert "nonexistent_cli" in output
