"""World entities - NumberBlock, CraftingStation, Portal, HintStone."""
import os
import math
import random
import pygame
from settings import (
    TILE_SIZE, WALL_HEIGHT,
    COLOR_BLOCK_T1, COLOR_BLOCK_T1_DARK,
    COLOR_BLOCK_T2, COLOR_BLOCK_T2_DARK,
    COLOR_BLOCK_T3, COLOR_BLOCK_T3_DARK,
    COLOR_BLOCK_TEXT,
    COLOR_STATION, COLOR_STATION_DARK, COLOR_STATION_TOP,
    COLOR_PORTAL, COLOR_PORTAL_DARK, COLOR_PORTAL_CHARGE, COLOR_PORTAL_EMPTY,
    COLOR_HINT, COLOR_HINT_TEXT,
)
from assets.sprite_loader import load_sprite

# Block tier colors
TIER_COLORS = {
    1: (COLOR_BLOCK_T1, COLOR_BLOCK_T1_DARK),
    2: (COLOR_BLOCK_T2, COLOR_BLOCK_T2_DARK),
    3: (COLOR_BLOCK_T3, COLOR_BLOCK_T3_DARK),
}


class NumberBlock(pygame.sprite.Sprite):
    """A collectible number block in the world."""

    def __init__(self, x, y, value, tier=1):
        super().__init__()
        self.value = value
        self.tier = min(tier, 3)
        self.size = 30
        glow = 4  # extra padding for glow
        self.image = pygame.Surface(
            (self.size + glow * 2, self.size + 10 + glow * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x - glow
        self.rect.y = y - glow
        self._glow = glow
        # Bob animation: random phase so blocks don't sync
        self._bob_offset = random.uniform(0, math.pi * 2)
        # Load sprite
        self._base_sprite = load_sprite(
            os.path.join('sprites', 'blocks', f'block_t{self.tier}.png'),
            (self.size + glow * 2, self.size + 10 + glow * 2),
            TIER_COLORS.get(self.tier, TIER_COLORS[1])[0])
        self._render()

    def _render(self):
        """Draw the block using sprite base + dynamic number overlay."""
        self.image.fill((0, 0, 0, 0))

        # Check if we have a real sprite (not a fallback magenta rect)
        sprite_path = os.path.join('sprites', 'blocks',
                                   f'block_t{self.tier}.png')
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'assets', sprite_path)
        if os.path.exists(full_path):
            self.image.blit(self._base_sprite, (0, 0))
        else:
            self._render_procedural()

        # Number text (always dynamic since value varies)
        font = pygame.font.SysFont('arial', 18, bold=True)
        text = font.render(str(self.value), True, COLOR_BLOCK_TEXT)
        shadow = font.render(str(self.value), True, (0, 0, 0))
        g = self._glow
        s = self.size
        center = (g + s // 2, g + s // 2)
        self.image.blit(shadow, shadow.get_rect(
            center=(center[0] + 1, center[1] + 1)))
        self.image.blit(text, text.get_rect(center=center))

    def _render_procedural(self):
        """Fallback procedural rendering."""
        color, dark_color = TIER_COLORS.get(self.tier, TIER_COLORS[1])
        s = self.size
        g = self._glow

        glow_surf = pygame.Surface((s + 6, s + 6), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*color, 55),
                         pygame.Rect(0, 0, s + 6, s + 6), border_radius=6)
        self.image.blit(glow_surf, (g - 3, g - 3))

        pygame.draw.rect(self.image, color,
                         pygame.Rect(g, g, s, s), border_radius=4)
        pygame.draw.rect(self.image, dark_color,
                         pygame.Rect(g, g + s - 2, s, 10), border_radius=3)
        pygame.draw.rect(self.image, dark_color,
                         pygame.Rect(g, g, s, s), 2, border_radius=4)
        highlight = tuple(min(c + 40, 255) for c in color)
        pygame.draw.line(self.image, highlight,
                         (g + 3, g + 2), (g + s - 4, g + 2), 1)

    def draw(self, surface, camera):
        """Draw at screen position with bob animation."""
        screen_pos = camera.apply(self.rect)
        # Bob: 2px amplitude sine wave, visual only
        bob = int(2 * math.sin(pygame.time.get_ticks() * 0.003 + self._bob_offset))
        surface.blit(self.image, (screen_pos.x, screen_pos.y + bob))


class CraftingStation(pygame.sprite.Sprite):
    """A crafting station where the player combines blocks."""

    # Kid-friendly operator display symbols
    _OP_DISPLAY = {'*': 'x', '/': '\u00f7'}

    def __init__(self, x, y, operation='+'):
        super().__init__()
        self.operation = operation
        self.size = TILE_SIZE
        self.image = pygame.Surface((self.size, self.size + WALL_HEIGHT),
                                    pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Load sprite
        self._base_sprite = load_sprite(
            os.path.join('sprites', 'entities', 'crafting_station.png'),
            (self.size, self.size + WALL_HEIGHT),
            COLOR_STATION_TOP)
        self._render()

    def _render(self):
        """Draw the station using sprite base + dynamic operation symbol."""
        self.image.fill((0, 0, 0, 0))

        sprite_path = os.path.join('sprites', 'entities', 'crafting_station.png')
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'assets', sprite_path)
        if os.path.exists(full_path):
            self.image.blit(self._base_sprite, (0, 0))
        else:
            self._render_procedural()

        # Operation symbol on top (always dynamic)
        display = self._OP_DISPLAY.get(self.operation, self.operation)
        font = pygame.font.SysFont('arial', 20, bold=True)
        text = font.render(display, True, (255, 255, 255))
        shadow = font.render(display, True, (0, 0, 0))
        s = self.size
        center = (s // 2, s // 2)
        self.image.blit(shadow, shadow.get_rect(
            center=(center[0] + 1, center[1] + 1)))
        self.image.blit(text, text.get_rect(center=center))

    def _render_procedural(self):
        """Fallback procedural rendering."""
        s = self.size
        pygame.draw.rect(self.image, COLOR_STATION_TOP,
                         pygame.Rect(2, 2, s - 4, s - 4), border_radius=4)
        pygame.draw.rect(self.image, COLOR_STATION_DARK,
                         pygame.Rect(2, s - 4, s - 4, WALL_HEIGHT),
                         border_radius=2)
        pygame.draw.rect(self.image, COLOR_STATION,
                         pygame.Rect(2, 2, s - 4, s - 4), 2, border_radius=4)

    def draw(self, surface, camera):
        screen_pos = camera.apply(self.rect)
        surface.blit(self.image, screen_pos)


class Portal(pygame.sprite.Sprite):
    """A portal that charges with mastery and connects biomes."""

    def __init__(self, x, y, destination_biome, locked=False, label='',
                 portal_color=None):
        super().__init__()
        self.destination = destination_biome
        self.charge = 0.0  # 0.0 to 1.0
        self.charge_max = 100.0
        self.charge_current = 0.0
        self.locked = locked
        self.label = label
        self.portal_color = portal_color  # biome-specific frame color
        self.width = TILE_SIZE * 2
        self.height = TILE_SIZE * 2
        self.image = pygame.Surface((self.width, self.height + WALL_HEIGHT),
                                    pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # Load sprites
        self._frame_sprite = load_sprite(
            os.path.join('sprites', 'entities', 'portal_frame.png'),
            (self.width, self.height + WALL_HEIGHT))
        self._locked_sprite = load_sprite(
            os.path.join('sprites', 'entities', 'portal_locked.png'),
            (self.width, self.height + WALL_HEIGHT))
        self._render()

    def _render(self):
        """Draw the portal with charge bar."""
        self.image.fill((0, 0, 0, 0))
        w, h = self.width, self.height

        # Check for sprites
        frame_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  'assets', 'sprites', 'entities',
                                  'portal_frame.png')
        has_sprites = os.path.exists(frame_path)

        if self.locked:
            if has_sprites:
                self.image.blit(self._locked_sprite, (0, 0))
                # Overlay text
                font = pygame.font.SysFont('arial', 12)
                lock_text = font.render('Locked', True, (120, 120, 120))
                lock_rect = lock_text.get_rect(center=(w // 2, h // 2 - 6))
                self.image.blit(lock_text, lock_rect)
                if self.label:
                    lbl = font.render(self.label, True, (100, 100, 100))
                    lbl_rect = lbl.get_rect(center=(w // 2, h // 2 + 10))
                    self.image.blit(lbl, lbl_rect)
            else:
                self._render_locked_procedural()
            return

        charge_ratio = self.charge_current / self.charge_max

        if has_sprites:
            # Use sprite frame, tint inner area based on charge
            self.image.blit(self._frame_sprite, (0, 0))
            # Fill inner area with charge color
            inner = pygame.Surface((w - 16, h - 16), pygame.SRCALPHA)
            if charge_ratio >= 1.0:
                inner.fill((40, 180, 140, 200))
            else:
                inner.fill((20, 20, 30, 200))
                if charge_ratio > 0 and self.portal_color:
                    cr, cg, cb = self.portal_color
                    glow_alpha = int(80 * charge_ratio)
                    glow = pygame.Surface((w - 16, h - 16), pygame.SRCALPHA)
                    glow.fill((cr, cg, cb, glow_alpha))
                    inner.blit(glow, (0, 0))
            self.image.blit(inner, (8, 8))
        else:
            self._render_unlocked_procedural(charge_ratio)

        # Charge bar below portal
        bar_y = h + 4
        bar_h = 8
        pygame.draw.rect(self.image, COLOR_PORTAL_EMPTY,
                         pygame.Rect(4, bar_y, w - 8, bar_h), border_radius=3)
        if charge_ratio > 0:
            fill_w = int((w - 8) * charge_ratio)
            pygame.draw.rect(self.image, COLOR_PORTAL_CHARGE,
                             pygame.Rect(4, bar_y, fill_w, bar_h),
                             border_radius=3)

        # Label
        font = pygame.font.SysFont('arial', 12)
        if charge_ratio >= 1.0:
            txt = font.render('ENTER', True, (255, 255, 255))
        else:
            pct = int(charge_ratio * 100)
            txt = font.render(f'{pct}%', True, (200, 200, 200))
        txt_rect = txt.get_rect(center=(w // 2, h // 2 - 6))
        self.image.blit(txt, txt_rect)
        if self.label:
            lbl = font.render(self.label, True, (220, 220, 220))
            lbl_rect = lbl.get_rect(center=(w // 2, h // 2 + 10))
            self.image.blit(lbl, lbl_rect)

    def _render_locked_procedural(self):
        """Fallback locked portal rendering."""
        w, h = self.width, self.height
        pygame.draw.rect(self.image, (60, 60, 65),
                         pygame.Rect(0, 0, w, h), border_radius=6)
        inner = pygame.Rect(6, 6, w - 12, h - 12)
        pygame.draw.rect(self.image, (30, 30, 35), inner, border_radius=4)
        pygame.draw.rect(self.image, (50, 50, 55),
                         pygame.Rect(0, h - 4, w, WALL_HEIGHT + 4),
                         border_radius=3)
        font = pygame.font.SysFont('arial', 12)
        lock_text = font.render('Locked', True, (120, 120, 120))
        lock_rect = lock_text.get_rect(center=(w // 2, h // 2 - 6))
        self.image.blit(lock_text, lock_rect)
        if self.label:
            lbl = font.render(self.label, True, (100, 100, 100))
            lbl_rect = lbl.get_rect(center=(w // 2, h // 2 + 10))
            self.image.blit(lbl, lbl_rect)

    def _render_unlocked_procedural(self, charge_ratio):
        """Fallback unlocked portal rendering."""
        w, h = self.width, self.height
        frame_color = self.portal_color or COLOR_PORTAL
        frame_dark = tuple(max(0, c - 30) for c in frame_color)

        base_r, base_g, base_b = frame_dark
        if charge_ratio > 0:
            cr, cg, cb = frame_color
            base_r = int(base_r + (cr - base_r) * charge_ratio)
            base_g = int(base_g + (cg - base_g) * charge_ratio)
            base_b = int(base_b + (cb - base_b) * charge_ratio)

        pygame.draw.rect(self.image, (base_r, base_g, base_b),
                         pygame.Rect(0, 0, w, h), border_radius=6)
        inner = pygame.Rect(6, 6, w - 12, h - 12)
        inner_color = (20, 20, 30) if charge_ratio < 1.0 else (40, 180, 140)
        pygame.draw.rect(self.image, inner_color, inner, border_radius=4)
        pygame.draw.rect(self.image, frame_dark,
                         pygame.Rect(0, h - 4, w, WALL_HEIGHT + 4),
                         border_radius=3)

    def add_charge(self, amount):
        """Add charge to the portal."""
        self.charge_current = min(self.charge_max, self.charge_current + amount)
        self._render()

    def remove_charge(self, amount):
        """Remove charge from the portal."""
        self.charge_current = max(0, self.charge_current - amount)
        self._render()

    def is_ready(self):
        return self.charge_current >= self.charge_max

    def draw(self, surface, camera):
        screen_pos = camera.apply(self.rect)
        surface.blit(self.image, screen_pos)

    def serialize(self):
        return {'charge': self.charge_current, 'destination': self.destination}

    def deserialize(self, data):
        self.charge_current = data.get('charge', 0.0)
        self.destination = data.get('destination', self.destination)
        self._render()


class HintStone(pygame.sprite.Sprite):
    """A hint stone that shows decomposition hints near the player."""

    def __init__(self, x, y, hint_text=""):
        super().__init__()
        self.hint_text = hint_text
        self.visible = True
        self.size = 28
        self._bubble_font = pygame.font.SysFont('arial', 15, bold=True)
        self._bubble_surf = None
        # Load sprite
        self._base_sprite = load_sprite(
            os.path.join('sprites', 'entities', 'hint_stone.png'),
            (self.size, self.size + 8),
            COLOR_HINT)
        self._build_image()

    def _build_image(self):
        self.image = pygame.Surface((self.size, self.size + 8), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._render()

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        if not self.visible:
            return

        sprite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                   'assets', 'sprites', 'entities',
                                   'hint_stone.png')
        if os.path.exists(sprite_path):
            self.image.blit(self._base_sprite, (0, 0))
        else:
            self._render_procedural()

        # Pre-render hint bubble
        if self.hint_text:
            self._bubble_surf = self._render_bubble()

    def _render_procedural(self):
        """Fallback procedural rendering."""
        s = self.size
        pygame.draw.rect(self.image, COLOR_HINT,
                         pygame.Rect(0, 0, s, s), border_radius=6)
        pygame.draw.rect(self.image, (140, 120, 100),
                         pygame.Rect(0, s - 2, s, 8), border_radius=3)
        font = pygame.font.SysFont('arial', 16, bold=True)
        text = font.render('?', True, COLOR_HINT_TEXT)
        text_rect = text.get_rect(center=(s // 2, s // 2))
        self.image.blit(text, text_rect)

    def _render_bubble(self):
        """Render the speech bubble with hint text."""
        text = self._bubble_font.render(self.hint_text, True, (255, 255, 240))
        w = text.get_width() + 16
        h = text.get_height() + 10
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (50, 40, 30, 210),
                         pygame.Rect(0, 0, w, h), border_radius=6)
        pygame.draw.rect(surf, (180, 160, 120, 200),
                         pygame.Rect(0, 0, w, h), 2, border_radius=6)
        surf.blit(text, (8, 5))
        return surf

    def set_hint(self, hint_text):
        """Update the hint text."""
        self.hint_text = hint_text
        if self.visible:
            self._bubble_surf = self._render_bubble() if hint_text else None

    def set_visible(self, visible):
        if self.visible != visible:
            self.visible = visible
            self._render()

    def draw(self, surface, camera):
        if not self.visible:
            return
        screen_pos = camera.apply(self.rect)
        surface.blit(self.image, screen_pos)
        # Draw hint bubble above the stone
        if self._bubble_surf:
            bx = screen_pos.x + self.size // 2 - self._bubble_surf.get_width() // 2
            by = screen_pos.y - self._bubble_surf.get_height() - 4
            surface.blit(self._bubble_surf, (bx, by))
