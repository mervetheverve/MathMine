"""Menu UI - title screen and pause menu."""
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT, COLOR_UI_HIGHLIGHT,
)


class MenuUI:
    """Title screen and pause menu."""

    def __init__(self):
        self.font_title = pygame.font.SysFont('arial', 48, bold=True)
        self.font_subtitle = pygame.font.SysFont('arial', 20)
        self.font_button = pygame.font.SysFont('arial', 24)
        self.font_small = pygame.font.SysFont('arial', 14)
        self.button_rects = {}

    def draw_title(self, surface, has_save=False):
        """Draw the title screen."""
        surface.fill((25, 30, 40))

        # Title
        title = self.font_title.render('MathCraft', True, (46, 204, 113))
        surface.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 120))

        # Subtitle
        sub = self.font_subtitle.render(
            'Explore. Collect. Craft. Build!', True, (180, 180, 190))
        surface.blit(sub, ((SCREEN_WIDTH - sub.get_width()) // 2, 185))

        # Buttons
        self.button_rects = {}
        btn_w, btn_h = 200, 50
        btn_x = (SCREEN_WIDTH - btn_w) // 2
        start_y = 280

        # New Game button
        new_rect = pygame.Rect(btn_x, start_y, btn_w, btn_h)
        self.button_rects['new_game'] = new_rect
        self._draw_button(surface, new_rect, 'New Game')

        # Continue button (only if save exists)
        if has_save:
            cont_rect = pygame.Rect(btn_x, start_y + 70, btn_w, btn_h)
            self.button_rects['continue'] = cont_rect
            self._draw_button(surface, cont_rect, 'Continue')

        # Version info
        ver = self.font_small.render('MathCraft v1.0 - Phase 1', True,
                                     (100, 100, 110))
        surface.blit(ver, ((SCREEN_WIDTH - ver.get_width()) // 2,
                           SCREEN_HEIGHT - 30))

    def draw_pause(self, surface):
        """Draw the pause menu overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.font_title.render('Paused', True, COLOR_UI_TEXT)
        surface.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 180))

        # Buttons
        self.button_rects = {}
        btn_w, btn_h = 200, 50
        btn_x = (SCREEN_WIDTH - btn_w) // 2

        resume_rect = pygame.Rect(btn_x, 280, btn_w, btn_h)
        self.button_rects['resume'] = resume_rect
        self._draw_button(surface, resume_rect, 'Resume')

        save_rect = pygame.Rect(btn_x, 350, btn_w, btn_h)
        self.button_rects['save_quit'] = save_rect
        self._draw_button(surface, save_rect, 'Save & Quit')

    def handle_click(self, pos):
        """Check if a button was clicked. Returns button name or None."""
        for name, rect in self.button_rects.items():
            if rect.collidepoint(pos):
                return name
        return None

    def _draw_button(self, surface, rect, text):
        """Draw a styled button."""
        # Check hover
        mx, my = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mx, my)

        bg = COLOR_UI_HIGHLIGHT if hovered else (60, 60, 75)
        pygame.draw.rect(surface, bg, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_UI_BORDER, rect, 2, border_radius=8)

        label = self.font_button.render(text, True, (255, 255, 255))
        label_rect = label.get_rect(center=rect.center)
        surface.blit(label, label_rect)
