"""
Preview window for Windows screensaver settings dialog
"""

import pygame
import random
import math
import os
from retro_snake import constants
from retro_snake.utils import cleanup_pygame

# Windows API using ctypes (no external dependencies)
import ctypes
from ctypes import wintypes

# Try to load Windows DLLs
try:
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    HAS_WIN32 = True
except (OSError, AttributeError):
    HAS_WIN32 = False

# Windows constants
ERROR_ALREADY_EXISTS = 183
GWL_STYLE = -16
WS_CHILD = 0x40000000
WS_VISIBLE = 0x10000000
HWND_TOP = 0
SWP_SHOWWINDOW = 0x0040

# Windows structures
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

# Define Windows API functions
if HAS_WIN32:
    # Mutex functions
    CreateMutex = kernel32.CreateMutexW
    CreateMutex.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    CreateMutex.restype = wintypes.HANDLE
    
    GetLastError = kernel32.GetLastError
    GetLastError.argtypes = []
    GetLastError.restype = wintypes.DWORD
    
    CloseHandle = kernel32.CloseHandle
    CloseHandle.argtypes = [wintypes.HANDLE]
    CloseHandle.restype = wintypes.BOOL
    
    # Window functions
    GetClientRect = user32.GetClientRect
    GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
    GetClientRect.restype = wintypes.BOOL
    
    SetParent = user32.SetParent
    SetParent.argtypes = [wintypes.HWND, wintypes.HWND]
    SetParent.restype = wintypes.HWND
    
    GetWindowLong = user32.GetWindowLongW
    GetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int]
    GetWindowLong.restype = ctypes.c_long
    
    SetWindowLong = user32.SetWindowLongW
    SetWindowLong.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
    SetWindowLong.restype = ctypes.c_long
    
    SetWindowPos = user32.SetWindowPos
    SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, 
                             ctypes.c_int, ctypes.c_int, wintypes.UINT]
    SetWindowPos.restype = wintypes.BOOL
    
    IsWindow = user32.IsWindow
    IsWindow.argtypes = [wintypes.HWND]
    IsWindow.restype = wintypes.BOOL
    
    DestroyWindow = user32.DestroyWindow
    DestroyWindow.argtypes = [wintypes.HWND]
    DestroyWindow.restype = wintypes.BOOL
    
    IsWindowVisible = user32.IsWindowVisible
    IsWindowVisible.argtypes = [wintypes.HWND]
    IsWindowVisible.restype = wintypes.BOOL
    
    GetParent = user32.GetParent
    GetParent.argtypes = [wintypes.HWND]
    GetParent.restype = wintypes.HWND
else:
    # Stub functions for non-Windows or when DLLs unavailable
    def CreateMutex(*args):
        return None
    def GetLastError():
        return 0
    def CloseHandle(*args):
        return False
    def GetClientRect(*args):
        return False
    def SetParent(*args):
        return None
    def GetWindowLong(*args):
        return 0
    def SetWindowLong(*args):
        return 0
    def SetWindowPos(*args):
        return False
    def IsWindow(*args):
        return False
    def DestroyWindow(*args):
        return False
    def IsWindowVisible(*args):
        return False
    def GetParent(*args):
        return None


# Mutex name for preventing multiple preview instances
PREVIEW_MUTEX_NAME = "RetroSnakeScreensaverPreviewMutex"


def acquire_preview_mutex():
    """
    Try to acquire a named mutex to prevent multiple preview instances.
    Returns (mutex_handle, acquired) where acquired is True if we got the mutex,
    False if another instance already has it.
    """
    if not HAS_WIN32:
        return None, True  # No mutex available, allow to proceed
    
    try:
        # Try to create/open the mutex
        mutex_name = ctypes.c_wchar_p(PREVIEW_MUTEX_NAME)
        mutex = CreateMutex(None, False, mutex_name)
        if not mutex:
            return None, True  # Failed to create, allow to proceed
        
        # Check if we got the mutex or if it already existed
        last_error = GetLastError()
        if last_error == ERROR_ALREADY_EXISTS:
            # Another instance is running, close our handle and exit
            try:
                CloseHandle(mutex)
            except:
                pass
            return None, False
        return mutex, True
    except Exception:
        # If mutex creation fails for any reason, allow to proceed
        return None, True


def release_preview_mutex(mutex_handle):
    """Release the preview mutex handle"""
    if mutex_handle and HAS_WIN32:
        try:
            CloseHandle(mutex_handle)
        except:
            pass


