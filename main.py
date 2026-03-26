"""MathCraft - Main game entry point."""
import sys
import os
import random
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE, HUD_HEIGHT,
    PORTAL_CHARGE_MULTIPLIER,
)
from states import GameState
from player.player import Player
from player.inventory import Inventory
from world.tilemap import Camera, TILE_SPAWN, TILE_PORTAL, TILE_STATION
from world.biomes import (
    BIOMES, BIOME_ORDER, HUB_PORTAL_BIOMES,
    create_tilemap, get_next_biome,
)
from world.entities import NumberBlock, CraftingStation, Portal, HintStone
from systems.blueprint import (
    Blueprint, BIOME_TEMPLATES,
    create_blueprint_from_template,
)
from systems.crafting import compute, check_against_blueprint
from systems.difficulty import AdaptiveDifficulty
from systems.portal import PortalSystem
from systems.feedback import generate_feedback, generate_penalty_feedback
from systems.save import SaveManager
from systems.sounds import SoundManager
from systems.particles import ParticleSystem
from ui.hud import HUD
from ui.crafting_ui import CraftingUI
from ui.blueprint_ui import BlueprintUI
from ui.feedback_ui import FeedbackUI
from ui.menu import MenuUI

# Biome portal colors for hub display
_BIOME_PORTAL_COLORS = {
    'stacklands': (106, 190, 48),
    'crumble_caves': (120, 100, 85),
    'factor_forest': (58, 120, 50),
    'dividing_desert': (218, 190, 130),
}


