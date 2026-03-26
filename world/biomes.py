"""Biome definitions - layouts, colors, and spawn rules."""
from settings import (
    COLOR_STACKLANDS_FLOOR, COLOR_STACKLANDS_FLOOR_ALT,
    COLOR_STACKLANDS_WALL_TOP, COLOR_STACKLANDS_WALL_FRONT,
    COLOR_CAVES_FLOOR, COLOR_CAVES_FLOOR_ALT,
    COLOR_CAVES_WALL_TOP, COLOR_CAVES_WALL_FRONT,
    COLOR_FOREST_FLOOR, COLOR_FOREST_FLOOR_ALT,
    COLOR_FOREST_WALL_TOP, COLOR_FOREST_WALL_FRONT,
    COLOR_DESERT_FLOOR, COLOR_DESERT_FLOOR_ALT,
    COLOR_DESERT_WALL_TOP, COLOR_DESERT_WALL_FRONT,
    COLOR_HUB_FLOOR, COLOR_HUB_FLOOR_ALT,
    COLOR_HUB_WALL_TOP, COLOR_HUB_WALL_FRONT,
)
from world.tilemap import (
    TileMap, TILE_FLOOR, TILE_WALL, TILE_SPAWN, TILE_PORTAL, TILE_STATION,
)

# Shorthand for readability
F = TILE_FLOOR
W = TILE_WALL
S = TILE_SPAWN
P = TILE_PORTAL
C = TILE_STATION  # crafting station

# Hub - small home base with 4 portal doors
# 25 cols x 20 rows
HUB_LAYOUT = [
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, P, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W, W, W],
    [W, W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W, W],
    [W, W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W, W],
    [W, W, W, W, P, F, F, F, F, F, F, F, S, F, F, F, F, F, F, F, P, W, W, W, W],
    [W, W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W, W],
    [W, W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W, W],
    [W, W, W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, P, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
]

# Portal positions sorted by (row, col) → biome assignment:
# Top (12,4) → Stacklands, Left (4,9) → Crumble Caves,
# Right (20,9) → Factor Forest, Bottom (12,14) → Dividing Desert
HUB_PORTAL_BIOMES = ['stacklands', 'crumble_caves', 'factor_forest', 'dividing_desert']

# Stacklands - bright open fields, addition biome
# 25 cols x 20 rows
STACKLANDS_LAYOUT = [
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, W, W, F, F, F, F, F, F, F, F, F, F, F, W, W, F, F, F, W, W],
    [W, W, F, F, F, W, W, F, F, F, F, F, F, F, F, F, F, F, W, W, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, S, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, C, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, W, F, F, F, F, F, F, F, F, F, F, F, F, F, W, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, P, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
]

# Crumble Caves - underground caverns, subtraction biome
CRUMBLE_CAVES_LAYOUT = [
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, F, F, F, F, F, W, W, W, F, F, F, F, F, W, W, W, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, W, F, F, F, F, F, F, F, W, F, F, F, F, F, F, W, W],
    [W, W, F, F, S, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, W, W, W, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, W, W, W, F, F, F, F, F, F, C, F, F, W, W],
    [W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W],
    [W, W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W, W],
    [W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, W, W, F, F, F, F, F, F, F, F, F, W, W, F, F, F, F, W, W],
    [W, W, F, F, F, F, W, W, F, F, F, F, F, F, F, F, F, W, W, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, P, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
]

# Factor Forest - dense woodland paths, multiplication biome
FACTOR_FOREST_LAYOUT = [
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, F, F, F, F, W, F, F, F, F, F, F, F, F, F, F, F, F, W, F, F, F, W, W],
    [W, W, F, F, S, F, W, F, F, F, F, F, F, F, F, F, F, F, F, W, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, W, F, F, F, F, F, W, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, W, F, F, F, F, F, W, F, F, F, F, F, F, F, W, W],
    [W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, W, F, F, F, F, F, F, F, F, F, F, F, F, F, W, F, F, F, W, W],
    [W, W, F, F, F, W, F, F, F, F, F, C, F, F, F, F, F, F, F, W, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, W, F, F, F, F, F, W, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, W, F, F, F, F, F, W, F, F, F, F, F, F, F, F, W, W],
    [W, W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, P, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
]

