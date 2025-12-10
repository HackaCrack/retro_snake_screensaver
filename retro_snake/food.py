"""
Food class for Retro Snake Screensaver
"""

import pygame
import random
import math
from retro_snake import constants


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = random.choice([constants.RED, constants.YELLOW, constants.CYAN, constants.MAGENTA])
        self.pulse_timer = 0
        self.base_size = constants.CELL_SIZE - 4
        
    def get_pos(self):
        return (self.x, self.y)
    
    def draw(self, surface, screen_saver=None):
        """Draw food with pulsing effect"""
        self.pulse_timer += 0.15
        pulse = math.sin(self.pulse_timer) * 2
        size = self.base_size + pulse
        
        center_x = self.x * constants.CELL_SIZE + constants.CELL_SIZE // 2
        center_y = self.y * constants.CELL_SIZE + constants.CELL_SIZE // 2
        
        # Draw pixelated diamond/apple shape
        points = [
            (center_x, center_y - size // 2),
            (center_x + size // 2, center_y),
            (center_x, center_y + size // 2),
            (center_x - size // 2, center_y)
        ]
        pygame.draw.polygon(surface, self.color, points)
        
        # Retro highlight
        pygame.draw.line(surface, constants.WHITE, 
                        (center_x - 2, center_y - 2),
                        (center_x - 4, center_y - 4), 2)
    
    def draw_on_monitor(self, surface, monitor):
        """Draw food if it's visible on a specific monitor"""
        # Don't update pulse_timer here - it's updated in the main draw loop
        pulse = math.sin(self.pulse_timer) * 2
        size = self.base_size + pulse
        
        center_x = self.x * constants.CELL_SIZE + constants.CELL_SIZE // 2
        center_y = self.y * constants.CELL_SIZE + constants.CELL_SIZE // 2
        
        mon_x = monitor['x']
        mon_y = monitor['y']
        mon_w = monitor['width']
        mon_h = monitor['height']
        
        # Skip drawing if not visible on this monitor
        if not (mon_x <= center_x < mon_x + mon_w and mon_y <= center_y < mon_y + mon_h):
            return
        
        # Convert to monitor-local coordinates
        local_center_x = center_x - mon_x
        local_center_y = center_y - mon_y
        
        # Draw pixelated diamond/apple shape
        points = [
            (local_center_x, local_center_y - size // 2),
            (local_center_x + size // 2, local_center_y),
            (local_center_x, local_center_y + size // 2),
            (local_center_x - size // 2, local_center_y)
        ]
        pygame.draw.polygon(surface, self.color, points)
        
        # Retro highlight
        pygame.draw.line(surface, constants.WHITE,
                        (local_center_x - 2, local_center_y - 2),
                        (local_center_x - 4, local_center_y - 4), 2)

