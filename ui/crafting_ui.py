"""Crafting UI overlay - opens when player is near a crafting station."""
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_UI_BG, COLOR_UI_BORDER, COLOR_UI_TEXT, COLOR_UI_HIGHLIGHT,
    COLOR_UI_SUCCESS, COLOR_UI_ERROR, COLOR_UI_SLOT_EMPTY,
    COLOR_BLOCK_T1, COLOR_BLOCK_T2, COLOR_BLOCK_T3,
)
from systems.crafting import compute_multi

TIER_COLORS = {1: COLOR_BLOCK_T1, 2: COLOR_BLOCK_T2, 3: COLOR_BLOCK_T3}

# Kid-friendly operator symbols
_OP_DISPLAY = {'*': 'x', '/': '\u00f7'}


def _op_display(op):
    """Return a display-friendly symbol for an operator."""
    return _OP_DISPLAY.get(op, op)


class CraftingUI:
    """Full-screen overlay for the crafting interface."""

    MAX_SELECTED = 4

    def __init__(self):
        self.font = pygame.font.SysFont('arial', 20)
        self.font_big = pygame.font.SysFont('arial', 32, bold=True)
        self.font_small = pygame.font.SysFont('arial', 16)
        self.font_title = pygame.font.SysFont('arial', 28, bold=True)
        self.font_order = pygame.font.SysFont('arial', 13, bold=True)

        # Selection state
        self.selected_blocks = []  # list of inventory indices, max MAX_SELECTED
        self.selected_op = '+'
        self.result = None

        # Button rects (computed in draw)
        self.slot_rects = []
        self.op_rects = {}
        self.close_rect = pygame.Rect(0, 0, 0, 0)
        self.submit_rect = pygame.Rect(0, 0, 0, 0)

        # Flash effect for auto-solve
        self.flash_timer = 0
        self.flash_type = None  # 'success', 'error', 'penalty'

    def reset(self):
        """Reset selection state."""
        self.selected_blocks = []
        self.selected_op = '+'
        self.result = None
        self.flash_timer = 0
        self.flash_type = None

    def handle_event(self, event, inventory, operations):
        """Handle mouse clicks in the crafting UI.
        Returns: 'close', 'submit', or None."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Close button
            if self.close_rect.collidepoint(mx, my):
                return 'close'

            # Submit button
            if self.submit_rect.collidepoint(mx, my):
                if len(self.selected_blocks) >= 2 and self.result is not None:
                    return 'submit'

            # Inventory slot clicks
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(mx, my) and i < inventory.count():
                    if i in self.selected_blocks:
                        self.selected_blocks.remove(i)  # deselect
                    elif len(self.selected_blocks) < self.MAX_SELECTED:
                        self.selected_blocks.append(i)  # add to selection
                    self._compute_result(inventory)
                    break

            # Operation button clicks
            for op, rect in self.op_rects.items():
                if rect.collidepoint(mx, my) and op in operations:
                    self.selected_op = op
                    self._compute_result(inventory)
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'close'
            elif event.key == pygame.K_RETURN:
                if len(self.selected_blocks) >= 2 and self.result is not None:
                    return 'submit'

        return None

    def _compute_result(self, inventory):
        """Compute the result of the current multi-block selection."""
        if len(self.selected_blocks) >= 2:
            values = []
            for idx in self.selected_blocks:
                if idx < inventory.count():
                    values.append(inventory.items[idx].value)
                else:
                    self.result = None
                    return
            self.result = compute_multi(values, self.selected_op)
        else:
            self.result = None

    def check_auto_solve(self, inventory, blueprint):
        """Check if current selection auto-solves the NEXT blueprint slot.
        Only matches the first unfilled slot (the one shown in the objective).
        Returns (result_value, slot_index, selected_indices_list) or None."""
        if self.result is not None and blueprint and len(self.selected_blocks) >= 2:
            for i, slot in enumerate(blueprint.slots):
                if not slot.filled:
                    if slot.target == self.result:
                        return (self.result, i, list(self.selected_blocks))
                    break  # only check the first unfilled slot
        return None

    def flash(self, flash_type):
        """Trigger a flash effect."""
        self.flash_type = flash_type
        self.flash_timer = 30  # frames

    def draw(self, surface, inventory, blueprint, operations):
        """Draw the crafting overlay."""
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Flash effect
        if self.flash_timer > 0:
            self.flash_timer -= 1
            alpha = int(100 * (self.flash_timer / 30))
            flash_color = COLOR_UI_SUCCESS if self.flash_type == 'success' else COLOR_UI_ERROR
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*flash_color, alpha))
            surface.blit(flash_surf, (0, 0))

        # Main panel
        panel_w, panel_h = 500, 420
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(surface, COLOR_UI_BG, panel, border_radius=12)
        pygame.draw.rect(surface, COLOR_UI_BORDER, panel, 3, border_radius=12)

        # Title
        title = self.font_title.render('Crafting Station', True, COLOR_UI_TEXT)
        surface.blit(title, (panel_x + (panel_w - title.get_width()) // 2,
                             panel_y + 15))

        # Close button (X)
        self.close_rect = pygame.Rect(panel_x + panel_w - 40, panel_y + 10,
                                      30, 30)
        pygame.draw.rect(surface, (180, 60, 60), self.close_rect,
                         border_radius=4)
        x_text = self.font.render('X', True, (255, 255, 255))
        surface.blit(x_text, (self.close_rect.x + 7, self.close_rect.y + 3))

        # Blueprint target info
        if blueprint:
            unfilled = blueprint.get_unfilled_slots()
            if unfilled:
                idx, slot = unfilled[0]
                target_text = self.font.render(
                    f'Build: {slot.label} (need {slot.target})',
                    True, (255, 220, 100))
                surface.blit(target_text,
                             (panel_x + (panel_w - target_text.get_width()) // 2,
                              panel_y + 50))

        # Inventory blocks
        inv_label = self.font_small.render('Your Blocks:', True,
                                           (180, 180, 180))
        surface.blit(inv_label, (panel_x + 20, panel_y + 85))

        # Show help message if inventory is empty
        if inventory.count() == 0:
            empty_msg = self.font.render(
                'Go collect number blocks first!', True, (255, 180, 80))
            surface.blit(empty_msg,
                         (panel_x + (panel_w - empty_msg.get_width()) // 2,
                          panel_y + 140))
            arrow_msg = self.font_small.render(
                'Walk over the numbered tiles in the world',
                True, (150, 150, 150))
            surface.blit(arrow_msg,
                         (panel_x + (panel_w - arrow_msg.get_width()) // 2,
                          panel_y + 170))

        self.slot_rects = []
        slot_size = 52
        cols = 4
        start_x = panel_x + (panel_w - cols * (slot_size + 10) + 10) // 2
        start_y = panel_y + 110

        for i in range(inventory.count()):
            col = i % cols
            row = i // cols
            x = start_x + col * (slot_size + 10)
            y = start_y + row * (slot_size + 10)
            rect = pygame.Rect(x, y, slot_size, slot_size)
            self.slot_rects.append(rect)

            item = inventory.items[i]
            color = TIER_COLORS.get(item.tier, COLOR_BLOCK_T1)

            # Highlight if selected
            if i in self.selected_blocks:
                pygame.draw.rect(surface, COLOR_UI_HIGHLIGHT,
                                 rect.inflate(6, 6), border_radius=6)

            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_UI_BORDER, rect, 2,
                             border_radius=6)

            # Number
            text = self.font_big.render(str(item.value), True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

            # Selection order number badge
            if i in self.selected_blocks:
                order = self.selected_blocks.index(i) + 1
                order_text = self.font_order.render(
                    str(order), True, (255, 255, 100))
                surface.blit(order_text, (rect.x + 3, rect.y + 2))

        # Operation buttons
        op_y = start_y + ((inventory.count() // cols + 1) * (slot_size + 10)) + 10
        op_y = max(op_y, panel_y + 250)
        self.op_rects = {}
        op_list = operations
        op_start_x = panel_x + panel_w // 2 - len(op_list) * 35

        for j, op in enumerate(op_list):
            rect = pygame.Rect(op_start_x + j * 70, op_y, 50, 40)
            self.op_rects[op] = rect
            is_selected = op == self.selected_op

            bg_color = COLOR_UI_HIGHLIGHT if is_selected else (70, 70, 85)
            pygame.draw.rect(surface, bg_color, rect, border_radius=6)
            pygame.draw.rect(surface, COLOR_UI_BORDER, rect, 2,
                             border_radius=6)

            display = _op_display(op)
            text = self.font_big.render(display, True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)

        # Result display
        result_y = op_y + 55
        if len(self.selected_blocks) >= 2:
            values = [inventory.items[idx].value
                      for idx in self.selected_blocks
                      if idx < inventory.count()]
            op_sym = _op_display(self.selected_op)
            eq_str = f' {op_sym} '.join(str(v) for v in values) + ' = '
            if self.result is not None:
                eq_str += str(self.result)
            else:
                eq_str += '???'
            # Use smaller font if equation is too wide
            eq_font = self.font_big
            eq_text = eq_font.render(eq_str, True, COLOR_UI_TEXT)
            if eq_text.get_width() > panel_w - 40:
                eq_font = self.font
                eq_text = eq_font.render(eq_str, True, COLOR_UI_TEXT)
            surface.blit(eq_text,
                         (panel_x + (panel_w - eq_text.get_width()) // 2,
                          result_y))

            # Submit button
            submit_y = result_y + 40
            btn_w, btn_h = 140, 38
            self.submit_rect = pygame.Rect(
                panel_x + (panel_w - btn_w) // 2, submit_y, btn_w, btn_h)
            can_submit = self.result is not None
            btn_color = (46, 160, 100) if can_submit else (70, 70, 85)
            pygame.draw.rect(surface, btn_color, self.submit_rect,
                             border_radius=8)
            pygame.draw.rect(surface, COLOR_UI_BORDER, self.submit_rect, 2,
                             border_radius=8)
            submit_label = self.font.render('Submit (Enter)', True,
                                            (255, 255, 255))
            surface.blit(submit_label,
                         (self.submit_rect.x +
                          (btn_w - submit_label.get_width()) // 2,
                          self.submit_rect.y + 8))
        else:
            self.submit_rect = pygame.Rect(0, 0, 0, 0)
            op_names = ' or '.join(_op_display(o) for o in operations)
            hint = self.font_small.render(
                f'Click 2-4 blocks, then press Enter',
                True, (140, 140, 140))
            surface.blit(hint,
                         (panel_x + (panel_w - hint.get_width()) // 2,
                          result_y + 8))