class PreviewWindow:
    """Embedded preview window for Windows screensaver settings dialog"""
    def __init__(self, parent_hwnd, mutex_handle=None):
        """
        Initialize preview window embedded in Windows screensaver preview pane
        
        Args:
            parent_hwnd: Windows handle to the preview control in the settings dialog
            mutex_handle: Mutex handle from main.py (for cleanup)
        """
        if not HAS_WIN32:
            raise ImportError("Windows API not available for preview mode")
        
        # Store mutex handle for cleanup (acquired in main.py)
        self.mutex_handle = mutex_handle
        
        self.parent_hwnd = parent_hwnd
        
        # Get the client area size of the preview window
        rect = RECT()
        result = GetClientRect(parent_hwnd, ctypes.byref(rect))
        if not result:
            error_code = GetLastError()
            raise RuntimeError(f"Failed to get client rect, error={error_code}")
        self.width = rect.right - rect.left
        self.height = rect.bottom - rect.top
        
        # Clean up any existing pygame instance first
        try:
            pygame.quit()
        except:
            pass
        
        # Set SDL_WINDOWID BEFORE pygame.init() to embed in parent window
        os.environ['SDL_WINDOWID'] = str(parent_hwnd)
        
        # Initialize pygame fresh
        pygame.init()
        
        # Create pygame display - it will be embedded in parent_hwnd due to SDL_WINDOWID
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Get the pygame window handle
        pygame_hwnd = pygame.display.get_wm_info()['window']
        
        # Store pygame hwnd for later use
        self.pygame_hwnd = pygame_hwnd
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create a mini snake for preview animation
        self.snake_segments = 6
        self.snake_size = 6
        self.snake_spacing = 8
        self.snake_pos = [(self.width // 2, self.height // 2)]
        self.snake_direction = (1, 0)  # Moving right initially (tuple not list)
        self.move_timer = 0
        self.move_delay = 3  # Frames between moves (faster like settings demo)
        
        # Initialize snake body
        for i in range(1, self.snake_segments):
            last = self.snake_pos[-1]
            self.snake_pos.append((
                last[0] - self.snake_spacing,
                last[1]
            ))
        
        # Food position
        self.food_pos = self.generate_food()
        
        # Animation state
        self.frame = 0
    
    def generate_food(self):
        """Generate food position away from snake"""
        margin = 20
        max_attempts = 10
        for _ in range(max_attempts):
            x = random.randint(margin, self.width - margin)
            y = random.randint(margin, self.height - margin)
            # Check if far enough from snake head
            head = self.snake_pos[0]
            if math.sqrt((x - head[0])**2 + (y - head[1])**2) > 30:
                return (x, y)
        return (self.width // 2 + 40, self.height // 2 + 40)
    
    def update(self):
        """Update snake animation"""
        self.frame += 1
        self.move_timer += 1
        
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            
            # Move snake
            head = self.snake_pos[0]
            new_head = (
                head[0] + self.snake_direction[0] * self.snake_spacing,
                head[1] + self.snake_direction[1] * self.snake_spacing
            )
            
            # Random turns for more interesting movement (like settings demo)
            if random.random() < 0.15:
                if self.snake_direction[0] != 0:
                    self.snake_direction = (0, random.choice([-1, 1]))
                else:
                    self.snake_direction = (random.choice([-1, 1]), 0)
            
            # Check if heading towards food
            head_to_food_x = self.food_pos[0] - new_head[0]
            head_to_food_y = self.food_pos[1] - new_head[1]
            
            # Simple AI - turn towards food sometimes
            if random.random() < 0.3:
                if abs(head_to_food_x) > abs(head_to_food_y):
                    if head_to_food_x > 0 and self.snake_direction[0] != -1:
                        self.snake_direction = (1, 0)
                    elif head_to_food_x < 0 and self.snake_direction[0] != 1:
                        self.snake_direction = (-1, 0)
                else:
                    if head_to_food_y > 0 and self.snake_direction[1] != -1:
                        self.snake_direction = (0, 1)
                    elif head_to_food_y < 0 and self.snake_direction[1] != 1:
                        self.snake_direction = (0, -1)
            
            # Recalculate new head with potentially updated direction
            new_head = (
                head[0] + self.snake_direction[0] * self.snake_spacing,
                head[1] + self.snake_direction[1] * self.snake_spacing
            )
            
            # Bounce off edges instead of wrapping for more visible movement
            if new_head[0] < 10 or new_head[0] > self.width - 10:
                self.snake_direction = (-self.snake_direction[0], self.snake_direction[1])
                new_head = (
                    head[0] + self.snake_direction[0] * self.snake_spacing,
                    head[1]
                )
            if new_head[1] < 10 or new_head[1] > self.height - 10:
                self.snake_direction = (self.snake_direction[0], -self.snake_direction[1])
                new_head = (
                    new_head[0],
                    head[1] + self.snake_direction[1] * self.snake_spacing
                )
            
            # Check if food eaten
            if math.sqrt((new_head[0] - self.food_pos[0])**2 + 
                        (new_head[1] - self.food_pos[1])**2) < self.snake_spacing:
                self.food_pos = self.generate_food()
                # Don't remove tail (grow)
                self.snake_pos.insert(0, new_head)
                if len(self.snake_pos) > 15:  # Max length in preview
                    self.snake_pos.pop()
            else:
                # Normal move
                self.snake_pos.insert(0, new_head)
                self.snake_pos.pop()
    
    def draw(self):
        """Draw preview animation"""
        # Background
        self.screen.fill(constants.BLACK)
        
        # Draw grid (subtle)
        grid_size = 20
        for x in range(0, self.width, grid_size):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, self.height))
        for y in range(0, self.height, grid_size):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (self.width, y))
        
        # Draw food
        food_pulse = int(128 + 127 * math.sin(self.frame * 0.1))
        food_color = (255, food_pulse, 0)
        pygame.draw.circle(self.screen, food_color, self.food_pos, self.snake_size - 1)
        
        # Draw snake
        for i, pos in enumerate(self.snake_pos):
            if i == 0:
                # Head - brighter
                color = constants.BRIGHT_GREEN
                size = self.snake_size
            else:
                # Body - darker
                fade = 1 - (i / len(self.snake_pos)) * 0.5
                color = (0, int(200 * fade), 0)
                size = self.snake_size - 1
            
            pygame.draw.rect(self.screen, color, 
                           (pos[0] - size//2, pos[1] - size//2, size, size))
        
        # Draw title text
        try:
            font = pygame.font.Font(None, 16)
            text = font.render("Hack's Retro Snakes", True, constants.CYAN)
            text_rect = text.get_rect(center=(self.width // 2, self.height - 15))
            # Draw shadow
            shadow = font.render("Hack's Retro Snakes", True, constants.BLACK)
            self.screen.blit(shadow, (text_rect.x + 1, text_rect.y + 1))
            self.screen.blit(text, text_rect)
        except:
            pass
        
        pygame.display.flip()
    
    def run(self):
        """Run the preview loop"""
        pygame_hwnd = getattr(self, 'pygame_hwnd', None)
        try:
            # Store pygame window handle for cleanup
            if not pygame_hwnd:
                try:
                    pygame_hwnd = pygame.display.get_wm_info()['window']
                except:
                    pass
            
            frame_count = 0
            
            while self.running:
                frame_count += 1
                
                # Check if parent window still exists
                try:
                    if not IsWindow(self.parent_hwnd):
                        self.running = False
                        break
                except:
                    self.running = False
                    break
                
                # Only check visibility after window has had time to initialize (after frame 30)
                # This prevents false positives during startup
                if frame_count > 30 and pygame_hwnd:
                    try:
                        if not IsWindow(pygame_hwnd):
                            self.running = False
                            break
                        # Check if window is still visible (indicates another screensaver selected)
                        if not IsWindowVisible(pygame_hwnd):
                            self.running = False
                            break
                    except:
                        pass
                
                # Process events - check for quit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                
                if not self.running:
                    break
                
                self.update()
                self.draw()
                self.clock.tick(30)
        except Exception as e:
            pass  # Silently handle errors in preview
        finally:
            # Clean up properly to prevent stacking instances
            self.running = False
            
            # Release the mutex
            release_preview_mutex(getattr(self, 'mutex_handle', None))
            
            try:
                if pygame_hwnd and IsWindow(pygame_hwnd):
                    DestroyWindow(pygame_hwnd)
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
            
            # Force immediate process termination for preview mode
            os._exit(0)


def run_fallback_preview():
    """Run a simple fallback preview window"""
    # Check for existing preview instance
    mutex_handle, acquired = acquire_preview_mutex()
    if not acquired:
        # Another instance is already running, exit immediately
        os._exit(0)
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((200, 150))
        pygame.display.set_caption("Hack's Retro Snakes preview")
        
        font = pygame.font.Font(None, 20)
        clock = pygame.time.Clock()
        
        running = True
        snake_pos = [(100, 75), (110, 75), (120, 75)]
        direction = (-1, 0)
        timer = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            screen.fill(constants.BLACK)
            
            # Animate mini snake
            timer += 1
            if timer % 10 == 0:
                head = snake_pos[0]
                new_head = (head[0] + direction[0] * 10, head[1] + direction[1] * 10)
                if new_head[0] < 10 or new_head[0] > 180:
                    direction = (-direction[0], direction[1])
                    new_head = (head[0] + direction[0] * 10, head[1] + direction[1] * 10)
                snake_pos.insert(0, new_head)
                snake_pos.pop()
            
            for i, pos in enumerate(snake_pos):
                color = constants.BRIGHT_GREEN if i == 0 else (0, 180, 0)
                pygame.draw.rect(screen, color, (pos[0], pos[1], 8, 8))
            
            text = font.render("Snake Screensaver", True, constants.CYAN)
            screen.blit(text, (35, 130))
            
            pygame.display.flip()
            clock.tick(30)
    finally:
        # Release the mutex
        release_preview_mutex(mutex_handle)
        cleanup_pygame()
        # Force immediate process termination for preview mode
        os._exit(0)

