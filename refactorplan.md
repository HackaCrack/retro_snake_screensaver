# Refactor Plan for snake_screensaver.py

Explored 1 directory, 1 file, 0 searches

Here's a refactor plan to split the 1603-line file into a package in `retro_snake/`.

## Proposed File Structure

```
Snakes/
├── backup/                     # Created during execution; mirrors original sources
│   └── snake_screensaver.py
└── retro_snake/                # New package layout (final destination)
    ├── __init__.py             # Export surface
    ├── config.py               # Configuration management
    ├── constants.py            # Colors, enums, constants
    ├── snake.py                # Snake class with AI logic
    ├── food.py                 # Food class
    ├── starfield.py            # StarField background effect
    ├── ui.py                   # UI components (RetroButton, RetroSlider, ConfigDialog)
    ├── preview.py              # PreviewWindow and preview functions
    ├── screensaver.py          # ScreenSaver main manager class
    ├── utils.py                # Utility functions (cleanup, DPI, atexit)
    └── main.py                 # Entry point and argument parsing
```

## Module Breakdown

1. **config.py** (~60 lines)
   - `get_config_path()`, `load_config()`, `save_config()`
   - `DEFAULT_CONFIG` dictionary
   - Global config variable management
   - Dependencies: `os`, `json`, `pathlib`

2. **constants.py** (~50 lines)
   - `Direction` enum
   - Color constants (BLACK, DARK_BLUE, BRIGHT_GREEN, etc.)
   - `RETRO_COLORS` list
   - Grid constants (CELL_SIZE, will be updated by ScreenSaver)
   - Dependencies: `enum`

3. **snake.py** (~230 lines)
   - `Snake` class with AI logic, movement, collision detection, drawing
   - Methods: `get_head()`, `get_body_set()`, `choose_direction()`, `move()`, `grow()`, `check_self_collision()`, `draw()`, `draw_on_monitor()`
   - Dependencies: `pygame`, `random`, `collections.deque`, `constants`, `config` (for DODGE_CHANCE)

4. **food.py** (~70 lines)
   - `Food` class with pulsing animation
   - Methods: `get_pos()`, `draw()`, `draw_on_monitor()`
   - Dependencies: `pygame`, `random`, `math`, `constants`

5. **starfield.py** (~25 lines)
   - `StarField` class for background effect
   - Methods: `update()`, `draw()`
   - Dependencies: `pygame`, `random`, `math`

6. **ui.py** (~350 lines)
   - `RetroButton` class (Windows 95 style button)
   - `RetroSlider` class (Windows 95 style slider)
   - `ConfigDialog` class (configuration UI dialog)
   - Dependencies: `pygame`, `constants`, `config`

7. **preview.py** (~200 lines)
   - `PreviewWindow` class (embedded preview for Windows screensaver)
   - `run_fallback_preview()` function
   - Windows API integration for preview embedding
   - Dependencies: `pygame`, `win32gui`, `win32con`, `constants`, `config`, `screensaver`

8. **screensaver.py** (~420 lines)
   - `ScreenSaver` class (main game manager)
   - Methods: `__init__()`, `handle_events()`, `update()`, `draw()`, `run()`, `create_snake()`, `spawn_food()`, `start_death_animation()`, `update_death_animations()`
   - Multi-monitor support, game loop, collision detection
   - Dependencies: `pygame`, `screeninfo`, `constants`, `config`, `snake`, `food`, `starfield`, `utils`

9. **utils.py** (~80 lines)
   - `register_atexit_cleanup()`, `_emergency_cleanup()`
   - DPI awareness setup
   - `cleanup_pygame()` function
   - Dependencies: `pygame`, `ctypes`, `atexit`

10. **main.py** (~60 lines)
    - `parse_windows_args()` function
    - `main()` entry point
    - Mode routing (screensaver, configure, preview, windowed)
    - Dependencies: `sys`, `config`, `screensaver`, `ui`, `preview`, `utils`

11. **__init__.py** (~20 lines)
    - Public exports: `main`, `ScreenSaver`, `ConfigDialog`, `PreviewWindow`
    - Re-export key classes for backward compatibility if needed
    - Dependencies: All modules

## Benefits

- Each module ≤ 500 lines (largest is screensaver.py at ~420 lines)
- Clear separation of concerns (game logic, UI, configuration, utilities)
- Easier testing (can test Snake AI, Food, UI components independently)
- Lower cognitive load and faster iteration
- Better maintainability (changes to UI don't affect game logic)

## Migration Plan

- Create `backup/` beside the current sources and move `snake_screensaver.py` into it
- Create `retro_snake/` package and split `snake_screensaver.py` into modules above
- Add `__init__.py` with public exports (`main`, `ScreenSaver`, `ConfigDialog`, `PreviewWindow`)
- Update `build.bat` to use `retro_snake/main.py` as entry point instead of `snake_screensaver.py`
- Update PyInstaller spec file (`RetroSnake.spec`) if it exists to reference new entry point
- Run tests and verify screensaver still works in all modes (/s, /c, /p)

