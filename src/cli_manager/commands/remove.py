from typing import List
from cleo.commands.command import Command
from cleo.helpers import argument, option

from ..utils.wrapper_utils import get_registered_clis, update_wrapper_script
from ..utils.completion_utils import remove_cli_completion


class RemoveCommand(Command):
    name = "remove"
    description = "Remove one or more CLIs from supercli"

    arguments = [
        argument(
            "cli_names",
            "Names of CLIs to remove (space-separated)",
            multiple=True
        )
    ]

    options = [
        option(
            "force",
            "f",
            "Force remove without confirmation",
            flag=True
        )
    ]

    help = """
    The remove command unregisters CLIs from supercli management.
    
    It will:
    1. Remove the CLI from superclisubs wrapper
    2. Remove the completion script
    3. Update the wrapper completion
    
    Example:
        supercli remove mycli
        supercli remove cli1 cli2 cli3
        supercli remove --force mycli
    """

    def handle(self) -> int:
        cli_names: List[str] = self.argument("cli_names")
        force: bool = self.option("force")
        
        # Get currently registered CLIs
        registered_clis = get_registered_clis()
        
        # Confirm removal if not forced
        if not force:
            not_found = [cli for cli in cli_names if cli not in registered_clis]
            to_remove = [cli for cli in cli_names if cli in registered_clis]
            
            if not to_remove:
                self.line("<error>None of the specified CLIs are registered.</error>")
                return 1
                
            if not_found:
                self.line(f"<comment>Note: Following CLIs are not registered: {', '.join(not_found)}</comment>")
            
            # Ask for confirmation
            if not self.confirm(
                f"Are you sure you want to remove these CLIs: {', '.join(to_remove)}?",
                False
            ):
                self.line("<comment>Operation cancelled.</comment>")
                return 0
        
        success_clis: List[str] = []
        failed_clis: List[str] = []
        
        for cli_name in cli_names:
            try:
                if cli_name not in registered_clis:
                    self.line(f"<comment>CLI '{cli_name}' is not registered, skipping.</comment>")
                    continue
                
                # Remove completion script
                success, message = remove_cli_completion(cli_name)
                if not success:
                    self.line(f"<error>{message}</error>")
                    failed_clis.append(cli_name)
                    continue
                
                self.line(f"<info>{message}</info>")
                
                # Remove from registered list
                registered_clis.remove(cli_name)
                success_clis.append(cli_name)
                
            except Exception as e:
                self.line(f"<error>Failed to remove '{cli_name}': {str(e)}</error>")
                failed_clis.append(cli_name)
        
        if success_clis:
            # Update wrapper script with remaining CLIs
            wrapper_success, message = update_wrapper_script(registered_clis)
            if not wrapper_success:
                self.line(f"<error>Warning: Failed to update wrapper script: {message}</error>")
            else:
                self.line(f"<info>{message}</info>")
        
        # Summary
        if success_clis:
            self.line(f"\n<info>Successfully removed {len(success_clis)} CLI(s): {', '.join(success_clis)}</info>")
        if failed_clis:
            self.line(f"<error>Failed to remove {len(failed_clis)} CLI(s): {', '.join(failed_clis)}</error>")
            return 1
            
        return 0 