"""Programmatic pixel art sprite generator for MathMine.

Run this script to regenerate all game sprites:
    python tools/generate_sprites.py

All output goes to assets/ directory as PNG files.
Uses only pygame (no Pillow/numpy) for pure per-pixel art generation.
"""
import os
import sys
import math
import random

# Add project root to path so we can import settings
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import pygame

ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')

# ---------------------------------------------------------------------------
# Noise & utility functions
# ---------------------------------------------------------------------------

def value_noise_2d(width, height, grid_size=8, seed=42):
    """Generate a 2D noise field as a width x height list of floats [0..1]."""
    rng = random.Random(seed)
    gw = width // grid_size + 2
    gh = height // grid_size + 2
    grid = [[rng.random() for _ in range(gw)] for _ in range(gh)]

    result = []
    for y in range(height):
        row = []
        for x in range(width):
            gx = x / grid_size
            gy = y / grid_size
            ix, iy = int(gx), int(gy)
            fx, fy = gx - ix, gy - iy
            # Smoothstep interpolation
            fx = fx * fx * (3 - 2 * fx)
            fy = fy * fy * (3 - 2 * fy)
            top = grid[iy][ix] * (1 - fx) + grid[iy][ix + 1] * fx
            bot = grid[iy + 1][ix] * (1 - fx) + grid[iy + 1][ix + 1] * fx
            val = top * (1 - fy) + bot * fy
            row.append(val)
        result.append(row)
    return result


def fbm_noise_2d(width, height, octaves=3, base_grid=8, seed=42):
    """Fractal Brownian Motion - sum multiple noise octaves for richer texture."""
    combined = [[0.0] * width for _ in range(height)]
    amplitude = 1.0
    total_amp = 0.0
    for octave in range(octaves):
        noise = value_noise_2d(width, height,
                               grid_size=max(2, base_grid >> octave),
                               seed=seed + octave * 1000)
        for y in range(height):
            for x in range(width):
                combined[y][x] += noise[y][x] * amplitude
        total_amp += amplitude
        amplitude *= 0.5
    for y in range(height):
        for x in range(width):
            combined[y][x] /= total_amp
    return combined


def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def color_ramp(t, colors):
    """Map t in [0,1] to a color from a list of color stops."""
    if len(colors) == 1:
        return colors[0]
    t = max(0.0, min(1.0, t))
    segment = t * (len(colors) - 1)
    idx = int(segment)
    frac = segment - idx
    if idx >= len(colors) - 1:
        return colors[-1]
    return lerp_color(colors[idx], colors[idx + 1], frac)


def darken(color, amount=30):
    """Darken an RGB color."""
    return (max(0, color[0] - amount), max(0, color[1] - amount),
            max(0, color[2] - amount))


def brighten(color, amount=30):
    """Brighten an RGB color."""
    return (min(255, color[0] + amount), min(255, color[1] + amount),
            min(255, color[2] + amount))


def pixel_outline(surface, outline_color=None):
    """Add 1px dark outline around non-transparent pixels."""
    w, h = surface.get_size()
    outline = surface.copy()
    if outline_color is None:
        outline_color = (20, 20, 20, 255)
    for y in range(h):
        for x in range(w):
            r, g, b, a = surface.get_at((x, y))
            if a > 0:
                continue
            # Check neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    _, _, _, na = surface.get_at((nx, ny))
                    if na > 128:
                        outline.set_at((x, y), outline_color)
                        break
    return outline


def draw_crack_lines(surface, count, color, seed=0):
    """Draw random wandering crack lines for stone texture."""
    rng = random.Random(seed)
    w, h = surface.get_size()
    for _ in range(count):
        x = rng.randint(2, w - 3)
        y = rng.randint(2, h - 3)
        length = rng.randint(3, 8)
        for _ in range(length):
            if 0 <= x < w and 0 <= y < h:
                surface.set_at((x, y), color)
            x += rng.choice([-1, 0, 1])
            y += rng.choice([-1, 0, 1])
            x = max(0, min(w - 1, x))
            y = max(0, min(h - 1, y))


def draw_grass_blades(surface, count, colors, seed=0):
    """Draw small vertical grass blade strokes."""
    rng = random.Random(seed)
    w, h = surface.get_size()
    for _ in range(count):
        bx = rng.randint(1, w - 2)
        by = rng.randint(4, h - 2)
        blade_h = rng.randint(2, 4)
        blade_color = rng.choice(colors)
        for dy in range(blade_h):
            py = by - dy
            if 0 <= py < h:
                surface.set_at((bx, py), blade_color)


def draw_dots(surface, count, colors, seed=0):
    """Scatter colored dot details."""
    rng = random.Random(seed)
    w, h = surface.get_size()
    for _ in range(count):
        x = rng.randint(1, w - 2)
        y = rng.randint(1, h - 2)
        surface.set_at((x, y), rng.choice(colors))


def fill_with_noise(surface, palette, noise, offset_x=0, offset_y=0):
    """Fill surface pixels using noise field to select from palette."""
    w, h = surface.get_size()
    for y in range(h):
        for x in range(w):
            ny = (y + offset_y) % len(noise)
            nx = (x + offset_x) % len(noise[0])
            n = noise[ny][nx]
            idx = min(int(n * len(palette)), len(palette) - 1)
            surface.set_at((x, y), palette[idx])


# ---------------------------------------------------------------------------
# Tile generators
# ---------------------------------------------------------------------------

