# MathCraft — Complete Project State & Implementation Reference

## Project Overview
MathCraft is an educational math game for an 8-9 year old girl, built with Python 3.13.5 and Pygame 2.6.1. The player explores a Zelda-style top-down world, collects number blocks, combines them at crafting stations to solve equations, fills blueprint slots to build structures, and charges a portal to travel between biomes. Each biome teaches a different math operation.

**Run command:** `python main.py`
**Project root:** `C:\Users\GabeC\OneDrive\Desktop\Python Projects\MathMine`

---

## File Structure & Complete Code Map

```
MathMine/
├── main.py                  # Game class — orchestrates all systems (590 lines)
├── settings.py              # All constants: screen, tiles, colors, difficulty (96 lines)
├── states.py                # GameState enum: TITLE, PLAYING, CRAFTING, FEEDBACK, PAUSED (13 lines)
├── player/
│   ├── player.py            # Player sprite — grid movement, collision, face rendering (126 lines)
│   └── inventory.py         # Inventory class — list of InventoryItems, max 8 (47 lines)
├── world/
│   ├── biomes.py            # Biome definitions — layouts, colors, BIOMES dict (104 lines)
│   ├── tilemap.py           # TileMap + Camera — tile rendering, collision, 3/4 perspective (141 lines)
│   └── entities.py          # NumberBlock, CraftingStation, Portal, HintStone sprites (279 lines)
├── systems/
│   ├── difficulty.py        # AdaptiveDifficulty — 5 tiers, streak tracking, pair generation (154 lines)
│   ├── crafting.py          # compute(a, b, op) — currently handles + and - only
│   ├── blueprint.py         # Blueprint + Slot classes, templates per biome (95 lines)
│   ├── portal.py            # PortalSystem — charge tracking, tier-weighted charging (46 lines)
│   ├── feedback.py          # 3-level hint escalation: show → decompose → worked example (86 lines)
│   ├── sounds.py            # SoundManager — synthesized tones, no external files (112 lines)
│   └── save.py              # SaveManager — JSON persistence (42 lines)
├── ui/
│   ├── hud.py               # Bottom bar — inventory slots, score, biome name, blueprint summary (78 lines)
│   ├── crafting_ui.py       # Full-screen crafting overlay — block selection, operation, result (254 lines)
│   ├── blueprint_ui.py      # Blueprint panel (toggleable) + mini indicator (88 lines)
│   ├── feedback_ui.py       # Popup overlay for correct/wrong feedback (107 lines)
│   └── menu.py              # Title screen + pause menu (98 lines)
├── saves/
│   └── save.json            # Auto-saved game state
└── data/                    # (empty, reserved for future assets)
```

---

## Core Game Loop (main.py)

The `Game` class owns everything. The main loop is:
```
while running:
    clock.tick(60)
    _handle_events()   # Input → state transitions
    _update()          # Game logic (movement, pickup, portal)
    _draw()            # Render world, entities, UI overlays
```

### State Machine (states.py)
```
TITLE → (New Game / Continue) → PLAYING
PLAYING → (SPACE at station) → CRAFTING
CRAFTING → (auto-solve match) → FEEDBACK → PLAYING or CRAFTING
PLAYING → (ESC) → PAUSED → (Resume / Save & Quit) → PLAYING or TITLE
```
Unused states exist in the enum: `BLUEPRINT_VIEW`, `PORTAL_CHALLENGE`.

### Key Bindings
| Key | State | Action |
|-----|-------|--------|
| Arrow keys | PLAYING | Move player (grid-snapped, 8-frame cooldown) |
| SPACE or E | PLAYING (near station) | Open crafting UI |
| D | PLAYING | Drop last inventory block |
| B | PLAYING | Toggle blueprint detail panel |
| ESC | PLAYING | Pause menu |
| ESC | CRAFTING | Close crafting UI |
| Click | CRAFTING | Select blocks, operator, close button |
| Click/any key | FEEDBACK | Dismiss popup early |

---

## World System

