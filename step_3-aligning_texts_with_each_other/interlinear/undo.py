"""
Undo Module for Interlinear Text Creator

Provides undo/redo functionality for text editing.
"""

class UndoManager:
    """
    Simple undo/redo manager for text states.
    """
    
    def __init__(self, max_history=50):
        self.history = []
        self.future = []
        self.max_history = max_history
    
    def save_state(self, state):
        """
        Save current state to history.
        """
        self.history.append(state)
        self.future.clear()  # Clear redo stack on new action
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def undo(self):
        """
        Undo last action, return previous state.
        """
        if len(self.history) <= 1:
            return None
        
        current = self.history.pop()
        self.future.append(current)
        return self.history[-1] if self.history else None
    
    def redo(self):
        """
        Redo previously undone action.
        """
        if not self.future:
            return None
        
        state = self.future.pop()
        self.history.append(state)
        return state
    
    def can_undo(self):
        return len(self.history) > 1
    
    def can_redo(self):
        return len(self.future) > 0