def generate_stacklands_tiles():
    """Generate grass floor and leafy wall tiles for Stacklands."""
    # Floor
    floor = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette = [(96, 180, 42), (106, 190, 48), (115, 198, 55), (125, 208, 65)]
    noise = fbm_noise_2d(32, 32, octaves=3, base_grid=8, seed=100)
    fill_with_noise(floor, palette, noise)
    draw_grass_blades(floor, 10, [(130, 215, 70), (140, 220, 80)], seed=101)

    # Floor alt - slightly different shade + flower dots
    floor_alt = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette_alt = [(105, 195, 52), (118, 200, 58), (110, 192, 50), (128, 210, 68)]
    noise_alt = fbm_noise_2d(32, 32, octaves=3, base_grid=8, seed=200)
    fill_with_noise(floor_alt, palette_alt, noise_alt)
    draw_grass_blades(floor_alt, 8, [(135, 218, 72), (145, 225, 85)], seed=201)
    draw_dots(floor_alt, 3, [(255, 200, 80), (255, 150, 180), (200, 160, 255)],
              seed=202)

    # Wall top - darker green earth/hedge
    wall_top = pygame.Surface((32, 32), pygame.SRCALPHA)
    wt_palette = [(70, 110, 42), (80, 120, 50), (65, 105, 38), (75, 115, 45)]
    noise_wt = fbm_noise_2d(32, 32, octaves=2, base_grid=6, seed=300)
    fill_with_noise(wall_top, wt_palette, noise_wt)
    # Add leaf clusters on top
    draw_dots(wall_top, 8, [(90, 140, 55), (100, 150, 60)], seed=301)
    # Dark border on bottom edge
    for x in range(32):
        wall_top.set_at((x, 31), darken(wt_palette[1], 20))

    # Wall front - dark earthy face
    wall_front = pygame.Surface((32, 16), pygame.SRCALPHA)
    wf_palette = [(50, 80, 32), (55, 85, 35), (45, 75, 28)]
    noise_wf = fbm_noise_2d(32, 16, octaves=2, base_grid=6, seed=400)
    fill_with_noise(wall_front, wf_palette, noise_wf)
    # Highlight line on top
    for x in range(32):
        wall_front.set_at((x, 0), brighten(wf_palette[1], 15))

    return floor, floor_alt, wall_top, wall_front


def generate_crumble_caves_tiles():
    """Generate dark stone tiles for Crumble Caves."""
    floor = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette = [(110, 92, 78), (120, 100, 85), (105, 88, 72), (115, 96, 80)]
    noise = fbm_noise_2d(32, 32, octaves=3, base_grid=6, seed=500)
    fill_with_noise(floor, palette, noise)
    draw_crack_lines(floor, 3, darken(palette[0], 20), seed=501)
    # Ore sparkle dots
    draw_dots(floor, 2, [(180, 170, 140), (160, 150, 120)], seed=502)

    floor_alt = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette_alt = [(105, 88, 72), (110, 92, 78), (100, 84, 68), (108, 90, 76)]
    noise_alt = fbm_noise_2d(32, 32, octaves=3, base_grid=6, seed=600)
    fill_with_noise(floor_alt, palette_alt, noise_alt)
    draw_crack_lines(floor_alt, 2, darken(palette_alt[0], 25), seed=601)
    draw_dots(floor_alt, 1, [(190, 180, 150)], seed=602)

    wall_top = pygame.Surface((32, 32), pygame.SRCALPHA)
    wt_palette = [(68, 55, 45), (75, 60, 50), (62, 50, 40), (72, 58, 48)]
    noise_wt = fbm_noise_2d(32, 32, octaves=2, base_grid=5, seed=700)
    fill_with_noise(wall_top, wt_palette, noise_wt)
    draw_crack_lines(wall_top, 4, darken(wt_palette[0], 15), seed=701)
    # Stalactite hints at bottom
    rng = random.Random(702)
    for _ in range(3):
        sx = rng.randint(4, 27)
        for dy in range(rng.randint(2, 4)):
            wall_top.set_at((sx, 31 - dy), darken(wt_palette[2], 10))
    for x in range(32):
        wall_top.set_at((x, 31), darken(wt_palette[0], 20))

    wall_front = pygame.Surface((32, 16), pygame.SRCALPHA)
    wf_palette = [(45, 36, 30), (50, 40, 35), (40, 32, 26)]
    noise_wf = fbm_noise_2d(32, 16, octaves=2, base_grid=5, seed=800)
    fill_with_noise(wall_front, wf_palette, noise_wf)
    for x in range(32):
        wall_front.set_at((x, 0), brighten(wf_palette[1], 12))

    return floor, floor_alt, wall_top, wall_front


def generate_factor_forest_tiles():
    """Generate dark earthy forest tiles for Factor Forest."""
    floor = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette = [(50, 108, 44), (58, 120, 50), (45, 100, 38), (55, 115, 48)]
    noise = fbm_noise_2d(32, 32, octaves=3, base_grid=7, seed=900)
    fill_with_noise(floor, palette, noise)
    # Leaf litter
    leaf_colors = [(80, 60, 30), (100, 80, 40), (70, 90, 35), (110, 85, 45)]
    rng = random.Random(901)
    for _ in range(6):
        lx = rng.randint(2, 29)
        ly = rng.randint(2, 29)
        lc = rng.choice(leaf_colors)
        floor.set_at((lx, ly), lc)
        floor.set_at((lx + 1, ly), lc)
        floor.set_at((lx, ly + 1), darken(lc, 10))

    floor_alt = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette_alt = [(48, 105, 42), (52, 112, 46), (42, 98, 36), (50, 108, 44)]
    noise_alt = fbm_noise_2d(32, 32, octaves=3, base_grid=7, seed=1000)
    fill_with_noise(floor_alt, palette_alt, noise_alt)
    rng2 = random.Random(1001)
    for _ in range(5):
        lx = rng2.randint(2, 29)
        ly = rng2.randint(2, 29)
        lc = rng2.choice(leaf_colors)
        floor_alt.set_at((lx, ly), lc)
        floor_alt.set_at((lx + 1, ly), lc)

    wall_top = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Tree trunk / bark texture
    wt_palette = [(28, 78, 25), (34, 85, 30), (24, 70, 20), (30, 80, 27)]
    noise_wt = fbm_noise_2d(32, 32, octaves=2, base_grid=5, seed=1100)
    fill_with_noise(wall_top, wt_palette, noise_wt)
    # Vertical bark lines
    rng3 = random.Random(1101)
    for _ in range(5):
        bx = rng3.randint(3, 28)
        for by in range(0, 32, rng3.randint(2, 4)):
            if by < 32:
                wall_top.set_at((bx, by), darken(wt_palette[2], 10))
    for x in range(32):
        wall_top.set_at((x, 31), darken(wt_palette[0], 20))

    wall_front = pygame.Surface((32, 16), pygame.SRCALPHA)
    wf_palette = [(18, 55, 16), (22, 60, 20), (15, 48, 12)]
    noise_wf = fbm_noise_2d(32, 16, octaves=2, base_grid=5, seed=1200)
    fill_with_noise(wall_front, wf_palette, noise_wf)
    for x in range(32):
        wall_front.set_at((x, 0), brighten(wf_palette[1], 12))

    return floor, floor_alt, wall_top, wall_front


