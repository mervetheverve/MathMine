"""Tile map and camera for the game world."""
import pygame
from settings import TILE_SIZE, WALL_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, HUD_HEIGHT
from assets.sprite_loader import load_tile_set


class Camera:
    """Camera that follows the player, clamped to map bounds."""

    def __init__(self, map_pixel_width, map_pixel_height):
        self.offset_x = 0
        self.offset_y = 0
        self.map_width = map_pixel_width
        self.map_height = map_pixel_height

    def update(self, player):
        """Center camera on the player within the visible area above the HUD."""
        visible_height = SCREEN_HEIGHT - HUD_HEIGHT
        self.offset_x = player.rect.centerx - SCREEN_WIDTH // 2
        self.offset_y = player.rect.centery - visible_height // 2
        # Clamp to map bounds (bottom clamp ensures map doesn't hide behind HUD)
        self.offset_x = max(0, min(self.offset_x,
                                   self.map_width - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y,
                                   self.map_height - visible_height))

    def apply(self, rect):
        """Return a rect adjusted for camera offset."""
        return rect.move(-self.offset_x, -self.offset_y)

    def apply_pos(self, x, y):
        """Return (x, y) adjusted for camera offset."""
        return (x - self.offset_x, y - self.offset_y)


# Tile types
TILE_FLOOR = 0
TILE_WALL = 1
TILE_SPAWN = 2       # player spawn (renders as floor)
TILE_PORTAL = 3      # portal location (renders as floor)
TILE_STATION = 4     # crafting station location (renders as floor)


class TileMap:
    """Manages the tile-based world."""

    def __init__(self, layout, colors, biome_key=None):
        """
        layout: 2D list of tile type integers
        colors: dict with keys 'floor', 'floor_alt', 'wall_top', 'wall_front'
        biome_key: optional biome name to load tile sprites
        """
        self.layout = layout
        self.colors = colors
        self.rows = len(layout)
        self.cols = len(layout[0]) if self.rows > 0 else 0
        self.pixel_width = self.cols * TILE_SIZE
        self.pixel_height = self.rows * TILE_SIZE
        # Load tile sprites (None if assets don't exist yet)
        self.tile_sprites = load_tile_set(biome_key) if biome_key else None

    def get_tile(self, col, row):
        """Get tile type at grid position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.layout[row][col]
        return TILE_WALL  # out of bounds = wall

    def is_wall(self, col, row):
        """Check if a tile is a wall."""
        return self.get_tile(col, row) == TILE_WALL

    def collides(self, rect):
        """Check if a rect collides with any wall tiles."""
        # Check all tiles the rect overlaps
        left_col = rect.left // TILE_SIZE
        right_col = rect.right // TILE_SIZE
        top_row = rect.top // TILE_SIZE
        bottom_row = rect.bottom // TILE_SIZE

        for row in range(top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                if self.is_wall(col, row):
                    return True
        return False

    def find_tile(self, tile_type):
        """Find the first tile of a given type. Returns (col, row) or None."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.layout[row][col] == tile_type:
                    return (col, row)
        return None

    def find_all_tiles(self, tile_type):
        """Find all tiles of a given type. Returns list of (col, row)."""
        result = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.layout[row][col] == tile_type:
                    result.append((col, row))
        return result

    def draw(self, surface, camera):
        """Draw visible tiles with 3/4 perspective."""
        # Calculate visible tile range
        start_col = max(0, camera.offset_x // TILE_SIZE)
        end_col = min(self.cols, (camera.offset_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        start_row = max(0, camera.offset_y // TILE_SIZE)
        end_row = min(self.rows, (camera.offset_y + SCREEN_HEIGHT) // TILE_SIZE + 2)

        # Draw back-to-front (top rows first) for correct overlap
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = self.layout[row][col]
                world_x = col * TILE_SIZE
                world_y = row * TILE_SIZE
                screen_x = world_x - camera.offset_x
                screen_y = world_y - camera.offset_y

                if tile == TILE_WALL:
                    self._draw_wall(surface, screen_x, screen_y)
                else:
                    self._draw_floor(surface, screen_x, screen_y, col, row)

    def _draw_floor(self, surface, x, y, col, row):
        """Draw a floor tile with sprite or color fallback."""
        if self.tile_sprites:
            key = 'floor' if (col + row) % 2 == 0 else 'floor_alt'
            surface.blit(self.tile_sprites[key], (x, y))
        else:
            color = self.colors['floor'] if (col + row) % 2 == 0 else self.colors['floor_alt']
            pygame.draw.rect(surface, color,
                             pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

    def _draw_wall(self, surface, x, y):
        """Draw a wall tile with sprite or color fallback."""
        if self.tile_sprites:
            surface.blit(self.tile_sprites['wall_top'],
                         (x, y - WALL_HEIGHT))
            surface.blit(self.tile_sprites['wall_front'], (x, y))
        else:
            # Top face
            top_rect = pygame.Rect(x, y - WALL_HEIGHT, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, self.colors['wall_top'], top_rect)
            pygame.draw.rect(surface, self.colors['wall_front'], top_rect, 1)
            # Front face
            front_rect = pygame.Rect(x, y, TILE_SIZE, WALL_HEIGHT)
            pygame.draw.rect(surface, self.colors['wall_front'], front_rect)
            pygame.draw.line(surface, self.colors['wall_top'],
                             (x, y), (x + TILE_SIZE - 1, y))
