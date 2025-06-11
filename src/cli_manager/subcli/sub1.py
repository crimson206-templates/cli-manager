from cleo.application import Application
from cleo.commands.command import Command
from cleo.helpers import argument, option


class ExampleCommand(Command):
    name = "example-command"
    description = "An example command with completion"

    arguments = [argument("file_path", "Path to a file", optional=True)]

    options = [option("type", "t", "Type of operation", flag=False)]

    def handle(self):
        file_path = self.argument("file_path")
        op_type = self.option("type")

        self.line(f"Processing {file_path} with type {op_type}")

    def complete(self, words: list[str], word: str) -> list[str]:
        """
        자동완성 구현

        Args:
            words: 현재까지 입력된 단어들의 리스트
            word: 현재 완성하려는 단어

        Returns:
            가능한 completion 목록
        """
        # command 이름 다음의 첫 번째 argument (file_path)
        if len(words) == 2:
            # 파일 시스템 completion
            from glob import glob

            return [p for p in glob(word + "*") if not p.startswith(".")]

        # --type 옵션의 값
        if len(words) >= 2 and words[-2] == "--type":
            return ["read", "write", "append"]

        return []


def main():
    app = Application()
    app.add(ExampleCommand())
    app.run()


if __name__ == "__main__":
    main()
