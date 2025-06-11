from cleo.application import Application
from cli_manager.commands.add import AddCommand
from cli_manager.commands.remove import RemoveCommand
from cli_manager.commands.show import ShowCommand
from cli_manager.commands.completioninit import CompletionInitCommand
from cli_manager.commands.completionrefresh import CompletionRefreshCommand


class SupercliApplication(Application):
    """
    Supercli application
    """

    help = "Supercli is a tool for managing your CLI tools."

    def __init__(self):
        super().__init__()
        self.set_name("supercli")
        self.add(AddCommand())
        self.add(RemoveCommand())
        self.add(ShowCommand())
        self.add(CompletionInitCommand())
        self.add(CompletionRefreshCommand())


def main():
    app = SupercliApplication()
    app.run()


if __name__ == "__main__":
    main()