### Tile Types (tilemap.py)
```python
TILE_FLOOR   = 0   # walkable, renders as checkerboard
TILE_WALL    = 1   # impassable, 3/4 perspective (top face + 16px front face)
TILE_SPAWN   = 2   # player start position (renders as floor)
TILE_PORTAL  = 3   # portal location (renders as floor)
TILE_STATION = 4   # crafting station location (renders as floor)
```

### Camera (tilemap.py)
- Centers player in the visible area above the HUD
- `visible_height = SCREEN_HEIGHT - HUD_HEIGHT` (600 - 80 = 520)
- Clamped to map bounds so the map never scrolls past edges
- Bottom clamp uses `visible_height` not `SCREEN_HEIGHT` so map content doesn't hide behind HUD

### Biomes (biomes.py)
Each biome is a dict:
```python
{
    'name': 'Display Name',           # shown in HUD top-right
    'layout': 25x20_tile_grid,        # using F, W, S, P, C shorthand
    'colors': {                        # 4 colors for floor/wall rendering
        'floor': (r, g, b),
        'floor_alt': (r, g, b),        # checkerboard alternating
        'wall_top': (r, g, b),
        'wall_front': (r, g, b),
    },
    'operations': ['+'],              # list with one operation string
    'block_count': 12,                # number of blocks to spawn
}
```

**Current biomes:**
- `'stacklands'` — The Stacklands (addition) — bright green fields, open layout with 4 interior wall clusters
- `'crumble_caves'` — The Crumble Caves (subtraction) — brown/gray underground, more confined with cave-like walls

**Biome color constants** live in `settings.py`:
```python
# Stacklands: green fields
COLOR_STACKLANDS_FLOOR      = (106, 190, 48)
COLOR_STACKLANDS_FLOOR_ALT  = (118, 200, 58)
COLOR_STACKLANDS_WALL_TOP   = (80, 120, 50)
COLOR_STACKLANDS_WALL_FRONT = (55, 85, 35)

# Crumble Caves: brown stone
COLOR_CAVES_FLOOR      = (120, 100, 85)
COLOR_CAVES_FLOOR_ALT  = (110, 92, 78)
COLOR_CAVES_WALL_TOP   = (75, 60, 50)
COLOR_CAVES_WALL_FRONT = (50, 40, 35)
```

### Entities (entities.py)

**NumberBlock** — Collectible number tile
- 30px square with 4px glow padding, 10px 3/4 depth front face
- 3 tier colors: gray (T1), gold (T2), purple (T3)
- Glow effect, highlight edge on top, text shadow behind number
- Font: Arial 18 bold
- `rect.x = x - glow` (glow offset affects world position)

**CraftingStation** — Where player combines blocks
- TILE_SIZE (32px) square with WALL_HEIGHT (16px) depth
- Shows "+" symbol on top (hardcoded, not operation-aware)
- Brown wood colors

**Portal** — Connects biomes
- 2×TILE_SIZE (64px) square with depth and charge bar
- Color interpolates from dark to teal based on charge ratio
- Shows percentage or "ENTER" text
- Charge bar below portal frame
- `charge_current` / `charge_max` (100.0)

**HintStone** — Decomposition hint near station
- 28px stone with "?" symbol
- Speech bubble rendered above showing hint text
- Appears after 2 wrong combos, hides on correct answer

---

## Player System

### Player (player/player.py)
- Grid-snapped movement: moves exactly one TILE_SIZE per step
- Direction tracking (0=down, 1=left, 2=right, 3=up) — pupils shift
- MOVE_COOLDOWN = 8 frames between steps
- PLAYER_SIZE = 28px (slightly smaller than 32px tile for comfortable fit)
- Simple face: body, darker front face, white eyes with shifting pupils
- `grid_col` / `grid_row` properties track grid position

### Inventory (player/inventory.py)
- Max 8 items (INVENTORY_MAX)
- Each item: `InventoryItem(value, tier)` — tier clamped to 1-3
- `add(value, tier)` returns False if full
- `remove(index)` pops and returns item
- Serializes to `[{"value": N, "tier": T}, ...]`

---

## Systems

### Adaptive Difficulty (systems/difficulty.py)

