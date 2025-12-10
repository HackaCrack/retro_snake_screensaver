"""
Constants and enums for Retro Snake Screensaver
"""

from enum import Enum

# Grid settings - these will be set properly when ScreenSaver initializes
CELL_SIZE = 20
SCREEN_WIDTH = 1920  # Default, will be overwritten
SCREEN_HEIGHT = 1080  # Default, will be overwritten
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Colors - Retro Windows 95 palette
BLACK = (0, 0, 0)
DARK_BLUE = (0, 0, 128)
BRIGHT_GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Retro color palette for variety
RETRO_COLORS = [BRIGHT_GREEN, CYAN, MAGENTA, YELLOW, RED]


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

