"""Blueprint display UI - shows the current structure being built."""
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT,
    COLOR_UI_SLOT_EMPTY, COLOR_UI_SLOT_FILLED,
)


class BlueprintUI:
    """Shows the current blueprint and its slot status."""

    def __init__(self):
        self.font = pygame.font.SysFont('arial', 16)
        self.font_big = pygame.font.SysFont('arial', 20, bold=True)
        self.font_small = pygame.font.SysFont('arial', 13)
        self.font_objective = pygame.font.SysFont('arial', 26, bold=True)
        self.font_objective_detail = pygame.font.SysFont('arial', 16)
        self.visible = False  # full panel hidden by default

    def toggle(self):
        self.visible = not self.visible

    def draw(self, surface, blueprint):
        """Draw the full blueprint panel on the right side of the screen."""
        if not self.visible or not blueprint:
            return

        panel_w = 170
        panel_h = 50 + len(blueprint.slots) * 32
        panel_x = SCREEN_WIDTH - panel_w - 8
        panel_y = 8

        # Semi-transparent background
        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((40, 40, 50, 160))
        surface.blit(bg, (panel_x, panel_y))
        pygame.draw.rect(surface, COLOR_UI_BORDER,
                         pygame.Rect(panel_x, panel_y, panel_w, panel_h),
                         1, border_radius=6)

        # Title
        title = self.font_big.render(blueprint.name, True, COLOR_UI_TEXT)
        surface.blit(title, (panel_x + (panel_w - title.get_width()) // 2,
                             panel_y + 6))

        # Slots - compact
        for i, slot in enumerate(blueprint.slots):
            y = panel_y + 34 + i * 30
            slot_rect = pygame.Rect(panel_x + 8, y, panel_w - 16, 26)

            if slot.filled:
                pygame.draw.rect(surface, COLOR_UI_SLOT_FILLED, slot_rect,
                                 border_radius=3)
                check = self.font.render('Done', True, (255, 255, 255))
                surface.blit(check, (slot_rect.right - 38, y + 4))
            else:
                pygame.draw.rect(surface, COLOR_UI_SLOT_EMPTY, slot_rect,
                                 border_radius=3)
                target = self.font.render(str(slot.target), True,
                                          (255, 220, 100))
                surface.blit(target, (slot_rect.right - 30, y + 4))

            label = self.font_small.render(slot.label, True, (200, 200, 200))
            surface.blit(label, (slot_rect.x + 6, y + 6))

    def draw_mini(self, surface, blueprint):
        """Draw a compact indicator showing current target at top-left."""
        if not blueprint:
            return
        filled = sum(1 for s in blueprint.slots if s.filled)
        total = len(blueprint.slots)

        # Show building name + progress + current target
        next_target = blueprint.get_next_target()
        if next_target is not None:
            text = f'Building: {blueprint.name} ({filled}/{total}) - Next: {next_target}'
        else:
            text = f'{blueprint.name} Complete!'

        rendered = self.font_small.render(text, True, (220, 220, 220))
        bg = pygame.Surface((rendered.get_width() + 16, 22), pygame.SRCALPHA)
        bg.fill((40, 40, 50, 160))
        surface.blit(bg, (8, 8))
        surface.blit(rendered, (16, 11))

        # Hint to toggle full view
        hint = self.font_small.render('[B] details', True, (140, 140, 140))
        surface.blit(hint, (rendered.get_width() + 28, 11))

    def draw_objective_banner(self, surface, blueprint):
        """Draw a prominent objective banner at top-center showing current target."""
        if not blueprint:
            return
        next_slot = None
        for slot in blueprint.slots:
            if not slot.filled:
                next_slot = slot
                break
        if next_slot is None:
            return

        # Progress info
        filled = sum(1 for s in blueprint.slots if s.filled)
        total = len(blueprint.slots)

        # Main text: "Make: {target}"
        main_text = self.font_objective.render(
            f'Make: {next_slot.target}', True, (255, 220, 80))
        # Detail: "{label} for {blueprint_name}"
        detail_text = self.font_objective_detail.render(
            f'{next_slot.label} for {blueprint.name}', True, (200, 200, 210))

        # Progress dots
        dot_w = total * 16 + 4
        banner_w = max(main_text.get_width(), detail_text.get_width(),
                       dot_w) + 40
        banner_h = 72
        banner_x = (SCREEN_WIDTH - banner_w) // 2
        banner_y = 6

        # Semi-transparent background
        bg = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        bg.fill((30, 30, 40, 180))
        surface.blit(bg, (banner_x, banner_y))
        pygame.draw.rect(surface, (255, 220, 80, 120),
                         pygame.Rect(banner_x, banner_y, banner_w, banner_h),
                         2, border_radius=8)

        # Main text centered
        surface.blit(main_text, (
            banner_x + (banner_w - main_text.get_width()) // 2,
            banner_y + 6))
        # Detail below
        surface.blit(detail_text, (
            banner_x + (banner_w - detail_text.get_width()) // 2,
            banner_y + 34))

        # Progress dots at bottom
        dots_x = banner_x + (banner_w - total * 16) // 2
        dots_y = banner_y + 55
        for i in range(total):
            color = (46, 204, 113) if i < filled else (80, 80, 90)
            pygame.draw.circle(surface, color,
                               (dots_x + i * 16 + 6, dots_y + 5), 5)
