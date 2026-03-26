"""Player character - grid-based movement with smooth interpolation."""
import os
import math
import pygame
from settings import (
    PLAYER_SIZE, TILE_SIZE,
    COLOR_PLAYER, COLOR_PLAYER_DARK, COLOR_PLAYER_EYES, COLOR_PLAYER_PUPILS,
)
from player.inventory import Inventory
from assets.sprite_loader import load_sprite

# Frames to slide between tiles (must match or be less than MOVE_COOLDOWN)
MOVE_COOLDOWN = 8
SLIDE_FRAMES = 6  # how many frames the slide animation takes (rest is buffer)

# Direction names for sprite loading
_DIR_NAMES = {0: 'down', 1: 'left', 2: 'right', 3: 'up'}


class Player(pygame.sprite.Sprite):
    """The player character with smooth grid movement and walk animation."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        # Grid position (logical)
        self.grid_col = x // TILE_SIZE
        self.grid_row = y // TILE_SIZE
        self._snap_to_grid()

        # Smooth movement interpolation
        self._sliding = False
        self._slide_timer = 0
        self._slide_start_x = 0.0
        self._slide_start_y = 0.0
        self._slide_end_x = 0.0
        self._slide_end_y = 0.0
        self._visual_x = float(self.rect.x)
        self._visual_y = float(self.rect.y)

        # Direction: 0=down, 1=left, 2=right, 3=up
        self.direction = 0
        self.move_cooldown = 0
        self.inventory = Inventory()

        # Animation state
        self._anim_frame = 0  # 0=idle, 1=walk1, 2=walk2
        self._walking = False
        self._step_count = 0  # counts total steps for alternating

        # Load sprite frames
        self._sprites = {}
        self._load_sprites()
        self._draw_sprite()

    def _load_sprites(self):
        """Load all player sprite frames from assets."""
        for d, dname in _DIR_NAMES.items():
            for f, fname in [(0, 'idle'), (1, 'walk1'), (2, 'walk2')]:
                path = os.path.join('sprites', 'player',
                                    f'player_{dname}_{fname}.png')
                sprite = load_sprite(path, (PLAYER_SIZE, PLAYER_SIZE),
                                     COLOR_PLAYER)
                self._sprites[(d, f)] = sprite

    def _grid_pixel_pos(self):
        """Get the pixel position for current grid cell (centered)."""
        px = self.grid_col * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) // 2
        py = self.grid_row * TILE_SIZE + (TILE_SIZE - PLAYER_SIZE) // 2
        return px, py

    def _snap_to_grid(self):
        """Position the player centered on its grid cell."""
        px, py = self._grid_pixel_pos()
        self.rect.x = px
        self.rect.y = py
        self._visual_x = float(px)
        self._visual_y = float(py)

    def _draw_sprite(self):
        """Select the correct sprite frame for current direction and animation."""
        key = (self.direction, self._anim_frame)
        sprite = self._sprites.get(key)
        if sprite:
            self.image = sprite
        else:
            self._draw_sprite_procedural()

    def _draw_sprite_procedural(self):
        """Fallback: draw the player as a colored square with a simple face."""
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        s = PLAYER_SIZE

        body_top = pygame.Rect(0, 0, s, s - 6)
        body_front = pygame.Rect(0, s - 6, s, 6)
        pygame.draw.rect(self.image, COLOR_PLAYER, body_top, border_radius=4)
        pygame.draw.rect(self.image, COLOR_PLAYER_DARK, body_front,
                         border_radius=2)

        eye_y = 8
        pygame.draw.rect(self.image, COLOR_PLAYER_EYES,
                         pygame.Rect(6, eye_y, 6, 6), border_radius=2)
        pygame.draw.rect(self.image, COLOR_PLAYER_EYES,
                         pygame.Rect(s - 12, eye_y, 6, 6), border_radius=2)

        dx, dy = 0, 0
        if self.direction == 0:
            dy = 2
        elif self.direction == 1:
            dx = -1
        elif self.direction == 2:
            dx = 1
        elif self.direction == 3:
            dy = -1
        pygame.draw.rect(self.image, COLOR_PLAYER_PUPILS,
                         pygame.Rect(8 + dx, eye_y + 1 + dy, 3, 3))
        pygame.draw.rect(self.image, COLOR_PLAYER_PUPILS,
                         pygame.Rect(s - 11 + dx, eye_y + 1 + dy, 3, 3))

    def update(self, keys, tilemap=None):
        """Move the player one grid tile per step with smooth sliding."""
        # Continue slide animation even during cooldown
        if self._sliding:
            self._slide_timer += 1
            if self._slide_timer >= SLIDE_FRAMES:
                # Slide complete — snap to end position
                self._sliding = False
                self._visual_x = self._slide_end_x
                self._visual_y = self._slide_end_y
            else:
                # Interpolate with ease-out curve
                t = self._slide_timer / SLIDE_FRAMES
                t = 1.0 - (1.0 - t) * (1.0 - t)  # ease-out quadratic
                self._visual_x = self._slide_start_x + (self._slide_end_x - self._slide_start_x) * t
                self._visual_y = self._slide_start_y + (self._slide_end_y - self._slide_start_y) * t

        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dc, dr = 0, 0
        new_dir = self.direction

        if keys[pygame.K_LEFT]:
            dc = -1
            new_dir = 1
        elif keys[pygame.K_RIGHT]:
            dc = 1
            new_dir = 2
        elif keys[pygame.K_UP]:
            dr = -1
            new_dir = 3
        elif keys[pygame.K_DOWN]:
            dr = 1
            new_dir = 0

        if dc == 0 and dr == 0:
            # Idle — stop walking animation
            if self._walking or self._anim_frame != 0:
                self._walking = False
                self._anim_frame = 0
                self._draw_sprite()
            return

        # Update facing direction
        dir_changed = new_dir != self.direction
        self.direction = new_dir

        # Check if the target tile is walkable
        target_col = self.grid_col + dc
        target_row = self.grid_row + dr

        if tilemap and tilemap.is_wall(target_col, target_row):
            if dir_changed:
                self._draw_sprite()
            self.move_cooldown = MOVE_COOLDOWN
            return

        # Start slide from current visual position to new grid position
        self._slide_start_x = self._visual_x
        self._slide_start_y = self._visual_y

        # Move logical grid position
        self.grid_col = target_col
        self.grid_row = target_row
        px, py = self._grid_pixel_pos()
        self.rect.x = px
        self.rect.y = py

        self._slide_end_x = float(px)
        self._slide_end_y = float(py)
        self._sliding = True
        self._slide_timer = 0
        self.move_cooldown = MOVE_COOLDOWN

        # Walk animation: alternate walk1/walk2 each step
        self._walking = True
        self._step_count += 1
        self._anim_frame = 1 if (self._step_count % 2 == 0) else 2
        self._draw_sprite()

    def set_grid_pos(self, col, row):
        """Teleport the player to a specific grid cell."""
        self.grid_col = col
        self.grid_row = row
        self._sliding = False
        self._snap_to_grid()

    def draw(self, surface, camera):
        """Draw the player at interpolated screen position with walk bounce."""
        # Use visual position for smooth movement
        screen_x = self._visual_x - camera.offset_x
        screen_y = self._visual_y - camera.offset_y

        # Walk bounce: small vertical bob while sliding
        if self._sliding and self._slide_timer < SLIDE_FRAMES:
            t = self._slide_timer / SLIDE_FRAMES
            # Single bounce arc: sin(0..pi) peaks at 0.5
            bounce = -2.0 * math.sin(t * math.pi)
            screen_y += bounce

        surface.blit(self.image, (int(screen_x), int(screen_y)))

    def get_center(self):
        """Get the player's world center position."""
        return (self.rect.centerx, self.rect.centery)