5 tiers with confidence tracking per tier:
```python
TIER_DEFS = {
    1: {'addend': (1, 5),   'target': (2, 9),    'label': 'Easy'},
    2: {'addend': (1, 9),   'target': (5, 15),   'label': 'Single Digit'},
    3: {'addend': (2, 12),  'target': (10, 20),  'label': 'Bridging 10'},
    4: {'addend': (5, 25),  'target': (15, 40),  'label': 'Two Digit'},
    5: {'addend': (10, 50), 'target': (30, 80),  'label': 'Big Numbers'},
}
```

**Advancement:** After N correct in a row with variety (at least 2 unique answers in last 3):
- Tier 1: 3 correct to advance
- Tier 2: 4 correct to advance
- Tier 3: 5 correct to advance
- Tier 4: 6 correct to advance
- Tier 5: stays

**Demotion:** 3 incorrect in a row drops one tier.

**Key methods:**
- `generate_target(operation)` — random target in tier's target range
- `generate_pair_for_target(target, operation)` — finds (a, b) where a op b = target, constraining a/b to tier's addend range
- `generate_blocks_for_blueprint(blueprint, operation)` — produces blocks that CAN solve the blueprint, plus 2-3 distractors
- `generate_blueprint_targets(num_slots, operation)` — list of targets for blueprint slots

**Pair generation logic:**
- Addition: `a + b = target` — picks random `a` in addend range, `b = target - a`
- Subtraction: `a - b = target` — picks random `b` in addend range, `a = target + b`
- Multiplication/Division: **not yet implemented** (returns `(target, 0)`)

**Difficulty resets to tier 1** when portaling to a new biome (AdaptiveDifficulty is freshly instantiated).

### Crafting (systems/crafting.py)
```python
def compute(value_a, value_b, operation):
    '+' returns value_a + value_b
    '-' returns value_a - value_b (None if negative)
    '*' or '/' NOT YET IMPLEMENTED (returns None)
```

Auto-solve: When the player selects 2 blocks and an operator in the crafting UI, if the result matches any unfilled blueprint slot target, it auto-fills immediately. No submit button needed.

### Blueprint (systems/blueprint.py)

**Template structure:**
```python
{'id': 'garden_wall', 'name': 'Garden Wall', 'labels': ['Stone', 'Stone', 'Post']}
```
Labels are cosmetic (e.g., "Stone", "Plank"). Targets are filled in dynamically by the difficulty system when a blueprint is created.

**Stacklands templates (6):** Garden Wall (3 slots), Wooden House (4), Watch Tower (4), Grand Bridge (5), Windmill (4), Fountain (3)

**Crumble Caves templates (5):** Cave Bridge (3), Lantern Post (4), Mining Cart (5), Rock Arch (3), Crystal Lamp (3)

**Blueprint lifecycle:**
1. `create_blueprint_from_template(template, difficulty)` generates fresh targets
2. Player crafts values matching slot targets — slots fill
3. When all slots filled — blueprint complete, score +50, next blueprint loads
4. Templates cycle by index (wraps around)

**Bug note:** `create_blueprint_from_template` calls `difficulty.generate_blueprint_targets(num_slots)` WITHOUT passing the operation. Currently this works because + and - share the same TIER_DEFS target ranges, but this MUST be fixed when adding multiplication/division (products need completely different ranges).

### Portal System (systems/portal.py)
- `CHARGE_MAX = 100.0`
- `PORTAL_CHARGE_BASE = 2.0` (settings.py)
- Charge per correct answer = `BASE * MULTIPLIER[tier]`
- Multipliers: `{1: 1, 2: 2, 3: 5, 4: 10, 5: 20}`
- At tier 1: 2 charge per answer — 50 answers to fill portal
- At tier 5: 40 charge per answer — 3 answers to fill portal
- This incentivizes advancing through tiers to charge the portal faster

**Portal destination** is currently a hardcoded toggle in main.py:
```python
dest = 'crumble_caves' if biome_key == 'stacklands' else 'stacklands'
```
This must become a progression chain when adding more biomes.

