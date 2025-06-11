from cleo.application import Application
from cleo.commands.command import Command
from cleo.helpers import argument, option


class ExampleCommand(Command):
    name = "example-command"
    description = "Example command"

    def handle(self):
        self.info("Example command")


def main():
    app = Application()
    app.add(ExampleCommand())
    app.run()


if __name__ == "__main__":
    main()