# Dividing Desert - sandy dunes with rock outcrops, division biome
DIVIDING_DESERT_LAYOUT = [
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, S, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, W, W, F, F, F, W, W, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, W, F, F, F, F, F, F, F, F, F, F, F, W, F, F, F, F, W, W],
    [W, W, F, F, F, F, W, F, F, F, F, C, F, F, F, F, F, F, W, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, P, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
    [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
]

STACKLANDS_COLORS = {
    'floor': COLOR_STACKLANDS_FLOOR,
    'floor_alt': COLOR_STACKLANDS_FLOOR_ALT,
    'wall_top': COLOR_STACKLANDS_WALL_TOP,
    'wall_front': COLOR_STACKLANDS_WALL_FRONT,
}

CRUMBLE_CAVES_COLORS = {
    'floor': COLOR_CAVES_FLOOR,
    'floor_alt': COLOR_CAVES_FLOOR_ALT,
    'wall_top': COLOR_CAVES_WALL_TOP,
    'wall_front': COLOR_CAVES_WALL_FRONT,
}

FACTOR_FOREST_COLORS = {
    'floor': COLOR_FOREST_FLOOR,
    'floor_alt': COLOR_FOREST_FLOOR_ALT,
    'wall_top': COLOR_FOREST_WALL_TOP,
    'wall_front': COLOR_FOREST_WALL_FRONT,
}

DIVIDING_DESERT_COLORS = {
    'floor': COLOR_DESERT_FLOOR,
    'floor_alt': COLOR_DESERT_FLOOR_ALT,
    'wall_top': COLOR_DESERT_WALL_TOP,
    'wall_front': COLOR_DESERT_WALL_FRONT,
}

HUB_COLORS = {
    'floor': COLOR_HUB_FLOOR,
    'floor_alt': COLOR_HUB_FLOOR_ALT,
    'wall_top': COLOR_HUB_WALL_TOP,
    'wall_front': COLOR_HUB_WALL_FRONT,
}

# Biome progression order
BIOME_ORDER = ['stacklands', 'crumble_caves', 'factor_forest', 'dividing_desert']

BIOMES = {
    'stacklands': {
        'name': 'The Stacklands',
        'layout': STACKLANDS_LAYOUT,
        'colors': STACKLANDS_COLORS,
        'operations': ['+'],
        'block_count': 12,
    },
    'crumble_caves': {
        'name': 'The Crumble Caves',
        'layout': CRUMBLE_CAVES_LAYOUT,
        'colors': CRUMBLE_CAVES_COLORS,
        'operations': ['-'],
        'block_count': 12,
    },
    'factor_forest': {
        'name': 'The Factor Forest',
        'layout': FACTOR_FOREST_LAYOUT,
        'colors': FACTOR_FOREST_COLORS,
        'operations': ['*'],
        'block_count': 12,
    },
    'dividing_desert': {
        'name': 'The Dividing Desert',
        'layout': DIVIDING_DESERT_LAYOUT,
        'colors': DIVIDING_DESERT_COLORS,
        'operations': ['/'],
        'block_count': 12,
    },
    'hub': {
        'name': 'Home Base',
        'layout': HUB_LAYOUT,
        'colors': HUB_COLORS,
        'operations': [],
        'block_count': 0,
    },
}


def get_next_biome(current_key):
    """Get the next biome after completing current one. Regular biomes → hub."""
    if current_key == 'hub':
        return 'hub'  # hub doesn't auto-transition
    return 'hub'


def create_tilemap(biome_key):
    """Create a TileMap for the given biome."""
    biome = BIOMES[biome_key]
    return TileMap(biome['layout'], biome['colors'], biome_key=biome_key)
