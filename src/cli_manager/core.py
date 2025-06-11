from cleo.application import Application
from cleo.commands.command import Command
from cleo.helpers import argument, option
from cli_manager.autocompletion import CompletionInitCommand


class AddCommand(Command):
    """
    Add command
    """
    name = "add"

    def handle(self):
        self.info("Add command")


class SupercliApplication(Application):
    """
    Supercli application
    """

    def __init__(self):
        super().__init__()
        self.add(AddCommand())
        self.add(CompletionInitCommand())


def main():


    app = SupercliApplication()
    app.run()


if __name__ == "__main__":
    main()