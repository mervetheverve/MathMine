"""Particle effect system for visual juice."""
import os
import random
import pygame
from assets.sprite_loader import load_sprite


class Particle:
    """A single particle with position, velocity, lifetime, and sprite."""

    def __init__(self, x, y, vx, vy, lifetime, sprite):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.sprite = sprite

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.05  # slight upward drift
        self.lifetime -= 1

    @property
    def alive(self):
        return self.lifetime > 0


class ParticleSystem:
    """Manages all active particles."""

    def __init__(self):
        self.particles = []
        self._sparkle_frames = []
        self._load_sparkles()

    def _load_sparkles(self):
        """Load sparkle sprite frames."""
        for i in range(4):
            path = os.path.join('particles', f'sparkle_{i:02d}.png')
            self._sparkle_frames.append(
                load_sprite(path, (8, 8), (255, 255, 200)))

    def emit_sparkle(self, x, y, count=6):
        """Emit sparkle particles at a world position."""
        for _ in range(count):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-2.5, -0.5)
            lifetime = random.randint(15, 30)
            sprite = random.choice(self._sparkle_frames)
            self.particles.append(Particle(x, y, vx, vy, lifetime, sprite))

    def update(self):
        """Tick all particles, remove dead ones."""
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface, camera):
        """Draw all living particles."""
        for p in self.particles:
            # Fade out based on remaining lifetime
            ratio = p.lifetime / p.max_lifetime
            alpha = int(255 * ratio)
            sprite = p.sprite.copy()
            sprite.set_alpha(alpha)
            sx = p.x - camera.offset_x - sprite.get_width() // 2
            sy = p.y - camera.offset_y - sprite.get_height() // 2
            surface.blit(sprite, (sx, sy))