def generate_dividing_desert_tiles():
    """Generate sandy tiles for Dividing Desert."""
    floor = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette = [(210, 182, 122), (218, 190, 130), (205, 178, 118), (222, 195, 135)]
    noise = fbm_noise_2d(32, 32, octaves=3, base_grid=8, seed=1300)
    fill_with_noise(floor, palette, noise)
    # Wind lines - thin horizontal streaks
    rng = random.Random(1301)
    for _ in range(3):
        wy = rng.randint(3, 28)
        wx_start = rng.randint(0, 10)
        wx_len = rng.randint(8, 18)
        wc = brighten(palette[1], 12)
        for wx in range(wx_start, min(32, wx_start + wx_len)):
            floor.set_at((wx, wy), wc)
    # Pebble dots
    draw_dots(floor, 2, [darken(palette[0], 25), darken(palette[1], 20)], seed=1302)

    floor_alt = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette_alt = [(200, 172, 115), (205, 178, 120), (195, 168, 110),
                   (210, 183, 125)]
    noise_alt = fbm_noise_2d(32, 32, octaves=3, base_grid=8, seed=1400)
    fill_with_noise(floor_alt, palette_alt, noise_alt)
    rng2 = random.Random(1401)
    for _ in range(2):
        wy = rng2.randint(3, 28)
        wx_start = rng2.randint(5, 15)
        wx_len = rng2.randint(6, 14)
        wc = brighten(palette_alt[1], 10)
        for wx in range(wx_start, min(32, wx_start + wx_len)):
            floor_alt.set_at((wx, wy), wc)

    wall_top = pygame.Surface((32, 32), pygame.SRCALPHA)
    wt_palette = [(162, 132, 82), (170, 140, 90), (155, 125, 75), (165, 135, 85)]
    noise_wt = fbm_noise_2d(32, 32, octaves=2, base_grid=6, seed=1500)
    fill_with_noise(wall_top, wt_palette, noise_wt)
    # Horizontal sandstone layering
    for y in [7, 15, 23]:
        layer_c = darken(wt_palette[1], 12)
        for x in range(32):
            wall_top.set_at((x, y), layer_c)
    for x in range(32):
        wall_top.set_at((x, 31), darken(wt_palette[0], 20))

    wall_front = pygame.Surface((32, 16), pygame.SRCALPHA)
    wf_palette = [(132, 105, 65), (140, 112, 70), (125, 98, 58)]
    noise_wf = fbm_noise_2d(32, 16, octaves=2, base_grid=6, seed=1600)
    fill_with_noise(wall_front, wf_palette, noise_wf)
    for y in [4, 10]:
        for x in range(32):
            wall_front.set_at((x, y), darken(wf_palette[1], 10))
    for x in range(32):
        wall_front.set_at((x, 0), brighten(wf_palette[1], 12))

    return floor, floor_alt, wall_top, wall_front


def generate_hub_tiles():
    """Generate stone brick tiles for Hub."""
    floor = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette = [(132, 128, 122), (140, 135, 130), (128, 122, 118), (136, 130, 126)]
    noise = fbm_noise_2d(32, 32, octaves=2, base_grid=6, seed=1700)
    fill_with_noise(floor, palette, noise)
    # Brick/tile grid pattern - mortar lines
    mortar = darken(palette[0], 20)
    for x in range(32):
        floor.set_at((x, 15), mortar)
        floor.set_at((x, 31), mortar)
    for y in range(16):
        floor.set_at((15, y), mortar)
    for y in range(16, 32):
        floor.set_at((0, y), mortar)
        floor.set_at((31, y), mortar)

    floor_alt = pygame.Surface((32, 32), pygame.SRCALPHA)
    palette_alt = [(125, 120, 115), (130, 125, 120), (120, 115, 110),
                   (128, 123, 118)]
    noise_alt = fbm_noise_2d(32, 32, octaves=2, base_grid=6, seed=1800)
    fill_with_noise(floor_alt, palette_alt, noise_alt)
    mortar2 = darken(palette_alt[0], 18)
    for x in range(32):
        floor_alt.set_at((x, 15), mortar2)
        floor_alt.set_at((x, 31), mortar2)
    for y in range(16):
        floor_alt.set_at((0, y), mortar2)
        floor_alt.set_at((31, y), mortar2)
    for y in range(16, 32):
        floor_alt.set_at((15, y), mortar2)

    wall_top = pygame.Surface((32, 32), pygame.SRCALPHA)
    wt_palette = [(92, 88, 82), (100, 95, 90), (88, 82, 78), (96, 90, 86)]
    noise_wt = fbm_noise_2d(32, 32, octaves=2, base_grid=5, seed=1900)
    fill_with_noise(wall_top, wt_palette, noise_wt)
    # Stone block pattern
    stone_mortar = darken(wt_palette[0], 15)
    for x in range(32):
        wall_top.set_at((x, 10), stone_mortar)
        wall_top.set_at((x, 21), stone_mortar)
    for y in range(11):
        wall_top.set_at((15, y), stone_mortar)
    for y in range(11, 22):
        wall_top.set_at((7, y), stone_mortar)
        wall_top.set_at((23, y), stone_mortar)
    for y in range(22, 32):
        wall_top.set_at((15, y), stone_mortar)
    for x in range(32):
        wall_top.set_at((x, 31), darken(wt_palette[0], 20))

    wall_front = pygame.Surface((32, 16), pygame.SRCALPHA)
    wf_palette = [(68, 62, 58), (75, 70, 65), (62, 58, 52)]
    noise_wf = fbm_noise_2d(32, 16, octaves=2, base_grid=5, seed=2000)
    fill_with_noise(wall_front, wf_palette, noise_wf)
    fm = darken(wf_palette[0], 12)
    for x in range(32):
        wall_front.set_at((x, 7), fm)
    for y in range(8):
        wall_front.set_at((10, y), fm)
        wall_front.set_at((22, y), fm)
    for y in range(8, 16):
        wall_front.set_at((16, y), fm)
    for x in range(32):
        wall_front.set_at((x, 0), brighten(wf_palette[1], 12))

    return floor, floor_alt, wall_top, wall_front


# ---------------------------------------------------------------------------
# Player sprite generator
# ---------------------------------------------------------------------------

def _set_px(surf, x, y, color):
    """Safe set_at with bounds check."""
    w, h = surf.get_size()
    if 0 <= x < w and 0 <= y < h:
        surf.set_at((x, y), color)