**On portal activation:**
1. Portal charge resets to 0
2. Difficulty resets to tier 1 (fresh `AdaptiveDifficulty()`)
3. New biome loads (new tilemap, entities, blocks, blueprint)

### Feedback (systems/feedback.py)
3-level hint escalation based on attempt number:
1. **Level 1:** "You made X. The slot needs Y."
2. **Level 2:** Decomposition hint (break target into friendly pair, bridge through 10)
3. **Level 3:** Worked example of a similar problem

Currently only has hints for + and - operations.

### Sound (systems/sounds.py)
All sounds are synthesized with pure Python (wave + struct + math, no numpy):
- **pickup**: 80ms rising chirp (600 to 1200 Hz)
- **correct**: Two-note chime C5 then E5
- **wrong**: Gentle low wobble (200 Hz + 207 Hz beating)
- **blueprint_complete**: Three-note arpeggio C5 then E5 then G5

### Save (systems/save.py)
JSON persistence at `saves/save.json`. Saved state:
```python
{
    'version': 1,
    'score': int,
    'biome': 'stacklands' | 'crumble_caves',
    'player': {'x': int, 'y': int},
    'inventory': [{'value': int, 'tier': int}, ...],
    'difficulty': {'current_tier': int, 'confidence': {...}},
    'portal': {'charge': float},
    'completed_blueprints': [str, ...],
    'blueprint_progress': {serialized blueprint or null},
}
```

---

## UI System

### HUD (ui/hud.py)
- Bottom bar, 80px tall, semi-transparent dark background
- 8 inventory slots centered horizontally (48px each)
- Score top-left, biome name top-right
- Blueprint name + progress below score

### Crafting UI (ui/crafting_ui.py)
- Full-screen semi-transparent overlay with 500x420 panel
- Shows inventory blocks as clickable 52px tiles (4 columns)
- Operation buttons below inventory
- **BUG:** Operation buttons are hardcoded to `['+', '-']` on line 212 instead of using the `operations` parameter passed to `draw()`. This must be fixed for * and /.
- Equation display shows `a op b = result` or `???` for invalid
- Flash effect on auto-solve (green for success)
- Close with X button or ESC

**Hint text** on line 249 is hardcoded: "Click two blocks, then pick + or -"
**Equation display** on line 238 uses raw operator string — needs display mapping for multiplication and division symbols

### Blueprint UI (ui/blueprint_ui.py)
- Toggle with B key
- Full panel: right side, shows all slots with labels, targets, filled status
- Mini indicator: top-left, shows "Building: Name (filled/total) - Next: target"

### Feedback UI (ui/feedback_ui.py)
- Centered popup overlay
- Green background for correct, dark for wrong
- Star icon for correct, arrow for wrong
- Dismissible by click or keypress
- Duration: 90 frames (correct), 180 frames (wrong hints)

### Menu UI (ui/menu.py)
- Title screen: "MathCraft" heading, "Explore. Collect. Craft. Build!" subtitle
- New Game button always shown, Continue button if save exists
- Pause menu: Resume and Save & Quit buttons
- Version text: "MathCraft v1.0 - Phase 1"

---

## Block Spawning & Placement Rules (main.py _spawn_blocks)

Blocks are placed only on tiles that satisfy ALL of these conditions:
1. Tile type is `0` (plain floor) — excludes walls, spawn, portal, station
2. No wall tile adjacent on ANY of the 4 sides (up, down, left, right)
3. Not within the portal exclusion zone (3x4 tiles around portal tile)
4. Not within the station exclusion zone (3x3 tiles around each station)
5. Manhattan distance > 2 from player spawn position

After filtering, positions are shuffled and blocks are placed sequentially.

## Drop Block Mechanic (main.py)

When player presses D:
1. Last item removed from inventory
2. NumberBlock created at `(player.x + 2, player.y + TILE_SIZE + 4)` — one tile below player
3. Block gets `_pickup_immune = pygame.time.get_ticks() + 500` attribute
4. Pickup loop in `_update()` skips blocks where `_pickup_immune > now`
5. After 500ms, block becomes collectible again

## Crafting Flow (main.py)