class Game:
    """Main game class - orchestrates all systems."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('MathCraft')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.TITLE

        # Systems
        self.difficulty = AdaptiveDifficulty()
        self.portal_system = PortalSystem()
        self.save_manager = SaveManager()
        self.sound = SoundManager()
        self.sound.init()
        self.particles = ParticleSystem()

        # UI
        self.hud = HUD()
        self.crafting_ui = CraftingUI()
        self.blueprint_ui = BlueprintUI()
        self.feedback_ui = FeedbackUI()
        self.menu_ui = MenuUI()

        # Game state
        self.current_biome = 'hub'
        self.score = 0
        self.current_blueprint = None
        self.blueprint_index = 0
        self.attempt_count = 0
        self.completed_blueprints = []
        self.unlocked_biomes = ['stacklands']

        # World objects (set up in load_biome)
        self.tilemap = None
        self.camera = None
        self.player = None
        self.blocks_group = pygame.sprite.Group()
        self.stations_group = pygame.sprite.Group()
        self.portals_group = pygame.sprite.Group()
        self.hints_group = pygame.sprite.Group()
        self.portal_entity = None
        self.hub_portals = []  # list of Portal entities in hub

        # Interaction prompts
        self.near_station = False
        self.near_portal = False
        self.near_hub_portal = None  # the hub portal entity we're near
        self.prompt_font = pygame.font.SysFont('arial', 18, bold=True)

        # Hint stone (spawned near station when struggling)
        self.hint_stone = None
        self.wrong_attempts = 0
        self._last_wrong_combo = None

        # Penalty system
        self.consecutive_wrong = 0

    def load_biome(self, biome_key, player_pos=None):
        """Load a biome - create tilemap, spawn entities."""
        self.current_biome = biome_key
        biome_data = BIOMES[biome_key]

        # Create tilemap
        self.tilemap = create_tilemap(biome_key)
        self.camera = Camera(self.tilemap.pixel_width, self.tilemap.pixel_height)

        # Find spawn point
        spawn = self.tilemap.find_tile(TILE_SPAWN)
        if player_pos:
            col = player_pos[0] // TILE_SIZE
            row = player_pos[1] // TILE_SIZE
        elif spawn:
            col, row = spawn
        else:
            col, row = 3, 3

        # Create player
        if self.player is None:
            self.player = Player(col * TILE_SIZE, row * TILE_SIZE)
        else:
            self.player.set_grid_pos(col, row)

        # Clear old entities
        self.blocks_group.empty()
        self.stations_group.empty()
        self.portals_group.empty()
        self.hints_group.empty()
        self.hint_stone = None
        self.portal_entity = None
        self.hub_portals = []
        self.near_hub_portal = None
        self.consecutive_wrong = 0

        if biome_key == 'hub':
            self._load_hub()
        else:
            self._load_gameplay_biome(biome_data, biome_key)

    def _load_hub(self):
        """Set up the hub with 4 portal doors."""
        self.current_blueprint = None

        # Find all portal tiles, sort by (row, col) for consistent assignment
        portal_tiles = self.tilemap.find_all_tiles(TILE_PORTAL)
        portal_tiles.sort(key=lambda t: (t[1], t[0]))  # sort by row then col

        for i, (col, row) in enumerate(portal_tiles):
            if i < len(HUB_PORTAL_BIOMES):
                dest = HUB_PORTAL_BIOMES[i]
                is_locked = dest not in self.unlocked_biomes
                biome_name = BIOMES[dest]['name']
                portal_color = _BIOME_PORTAL_COLORS.get(dest)
                portal = Portal(
                    col * TILE_SIZE - TILE_SIZE // 2,
                    row * TILE_SIZE - TILE_SIZE // 2,
                    dest,
                    locked=is_locked,
                    label=biome_name,
                    portal_color=portal_color,
                )
                if not is_locked:
                    portal.charge_current = portal.charge_max
                    portal._render()
                self.hub_portals.append(portal)
                self.portals_group.add(portal)

    def _load_gameplay_biome(self, biome_data, biome_key):
        """Set up a regular gameplay biome with station, portal, blocks."""
        operation = biome_data['operations'][0]

        # Spawn crafting station(s)
        station_tiles = self.tilemap.find_all_tiles(TILE_STATION)
        for col, row in station_tiles:
            station = CraftingStation(col * TILE_SIZE, row * TILE_SIZE,
                                      operation)
            self.stations_group.add(station)

        # Spawn portal back to hub
        portal_tile = self.tilemap.find_tile(TILE_PORTAL)
        if portal_tile:
            dest = get_next_biome(biome_key)
            self.portal_entity = Portal(
                portal_tile[0] * TILE_SIZE - TILE_SIZE // 2,
                portal_tile[1] * TILE_SIZE - TILE_SIZE // 2,
                dest
            )
            self.portal_entity.charge_current = self.portal_system.charge
            self.portal_entity._render()
            self.portals_group.add(self.portal_entity)

        # Load blueprint for this biome
        self._load_next_blueprint()

        # Spawn number blocks
        self._spawn_blocks()

    def _load_next_blueprint(self):
        """Load the next blueprint with targets based on current difficulty."""
        templates = BIOME_TEMPLATES.get(self.current_biome,
                                        BIOME_TEMPLATES['stacklands'])

        # Cycle through templates
        self.blueprint_index = (self.blueprint_index + 1) % len(templates)
        template = templates[self.blueprint_index]

        # Generate fresh targets from the difficulty system
        operation = BIOMES[self.current_biome]['operations'][0]
        self.current_blueprint = create_blueprint_from_template(
            template, self.difficulty, operation)
        self.attempt_count = 0

    def _spawn_blocks(self):
        """Spawn number blocks in the world based on difficulty and blueprint."""
        self.blocks_group.empty()
        biome_data = BIOMES[self.current_biome]
        operation = biome_data['operations'][0]

        if self.current_blueprint:
            block_data = self.difficulty.generate_blocks_for_blueprint(
                self.current_blueprint, operation)
        else:
            # Fallback: random blocks
            block_data = [(random.randint(1, 9), 1) for _ in range(10)]

        # Collect portal and station positions to keep blocks away from them
        excluded = set()
        portal_tile = self.tilemap.find_tile(TILE_PORTAL)
        if portal_tile:
            pc, pr = portal_tile
            # Portal sprite is 2x2 — exclude a generous area around it
            for dr in range(-1, 3):
                for dc in range(-1, 3):
                    excluded.add((pc + dc, pr + dr))
        for sc, sr in self.tilemap.find_all_tiles(TILE_STATION):
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    excluded.add((sc + dc, sr + dr))

        # Find floor positions for block placement
        floor_positions = []
        for row in range(self.tilemap.rows):
            for col in range(self.tilemap.cols):
                tile = self.tilemap.get_tile(col, row)
                if tile != 0:  # only plain floor
                    continue
                # Skip tiles adjacent to any wall (all four sides)
                if (self.tilemap.is_wall(col, row - 1) or
                        self.tilemap.is_wall(col - 1, row) or
                        self.tilemap.is_wall(col + 1, row) or
                        self.tilemap.is_wall(col, row + 1)):
                    continue
                # Skip tiles near portal or station
                if (col, row) in excluded:
                    continue
                floor_positions.append((col, row))

        # Remove positions too close to the player
        if self.player:
            pcol, prow = self.player.grid_col, self.player.grid_row
        else:
            spawn = self.tilemap.find_tile(TILE_SPAWN)
            pcol, prow = spawn if spawn else (0, 0)
        floor_positions = [
            (c, r) for c, r in floor_positions
            if abs(c - pcol) + abs(r - prow) > 2
        ]

        random.shuffle(floor_positions)

        for i, (value, tier) in enumerate(block_data):
            if i < len(floor_positions):
                col, row = floor_positions[i]
                x = col * TILE_SIZE + 3
                y = row * TILE_SIZE + 3
                block = NumberBlock(x, y, value, tier)
                self.blocks_group.add(block)

    def _show_hint_stone(self):
        """Spawn or update a hint stone near the crafting station."""
        if not self.current_blueprint:
            return
        target = self.current_blueprint.get_next_target()
        if target is None:
            return
        op = BIOMES[self.current_biome]['operations'][0]
        a, b = self.difficulty.generate_pair_for_target(target, op)
        op_display = {'*': 'x', '/': '\u00f7'}.get(op, op)
        hint_text = f"Need {target}?  Try {a} {op_display} {b}"

        if self.hint_stone:
            self.hint_stone.set_hint(hint_text)
            self.hint_stone.set_visible(True)
        else:
            # Place near the first crafting station
            station_tiles = self.tilemap.find_all_tiles(TILE_STATION)
            if station_tiles:
                sc, sr = station_tiles[0]
                hx = (sc + 1) * TILE_SIZE + 2
                hy = sr * TILE_SIZE + 2
            else:
                hx, hy = 160, 160
            self.hint_stone = HintStone(hx, hy, hint_text)
            self.hints_group.add(self.hint_stone)

    def _hide_hint_stone(self):
        """Hide the hint stone."""
        if self.hint_stone:
            self.hint_stone.set_visible(False)

    def _drop_last_block(self):
        """Drop the last block in inventory slightly below the player."""
        if self.player.inventory.count() == 0:
            return
        item = self.player.inventory.remove(self.player.inventory.count() - 1)
        if item:
            x = self.player.rect.x + 2
            y = self.player.rect.y + TILE_SIZE + 4
            block = NumberBlock(x, y, item.value, item.tier)
            block._pickup_immune = pygame.time.get_ticks() + 500
            self.blocks_group.add(block)
            self.sound.play('pickup')

    def _apply_wrong_penalty(self):
        """Apply penalty for 3 consecutive wrong combos."""
        charge_lost = self.portal_system.remove_charge(10)
        charge_remaining = self.portal_system.charge

        # Update portal visual
        if self.portal_entity:
            self.portal_entity.charge_current = self.portal_system.charge
            self.portal_entity._render()

        # Red flash + penalty sound + feedback
        self.crafting_ui.flash('penalty')
        self.sound.play('penalty')
        fb = generate_penalty_feedback(charge_lost, charge_remaining)
        self.feedback_ui.show(fb)

        self.consecutive_wrong = 0

        # If portal charge is 0, kick to hub
        if self.portal_system.charge <= 0:
            self._kick_to_hub()

    def _kick_to_hub(self):
        """Player lost all portal charge — reset biome progress and go to hub."""
        self.portal_system.reset()
        if self.current_blueprint:
            self.current_blueprint.reset()
        self.load_biome('hub')
        self.state = GameState.PLAYING

    def _unlock_next_biome(self):
        """Unlock the next biome in progression order."""
        for biome in BIOME_ORDER:
            if biome not in self.unlocked_biomes:
                self.unlocked_biomes.append(biome)
                return

    def new_game(self):
        """Start a new game."""
        self.score = 0
        self.current_biome = 'hub'
        self.difficulty = AdaptiveDifficulty()
        self.portal_system = PortalSystem()
        self.completed_blueprints = []
        self.blueprint_index = 0
        self.unlocked_biomes = ['stacklands']
        self.player = None
        self.load_biome('hub')
        self.state = GameState.PLAYING
        self.blueprint_ui.visible = False

    def continue_game(self):
        """Load saved game."""
        data = self.save_manager.load()
        if not data:
            self.new_game()
            return

        self.score = data.get('score', 0)
        self.current_biome = data.get('biome', 'hub')
        self.completed_blueprints = data.get('completed_blueprints', [])
        self.unlocked_biomes = data.get('unlocked_biomes', ['stacklands'])
        self.difficulty.deserialize(data.get('difficulty', {}))
        self.portal_system.deserialize(data.get('portal', {}))

        player_data = data.get('player', {})
        pos = (player_data.get('x', 100), player_data.get('y', 100))

        self.player = None
        self.load_biome(self.current_biome, player_pos=pos)

        # Restore inventory
        inv_data = data.get('inventory', [])
        self.player.inventory.deserialize(inv_data)

        # Restore blueprint progress
        bp_data = data.get('blueprint_progress')
        if bp_data:
            self.current_blueprint = Blueprint.deserialize(bp_data)

        self.state = GameState.PLAYING
        self.blueprint_ui.visible = False

    def save_game(self):
        """Save current game state."""
        state = {
            'version': 2,
            'score': self.score,
            'biome': self.current_biome,
            'player': {
                'x': self.player.rect.x,
                'y': self.player.rect.y,
            },
            'inventory': self.player.inventory.serialize(),
            'difficulty': self.difficulty.serialize(),
            'portal': self.portal_system.serialize(),
            'completed_blueprints': self.completed_blueprints,
            'unlocked_biomes': self.unlocked_biomes,
            'blueprint_progress': (self.current_blueprint.serialize()
                                   if self.current_blueprint else None),
        }
        self.save_manager.save(state)

    def run(self):
        """Main game loop."""
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Process all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.state == GameState.PLAYING:
                    self.save_game()
                self.running = False
                return

            if self.state == GameState.TITLE:
                self._handle_title_event(event)
            elif self.state == GameState.PLAYING:
                self._handle_playing_event(event)
            elif self.state == GameState.CRAFTING:
                self._handle_crafting_event(event)
            elif self.state == GameState.FEEDBACK:
                self.feedback_ui.handle_event(event)
            elif self.state == GameState.PAUSED:
                self._handle_pause_event(event)

    def _handle_title_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.menu_ui.handle_click(event.pos)
            if action == 'new_game':
                self.new_game()
            elif action == 'continue':
                self.continue_game()

    def _handle_playing_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
            elif event.key == pygame.K_b:
                self.blueprint_ui.toggle()
            elif event.key == pygame.K_d:
                self._drop_last_block()
            elif event.key in (pygame.K_e, pygame.K_SPACE):
                if self.near_station and self.current_biome != 'hub':
                    self.crafting_ui.reset()
                    ops = BIOMES[self.current_biome]['operations']
                    self.crafting_ui.selected_op = ops[0]
                    if self.player.inventory.count() < 2:
                        self._spawn_blocks()
                    self.state = GameState.CRAFTING

    def _handle_crafting_event(self, event):
        operations = BIOMES[self.current_biome]['operations']
        result = self.crafting_ui.handle_event(
            event, self.player.inventory, operations)

        if result == 'close':
            self.consecutive_wrong = 0
            self.state = GameState.PLAYING
            return

        if result != 'submit':
            return  # just selecting blocks, not submitting yet

        # Player pressed Enter or clicked Submit — evaluate their answer
        if not self.current_blueprint:
            return

        solve = self.crafting_ui.check_auto_solve(
            self.player.inventory, self.current_blueprint)
        if solve:
            result_val, slot_idx, selected_indices = solve
            # Mark the blueprint slot as filled
            self.current_blueprint.slots[slot_idx].filled = True
            # Remove used blocks (higher indices first to avoid shift issues)
            for idx in sorted(selected_indices, reverse=True):
                self.player.inventory.remove(idx)

            # Score and charge
            tier = self.difficulty.current_tier
            self.score += 10 * tier
            charge = self.portal_system.add_charge(tier, correct=True)
            self.difficulty.record_correct(
                answer_key=f"{result_val}")

            # Update portal visual
            if self.portal_entity:
                self.portal_entity.charge_current = self.portal_system.charge
                self.portal_entity._render()

            # Show success feedback
            fb = generate_feedback(result_val, result_val, 1,
                                   BIOMES[self.current_biome]['operations'][0])
            self.feedback_ui.show(fb)
            self.crafting_ui.flash('success')
            self.sound.play('correct')
            self.attempt_count = 0
            self.wrong_attempts = 0
            self.consecutive_wrong = 0
            self._last_wrong_combo = None
            self._hide_hint_stone()

            # Check blueprint completion
            if self.current_blueprint.is_complete():
                self.completed_blueprints.append(
                    self.current_blueprint.bp_id)
                self.score += 50
                self.sound.play('blueprint_complete')
                self._load_next_blueprint()

            # Always respawn blocks after a successful craft
            self._spawn_blocks()

            self.state = GameState.FEEDBACK
        else:
            # Wrong answer — only count on submit
            target = self.current_blueprint.get_next_target()
            if target and self.crafting_ui.result is not None:
                self.wrong_attempts += 1
                self.consecutive_wrong += 1
                self.sound.play('wrong')
                self.crafting_ui.flash('error')
                if self.wrong_attempts >= 2:
                    self._show_hint_stone()
                # Penalty at 3 consecutive wrong
                if self.consecutive_wrong >= 3:
                    self._apply_wrong_penalty()
                    self.state = GameState.FEEDBACK
                    return

    def _handle_pause_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = GameState.PLAYING
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = self.menu_ui.handle_click(event.pos)
            if action == 'resume':
                self.state = GameState.PLAYING
            elif action == 'save_quit':
                self.save_game()
                self.state = GameState.TITLE

    def _update(self):
        """Update game state."""
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.tilemap)
            self.camera.update(self.player)

            # Check block pickup (not in hub)
            if self.current_biome != 'hub':
                player_rect = self.player.rect
                now = pygame.time.get_ticks()
                for block in list(self.blocks_group):
                    if getattr(block, '_pickup_immune', 0) > now:
                        continue
                    if player_rect.colliderect(block.rect):
                        if self.player.inventory.add(block.value, block.tier):
                            # Sparkle effect at block center
                            self.particles.emit_sparkle(
                                block.rect.centerx, block.rect.centery)
                            block.kill()
                            self.sound.play('pickup')

            # Check proximity to crafting station
            self.near_station = False
            player_rect = self.player.rect
            for station in self.stations_group:
                dist = ((player_rect.centerx - station.rect.centerx) ** 2 +
                        (player_rect.centery - station.rect.centery) ** 2) ** 0.5
                if dist < TILE_SIZE * 2:
                    self.near_station = True
                    break

            if self.current_biome == 'hub':
                self._update_hub_portals()
            else:
                self._update_biome_portal()

            # Update particles
            self.particles.update()

        elif self.state == GameState.FEEDBACK:
            if not self.feedback_ui.update():
                # Feedback done - return to appropriate state
                fb = self.feedback_ui.feedback
                if fb and fb.feedback_type == 'penalty':
                    # After penalty feedback, if we're in hub we stay in PLAYING
                    # If still in biome, return to crafting
                    if self.current_biome == 'hub':
                        self.state = GameState.PLAYING
                    else:
                        self.crafting_ui.reset()
                        ops = BIOMES[self.current_biome]['operations']
                        self.crafting_ui.selected_op = ops[0]
                        self.state = GameState.CRAFTING
                elif fb and fb.feedback_type != 'correct':
                    self.state = GameState.CRAFTING
                elif self.player.inventory.count() >= 2:
                    # Still have blocks — stay in crafting, reset selection
                    self.crafting_ui.reset()
                    ops = BIOMES[self.current_biome]['operations']
                    self.crafting_ui.selected_op = ops[0]
                    self.state = GameState.CRAFTING
                else:
                    self.state = GameState.PLAYING

    def _update_hub_portals(self):
        """Check proximity to hub portals and auto-enter unlocked ones."""
        player_rect = self.player.rect
        self.near_hub_portal = None
        for portal in self.hub_portals:
            dist = ((player_rect.centerx - portal.rect.centerx) ** 2 +
                    (player_rect.centery - portal.rect.centery) ** 2) ** 0.5
            if dist < TILE_SIZE * 2.5:
                self.near_hub_portal = portal
                if not portal.locked:
                    # Auto-enter the biome
                    dest = portal.destination
                    self.portal_system.reset()
                    self.difficulty = AdaptiveDifficulty()
                    self.load_biome(dest)
                break

    def _update_biome_portal(self):
        """Check proximity to biome portal and auto-transition when ready."""
        self.near_portal = False
        if self.portal_entity:
            player_rect = self.player.rect
            dist = ((player_rect.centerx - self.portal_entity.rect.centerx) ** 2 +
                    (player_rect.centery - self.portal_entity.rect.centery) ** 2) ** 0.5
            if dist < TILE_SIZE * 2.5:
                self.near_portal = True
                if self.portal_system.is_ready():
                    # Unlock next biome and go to hub
                    self._unlock_next_biome()
                    self.portal_system.reset()
                    self.difficulty = AdaptiveDifficulty()
                    self.load_biome('hub')

    def _draw(self):
        """Render everything."""
        self.screen.fill((0, 0, 0))

        if self.state == GameState.TITLE:
            self.menu_ui.draw_title(self.screen,
                                    self.save_manager.has_save())

        elif self.state in (GameState.PLAYING, GameState.CRAFTING,
                            GameState.FEEDBACK, GameState.PAUSED):
            # Draw world
            self.tilemap.draw(self.screen, self.camera)

            # Draw entities (back to front by y position)
            all_drawables = []
            for block in self.blocks_group:
                all_drawables.append(block)
            for station in self.stations_group:
                all_drawables.append(station)
            for portal in self.portals_group:
                all_drawables.append(portal)
            for hint in self.hints_group:
                all_drawables.append(hint)
            all_drawables.append(self.player)

            # Sort by y position for correct overlap
            all_drawables.sort(key=lambda e: e.rect.bottom)
            for entity in all_drawables:
                entity.draw(self.screen, self.camera)

            # Particles (after entities, before UI)
            self.particles.draw(self.screen, self.camera)

            # Interaction prompts
            if self.current_biome == 'hub':
                if self.near_hub_portal and self.state == GameState.PLAYING:
                    p = self.near_hub_portal
                    if p.locked:
                        self._draw_prompt(f'{p.label} - Locked')
                    else:
                        self._draw_prompt(f'Enter {p.label}')
            else:
                if self.near_station and self.state == GameState.PLAYING:
                    prompt = 'SPACE: Craft'
                    if self.player.inventory.count() > 0:
                        prompt += '   D: Drop block'
                    self._draw_prompt(prompt)
                elif self.near_portal and self.state == GameState.PLAYING:
                    if self.portal_system.is_ready():
                        self._draw_prompt('Portal is ready!')
                    else:
                        pct = int(self.portal_system.get_charge_ratio() * 100)
                        self._draw_prompt(f'Portal: {pct}% charged')

            # HUD
            biome_name = BIOMES[self.current_biome]['name']
            self.hud.draw(self.screen, self.player.inventory,
                          self.score, biome_name, self.current_blueprint)

            # Blueprint / Objective UI
            if self.current_biome != 'hub':
                self.blueprint_ui.draw(self.screen, self.current_blueprint)
                if not self.blueprint_ui.visible:
                    self.blueprint_ui.draw_objective_banner(
                        self.screen, self.current_blueprint)

            # Overlay states
            if self.state == GameState.CRAFTING:
                operations = BIOMES[self.current_biome]['operations']
                self.crafting_ui.draw(self.screen, self.player.inventory,
                                     self.current_blueprint, operations)

            if self.state == GameState.FEEDBACK:
                self.feedback_ui.draw(self.screen)

            if self.state == GameState.PAUSED:
                self.menu_ui.draw_pause(self.screen)

        pygame.display.flip()

    def _draw_prompt(self, text):
        """Draw an interaction prompt above the player."""
        prompt = self.prompt_font.render(text, True, (255, 255, 255))
        bg = pygame.Surface((prompt.get_width() + 16, 28), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))

        screen_pos = self.camera.apply_pos(
            self.player.rect.centerx, self.player.rect.top - 35)
        x = screen_pos[0] - prompt.get_width() // 2
        y = screen_pos[1]

        self.screen.blit(bg, (x - 8, y - 4))
        self.screen.blit(prompt, (x, y))


if __name__ == '__main__':
    game = Game()
    game.run()
