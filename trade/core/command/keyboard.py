from trade.model.enums import RunnerStatus


class KeyBoardCommand:
    def execute(self, runner, command) -> bool:
        pass


class ContinueCommand(KeyBoardCommand):
    """
    继续命令
    """

    command = ''

    def execute(self, runner, command) -> bool:
        if command == self.command:
            runner.status = RunnerStatus.Next
            return True
        return False
