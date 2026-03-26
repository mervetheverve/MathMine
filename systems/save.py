"""Save system - JSON persistence for all game state."""
import json
import os


class SaveManager:
    """Handles saving and loading game state to/from JSON."""

    def __init__(self, save_path='saves/save.json'):
        self.save_path = save_path

    def save(self, game_state):
        """Save game state to JSON file."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        try:
            with open(self.save_path, 'w') as f:
                json.dump(game_state, f, indent=2)
            return True
        except (OSError, TypeError) as e:
            print(f"Save failed: {e}")
            return False

    def load(self):
        """Load game state from JSON file. Returns dict or None."""
        if not os.path.exists(self.save_path):
            return None
        try:
            with open(self.save_path, 'r') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Load failed: {e}")
            return None

    def has_save(self):
        """Check if a save file exists."""
        return os.path.exists(self.save_path)

    def delete_save(self):
        """Delete the save file."""
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
