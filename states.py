"""Game state machine."""
import enum


class GameState(enum.Enum):
    TITLE = "title"
    PLAYING = "playing"
    CRAFTING = "crafting"
    FEEDBACK = "feedback"
    BLUEPRINT_VIEW = "blueprint_view"
    PORTAL_CHALLENGE = "portal_challenge"
    PAUSED = "paused"
