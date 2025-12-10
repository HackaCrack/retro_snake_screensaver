"""
ScreenSaver main manager class for Retro Snake Screensaver
"""

import pygame
import random
import os
import colorsys
from screeninfo import get_monitors
from retro_snake import constants
from retro_snake.config import SPEED
from retro_snake.snake import Snake
from retro_snake.food import Food
from retro_snake.starfield import StarField
from retro_snake.name_generator import generate_name

# Try to import PIL for desktop screenshot
try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Windows API for power management - allow system to sleep during screensaver
try:
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    # Execution state constants
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    HAS_WIN32_POWER = True
except (OSError, AttributeError, ImportError):
    HAS_WIN32_POWER = False


def capture_desktop_screenshot():
    """Capture a screenshot of the entire desktop before pygame takes over"""
    if not HAS_PIL:
        return None
    try:
        # Capture the entire screen (all monitors)
        screenshot = ImageGrab.grab(all_screens=True)
        return screenshot
    except Exception as e:
        print(f"Failed to capture desktop screenshot: {e}")
        return None


class ScreenSaver:
    def __init__(self, windowed=False, desktop_screenshot=None):
        
        # Store desktop screenshot if provided (captured before pygame init)
        self.desktop_screenshot_pil = desktop_screenshot
        
        # Initialize pygame here (not at module level) for proper DPI handling
        pygame.init()
        
        # Detect all monitors and calculate virtual desktop dimensions
        self.monitors = []
        self.virtual_width = 0
        self.virtual_height = 0
        self.virtual_x_offset = 0
        self.virtual_y_offset = 0
        
        if windowed:
            self.screen = pygame.display.set_mode((1024, 768))
            constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT = 1024, 768
            # Single "monitor" for windowed mode
            self.monitors = [{'x': 0, 'y': 0, 'width': 1024, 'height': 768}]
            self.virtual_width = 1024
            self.virtual_height = 768
            self.windowed = True
        else:
            self.windowed = False
            # Detect all monitors
            try:
                monitors_info = get_monitors()
                if monitors_info:
                    # Print debug info about detected monitors
                    print(f"Detected {len(monitors_info)} monitor(s):")
                    for i, m in enumerate(monitors_info):
                        print(f"  Monitor {i+1}: {m.width}x{m.height} at ({m.x}, {m.y})")
                    
                    # Calculate bounding box of all monitors
                    min_x = min(m.x for m in monitors_info)
                    min_y = min(m.y for m in monitors_info)
                    max_x = max(m.x + m.width for m in monitors_info)
                    max_y = max(m.y + m.height for m in monitors_info)
                    
                    self.virtual_x_offset = min_x
                    self.virtual_y_offset = min_y
                    self.virtual_width = max_x - min_x
                    self.virtual_height = max_y - min_y
                    
                    print(f"Virtual desktop: {self.virtual_width}x{self.virtual_height}")
                    print(f"Window position: ({min_x}, {min_y})")
                    
                    # Store monitor info normalized to virtual space
                    self.monitors = [
                        {
                            'x': m.x - min_x,
                            'y': m.y - min_y,
                            'width': m.width,
                            'height': m.height
                        }
                        for m in monitors_info
                    ]
                    
                    # Position the window at the top-left of all monitors
                    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{min_x},{min_y}"
                    
                    # Create a single window spanning all monitors
                    self.screen = pygame.display.set_mode(
                        (self.virtual_width, self.virtual_height),
                        pygame.NOFRAME
                    )
                else:
                    # Fallback if no monitors detected
                    self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
                    constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT = self.screen.get_size()
                    self.monitors = [{'x': 0, 'y': 0, 'width': SCREEN_WIDTH, 'height': SCREEN_HEIGHT}]
                    self.virtual_width = SCREEN_WIDTH
                    self.virtual_height = SCREEN_HEIGHT
            except Exception as e:
                print(f"Failed to detect monitors: {e}")
                # Fallback to single monitor
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
                constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT = self.screen.get_size()
                self.monitors = [{'x': 0, 'y': 0, 'width': SCREEN_WIDTH, 'height': SCREEN_HEIGHT}]
                self.virtual_width = SCREEN_WIDTH
                self.virtual_height = SCREEN_HEIGHT
            
            # Use virtual dimensions for game logic
            constants.SCREEN_WIDTH = self.virtual_width
            constants.SCREEN_HEIGHT = self.virtual_height
        
        # Calculate grid to cover entire virtual screen space
        constants.GRID_WIDTH = (self.virtual_width + constants.CELL_SIZE - 1) // constants.CELL_SIZE
        constants.GRID_HEIGHT = (self.virtual_height + constants.CELL_SIZE - 1) // constants.CELL_SIZE
        
        pygame.display.set_caption("Retro Snake Screensaver")
        pygame.mouse.set_visible(False)
        
        self.windowed = windowed
        
        self.clock = pygame.time.Clock()
        self.running = True
        from retro_snake.config import SPEED
        self.fps = SPEED  # Configurable speed
        
        # Initialize starfield background (more stars for larger space)
        num_stars = int(150 * (self.virtual_width * self.virtual_height) / (1920 * 1080))
        self.starfield = StarField(num_stars, self.virtual_width, self.virtual_height)
        
        # Initialize multiple snakes with unique colors
        self.snakes = []
        from retro_snake.config import NUM_SNAKES, NUM_FOOD
        self.snake_colors = self.generate_unique_colors(NUM_SNAKES)
        # Generate unique names for each snake
        self.snake_names = [generate_name() for _ in range(NUM_SNAKES)]
        for i in range(NUM_SNAKES):
            snake = self.create_snake(self.snake_colors[i], self.snake_names[i])
            self.snakes.append(snake)
        
        # Initialize food items
        self.food_items = []
        self.spawn_initial_food(NUM_FOOD)
        
        # Score display (retro style)
        self.font = pygame.font.Font(None, 36)
        
        # Load config to check if leaderboard should be shown
        from retro_snake.config import load_config
        config = load_config()
        self.show_leaderboard = config.get('show_leaderboard', True)
        
        # Transparent mode settings
        self.transparent_mode = config.get('transparent_mode', False)
        # Support both old and new config key names for backwards compatibility
        self.trail_darkness = config.get('trail_darkness', config.get('trail_fade_rate', 5))
        self.accumulative_trails = config.get('accumulative_trails', True)
        
        # Setup desktop background and trail surface for transparent mode
        self.desktop_background = None
        self.trail_surface = None
        if self.transparent_mode and self.desktop_screenshot_pil:
            self._setup_transparent_mode()
        
        # Death animations - list of active animations
        self.death_animations = []  # List of {'snake_index': i, 'segments': [...], 'timer': 0, 'color': color}
        
        # Track mouse position for exit detection
        self.initial_mouse_pos = pygame.mouse.get_pos()
        
        # Allow Windows to sleep even while screensaver is running
        # This prevents the screensaver from blocking power management
        self.previous_execution_state = None
        if HAS_WIN32_POWER:
            try:
                # Get current execution state
                self.previous_execution_state = kernel32.SetThreadExecutionState(ES_CONTINUOUS)
                # Set to allow sleep - only use ES_CONTINUOUS (no ES_SYSTEM_REQUIRED)
                # This tells Windows the screensaver is running but shouldn't prevent sleep
                kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            except Exception as e:
                print(f"Failed to set Windows execution state: {e}")
                self.previous_execution_state = None
    
    def _setup_transparent_mode(self):
        """Setup surfaces for transparent background mode"""
        try:
            # Convert PIL image to pygame surface
            pil_image = self.desktop_screenshot_pil
            
            # Get the bounding box for the virtual desktop
            # PIL captures from (0,0) but our window might be offset
            # We need to crop to match our virtual desktop area
            
            # The screenshot is of the entire virtual desktop
            # Resize/crop to match our window size
            img_width, img_height = pil_image.size
            
            # If the screenshot matches our virtual desktop, use it directly
            # Otherwise, we may need to adjust
            if img_width >= self.virtual_width and img_height >= self.virtual_height:
                # Crop to the area we're covering
                # Note: virtual_x_offset and virtual_y_offset are the top-left of our window
                # in screen coordinates. PIL's grab(all_screens=True) captures from the 
                # top-left of the virtual desktop which may have negative coordinates
                
                # For simplicity, resize to fit our window
                pil_image = pil_image.resize((self.virtual_width, self.virtual_height))
            
            # Convert to pygame surface
            mode = pil_image.mode
            size = pil_image.size
            data = pil_image.tobytes()
            
            self.desktop_background = pygame.image.fromstring(data, size, mode)
            
            # Create trail surface for accumulating black trails
            self.trail_surface = pygame.Surface((self.virtual_width, self.virtual_height), pygame.SRCALPHA)
            self.trail_surface.fill((0, 0, 0, 0))  # Start fully transparent
            
            print(f"Transparent mode initialized: {self.virtual_width}x{self.virtual_height}")
        except Exception as e:
            print(f"Failed to setup transparent mode: {e}")
            self.transparent_mode = False
            self.desktop_background = None
            self.trail_surface = None
    
    def _draw_trail_at_position(self, x, y, size):
        """Add a black trail mark at the given pixel position"""
        if self.trail_surface is not None:
            # Trail darkness 0 = off (no trails)
            if self.trail_darkness <= 0:
                return
            
            # Higher darkness = more opaque trails = faster/darker coverage
            # Scale from 1-20 to 13-255 alpha (at max setting, trails are fully black)
            alpha = int(13 * self.trail_darkness)  # 13-260, clamped to 255
            alpha = min(255, alpha)
            
            left = max(0, x - size // 2)
            top = max(0, y - size // 2)
            width = min(self.virtual_width - left, size)
            height = min(self.virtual_height - top, size)
            
            if width <= 0 or height <= 0:
                return
            
            if self.accumulative_trails:
                # Accumulative mode: use BLEND_RGBA_ADD to add alpha values
                # Each pass increases the alpha, making trails darker
                # Alpha automatically clamps at 255 (full black)
                temp_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                temp_surf.fill((0, 0, 0, alpha))
                self.trail_surface.blit(temp_surf, (left, top), special_flags=pygame.BLEND_RGBA_ADD)
            else:
                # Non-accumulative: just draw fixed alpha (won't get darker on repeat passes)
                trail_rect = pygame.Rect(left, top, width, height)
                pygame.draw.rect(self.trail_surface, (0, 0, 0, alpha), trail_rect)
    
    def generate_unique_colors(self, count):
        """Generate unique, maximally different colors for each snake using HSV"""
        colors = []
        
        # Use golden ratio to spread hues maximally apart
        golden_ratio = 0.618033988749895
        hue = random.random()  # Start at random hue
        
        for i in range(count):
            # Convert HSV to RGB (high saturation and value for vibrant retro colors)
            saturation = 0.8 + random.random() * 0.2  # 0.8-1.0 for vivid colors
            value = 0.9 + random.random() * 0.1       # 0.9-1.0 for brightness
            
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            color = (int(r * 255), int(g * 255), int(b * 255))
            colors.append(color)
            
            # Move hue by golden ratio for maximum spread
            hue = (hue + golden_ratio) % 1.0
        
        return colors
    
    def create_snake(self, color, name=None):
        """Create a new snake at a random position"""
        start_x = random.randint(10, constants.GRID_WIDTH - 10)
        start_y = random.randint(10, constants.GRID_HEIGHT - 10)
        snake = Snake(start_x, start_y, color, name)
        # Load starting length from config
        from retro_snake.config import load_config
        config = load_config()
        min_length = config.get('min_starting_length', 4)
        max_length = config.get('max_starting_length', 4)
        # Ensure min is not greater than max
        if min_length > max_length:
            min_length, max_length = max_length, min_length
        starting_length = random.randint(min_length, max_length)
        for _ in range(starting_length):
            snake.grow(1)
        return snake
    
    def spawn_initial_food(self, count):
        """Spawn initial food items"""
        for _ in range(count):
            self.spawn_food()
    
    def spawn_food(self):
        """Spawn a new food item in empty location"""
        occupied = set()
        for snake in self.snakes:
            if snake.alive:
                occupied.update(snake.get_body_set())
        occupied.update((f.x, f.y) for f in self.food_items)
        
        attempts = 0
        while attempts < 100:
            x = random.randint(0, constants.GRID_WIDTH - 1)
            y = random.randint(0, constants.GRID_HEIGHT - 1)
            if (x, y) not in occupied:
                self.food_items.append(Food(x, y))
                break
            attempts += 1
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Any key exits screensaver
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                # Exit if mouse moved significantly
                current_pos = pygame.mouse.get_pos()
                dx = abs(current_pos[0] - self.initial_mouse_pos[0])
                dy = abs(current_pos[1] - self.initial_mouse_pos[1])
                if dx > 50 or dy > 50:
                    self.running = False
    
    def start_death_animation(self, snake, snake_index):
        """Start the dissolve death animation for a specific snake"""
        snake.alive = False
        segments = []
        
        # Create dissolving particles for each body segment
        for i, (x, y) in enumerate(snake.body):
            # Calculate color (head is brighter)
            if i == 0:
                color = snake.color
            else:
                color = tuple(max(0, c - 40) for c in snake.color)
            
            # Create multiple particles per segment for better effect
            for _ in range(4):
                vx = random.uniform(-2, 2)
                vy = random.uniform(-2, 2)
                # Pixel position (center of cell)
                px = int(x * constants.CELL_SIZE + constants.CELL_SIZE // 2 + random.randint(-5, 5))
                py = int(y * constants.CELL_SIZE + constants.CELL_SIZE // 2 + random.randint(-5, 5))
                size = random.randint(3, 8)
                segments.append({
                    'x': px, 'y': py,
                    'vx': vx, 'vy': vy,
                    'color': color,
                    'alpha': 255,
                    'size': size,
                    'decay': random.uniform(4, 8)
                })
        
        # Reset the snake's body immediately so leaderboard shows 0 length
        snake.body.clear()
        snake.score = 0
        
        self.death_animations.append({
            'snake_index': snake_index,
            'segments': segments,
            'timer': 0,
            'color': snake.color
        })
    
    def update_death_animations(self):
        """Update all dissolving particle animations"""
        completed = []
        
        for anim in self.death_animations:
            anim['timer'] += 1
            
            # Update each particle
            for particle in anim['segments']:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['vy'] += 0.1  # Gravity
                particle['alpha'] -= particle['decay']
                particle['size'] = max(1, particle['size'] - 0.1)
            
            # Remove dead particles
            anim['segments'] = [p for p in anim['segments'] if p['alpha'] > 0]
            
            # Animation complete when all particles are gone or timeout
            if len(anim['segments']) == 0 or anim['timer'] > 60:
                completed.append(anim)
        
        # Respawn completed snakes
        for anim in completed:
            self.death_animations.remove(anim)
            snake_index = anim['snake_index']
            # Respawn with same color and name, reset score
            name = self.snake_names[snake_index] if snake_index < len(self.snake_names) else None
            self.snakes[snake_index] = self.create_snake(anim['color'], name)
    
    def get_all_obstacles(self, exclude_snake_index=None):
        """Get all obstacle positions (all snake bodies)"""
        obstacles = set()
        for i, snake in enumerate(self.snakes):
            if snake.alive and i != exclude_snake_index:
                obstacles.update(snake.get_body_set())
        return obstacles
    
    def update(self):
        """Update game state"""
        # Update starfield
        self.starfield.update()
        
        # Update food pulse timers
        for food in self.food_items:
            food.pulse_timer += 0.15
        
        # Update death animations
        if self.death_animations:
            self.update_death_animations()
        
        # First pass: collect all snake info for prediction
        snake_info = []
        for i, snake in enumerate(self.snakes):
            if snake.alive:
                snake_info.append({
                    'index': i,
                    'head': snake.get_head(),
                    'direction': snake.direction,
                    'body_set': snake.get_body_set()
                })
        
        # Update each alive snake
        for i, snake in enumerate(self.snakes):
            if not snake.alive:
                continue
            
            # Get all obstacles (own body + other snakes' current positions + predicted next positions)
            obstacles = snake.get_body_set()  # Own body
            
            # Add other snakes' current positions
            for j, other_snake in enumerate(self.snakes):
                if j != i and other_snake.alive:
                    obstacles.update(other_snake.get_body_set())
                    
                    # PREDICT other snakes' next positions (suggestion #1)
                    other_head = other_snake.get_head()
                    other_dx, other_dy = other_snake.direction.value
                    predicted_next_x = (other_head[0] + other_dx) % constants.GRID_WIDTH
                    predicted_next_y = (other_head[1] + other_dy) % constants.GRID_HEIGHT
                    obstacles.add((predicted_next_x, predicted_next_y))
            
            # Build other snakes info for proximity checking (suggestion #4)
            other_snakes_info = []
            for info in snake_info:
                if info['index'] != i:
                    other_snakes_info.append({
                        'head': info['head'],
                        'direction': info['direction'],
                        'body_set': info['body_set']
                    })
            
            # AI chooses direction (with other snakes info for proximity check)
            snake.choose_direction(obstacles, other_snakes_info)
            
            # FINAL SAFETY CHECK: Re-check if the chosen direction is safe
            # This catches cases where other snakes moved into our path after we decided
            current_obstacles = snake.get_body_set()
            for j, other_snake in enumerate(self.snakes):
                if j != i and other_snake.alive:
                    current_obstacles.update(other_snake.get_body_set())
            
            # Check if the next position is actually safe right now
            head_x, head_y = snake.get_head()
            dx, dy = snake.direction.value
            next_x = (head_x + dx) % constants.GRID_WIDTH
            next_y = (head_y + dy) % constants.GRID_HEIGHT
            
            if (next_x, next_y) in current_obstacles:
                # Danger! Try to find a safe direction immediately
                safe_dirs = snake.get_safe_directions(current_obstacles)
                if safe_dirs:
                    # Pick the best safe direction
                    best_dir = None
                    best_score = -1
                    for d in safe_dirs:
                        score = snake.look_ahead(d, current_obstacles, depth=5)
                        if score > best_score:
                            best_score = score
                            best_dir = d
                    if best_dir:
                        snake.direction = best_dir
            
            # Move snake
            snake.move()
            
            # Check for food collision
            head = snake.get_head()
            for food in self.food_items[:]:
                if food.get_pos() == head:
                    snake.grow(3)
                    self.food_items.remove(food)
                    self.spawn_food()
                    snake.score += 10
            
            # Check for self collision
            if snake.check_self_collision():
                self.start_death_animation(snake, i)
                continue
            
            # Check for collision with other snakes (head hitting any body)
            for j, other_snake in enumerate(self.snakes):
                if j != i and other_snake.alive:
                    # Check if this snake's head hit the other snake's body
                    if head in other_snake.get_body_set():
                        self.start_death_animation(snake, i)
                        break
    
    def grid_to_screen(self, grid_x, grid_y):
        """Convert grid coordinates to screen pixel coordinates"""
        return (grid_x * constants.CELL_SIZE, grid_y * constants.CELL_SIZE)
    
    def is_in_monitor(self, x, y):
        """Check if pixel coordinates are within any monitor bounds"""
        for monitor in self.monitors:
            mx, my = monitor['x'], monitor['y']
            mw, mh = monitor['width'], monitor['height']
            if mx <= x < mx + mw and my <= y < my + mh:
                return True
        return False
    
    def draw(self):
        """Draw everything"""
        if self.transparent_mode and self.desktop_background is not None:
            # Transparent mode: draw desktop background with accumulated trails
            self.screen.blit(self.desktop_background, (0, 0))
            
            # Draw the accumulated trail surface on top
            self.screen.blit(self.trail_surface, (0, 0))
            
            # Add trails only at the tail (last segment) of each snake
            # This way the trail appears behind the snake as it moves away
            # Only draw trails once the snake has finished growing to its initial length
            for snake in self.snakes:
                if snake.alive and len(snake.body) > 0 and snake.grow_pending == 0:
                    # Get the tail position (last segment)
                    tail_gx, tail_gy = snake.body[-1]
                    px, py = self.grid_to_screen(tail_gx, tail_gy)
                    px += constants.CELL_SIZE // 2
                    py += constants.CELL_SIZE // 2
                    self._draw_trail_at_position(px, py, constants.CELL_SIZE)
        else:
            # Normal mode: black background with starfield
            self.screen.fill(constants.BLACK)
            
            # Draw starfield
            self.starfield.draw(self.screen)
            
            # Draw grid lines (very subtle, barely visible)
            for x in range(0, self.virtual_width, constants.CELL_SIZE * 5):
                pygame.draw.line(self.screen, (8, 8, 12), (x, 0), (x, self.virtual_height))
            for y in range(0, self.virtual_height, constants.CELL_SIZE * 5):
                pygame.draw.line(self.screen, (8, 8, 12), (0, y), (self.virtual_width, y))
        
        # Draw food
        for food in self.food_items:
            food.draw(self.screen, self)
        
        # Draw all alive snakes
        for snake in self.snakes:
            if snake.alive:
                snake.draw(self.screen, self)
        
        # Draw all death animations
        for anim in self.death_animations:
            for particle in anim['segments']:
                if particle['alpha'] > 0:
                    px, py = int(particle['x']), int(particle['y'])
                    size = int(particle['size'])
                    surf = pygame.Surface((size, size), pygame.SRCALPHA)
                    alpha = int(particle['alpha'])
                    color_with_alpha = (*particle['color'], alpha)
                    surf.fill(color_with_alpha)
                    self.screen.blit(surf, (px, py))
        
        # Draw scores for each snake (in their color), sorted by length descending
        # Only draw if show_leaderboard is enabled
        if self.show_leaderboard:
            y_offset = 10
            # Sort snakes by length (descending) for leaderboard
            sorted_snakes = sorted(enumerate(self.snakes), key=lambda x: len(x[1].body), reverse=True)
            
            for rank, (i, snake) in enumerate(sorted_snakes):
                # Create darker version of snake color for shadow
                shadow_color = tuple(max(0, c // 2) for c in snake.color)
                
                # Show name and length
                name = snake.name if snake.name else f"Snake {i+1}"
                display_text = f"{name}: {len(snake.body)}"
                score_text = self.font.render(display_text, True, snake.color)
                shadow_text = self.font.render(display_text, True, shadow_color)
                self.screen.blit(shadow_text, (12, y_offset + 2))
                self.screen.blit(score_text, (10, y_offset))
                y_offset += 30
        
        pygame.display.flip()
    
    def run(self):
        """Main loop"""
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(self.fps)
        finally:
            # Restore Windows execution state to previous value
            if HAS_WIN32_POWER and self.previous_execution_state is not None:
                try:
                    kernel32.SetThreadExecutionState(self.previous_execution_state)
                except Exception:
                    pass
            
            # Properly clean up pygame to restore display state
            try:
                pygame.mouse.set_visible(True)
            except:
                pass
            
            if not self.windowed:
                try:
                    # Switch back to windowed mode before quitting to restore desktop properly
                    pygame.display.set_mode((640, 480))
                except:
                    pass
            
            try:
                pygame.display.quit()
            except:
                pass
            
            try:
                pygame.quit()
            except:
                pass

