from cleo.commands.command import Command
from cleo.helpers import argument, option

from cli_manager.utils.install_completion import (
    generate_completion,
    add_wrapper_completion,
    install_completion,
)
from cli_manager.utils.meta_parser import add_meta_to_completion


class CompletionInitCommand(Command):
    name = "completion-init"
    description = "Install bash completion for any CLI to ~/.completions/"

    arguments = [
        argument("cli_name", "Name of the CLI to install completion for", optional=True)
    ]

    options = [
        option("wrapper", "w", "Also setup completion for a wrapper script", flag=False)
    ]

    def handle(self) -> int:
        # CLI 이름 결정
        cli_name = self.argument("cli_name") or self.application.name
        wrapper_name = self.option("wrapper")

        # completion 생성
        completion_script, message = generate_completion(cli_name)
        if completion_script:
            self.line(f"<comment>{message}</comment>")
        else:
            self.line(f"<error>{message}</error>")
            return 1

        # wrapper completion도 필요하면 추가
        if wrapper_name:
            completion_script = add_wrapper_completion(
                completion_script, wrapper_name, cli_name
            )

        # meta 정보 추가
        completion_script = add_meta_to_completion(
            self.application.name,  # backend name으로 app 이름 사용
            cli_name,
            wrapper_name or cli_name,
            completion_script,
        )

        # 설치
        success, messages = install_completion(
            cli_name, completion_script, wrapper_name
        )

        if success:
            for msg in messages:
                if msg.startswith("✅"):
                    self.line(f"<info>{msg}</info>")
                elif msg.startswith("Added completion loader"):
                    self.line(f"<info>{msg}</info>")
                else:
                    self.line(f"<comment>{msg}</comment>")
            return 0
        else:
            for msg in messages:
                self.line(f"<error>{msg}</error>")
            return 1
