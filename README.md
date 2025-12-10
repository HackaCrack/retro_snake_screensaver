# 🐍 Retro Snake Screensaver

A nostalgic Windows 95-era style screensaver featuring AI-controlled snakes that roam the screen, collecting food and growing longer.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)

## Features

- **Multiple AI-Controlled Snakes**: Watch multiple snakes compete for food (up to 150 snakes!)
- **Retro Aesthetics**: Classic Windows 95 era visual style with:
  - Pixelated graphics
  - Twinkling starfield background
  - Pulsing food items
  - Unique colors for each snake (using HSV golden ratio for maximum contrast)
  - Subtle grid lines
- **Desktop Background Mode**: Optional transparent mode that uses your desktop as the background, with configurable trail effects
- **Trail Effects**: Snakes leave trails that can accumulate and darken with each pass
- **Death Animations**: Cool dissolving particle effect when snakes crash
- **Growth Mechanics**: Snakes grow when they eat food
- **Wrap-Around Movement**: Snakes wrap around screen edges (toroidal topology)
- **Smart Turning**: Snakes only turn every couple seconds, with configurable dodge chance
- **Leaderboard**: Live-sorted display showing snake rankings by length (can be toggled)
- **Windows Screensaver Support**: Full /s, /c, /p argument support
- **Retro Configuration Dialog**: Windows 95-style settings menu with instant autosave

## Installation

1. Make sure you have Python 3.7+ installed
2. Run the install script:

```bash
install.bat
```

Or manually:
```bash
pip install -r requirements.txt
```

## Usage

### Run as Fullscreen Screensaver
```bash
python -m retro_snake.main
# or
python -m retro_snake.main /s
# or use the batch file:
run_snakescreensaver.bat
```

### Run in Windowed Mode (for testing)
```bash
python -m retro_snake.main -w
# or
run_snakescreensaver.bat -w
```

### Open Configuration Dialog
```bash
python -m retro_snake.main /c
# or
run_snakescreensaver.bat /c
```

### Preview Mode
```bash
python -m retro_snake.main /p
# or
run_snakescreensaver.bat /p
```

## Building as Windows Screensaver (.scr)

1. Run `install.bat` first (if not already done)
2. Run `build_snakescreensaver.bat` to create the executable
3. The script automatically renames `dist\RetroSnake.exe` to `RetroSnake.scr` (or `RetroSnake##.scr` if the file already exists)
4. Either:
   - Right-click `dist\RetroSnake.scr` and select "Install", OR
   - Copy to `C:\Windows\System32\`

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `/s`, `-s` | Run screensaver (fullscreen) |
| `/c`, `-c` | Open configuration dialog |
| `/p`, `-p` | Preview mode |
| `-w`, `--windowed` | Run in 1024x768 window for testing |

## Configuration

Settings are stored in `%APPDATA%\RetroSnakeScreensaver\config.json` and are automatically saved when changed in the configuration dialog.

| Setting | Range | Description |
|---------|-------|-------------|
| Number of Snakes | 1-150 | How many snakes on screen |
| Food Items | 5-200 | Amount of food spawned |
| Speed (FPS) | 5-120 | Game speed (frames per second) |
| Dodge Chance | 0-100% | How likely snakes avoid crashes (lower = more crashes!) |
| Min Starting Length | 1-100 | Minimum initial length of snakes when spawned |
| Max Starting Length | 1-100 | Maximum initial length of snakes when spawned |
| Show Scores and Names | On/Off | Toggle the leaderboard display |
| Desktop Background | On/Off | Use desktop screenshot as background (transparent mode) |
| Trail Darkness | 0-20 | How dark the trails are (0 = off, higher = darker) |
| Accumulative Trails | On/Off | Trails get darker with each pass (only in desktop background mode) |

## Controls

This is a screensaver - there are no controls! The snakes are fully AI-controlled.

**To Exit:**
- Press any key
- Click the mouse
- Move the mouse significantly (>50 pixels)

## How It Works

### Snake AI

1. **Turn Timer**: Snakes only consider turning after a certain number of frames
2. **Safe Direction Detection**: Before moving, checks which directions won't cause collision
3. **Look-Ahead**: Evaluates paths to find open space
4. **Dodge Chance**: Configurable chance to actually dodge when about to crash (more crashes = more fun!)

### Multi-Snake Interaction

- Each snake avoids all other snakes
- Head-to-body collisions cause death (with cool dissolving animation)
- Snakes respawn at starting size with a fresh score
- Leaderboard shows rankings in real-time

## File Structure

```
Snakes/
├── retro_snake/              # Main package
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Entry point (handles Windows screensaver args)
│   ├── screensaver.py       # Main screensaver logic
│   ├── snake.py             # Snake AI and behavior
│   ├── food.py              # Food spawning and management
│   ├── starfield.py         # Background starfield effect
│   ├── ui.py                # Configuration dialog UI
│   ├── preview.py           # Preview window implementation
│   ├── config.py            # Configuration management
│   ├── constants.py         # Game constants
│   ├── name_generator.py    # Snake name generation
│   └── utils.py             # Utility functions
├── requirements.txt         # Python dependencies
├── install.bat             # Install dependencies (creates venv)
├── run_snakescreensaver.bat # Run screensaver
├── build_snakescreensaver.bat # Build .scr with PyInstaller
├── RetroSnake.spec         # PyInstaller spec file
├── snake_icon.ico          # Screensaver icon
└── README.md               # This file
```

## License

Free to use, modify, and distribute.

## Nostalgia Factor

Remember when screensavers were actually necessary to prevent CRT burn-in? This is a tribute to that era of computing, when After Dark and Flying Toasters ruled the desktop. Enjoy the retro vibes! 🕹️
