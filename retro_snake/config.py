"""
Configuration management for Retro Snake Screensaver
"""

import json
import os
from pathlib import Path

# Default values (can be overridden by config file)
DEFAULT_CONFIG = {
    'num_snakes': 30, # sets the number of snakes on the screen
    'num_food': 50, # sets the number of food items on the screen
    'speed': 12, # sets the FPS of the game which affects the speed of the snakes
    'dodge_chance': 100,  # Percentage (0-100) (Even at 100% the snakes will still crash into each other if they get trapped.)
    'min_starting_length': 4,  # Minimum initial length of snakes when spawned (1-100)
    'max_starting_length': 4,  # Maximum initial length of snakes when spawned (1-100)
    'show_leaderboard': True, # Show the leaderboard with the names and scores of the snakes
    'transparent_mode': True,  # Use desktop screenshot as background 
    'trail_darkness': 1,  # Trail darkness level (0-20, 0 = off, higher = darker)
    'accumulative_trails': True,  # Trails get darker with each pass
}

# These will be set from config
NUM_SNAKES = DEFAULT_CONFIG['num_snakes']
NUM_FOOD = DEFAULT_CONFIG['num_food']
SPEED = DEFAULT_CONFIG['speed']
DODGE_CHANCE = DEFAULT_CONFIG['dodge_chance'] / 100.0


def get_config_path():
    """Get path to config file in AppData"""
    appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
    config_dir = Path(appdata) / 'RetroSnakeScreensaver'
    config_dir.mkdir(exist_ok=True)
    return config_dir / 'config.json'


def load_config():
    """Load configuration from file"""
    global NUM_SNAKES, NUM_FOOD, SPEED, DODGE_CHANCE
    config_path = get_config_path()
    
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key in DEFAULT_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_CONFIG[key]
        else:
            config = DEFAULT_CONFIG.copy()
    except Exception:
        config = DEFAULT_CONFIG.copy()
    
    NUM_SNAKES = config.get('num_snakes', DEFAULT_CONFIG['num_snakes'])
    NUM_FOOD = config.get('num_food', DEFAULT_CONFIG['num_food'])
    SPEED = config.get('speed', DEFAULT_CONFIG['speed'])
    DODGE_CHANCE = config.get('dodge_chance', DEFAULT_CONFIG['dodge_chance']) / 100.0
    
    return config


def save_config(config):
    """Save configuration to file"""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")

