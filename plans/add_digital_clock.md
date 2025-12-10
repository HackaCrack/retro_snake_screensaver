# Add Digital Clock Feature

## Overview
Add a retro-style digital clock display to the screensaver, centered on screen(s), with comprehensive configuration options.

## Requirements

### Core Functionality
- Digital clock display (LED/7-segment style or blocky pixel font)
- Centered positioning on monitor(s)
- Real-time time updates
- Own module: `retro_snake/clock.py`

### Configuration Options
1. **Enabled/Disabled** - Master toggle to show/hide clock
2. **Show Seconds** - Toggle seconds display (HH:MM vs HH:MM:SS)
3. **12/24 Hour Format** - Toggle between 12-hour (with AM/PM) and 24-hour format
4. **Show/Hide Date** - Toggle date display (e.g., "Mon Jan 15, 2024")
5. **Collision Enabled/Disabled** - When disabled, clock draws behind food and stars; when enabled, clock draws on top and snakes can collide with the clock
6. **Show on All Monitors** - When enabled, clock appears centered on each monitor; when disabled, only on primary/main monitor

## Implementation Plan

### 1. Create Clock Module (`retro_snake/clock.py`)
- **Clock class** similar to `StarField` structure
- Methods:
  - `__init__(config, monitors)` - Initialize with config and monitor info
  - `update()` - Update time (called each frame, but only recalc when needed)
  - `draw(surface, draw_order)` - Draw clock based on collision setting
  - `get_time_string()` - Format time based on config
  - `get_date_string()` - Format date string
  - `draw_digit(surface, digit, x, y, size)` - Draw individual digit (7-segment style or pixel font)
  - `get_clock_bounds()` - Return bounding rect for collision detection (if needed)

### 2. Update Config System (`retro_snake/config.py`)
- Add default values to `DEFAULT_CONFIG`:
  ```python
  'clock_enabled': True,
  'clock_show_seconds': True,
  'clock_24_hour': False,
  'clock_show_date': True,
  'clock_collision': False,  # False = behind, True = on top
  'clock_all_monitors': True,
  ```

### 3. Update UI Dialog (`retro_snake/ui.py`)
- Add new UI elements in `ConfigDialog.__init__()`:
  - Checkbox: "Enable Clock"
  - Checkbox: "Show Seconds"
  - Checkbox: "24 Hour Format"
  - Checkbox: "Show Date"
  - Checkbox: "Clock on Top (collision enabled)"
  - Checkbox: "Show on All Monitors"
- Update `save_settings()` to save clock config
- Position these controls in the dialog (may need to adjust layout or add scrolling)

### 4. Integrate into ScreenSaver (`retro_snake/screensaver.py`)
- Import clock module
- In `__init__()`:
  - Load clock config from config
  - Initialize `self.clock = Clock(config, self.monitors)` if enabled
- In `draw()`:
  - Determine draw order based on `clock_collision` setting
  - If collision disabled: draw clock after background/starfield but before food/snakes
  - If collision enabled: draw clock after everything (on top)
  - Handle multi-monitor: if `clock_all_monitors`, draw centered on each monitor; otherwise, find primary monitor and draw there only

### 5. Primary Monitor Detection
- Need to identify primary monitor
- Options:
  - Use `screeninfo` Monitor's `is_primary` attribute (if available in the monitor objects)
  - Use first monitor (index 0) as fallback
  - Store original monitor info with `is_primary` flag when initializing ScreenSaver

### 6. Visual Design Considerations
- **Font Style**: 
  - Option A: 7-segment LED style (blocky segments)
  - Option B: Pixel font (chunky retro font)
  - Option C: Simple large text with retro colors
- **Colors**: Match retro aesthetic (BRIGHT_GREEN, CYAN, or configurable)
- **Size**: Scale based on monitor size (e.g., 10% of screen height)
- **Positioning**: True center (both X and Y) of each monitor

### 7. Date Format
- Format: "Mon Jan 15, 2024" or similar
- Position: Below or above time
- Style: Smaller font than time

## Technical Details

### Drawing Order Logic
```python
# In draw() method:
if transparent_mode:
    draw desktop background
    draw trail surface
else:
    fill black
    draw starfield
    draw grid lines

# Clock position 1 (behind): if not clock_collision
if clock_enabled and not clock_collision:
    clock.draw(screen, monitors)

# Game elements
draw food
draw snakes
draw death animations

# Clock position 2 (on top): if clock_collision
if clock_enabled and clock_collision:
    clock.draw(screen, monitors)

# UI elements
draw leaderboard
```

### Multi-Monitor Logic
- If `clock_all_monitors`:
  - Loop through `self.monitors` list
  - For each monitor, calculate center: `(monitor['x'] + monitor['width']//2, monitor['y'] + monitor['height']//2)`
  - Draw clock at that position
- If not `clock_all_monitors`:
  - Find primary monitor (check `is_primary` or use first monitor)
  - Calculate center of primary monitor only
  - Draw clock there

### Performance
- Only recalculate time string when seconds change (if showing seconds) or minutes change (if not)
- Cache time string and date string
- Use efficient drawing (pre-render digits if using complex 7-segment style)

## Testing Considerations
- Test with single monitor
- Test with multiple monitors (2+)
- Test all configuration combinations
- Test in windowed mode
- Test in preview mode
- Verify clock updates correctly
- Verify positioning is truly centered
- Verify collision setting affects draw order correctly

## Future Enhancements (Optional)
- Customizable clock color
- Clock size slider
- Different font styles
- Blinking colon separator
- Timezone selection
- Custom date format