def _draw_player_frame(direction, frame, size=28):
    """Draw one player sprite frame with detailed pixel art.

    direction: 0=down, 1=left, 2=right, 3=up
    frame: 0=idle, 1=walk1, 2=walk2

    Character design: cute chibi adventurer with round head, small body,
    visible legs. Distinct look per direction. Clear walk cycle.
    """
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # Color palette
    hair = (60, 40, 30)          # dark brown hair
    skin = (255, 210, 170)       # warm skin
    skin_shadow = (230, 180, 140)
    shirt = (52, 152, 219)       # blue shirt
    shirt_light = (80, 175, 235)
    shirt_dark = (35, 120, 180)
    shirt_shadow = (28, 100, 155)
    pants = (70, 70, 90)         # dark pants
    pants_light = (85, 85, 105)
    shoe = (50, 40, 35)          # brown shoes
    shoe_light = (70, 55, 45)
    eye_white = (255, 255, 255)
    pupil = (25, 25, 35)
    mouth = (200, 130, 120)
    outline = (20, 20, 30)       # dark outline
    blush = (255, 180, 170)      # cheek blush
    backpack = (180, 120, 55)
    backpack_dark = (145, 95, 40)

    cx = size // 2  # center x = 14

    # Walk frame leg positions
    # frame 0 = idle (legs together)
    # frame 1 = left leg forward, right leg back
    # frame 2 = right leg forward, left leg back
    left_leg_dy = 0
    right_leg_dy = 0
    body_bob = 0
    if frame == 1:
        left_leg_dy = -2   # left leg forward (up)
        right_leg_dy = 1   # right leg back (down)
        body_bob = -1      # body bounces up slightly
    elif frame == 2:
        left_leg_dy = 1
        right_leg_dy = -2
        body_bob = -1

    if direction == 0:  # === FACING DOWN ===
        # Legs (drawn first, behind body)
        # Left leg
        ly = 21 + left_leg_dy
        for y in range(ly, ly + 4):
            _set_px(surf, cx - 4, y, pants)
            _set_px(surf, cx - 3, y, pants_light)
            _set_px(surf, cx - 2, y, pants)
        # Left shoe
        _set_px(surf, cx - 5, ly + 4, shoe)
        _set_px(surf, cx - 4, ly + 4, shoe_light)
        _set_px(surf, cx - 3, ly + 4, shoe_light)
        _set_px(surf, cx - 2, ly + 4, shoe)

        # Right leg
        ry = 21 + right_leg_dy
        for y in range(ry, ry + 4):
            _set_px(surf, cx + 1, y, pants)
            _set_px(surf, cx + 2, y, pants_light)
            _set_px(surf, cx + 3, y, pants)
        # Right shoe
        _set_px(surf, cx + 1, ry + 4, shoe)
        _set_px(surf, cx + 2, ry + 4, shoe_light)
        _set_px(surf, cx + 3, ry + 4, shoe_light)
        _set_px(surf, cx + 4, ry + 4, shoe)

        by = 2 + body_bob  # body top Y

        # Shirt / torso
        for y in range(by + 10, by + 17):
            for x in range(cx - 5, cx + 6):
                c = shirt
                if x == cx - 5 or x == cx + 5:
                    c = outline
                elif x == cx - 4:
                    c = shirt_dark
                elif x == cx + 4:
                    c = shirt_shadow
                elif y == by + 10:
                    c = shirt_light
                surf.set_at((x, y), c)
        # Shirt bottom edge
        for x in range(cx - 4, cx + 5):
            _set_px(surf, x, by + 17, shirt_dark)

        # Arms (at sides)
        for y in range(by + 11, by + 16):
            _set_px(surf, cx - 6, y, skin_shadow)
            _set_px(surf, cx - 7, y, outline)
            _set_px(surf, cx + 6, y, skin)
            _set_px(surf, cx + 7, y, outline)
        # Hands
        _set_px(surf, cx - 6, by + 16, skin)
        _set_px(surf, cx + 6, by + 16, skin)

        # Head (round, 12px wide, 10px tall)
        head_y = by
        # Row by row for round shape
        head_pixels = [
            (5, 9),   # row 0: x from cx-4 to cx+4  (9 wide)
            (4, 10),  # row 1
            (4, 10),  # row 2
            (4, 10),  # row 3
            (4, 10),  # row 4
            (4, 10),  # row 5
            (4, 10),  # row 6
            (4, 10),  # row 7
            (5, 9),   # row 8
            (6, 8),   # row 9
        ]
        for row, (start, end) in enumerate(head_pixels):
            y = head_y + row
            half_s = (end - start) // 2
            for i in range(end - start):
                x = cx - half_s + i
                if row < 2:
                    c = hair  # hair on top
                else:
                    c = skin
                    if i == 0 or i == end - start - 1:
                        c = outline
                    elif row == 2:
                        c = hair  # hair line
                _set_px(surf, x, y, c)

        # Hair on top (fluffy)
        for x in range(cx - 4, cx + 5):
            _set_px(surf, x, head_y, hair)
            _set_px(surf, x, head_y + 1, hair)
        _set_px(surf, cx - 5, head_y + 1, hair)
        _set_px(surf, cx + 5, head_y + 1, hair)
        # Hair outline
        for x in range(cx - 4, cx + 5):
            _set_px(surf, x, head_y - 1, outline)
        _set_px(surf, cx - 5, head_y, outline)
        _set_px(surf, cx + 5, head_y, outline)

        # Eyes (facing down = looking at camera)
        ey = head_y + 5
        # Left eye
        _set_px(surf, cx - 3, ey, eye_white)
        _set_px(surf, cx - 2, ey, eye_white)
        _set_px(surf, cx - 3, ey + 1, eye_white)
        _set_px(surf, cx - 2, ey + 1, pupil)
        _set_px(surf, cx - 3, ey + 2, pupil)
        _set_px(surf, cx - 2, ey + 2, pupil)
        # Right eye
        _set_px(surf, cx + 2, ey, eye_white)
        _set_px(surf, cx + 3, ey, eye_white)
        _set_px(surf, cx + 2, ey + 1, pupil)
        _set_px(surf, cx + 3, ey + 1, eye_white)
        _set_px(surf, cx + 2, ey + 2, pupil)
        _set_px(surf, cx + 3, ey + 2, pupil)

        # Blush
        _set_px(surf, cx - 4, ey + 2, blush)
        _set_px(surf, cx + 4, ey + 2, blush)

        # Mouth (small smile)
        _set_px(surf, cx - 1, head_y + 8, mouth)
        _set_px(surf, cx, head_y + 8, mouth)
        _set_px(surf, cx + 1, head_y + 8, mouth)

    elif direction == 3:  # === FACING UP ===
        # Legs
        ly = 21 + left_leg_dy
        for y in range(ly, ly + 4):
            _set_px(surf, cx - 4, y, pants)
            _set_px(surf, cx - 3, y, pants)
            _set_px(surf, cx - 2, y, pants)
        _set_px(surf, cx - 4, ly + 4, shoe)
        _set_px(surf, cx - 3, ly + 4, shoe_light)
        _set_px(surf, cx - 2, ly + 4, shoe)

        ry = 21 + right_leg_dy
        for y in range(ry, ry + 4):
            _set_px(surf, cx + 1, y, pants)
            _set_px(surf, cx + 2, y, pants)
            _set_px(surf, cx + 3, y, pants)
        _set_px(surf, cx + 1, ry + 4, shoe)
        _set_px(surf, cx + 2, ry + 4, shoe_light)
        _set_px(surf, cx + 3, ry + 4, shoe)

        by = 2 + body_bob

        # Backpack (visible from behind)
        for y in range(by + 11, by + 16):
            for x in range(cx - 3, cx + 4):
                if x == cx - 3 or x == cx + 3:
                    _set_px(surf, x, y, backpack_dark)
                else:
                    _set_px(surf, x, y, backpack)
        _set_px(surf, cx - 3, by + 11, outline)
        _set_px(surf, cx + 3, by + 11, outline)

        # Shirt
        for y in range(by + 10, by + 17):
            for x in range(cx - 5, cx + 6):
                c = shirt_dark  # back of shirt is darker
                if x == cx - 5 or x == cx + 5:
                    c = outline
                elif y == by + 10:
                    c = shirt
                _set_px(surf, x, y, c)
        for x in range(cx - 4, cx + 5):
            _set_px(surf, x, by + 17, shirt_shadow)

        # Arms
        for y in range(by + 11, by + 16):
            _set_px(surf, cx - 6, y, skin_shadow)
            _set_px(surf, cx + 6, y, skin_shadow)
        _set_px(surf, cx - 6, by + 16, skin)
        _set_px(surf, cx + 6, by + 16, skin)

        # Head (back of head = mostly hair)
        head_y = by
        for row in range(10):
            y = head_y + row
            w = 9 if row > 0 and row < 8 else (7 if row == 9 else 8)
            half = w // 2
            for i in range(w):
                x = cx - half + i
                c = hair
                if i == 0 or i == w - 1:
                    c = outline
                _set_px(surf, x, y, c)
        # Hair top outline
        for x in range(cx - 4, cx + 5):
            _set_px(surf, x, head_y - 1, outline)

    elif direction == 1:  # === FACING LEFT ===
        # Legs (side view — one in front, one behind)
        # Back leg (right side of sprite, partially hidden)
        ry = 21 + right_leg_dy
        for y in range(ry, ry + 4):
            _set_px(surf, cx, y, pants)
            _set_px(surf, cx + 1, y, pants)
        _set_px(surf, cx - 1, ry + 4, shoe)
        _set_px(surf, cx, ry + 4, shoe_light)
        _set_px(surf, cx + 1, ry + 4, shoe)

        # Front leg
        ly = 21 + left_leg_dy
        for y in range(ly, ly + 4):
            _set_px(surf, cx - 3, y, pants_light)
            _set_px(surf, cx - 2, y, pants)
            _set_px(surf, cx - 1, y, pants)
        _set_px(surf, cx - 4, ly + 4, shoe)
        _set_px(surf, cx - 3, ly + 4, shoe_light)
        _set_px(surf, cx - 2, ly + 4, shoe_light)
        _set_px(surf, cx - 1, ly + 4, shoe)

        by = 2 + body_bob

        # Shirt (side view, shifted left slightly)
        for y in range(by + 10, by + 17):
            for x in range(cx - 5, cx + 4):
                c = shirt
                if x == cx - 5:
                    c = outline
                elif x == cx + 3:
                    c = shirt_shadow
                elif x == cx - 4:
                    c = shirt_light
                _set_px(surf, x, y, c)
        for x in range(cx - 4, cx + 3):
            _set_px(surf, x, by + 17, shirt_dark)

        # Left arm (front, swinging)
        arm_dy = 0
        if frame == 1:
            arm_dy = -1
        elif frame == 2:
            arm_dy = 1
        for y in range(by + 11 + arm_dy, by + 16 + arm_dy):
            _set_px(surf, cx - 6, y, skin)
        _set_px(surf, cx - 6, by + 16 + arm_dy, skin)

        # Head (3/4 left view)
        head_y = by
        for row in range(10):
            y = head_y + row
            w = 9 if 1 <= row <= 7 else (7 if row >= 9 else 8)
            for i in range(w):
                x = cx - 5 + i
                if row < 2:
                    c = hair
                else:
                    c = skin
                    if i == 0:
                        c = outline
                    elif i == w - 1:
                        c = skin_shadow
                _set_px(surf, x, y, c)
        # Hair
        for x in range(cx - 5, cx + 4):
            _set_px(surf, x, head_y, hair)
            _set_px(surf, x, head_y + 1, hair)
        for x in range(cx - 5, cx + 4):
            _set_px(surf, x, head_y - 1, outline)

        # Eye (one eye visible facing left)
        ey = head_y + 5
        _set_px(surf, cx - 4, ey, eye_white)
        _set_px(surf, cx - 3, ey, eye_white)
        _set_px(surf, cx - 4, ey + 1, pupil)
        _set_px(surf, cx - 3, ey + 1, eye_white)
        _set_px(surf, cx - 4, ey + 2, pupil)
        _set_px(surf, cx - 3, ey + 2, pupil)

        # Blush
        _set_px(surf, cx - 5, ey + 2, blush)

        # Mouth
        _set_px(surf, cx - 3, head_y + 8, mouth)
        _set_px(surf, cx - 2, head_y + 8, mouth)

        # Backpack (visible on back when facing left)
        for y in range(by + 11, by + 15):
            _set_px(surf, cx + 4, y, backpack)
            _set_px(surf, cx + 5, y, backpack_dark)

    elif direction == 2:  # === FACING RIGHT ===
        # Mirror of facing left
        # Back leg
        ry = 21 + right_leg_dy
        for y in range(ry, ry + 4):
            _set_px(surf, cx - 2, y, pants)
            _set_px(surf, cx - 1, y, pants)
        _set_px(surf, cx - 2, ry + 4, shoe)
        _set_px(surf, cx - 1, ry + 4, shoe_light)
        _set_px(surf, cx, ry + 4, shoe)

        # Front leg
        ly = 21 + left_leg_dy
        for y in range(ly, ly + 4):
            _set_px(surf, cx, y, pants)
            _set_px(surf, cx + 1, y, pants)
            _set_px(surf, cx + 2, y, pants_light)
        _set_px(surf, cx, ly + 4, shoe)
        _set_px(surf, cx + 1, ly + 4, shoe_light)
        _set_px(surf, cx + 2, ly + 4, shoe_light)
        _set_px(surf, cx + 3, ly + 4, shoe)

        by = 2 + body_bob

        # Shirt
        for y in range(by + 10, by + 17):
            for x in range(cx - 4, cx + 5):
                c = shirt
                if x == cx + 4:
                    c = outline
                elif x == cx - 3:
                    c = shirt_shadow
                elif x == cx + 3:
                    c = shirt_light
                _set_px(surf, x, y, c)
        for x in range(cx - 3, cx + 4):
            _set_px(surf, x, by + 17, shirt_dark)

        # Right arm
        arm_dy = 0
        if frame == 1:
            arm_dy = 1
        elif frame == 2:
            arm_dy = -1
        for y in range(by + 11 + arm_dy, by + 16 + arm_dy):
            _set_px(surf, cx + 5, y, skin)
        _set_px(surf, cx + 5, by + 16 + arm_dy, skin)

        # Head (3/4 right view)
        head_y = by
        for row in range(10):
            y = head_y + row
            w = 9 if 1 <= row <= 7 else (7 if row >= 9 else 8)
            for i in range(w):
                x = cx - 4 + i
                if row < 2:
                    c = hair
                else:
                    c = skin
                    if i == w - 1:
                        c = outline
                    elif i == 0:
                        c = skin_shadow
                _set_px(surf, x, y, c)
        for x in range(cx - 4, cx + 5):
            _set_px(surf, x, head_y, hair)
            _set_px(surf, x, head_y + 1, hair)
        for x in range(cx - 4, cx + 5):
            _set_px(surf, x, head_y - 1, outline)

        # Eye
        ey = head_y + 5
        _set_px(surf, cx + 2, ey, eye_white)
        _set_px(surf, cx + 3, ey, eye_white)
        _set_px(surf, cx + 2, ey + 1, eye_white)
        _set_px(surf, cx + 3, ey + 1, pupil)
        _set_px(surf, cx + 2, ey + 2, pupil)
        _set_px(surf, cx + 3, ey + 2, pupil)

        # Blush
        _set_px(surf, cx + 4, ey + 2, blush)

        # Mouth
        _set_px(surf, cx + 1, head_y + 8, mouth)
        _set_px(surf, cx + 2, head_y + 8, mouth)

        # Backpack
        for y in range(by + 11, by + 15):
            _set_px(surf, cx - 5, y, backpack_dark)
            _set_px(surf, cx - 6, y, backpack)

    return surf