1. Player walks near station (< 2 tiles), prompt appears
2. SPACE opens crafting UI, operation defaults to biome's operation
3. Player clicks 2 inventory blocks — result auto-computes
4. If result matches an unfilled blueprint slot target — auto-solve:
   - Slot fills, blocks removed from inventory
   - Score += 10 x tier, portal charge added
   - Correct feedback shown, sound plays
   - Wrong attempt counter resets, hint stone hides
   - If blueprint complete — score +50, next blueprint loads
   - Blocks respawn in world
   - If player has 2+ blocks remaining — returns to CRAFTING (chain-solve)
   - Otherwise — returns to PLAYING
5. If result doesn't match any slot and two blocks + op selected:
   - Tracked as wrong combo (deduped by (idx_a, idx_b, op) tuple)
   - After 2 unique wrong combos — hint stone spawns near station

## Wrong Answer Tracking

- `wrong_attempts` counter incremented on unique wrong combos only
- `_last_wrong_combo = (idx_a, idx_b, op)` prevents double-counting same selection
- At 2 wrong attempts — `_show_hint_stone()` creates/updates hint near station
- On correct answer — counter resets to 0, `_last_wrong_combo = None`, hint hides

---

## Settings Constants Reference (settings.py)

| Constant | Value | Purpose |
|----------|-------|---------|
| SCREEN_WIDTH | 800 | Window width |
| SCREEN_HEIGHT | 600 | Window height |
| FPS | 60 | Frame rate |
| TILE_SIZE | 32 | Grid cell size in pixels |
| WALL_HEIGHT | 16 | 3/4 view wall front face depth |
| PLAYER_SPEED | 3 | (unused — grid movement uses MOVE_COOLDOWN) |
| PLAYER_SIZE | 28 | Player sprite size |
| INVENTORY_MAX | 8 | Maximum inventory slots |
| HUD_HEIGHT | 80 | Bottom HUD bar height |
| HUD_SLOT_SIZE | 48 | Inventory slot size in HUD |
| HUD_PADDING | 8 | Space between HUD slots |
| PORTAL_CHARGE_BASE | 2.0 | Base charge per correct answer |
| SAVE_PATH | "saves/save.json" | Save file location |

---

## Known Issues & Bugs to Fix

1. **Crafting UI operator buttons hardcoded** — `op_list = ['+', '-']` on line 212 of `crafting_ui.py` ignores the `operations` parameter. Must use `op_list = operations` to support * and /.

2. **Blueprint creation doesn't pass operation** — `create_blueprint_from_template` in `blueprint.py` calls `generate_blueprint_targets(num_slots)` without the operation. For +/- this doesn't matter (same target ranges), but multiplication needs much larger targets. Fix: pass operation through the chain.

3. **Crafting station shows "+"** — `CraftingStation._render()` in `entities.py` line 113 hardcodes `'+'`. Should ideally show biome's operation symbol. Low priority polish item.

4. **Portal destination is 2-biome toggle** — Line 128 of `main.py` hardcodes `dest = 'crumble_caves' if biome_key == 'stacklands' else 'stacklands'`. Must become a progression chain for 4 biomes.

---

## Next Feature: Multiplication & Division Worlds

### Plan Summary

**New biomes to add:**
- `'multiply_mines'` — The Multiply Mines (operation: `'*'`) — deep blue-gray crystal mine theme
- `'divide_dale'` — The Divide Dale (operation: `'/'`) — mossy green valley theme

**Biome progression cycle:**
```
Stacklands (+) → Crumble Caves (-) → Multiply Mines (x) → Divide Dale (÷) → back to Stacklands
```

### Files to Modify (8 files)

**1. `settings.py`** — Add color constants for 2 new biomes (8 new color tuples)

**2. `world/biomes.py`** — Add:
- 2 new 25x20 layouts (mine tunnels and split-path meadow)
- 2 color dicts and BIOMES entries
- `BIOME_ORDER = ['stacklands', 'crumble_caves', 'multiply_mines', 'divide_dale']` for portal routing

