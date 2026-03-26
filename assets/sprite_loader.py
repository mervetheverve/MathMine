"""Centralized sprite loading with caching and fallback."""
import os
import pygame

_cache = {}
_ASSET_ROOT = os.path.join(os.path.dirname(__file__))


def load_sprite(relative_path, fallback_size=None, fallback_color=None):
    """Load a sprite PNG, cache it, return the Surface.

    If the file doesn't exist, returns a fallback colored rectangle
    so the game never crashes during incremental development.
    """
    if relative_path in _cache:
        return _cache[relative_path]

    full_path = os.path.join(_ASSET_ROOT, relative_path)
    if os.path.exists(full_path):
        surface = pygame.image.load(full_path).convert_alpha()
    else:
        # Fallback: magenta rectangle = missing asset
        w, h = fallback_size or (32, 32)
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        color = fallback_color or (255, 0, 255, 200)
        pygame.draw.rect(surface, color, (0, 0, w, h))

    _cache[relative_path] = surface
    return surface


def load_tile_set(biome_name):
    """Load all 4 tile sprites for a biome. Returns dict or None if no assets."""
    base = os.path.join('tiles', biome_name)
    floor_path = os.path.join(base, 'floor.png')

    # Check if at least the floor sprite exists
    if not os.path.exists(os.path.join(_ASSET_ROOT, floor_path)):
        return None

    return {
        'floor': load_sprite(os.path.join(base, 'floor.png'), (32, 32)),
        'floor_alt': load_sprite(os.path.join(base, 'floor_alt.png'), (32, 32)),
        'wall_top': load_sprite(os.path.join(base, 'wall_top.png'), (32, 32)),
        'wall_front': load_sprite(os.path.join(base, 'wall_front.png'), (32, 16)),
    }


def preload_all():
    """Pre-load all assets at startup to avoid hitches."""
    for biome in ['hub', 'stacklands', 'crumble_caves', 'factor_forest',
                  'dividing_desert']:
        load_tile_set(biome)


def clear_cache():
    """Clear the sprite cache (useful when regenerating assets)."""
    _cache.clear()