def generate_player_sprites():
    """Generate all 12 player sprite frames."""
    sprites = {}
    dir_names = {0: 'down', 1: 'left', 2: 'right', 3: 'up'}
    frame_names = {0: 'idle', 1: 'walk1', 2: 'walk2'}
    for d, dname in dir_names.items():
        for f, fname in frame_names.items():
            surf = _draw_player_frame(d, f)
            sprites[f'{dname}_{fname}'] = surf
    return sprites


# ---------------------------------------------------------------------------
# Block sprite generator
# ---------------------------------------------------------------------------

def generate_block_sprite(tier, size=30):
    """Generate a number block sprite for the given tier (no number overlay)."""
    glow = 4
    total_w = size + glow * 2
    total_h = size + 10 + glow * 2
    surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    g = glow

    if tier == 1:
        # Stone block
        base_palette = [(140, 155, 158), (149, 165, 166), (135, 150, 152),
                        (145, 160, 162)]
        dark = (127, 140, 141)
        glow_color = (149, 165, 166, 55)
    elif tier == 2:
        # Gold block
        base_palette = [(230, 186, 10), (241, 196, 15), (220, 178, 8),
                        (235, 190, 12)]
        dark = (211, 172, 13)
        glow_color = (241, 196, 15, 55)
    else:
        # Gem block
        base_palette = [(145, 80, 172), (155, 89, 182), (138, 72, 165),
                        (150, 85, 178)]
        dark = (132, 76, 155)
        glow_color = (155, 89, 182, 55)

    # Glow
    glow_surf = pygame.Surface((size + 6, size + 6), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, glow_color, (0, 0, size + 6, size + 6),
                     border_radius=6)
    surf.blit(glow_surf, (g - 3, g - 3))

    # Top face with noise texture
    top_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    noise = fbm_noise_2d(size, size, octaves=2, base_grid=6, seed=3000 + tier * 100)
    fill_with_noise(top_surf, base_palette, noise)

    # Round the corners by clearing pixels outside radius
    for y in range(size):
        for x in range(size):
            # Simple corner rounding
            corners = [(0, 0), (size - 1, 0), (0, size - 1), (size - 1, size - 1)]
            for cx, cy in corners:
                dist = abs(x - cx) + abs(y - cy)
                if dist < 4:
                    r = 4
                    dx = min(x, size - 1 - x)
                    dy = min(y, size - 1 - y)
                    if dx + dy < 3:
                        top_surf.set_at((x, y), (0, 0, 0, 0))

    # Tier-specific details
    if tier == 1:
        draw_crack_lines(top_surf, 2, darken(base_palette[0], 20), seed=3001)
        # Moss spots
        draw_dots(top_surf, 3, [(80, 130, 60), (70, 120, 50)], seed=3002)
    elif tier == 2:
        # Shine highlight streak
        for i in range(5):
            sx = 5 + i * 2
            sy = 4 + i
            if sx < size and sy < size:
                top_surf.set_at((sx, sy), (255, 245, 180))
                if sx + 1 < size:
                    top_surf.set_at((sx + 1, sy), (255, 240, 160))
    else:
        # Crystal facet lines
        rng = random.Random(3003)
        for _ in range(3):
            x1 = rng.randint(5, size - 5)
            y1 = rng.randint(5, size - 5)
            length = rng.randint(4, 8)
            dx = rng.choice([-1, 1])
            for i in range(length):
                px, py = x1 + i * dx, y1 + i
                if 0 <= px < size and 0 <= py < size:
                    top_surf.set_at((px, py), brighten(base_palette[1], 30))
        # Sparkle pixels
        draw_dots(top_surf, 3, [(220, 200, 240), (240, 220, 255)], seed=3004)

    surf.blit(top_surf, (g, g))

    # Front face
    front = pygame.Surface((size, 10), pygame.SRCALPHA)
    pygame.draw.rect(front, dark, (0, 0, size, 10), border_radius=3)
    # Slight texture on front
    for x in range(1, size - 1, 3):
        front.set_at((x, 3), darken(dark, 8))
    surf.blit(front, (g, g + size - 2))

    # Border
    pygame.draw.rect(surf, dark, (g, g, size, size), 2, border_radius=4)

    # Highlight edge on top
    for x in range(g + 3, g + size - 3):
        surf.set_at((x, g + 2), brighten(base_palette[1], 35))

    return surf