**3. `systems/crafting.py`** — Add to `compute()`:
- `'*'` returns `value_a * value_b`
- `'/'` returns `value_a // value_b` only if `value_b != 0` and `value_a % value_b == 0`, else `None` (no remainders for this age)

**4. `systems/difficulty.py`** — Most complex change:
- Add `TIER_DEFS_MULT` with factor ranges (tier 1: factors 2-5, products 4-25 for easy times tables)
- Add `TIER_DEFS_DIV` with divisor/quotient ranges (tier 1: divisors 2-5, quotients 1-5)
- Helper `_get_tier_defs(operation)` returns correct tier dict
- `generate_target()` for `*`: picks two factors, returns product; for `/`: picks quotient directly
- `generate_pair_for_target()` for `*`: finds factor pairs of target; for `/`: computes `a = target * b`
- Update `generate_blocks_for_blueprint()` distractor range selection

**5. `systems/blueprint.py`** — Add:
- `MULTIPLY_MINES_TEMPLATES` (5 templates — crystal/mining themed)
- `DIVIDE_DALE_TEMPLATES` (5 templates — splitting/sharing themed)
- Fix `create_blueprint_from_template` to accept and pass `operation` parameter

**6. `systems/feedback.py`** — Add `*` and `/` branches to:
- `_decomposition_hint()` — "Think: X groups of Y = target"
- `_worked_example()` — show factor pair or clean division example

**7. `ui/crafting_ui.py`** — Fix:
- Line 212: `op_list = operations` instead of `['+', '-']`
- Display mapping: `{'*': 'x', '/': '÷'}` for button and equation text (Unicode symbols kids recognize)
- Update hint text dynamically

**8. `main.py`** — Fix:
- Import new templates and BIOME_ORDER
- Portal destination: use BIOME_ORDER index lookup instead of 2-biome toggle
- Blueprint template selection: dict lookup instead of if/else
- Pass operation to `create_blueprint_from_template`

### Multiplication Tier Definitions (planned)
| Tier | Factors | Products | Label |
|------|---------|----------|-------|
| 1 | 2-5 | 4-25 | Easy Tables |
| 2 | 2-9 | 6-45 | Single Digit |
| 3 | 3-12 | 12-72 | Harder Tables |
| 4 | 4-12 | 20-100 | Full Tables |
| 5 | 5-15 | 30-144 | Big Products |

### Division Tier Definitions (planned)
| Tier | Divisors | Quotients | Label |
|------|----------|-----------|-------|
| 1 | 2-5 | 1-5 | Easy Sharing |
| 2 | 2-9 | 2-9 | Single Digit |
| 3 | 2-12 | 3-12 | Harder Division |
| 4 | 3-12 | 5-15 | Full Division |
| 5 | 4-15 | 6-20 | Big Quotients |

### Edge Cases to Handle
- **Multiplication target factoring**: `generate_target('*')` produces target as product of 2 random factors, guaranteeing it is factorable within the tier range
- **Division zero-remainder**: block generation uses `a = target * b`, guaranteeing clean division. If player picks wrong blocks that don't divide evenly, `compute()` returns `None` (shown as "???")
- **Large numbers on blocks**: Division dividends can reach around 300 at tier 5 (quotient 20 x divisor 15). 3-digit numbers fit in 30px blocks but are tight — may need font size reduction for values >= 100
- **Save compatibility**: Old saves with `'biome': 'stacklands'` or `'crumble_caves'` work fine — BIOMES dict still has those keys. Portal destination just points to the correct next biome.

### Verification Plan
1. Run `python main.py` and start a new game
2. Play through Stacklands (+) — should work as before
3. Portal to Crumble Caves (-) — should work as before
4. Portal to Multiply Mines (x) — crafting UI should show x symbol, equations like 3 x 4 = 12, tier 1 easy times tables
5. Portal to Divide Dale (÷) — crafting UI should show ÷ symbol, clean division only (no remainders), tier 1 easy sharing
6. Portal from Divide Dale back to Stacklands — cycle completes
7. Verify difficulty resets to tier 1 on each portal transition
8. Verify wrong division combos (non-divisible) show ??? not crash
