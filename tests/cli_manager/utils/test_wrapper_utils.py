import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, PropertyMock

from cli_manager.utils.wrapper_utils import (
    get_wrapper_script_path,
    generate_wrapper_script,
    update_wrapper_script,
    get_registered_clis
)


def test_get_wrapper_script_path():
    """Test wrapper script path generation"""
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/home/test')
        
        path = get_wrapper_script_path()
        
        assert path == Path('/home/test/.local/bin/superclisubs')


def test_generate_wrapper_script():
    """Test wrapper script content generation"""
    clis = ["cli1", "cli2", "cli3"]
    script = generate_wrapper_script(clis)
    
    # 필수 요소들 확인
    assert '#!/bin/bash' in script
    assert 'registered_clis="cli1 cli2 cli3"' in script
    assert 'if [[ " $registered_clis " =~ " $1 " ]]' in script
    assert '"$@"' in script
    assert 'Unknown command: $1' in script
    assert 'Available commands: $registered_clis' in script


def test_update_wrapper_script_success():
    """Test successful wrapper script update"""
    clis = ["cli1", "cli2"]
    
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/home/test')
        with patch('pathlib.Path.write_text') as mock_write:
            with patch('subprocess.run') as mock_run:
                # Mock parent directory and mkdir
                mock_parent = MagicMock()
                with patch('pathlib.Path.parent', new_callable=PropertyMock) as mock_parent_prop:
                    mock_parent_prop.return_value = mock_parent
                    
                    success, message = update_wrapper_script(clis)
                    
                    assert success
                    assert "Updated wrapper script" in message
                    mock_write.assert_called_once()
                    mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
                    mock_run.assert_called_once_with(
                        ["chmod", "+x", "/home/test/.local/bin/superclisubs"],
                        check=True
                    )


def test_update_wrapper_script_failure():
    """Test wrapper script update failure"""
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/home/test')
        with patch('pathlib.Path.write_text', side_effect=Exception("Test error")):
            success, message = update_wrapper_script(["cli1"])
            
            assert not success
            assert "Failed to update wrapper script" in message


def test_get_registered_clis_success():
    """Test successful registered CLIs retrieval"""
    script_content = '''#!/bin/bash
registered_clis="cli1 cli2 cli3"
some other line
'''
    
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/home/test')
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=script_content):
                clis = get_registered_clis()
                
                assert clis == ["cli1", "cli2", "cli3"]


def test_get_registered_clis_no_file():
    """Test when wrapper script doesn't exist"""
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/home/test')
        with patch('pathlib.Path.exists', return_value=False):
            clis = get_registered_clis()
            
            assert clis == []


def test_get_registered_clis_invalid_format():
    """Test when wrapper script has invalid format"""
    script_content = '''#!/bin/bash
some invalid content
'''
    
    with patch('pathlib.Path.home') as mock_home:
        mock_home.return_value = Path('/home/test')
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text', return_value=script_content):
                clis = get_registered_clis()
                
                assert clis == [] 