# ---------------------------------------------------------------------------
# Entity sprite generators
# ---------------------------------------------------------------------------

def generate_crafting_station(size=32):
    """Generate a crafting station sprite (wooden workbench)."""
    surf = pygame.Surface((size, size + 16), pygame.SRCALPHA)

    wood_palette = [(180, 140, 100), (190, 150, 110), (170, 130, 90),
                    (185, 145, 105)]
    wood_dark = (140, 105, 70)

    # Table top
    top = pygame.Surface((size - 4, size - 4), pygame.SRCALPHA)
    noise = fbm_noise_2d(size - 4, size - 4, octaves=2, base_grid=6, seed=4000)
    fill_with_noise(top, wood_palette, noise)
    # Wood grain - horizontal lines
    rng = random.Random(4001)
    for _ in range(4):
        gy = rng.randint(3, size - 8)
        gc = darken(wood_palette[2], 10)
        for gx in range(size - 4):
            top.set_at((gx, gy), gc)
    pygame.draw.rect(top, wood_dark, (0, 0, size - 4, size - 4), 1,
                     border_radius=3)
    surf.blit(top, (2, 2))

    # Front face (legs/apron)
    front = pygame.Surface((size - 4, 16), pygame.SRCALPHA)
    pygame.draw.rect(front, wood_dark, (0, 0, size - 4, 16), border_radius=2)
    # Leg details
    leg_color = darken(wood_dark, 15)
    pygame.draw.rect(front, leg_color, (2, 2, 4, 14))
    pygame.draw.rect(front, leg_color, (size - 10, 2, 4, 14))
    # Cross brace
    for x in range(6, size - 10):
        front.set_at((x, 8), darken(wood_dark, 8))
    surf.blit(front, (2, size - 4))

    # Highlight on top edge of table
    for x in range(4, size - 4):
        surf.set_at((x, 3), brighten(wood_palette[1], 20))

    return surf


