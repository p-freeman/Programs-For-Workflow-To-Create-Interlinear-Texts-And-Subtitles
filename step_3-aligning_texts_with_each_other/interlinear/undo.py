class Command:
    def execute(self): ...
    def undo(self): ...

class CommandStack:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def do(self, cmd):
        cmd.execute()
        self.undo_stack.append(cmd)
        self.redo_stack.clear()
