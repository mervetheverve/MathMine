"""Feedback UI - shows correct/incorrect popups with hints."""
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT,
    COLOR_UI_SUCCESS, COLOR_UI_ERROR,
)


class FeedbackUI:
    """Displays feedback popups for correct/incorrect answers."""

    def __init__(self):
        self.font = pygame.font.SysFont('arial', 20)
        self.font_big = pygame.font.SysFont('arial', 28, bold=True)
        self.font_small = pygame.font.SysFont('arial', 16)
        self.active = False
        self.feedback = None
        self.timer = 0
        self.duration = 120  # frames (2 seconds at 60fps)

    def show(self, feedback_data):
        """Show feedback popup."""
        self.feedback = feedback_data
        self.active = True
        if feedback_data.feedback_type == 'correct':
            self.duration = 90  # shorter for correct
        elif feedback_data.feedback_type == 'penalty':
            self.duration = 150  # medium for penalty
        else:
            self.duration = 180  # longer for hints
        self.timer = self.duration

    def update(self):
        """Update timer. Returns True while active."""
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
                self.feedback = None
        return self.active

    def handle_event(self, event):
        """Handle clicks to dismiss feedback early."""
        if not self.active:
            return
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            self.timer = min(self.timer, 15)  # quick fade

    def draw(self, surface):
        """Draw the feedback popup."""
        if not self.active or not self.feedback:
            return

        fb = self.feedback
        is_correct = fb.feedback_type == 'correct'
        is_penalty = fb.feedback_type == 'penalty'

        # Fade alpha
        alpha = min(255, self.timer * 8)

        # Panel
        panel_w = 420
        panel_h = 150 if is_correct else 180
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 40

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)

        # Background
        if is_correct:
            bg_color = (*COLOR_UI_SUCCESS, min(230, alpha))
        elif is_penalty:
            bg_color = (*COLOR_UI_ERROR, min(200, alpha))
        else:
            bg_color = (*COLOR_UI_BG, min(230, alpha))
        panel_surf.fill(bg_color)

        # Border
        if is_correct:
            border_color = COLOR_UI_SUCCESS
        elif is_penalty:
            border_color = (255, 80, 60)
        else:
            border_color = COLOR_UI_ERROR
        pygame.draw.rect(panel_surf, border_color,
                         pygame.Rect(0, 0, panel_w, panel_h), 3,
                         border_radius=12)

        # Icon
        if is_correct:
            icon = self.font_big.render('\u2605', True, (255, 255, 255))
        elif is_penalty:
            icon = self.font_big.render('\u26a0', True, (255, 255, 100))
        else:
            icon = self.font_big.render('\u2192', True, (255, 200, 100))
        panel_surf.blit(icon, (20, 15))

        # Message
        msg = self.font_big.render(fb.message, True, (255, 255, 255))
        panel_surf.blit(msg, ((panel_w - msg.get_width()) // 2, 20))

        # Detail text
        if fb.feedback_type == 'wrong_decompose':
            detail = self.font.render(fb.detail.get('hint', ''),
                                      True, (255, 230, 150))
            panel_surf.blit(detail, ((panel_w - detail.get_width()) // 2, 65))
        elif fb.feedback_type == 'wrong_example':
            example = self.font.render(fb.detail.get('example', ''),
                                       True, (255, 230, 150))
            panel_surf.blit(example,
                            ((panel_w - example.get_width()) // 2, 65))
        elif fb.feedback_type == 'penalty':
            remaining = fb.detail.get('charge_remaining', 0)
            detail = self.font.render(
                f'Portal charge: {int(remaining)}%',
                True, (255, 200, 180))
            panel_surf.blit(detail, ((panel_w - detail.get_width()) // 2, 65))

        # Dismiss hint
        dismiss = self.font_small.render('Click or press any key to continue',
                                         True, (160, 160, 160))
        panel_surf.blit(dismiss,
                        ((panel_w - dismiss.get_width()) // 2, panel_h - 30))

        surface.blit(panel_surf, (panel_x, panel_y))