def generate_portal_frame(width=64, height=64):
    """Generate a portal stone archway frame."""
    surf = pygame.Surface((width, height + 16), pygame.SRCALPHA)

    stone_palette = [(80, 85, 95), (90, 95, 105), (75, 80, 90), (85, 90, 100)]
    stone_dark = (55, 60, 68)

    # Outer frame
    frame_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    noise = fbm_noise_2d(width, height, octaves=2, base_grid=8, seed=5000)
    fill_with_noise(frame_surf, stone_palette, noise)
    # Carve out inner area (transparent)
    inner_x, inner_y = 8, 8
    inner_w, inner_h = width - 16, height - 16
    for y in range(inner_y, inner_y + inner_h):
        for x in range(inner_x, inner_x + inner_w):
            frame_surf.set_at((x, y), (0, 0, 0, 0))

    # Inner border detail
    for x in range(inner_x - 1, inner_x + inner_w + 1):
        frame_surf.set_at((x, inner_y - 1), stone_dark)
        if inner_y + inner_h < height:
            frame_surf.set_at((x, inner_y + inner_h), stone_dark)
    for y in range(inner_y - 1, inner_y + inner_h + 1):
        frame_surf.set_at((inner_x - 1, y), stone_dark)
        if inner_x + inner_w < width:
            frame_surf.set_at((inner_x + inner_w, y), stone_dark)

    # Rune-like dots on frame
    rng = random.Random(5001)
    rune_color = (120, 130, 160)
    for _ in range(6):
        rx = rng.choice([3, width - 4])
        ry = rng.randint(10, height - 15)
        frame_surf.set_at((rx, ry), rune_color)
        frame_surf.set_at((rx, ry + 1), rune_color)

    # Arch stones on top
    for x in range(4, width - 4):
        frame_surf.set_at((x, 2), brighten(stone_palette[1], 15))

    surf.blit(frame_surf, (0, 0))

    # Front face depth
    front = pygame.Surface((width, 16), pygame.SRCALPHA)
    pygame.draw.rect(front, stone_dark, (0, 0, width, 16), border_radius=3)
    noise_f = fbm_noise_2d(width, 16, octaves=1, base_grid=8, seed=5002)
    for y in range(16):
        for x in range(width):
            n = noise_f[y][x]
            if n > 0.6:
                r, g, b = front.get_at((x, y))[:3]
                front.set_at((x, y), (min(255, r + 5), min(255, g + 5),
                                       min(255, b + 5)))
    for x in range(width):
        front.set_at((x, 0), brighten(stone_dark, 10))
    surf.blit(front, (0, height - 4))

    return surf


def generate_portal_locked(width=64, height=64):
    """Generate a locked portal overlay (chains across inner area)."""
    surf = pygame.Surface((width, height + 16), pygame.SRCALPHA)

    # Dark locked appearance
    locked_palette = [(55, 55, 60), (60, 60, 65), (50, 50, 55)]
    noise = fbm_noise_2d(width, height, octaves=2, base_grid=8, seed=5100)
    frame_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    fill_with_noise(frame_surf, locked_palette, noise)

    # Inner dark area
    inner_x, inner_y = 8, 8
    inner_w, inner_h = width - 16, height - 16
    for y in range(inner_y, inner_y + inner_h):
        for x in range(inner_x, inner_x + inner_w):
            frame_surf.set_at((x, y), (25, 25, 30, 255))

    # Chain / cross bars
    chain_color = (90, 85, 80)
    chain_highlight = (110, 105, 100)
    mid_y = height // 2
    mid_x = width // 2
    # Horizontal chain
    for x in range(inner_x, inner_x + inner_w):
        frame_surf.set_at((x, mid_y), chain_color)
        frame_surf.set_at((x, mid_y + 1), chain_highlight)
    # Vertical chain
    for y in range(inner_y, inner_y + inner_h):
        frame_surf.set_at((mid_x, y), chain_color)
        frame_surf.set_at((mid_x + 1, y), chain_highlight)

    surf.blit(frame_surf, (0, 0))

    # Front face
    front = pygame.Surface((width, 16), pygame.SRCALPHA)
    pygame.draw.rect(front, (45, 45, 50), (0, 0, width, 16), border_radius=3)
    surf.blit(front, (0, height - 4))

    return surf


