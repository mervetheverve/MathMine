"""All game constants and configuration."""
import os

# Paths
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Tiles
TILE_SIZE = 32
WALL_HEIGHT = 16  # extra pixels for the 3/4 view wall front face

# Player
PLAYER_SPEED = 3
PLAYER_SIZE = 28  # slightly smaller than tile for comfortable movement

# Inventory
INVENTORY_MAX = 8

# Colors - Stacklands (addition biome)
COLOR_STACKLANDS_FLOOR = (106, 190, 48)
COLOR_STACKLANDS_FLOOR_ALT = (118, 200, 58)
COLOR_STACKLANDS_WALL_TOP = (80, 120, 50)
COLOR_STACKLANDS_WALL_FRONT = (55, 85, 35)

# Colors - Crumble Caves (subtraction biome)
COLOR_CAVES_FLOOR = (120, 100, 85)
COLOR_CAVES_FLOOR_ALT = (110, 92, 78)
COLOR_CAVES_WALL_TOP = (75, 60, 50)
COLOR_CAVES_WALL_FRONT = (50, 40, 35)

# Colors - Factor Forest (multiplication biome)
COLOR_FOREST_FLOOR = (58, 120, 50)
COLOR_FOREST_FLOOR_ALT = (50, 108, 44)
COLOR_FOREST_WALL_TOP = (34, 85, 30)
COLOR_FOREST_WALL_FRONT = (22, 60, 20)

# Colors - Dividing Desert (division biome)
COLOR_DESERT_FLOOR = (218, 190, 130)
COLOR_DESERT_FLOOR_ALT = (205, 178, 120)
COLOR_DESERT_WALL_TOP = (170, 140, 90)
COLOR_DESERT_WALL_FRONT = (140, 112, 70)

# Colors - Hub (neutral stone)
COLOR_HUB_FLOOR = (140, 135, 130)
COLOR_HUB_FLOOR_ALT = (130, 125, 120)
COLOR_HUB_WALL_TOP = (100, 95, 90)
COLOR_HUB_WALL_FRONT = (75, 70, 65)

# Colors - Entities
COLOR_PLAYER = (52, 152, 219)
COLOR_PLAYER_DARK = (41, 128, 185)
COLOR_PLAYER_EYES = (255, 255, 255)
COLOR_PLAYER_PUPILS = (30, 30, 30)

# Number block tiers
COLOR_BLOCK_T1 = (149, 165, 166)       # gray stone
COLOR_BLOCK_T1_DARK = (127, 140, 141)
COLOR_BLOCK_T2 = (241, 196, 15)        # gold polished
COLOR_BLOCK_T2_DARK = (211, 172, 13)
COLOR_BLOCK_T3 = (155, 89, 182)        # purple gem
COLOR_BLOCK_T3_DARK = (132, 76, 155)
COLOR_BLOCK_TEXT = (255, 255, 255)

# Crafting station
COLOR_STATION = (170, 130, 90)
COLOR_STATION_DARK = (140, 105, 70)
COLOR_STATION_TOP = (190, 150, 110)

# Portal
COLOR_PORTAL = (26, 188, 156)
COLOR_PORTAL_DARK = (22, 160, 133)
COLOR_PORTAL_CHARGE = (46, 204, 113)
COLOR_PORTAL_EMPTY = (60, 60, 60)

# Hint stone
COLOR_HINT = (160, 140, 120)
COLOR_HINT_TEXT = (80, 60, 40)

# UI
COLOR_UI_BG = (40, 40, 50)
COLOR_UI_BORDER = (80, 80, 100)
COLOR_UI_TEXT = (240, 240, 240)
COLOR_UI_HIGHLIGHT = (52, 152, 219)
COLOR_UI_SUCCESS = (46, 204, 113)
COLOR_UI_ERROR = (231, 76, 60)
COLOR_UI_SLOT_EMPTY = (60, 60, 70)
COLOR_UI_SLOT_FILLED = (46, 204, 113)

# HUD
HUD_HEIGHT = 80
HUD_SLOT_SIZE = 48
HUD_PADDING = 8

# Save
SAVE_PATH = "saves/save.json"

# Difficulty tiers
TIER_RANGES = {
    1: (1, 9),      # single digit
    2: (1, 15),     # bridging through 10
    3: (10, 50),    # two-digit + single
    4: (10, 99),    # two-digit + two-digit
    5: (100, 500),  # three-digit
}

PORTAL_CHARGE_MULTIPLIER = {
    1: 1,     # 2 per answer → 50 answers (barely moves, practice zone)
    2: 2,     # 4 per answer → 25 answers (slow)
    3: 5,     # 10 per answer → 10 answers (crossing tens = real progress)
    4: 10,    # 20 per answer → 5 answers
    5: 20,    # 40 per answer → 3 answers
}
PORTAL_CHARGE_BASE = 2.0
