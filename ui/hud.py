"""In-game HUD - inventory bar, score, blueprint summary."""
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HUD_HEIGHT, HUD_SLOT_SIZE, HUD_PADDING,
    INVENTORY_MAX,
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT, COLOR_UI_HIGHLIGHT,
    COLOR_BLOCK_T1, COLOR_BLOCK_T2, COLOR_BLOCK_T3,
)

TIER_COLORS = {1: COLOR_BLOCK_T1, 2: COLOR_BLOCK_T2, 3: COLOR_BLOCK_T3}


class HUD:
    """Draws the in-game heads-up display."""

    def __init__(self):
        self.font = pygame.font.SysFont('arial', 16)
        self.font_big = pygame.font.SysFont('arial', 20, bold=True)
        self.font_small = pygame.font.SysFont('arial', 12)

    def draw(self, surface, inventory, score=0, biome_name="", blueprint=None):
        """Draw the HUD at the bottom of the screen."""
        hud_y = SCREEN_HEIGHT - HUD_HEIGHT

        # Background bar
        bg_rect = pygame.Rect(0, hud_y, SCREEN_WIDTH, HUD_HEIGHT)
        bg_surface = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        bg_surface.fill((40, 40, 50, 220))
        surface.blit(bg_surface, (0, hud_y))
        pygame.draw.line(surface, COLOR_UI_BORDER,
                         (0, hud_y), (SCREEN_WIDTH, hud_y), 2)

        # Inventory slots
        total_slots_width = INVENTORY_MAX * (HUD_SLOT_SIZE + HUD_PADDING) - HUD_PADDING
        start_x = (SCREEN_WIDTH - total_slots_width) // 2
        slot_y = hud_y + (HUD_HEIGHT - HUD_SLOT_SIZE) // 2

        for i in range(INVENTORY_MAX):
            x = start_x + i * (HUD_SLOT_SIZE + HUD_PADDING)
            slot_rect = pygame.Rect(x, slot_y, HUD_SLOT_SIZE, HUD_SLOT_SIZE)

            if i < inventory.count():
                item = inventory.items[i]
                color = TIER_COLORS.get(item.tier, COLOR_BLOCK_T1)
                pygame.draw.rect(surface, color, slot_rect, border_radius=4)
                pygame.draw.rect(surface, COLOR_UI_BORDER, slot_rect, 2,
                                 border_radius=4)
                # Number
                text = self.font_big.render(str(item.value), True, (255, 255, 255))
                text_rect = text.get_rect(center=slot_rect.center)
                surface.blit(text, text_rect)
            else:
                # Empty slot
                pygame.draw.rect(surface, (50, 50, 60), slot_rect, border_radius=4)
                pygame.draw.rect(surface, (70, 70, 80), slot_rect, 1,
                                 border_radius=4)

        # Score (top-left of HUD)
        score_text = self.font.render(f'Score: {score}', True, COLOR_UI_TEXT)
        surface.blit(score_text, (10, hud_y + 8))

        # Biome name (top-right of HUD)
        if biome_name:
            biome_text = self.font_small.render(biome_name, True,
                                                (180, 180, 180))
            surface.blit(biome_text,
                         (SCREEN_WIDTH - biome_text.get_width() - 10,
                          hud_y + 8))

        # Blueprint mini-summary (below score)
        if blueprint:
            filled = sum(1 for s in blueprint.slots if s.filled)
            total = len(blueprint.slots)
            bp_text = self.font_small.render(
                f'Blueprint: {blueprint.name} ({filled}/{total})',
                True, (180, 200, 180))
            surface.blit(bp_text, (10, hud_y + 28))
