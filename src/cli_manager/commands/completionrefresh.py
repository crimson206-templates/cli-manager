from cleo.commands.command import Command
from cleo.helpers import argument

from cli_manager.utils.managed_completion import (
    refresh_cli_completion,
    refresh_all_completions,
)


class CompletionRefreshCommand(Command):
    name = "completion-refresh"
    description = "Refresh bash completions for managed CLIs"

    arguments = [
        argument(
            "cli_name",
            "Name of the CLI to refresh completion for (if not specified, refresh all)",
            optional=True,
        )
    ]

    def handle(self) -> int:
        cli_name = self.argument("cli_name")

        if cli_name:
            # 특정 CLI completion 갱신
            success, messages = refresh_cli_completion(
                cli_name, self.application.name  # backend name으로 app 이름 사용
            )
        else:
            # 모든 completion 갱신
            success, messages = refresh_all_completions(self.application.name)

        # 결과 출력
        for msg in messages:
            if "Removed" in msg:
                self.line(f"<comment>{msg}</comment>")
            elif "Error" in msg or "Failed" in msg:
                self.line(f"<error>{msg}</error>")
            else:
                self.line(f"<info>{msg}</info>")

        return 0 if success else 1
