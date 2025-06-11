from typing import List, Dict
import shutil
from pathlib import Path
from cleo.commands.command import Command
from cleo.helpers import option
from cleo.ui.table import Table
import os

from ..utils.wrapper_utils import get_registered_clis, get_wrapper_script_path
from ..utils.completion_utils import get_completion_dir


class ShowCommand(Command):
    name = "show"
    description = "Show registered CLIs and their status"
    
    options = [
        option(
            "check",
            "c",
            "Check if registered CLIs are actually available in PATH",
            flag=True
        )
    ]
    
    help = """
    The show command displays all registered CLIs and their status.
    
    It shows:
    - CLI name
    - Completion script status
    - CLI availability in PATH (with --check option)
    
    Example:
        supercli show
        supercli show --check
    """
    
    def handle(self) -> int:
        check_availability: bool = self.option("check")
        registered_clis = get_registered_clis()
        
        if not registered_clis:
            self.line("<comment>No CLIs are registered.</comment>")
            return 0
            
        # Get completion status for all CLIs
        completion_dir = get_completion_dir()
        completion_status = self._get_completion_status(registered_clis, completion_dir)
        
        # Get CLI availability if requested
        cli_availability = {}
        if check_availability:
            cli_availability = self._check_cli_availability(registered_clis)
        
        # Create and configure table
        table = Table(self.io)
        headers = ["CLI", "Completion Status"]
        if check_availability:
            headers.append("Available in PATH")
        table.set_headers(headers)
        
        # Add rows
        for cli in registered_clis:
            row = [
                cli,
                self._format_completion_status(completion_status[cli])
            ]
            if check_availability:
                row.append(self._format_availability(cli_availability[cli]))
            table.add_row(row)
        
        # Show wrapper script status
        wrapper_path = get_wrapper_script_path()
        self.line(f"\n<info>Wrapper script status:</info>")
        if wrapper_path.exists():
            self.line(f"  Location: {wrapper_path}")
            if not wrapper_path.is_file():
                self.line("  <error>Warning: Wrapper script exists but is not a file</error>")
            elif not os.access(wrapper_path, os.X_OK):
                self.line("  <error>Warning: Wrapper script exists but is not executable</error>")
        else:
            self.line("  <error>Warning: Wrapper script does not exist</error>")
        
        # Show completion directory status
        self.line(f"\n<info>Completion directory status:</info>")
        if completion_dir.exists():
            self.line(f"  Location: {completion_dir}")
            if not completion_dir.is_dir():
                self.line("  <error>Warning: Completion path exists but is not a directory</error>")
        else:
            self.line("  <error>Warning: Completion directory does not exist</error>")
        
        # Render table
        self.line("\n<info>Registered CLIs:</info>")
        table.render()
        
        return 0
    
    def _get_completion_status(
        self, clis: List[str], completion_dir: Path
    ) -> Dict[str, bool]:
        """Check completion script status for each CLI"""
        status = {}
        for cli in clis:
            completion_file = completion_dir / cli
            status[cli] = completion_file.is_file()
        return status
    
    def _check_cli_availability(self, clis: List[str]) -> Dict[str, bool]:
        """Check if CLIs are available in PATH"""
        status = {}
        for cli in clis:
            status[cli] = shutil.which(cli) is not None
        return status
    
    def _format_completion_status(self, status: bool) -> str:
        """Format completion status for display"""
        return "<info>✓ Installed</info>" if status else "<error>✗ Missing</error>"
    
    def _format_availability(self, available: bool) -> str:
        """Format CLI availability for display"""
        return "<info>✓ Available</info>" if available else "<error>✗ Not found</error>" 