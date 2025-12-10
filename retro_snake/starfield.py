"""
StarField background effect for Retro Snake Screensaver
"""

import pygame
import random
import math
from retro_snake import constants


class StarField:
    """Retro starfield background effect"""
    def __init__(self, num_stars=100, width=None, height=None):
        self.stars = []
        # Use provided dimensions or fall back to globals
        w = width if width is not None else constants.SCREEN_WIDTH
        h = height if height is not None else constants.SCREEN_HEIGHT
        for _ in range(num_stars):
            x = random.randint(0, w)
            y = random.randint(0, h)
            brightness = random.randint(50, 150)
            twinkle_speed = random.uniform(0.02, 0.08)
            self.stars.append([x, y, brightness, twinkle_speed, random.uniform(0, math.pi * 2)])
    
    def update(self):
        for star in self.stars:
            star[4] += star[3]  # Update twinkle phase
    
    def draw(self, surface):
        for x, y, base_brightness, _, phase in self.stars:
            brightness = int(base_brightness + math.sin(phase) * 30)
            brightness = max(30, min(180, brightness))
            color = (brightness, brightness, brightness)
            surface.set_at((x, y), color)