def generate_hint_stone(size=28):
    """Generate a hint stone sprite."""
    surf = pygame.Surface((size, size + 8), pygame.SRCALPHA)

    stone_palette = [(152, 132, 112), (160, 140, 120), (145, 125, 105),
                     (155, 135, 115)]
    dark = (140, 120, 100)

    # Main stone body
    body = pygame.Surface((size, size), pygame.SRCALPHA)
    noise = fbm_noise_2d(size, size, octaves=2, base_grid=5, seed=6000)
    fill_with_noise(body, stone_palette, noise)

    # Round the edges
    for y in range(size):
        for x in range(size):
            dx = min(x, size - 1 - x)
            dy = min(y, size - 1 - y)
            if dx + dy < 4:
                body.set_at((x, y), (0, 0, 0, 0))

    # Moss at base
    rng = random.Random(6001)
    for _ in range(4):
        mx = rng.randint(4, size - 5)
        my = rng.randint(size - 6, size - 3)
        body.set_at((mx, my), (80, 120, 60))

    # Carved question mark
    q_color = (80, 60, 40)
    cx = size // 2
    # Top curve of ?
    for dx in range(-2, 3):
        body.set_at((cx + dx, 7), q_color)
    body.set_at((cx + 3, 8), q_color)
    body.set_at((cx + 3, 9), q_color)
    body.set_at((cx + 2, 10), q_color)
    body.set_at((cx + 1, 11), q_color)
    body.set_at((cx, 12), q_color)
    body.set_at((cx, 13), q_color)
    # Dot
    body.set_at((cx, 16), q_color)
    body.set_at((cx, 17), q_color)

    surf.blit(body, (0, 0))

    # Front face
    front = pygame.Surface((size, 8), pygame.SRCALPHA)
    pygame.draw.rect(front, dark, (0, 0, size, 8), border_radius=3)
    # Clear rounded corners
    for y in range(8):
        for x in range(size):
            dx = min(x, size - 1 - x)
            if dx < 3 and y < 2:
                front.set_at((x, y), (0, 0, 0, 0))
    surf.blit(front, (0, size - 2))

    return surf


# ---------------------------------------------------------------------------
# Particle sprite generator
# ---------------------------------------------------------------------------

def generate_sparkle_frames():
    """Generate 4 sparkle particle frames (small star shapes)."""
    frames = []
    colors = [(255, 255, 200), (255, 240, 150), (255, 220, 100), (255, 200, 80)]
    sizes = [6, 5, 4, 3]

    for i, (color, sz) in enumerate(zip(colors, sizes)):
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        c = 3  # center
        # Cross pattern star
        for d in range(sz // 2 + 1):
            alpha = max(50, 255 - d * 60)
            pc = (*color, alpha)
            if c - d >= 0:
                surf.set_at((c - d, c), pc)
            if c + d < 8:
                surf.set_at((c + d, c), pc)
            if c - d >= 0:
                surf.set_at((c, c - d), pc)
            if c + d < 8:
                surf.set_at((c, c + d), pc)
        # Center bright pixel
        surf.set_at((c, c), (255, 255, 255, 255))
        frames.append(surf)
    return frames


# ---------------------------------------------------------------------------
# Main generation pipeline
# ---------------------------------------------------------------------------

def save_surface(surface, relative_path):
    """Save a pygame surface as PNG to the assets directory."""
    full_path = os.path.join(ASSETS_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    pygame.image.save(surface, full_path)
    print(f'  Saved: {relative_path}')


def generate_all():
    """Generate all game sprites."""
    pygame.init()
    # We don't need a display, just surface operations
    pygame.display.set_mode((1, 1), pygame.HIDDEN)

    print('=== MathMine Sprite Generator ===\n')

    # --- Tiles ---
    tile_generators = {
        'stacklands': generate_stacklands_tiles,
        'crumble_caves': generate_crumble_caves_tiles,
        'factor_forest': generate_factor_forest_tiles,
        'dividing_desert': generate_dividing_desert_tiles,
        'hub': generate_hub_tiles,
    }

    for biome_name, gen_fn in tile_generators.items():
        print(f'Generating {biome_name} tiles...')
        floor, floor_alt, wall_top, wall_front = gen_fn()
        base = os.path.join('tiles', biome_name)
        save_surface(floor, os.path.join(base, 'floor.png'))
        save_surface(floor_alt, os.path.join(base, 'floor_alt.png'))
        save_surface(wall_top, os.path.join(base, 'wall_top.png'))
        save_surface(wall_front, os.path.join(base, 'wall_front.png'))

    # --- Player ---
    print('\nGenerating player sprites...')
    player_sprites = generate_player_sprites()
    for name, surf in player_sprites.items():
        save_surface(surf, os.path.join('sprites', 'player', f'player_{name}.png'))

    # --- Blocks ---
    print('\nGenerating block sprites...')
    for tier in [1, 2, 3]:
        block = generate_block_sprite(tier)
        save_surface(block, os.path.join('sprites', 'blocks', f'block_t{tier}.png'))

    # --- Entities ---
    print('\nGenerating entity sprites...')
    station = generate_crafting_station()
    save_surface(station, os.path.join('sprites', 'entities', 'crafting_station.png'))

    portal_frame = generate_portal_frame()
    save_surface(portal_frame,
                 os.path.join('sprites', 'entities', 'portal_frame.png'))

    portal_locked = generate_portal_locked()
    save_surface(portal_locked,
                 os.path.join('sprites', 'entities', 'portal_locked.png'))

    hint = generate_hint_stone()
    save_surface(hint, os.path.join('sprites', 'entities', 'hint_stone.png'))

    # --- Particles ---
    print('\nGenerating particle sprites...')
    sparkles = generate_sparkle_frames()
    for i, frame in enumerate(sparkles):
        save_surface(frame, os.path.join('particles', f'sparkle_{i:02d}.png'))

    print(f'\nDone! All sprites saved to {ASSETS_DIR}')
    pygame.quit()


if __name__ == '__main__':
    generate_all()
