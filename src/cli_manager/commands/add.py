from typing import List
from cleo.commands.command import Command
from cleo.helpers import argument, option

from ..utils.wrapper_utils import get_registered_clis, update_wrapper_script
from ..utils.managed_completion import refresh_cli_completion


class AddCommand(Command):
    name = "add"
    description = "Add one or more CLIs to supercli"

    arguments = [
        argument("cli_names", "Names of CLIs to add (space-separated)", multiple=True)
    ]

    options = [option("force", "f", "Force add even if CLI already exists", flag=True)]

    help = """
    The add command registers new CLIs to be managed by supercli.
    
    It will:
    1. Register the CLI in superclisubs wrapper
    2. Generate and install completion script
    3. Update the wrapper completion
    
    Example:
        supercli add mycli
        supercli add cli1 cli2 cli3
        supercli add --force existingcli
    """

    def handle(self) -> int:
        cli_names: List[str] = self.argument("cli_names")
        force: bool = self.option("force")

        success_clis: List[str] = []
        failed_clis: List[str] = []

        # Get currently registered CLIs
        registered_clis = get_registered_clis()

        for cli_name in cli_names:
            # Check if CLI already exists
            if cli_name in registered_clis and not force:
                self.line(
                    f"<error>CLI '{cli_name}' is already registered. Use --force to override.</error>"
                )
                failed_clis.append(cli_name)
                continue

            try:
                # Update completion for the CLI
                completion_success, messages = refresh_cli_completion(
                    cli_name=cli_name,
                    backend_name="supercli",
                    wrapper_name="superclisubs",
                )

                if not completion_success:
                    self.line(
                        f"<error>Failed to update completion for '{cli_name}': {messages[0]}</error>"
                    )
                    failed_clis.append(cli_name)
                    continue

                # Add to success list if not already registered
                if cli_name not in registered_clis:
                    registered_clis.append(cli_name)

                success_clis.append(cli_name)
                self.line(f"<info>Successfully added '{cli_name}'</info>")

                # Show completion messages
                for msg in messages:
                    self.line(f"  <comment>{msg}</comment>")

            except Exception as e:
                self.line(f"<error>Failed to add '{cli_name}': {str(e)}</error>")
                failed_clis.append(cli_name)

        if success_clis:
            # Update wrapper script with all registered CLIs
            wrapper_success, message = update_wrapper_script(registered_clis)
            if not wrapper_success:
                self.line(
                    f"<error>Warning: Failed to update wrapper script: {message}</error>"
                )
            else:
                self.line(f"<info>{message}</info>")

        # Summary
        if success_clis:
            self.line(
                f"\n<info>Successfully added {len(success_clis)} CLI(s): {', '.join(success_clis)}</info>"
            )
        if failed_clis:
            self.line(
                f"<error>Failed to add {len(failed_clis)} CLI(s): {', '.join(failed_clis)}</error>"
            )
            return 1

        return 0
