"""
UI components for Retro Snake Screensaver configuration dialog
"""

import pygame
import ctypes
from retro_snake import constants
from retro_snake.config import load_config, save_config

# Try to get Windows API for parent window detection
try:
    user32 = ctypes.windll.user32
    
    def find_screensaver_settings_window():
        """Find the Windows screensaver settings dialog window"""
        # Look for the Screen Saver Settings dialog
        # Class name is typically #32770 (dialog) with specific title
        hwnd = user32.FindWindowW(None, "Screen Saver Settings")
        if not hwnd:
            # Try alternative names
            hwnd = user32.FindWindowW(None, "Bildschirmschonereinstellungen")  # German
        return hwnd
    
    def is_window_valid(hwnd):
        """Check if a window handle is still valid"""
        if not hwnd:
            return False
        return user32.IsWindow(hwnd)
    
    HAS_WIN32_UI = True
except (OSError, AttributeError):
    HAS_WIN32_UI = False
    
    def find_screensaver_settings_window():
        return None
    
    def is_window_valid(hwnd):
        return True


class RetroButton:
    """Retro Windows 95 style button"""
    def __init__(self, x, y, width, height, text, color=constants.GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hovered = False
        self.pressed = False
    
    def draw(self, surface, font):
        # Button face
        pygame.draw.rect(surface, self.color, self.rect)
        
        # 3D border effect (Windows 95 style)
        if self.pressed:
            # Pressed - inverted borders
            pygame.draw.line(surface, (64, 64, 64), self.rect.topleft, self.rect.topright, 2)
            pygame.draw.line(surface, (64, 64, 64), self.rect.topleft, self.rect.bottomleft, 2)
            pygame.draw.line(surface, constants.WHITE, self.rect.bottomleft, self.rect.bottomright, 2)
            pygame.draw.line(surface, constants.WHITE, self.rect.topright, self.rect.bottomright, 2)
        else:
            # Normal - raised borders
            pygame.draw.line(surface, constants.WHITE, self.rect.topleft, self.rect.topright, 2)
            pygame.draw.line(surface, constants.WHITE, self.rect.topleft, self.rect.bottomleft, 2)
            pygame.draw.line(surface, (64, 64, 64), self.rect.bottomleft, self.rect.bottomright, 2)
            pygame.draw.line(surface, (64, 64, 64), self.rect.topright, self.rect.bottomright, 2)
        
        # Text
        text_surf = font.render(self.text, True, constants.BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        if self.pressed:
            text_rect.x += 1
            text_rect.y += 1
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                return True  # Click!
        return False


class RetroCheckbox:
    """Retro Windows 95 style checkbox"""
    def __init__(self, x, y, text, checked=False):
        self.x = x
        self.y = y
        self.text = text
        self.checked = checked
        self.size = 16
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.hovered = False
    
    def draw(self, surface, font):
        # Checkbox box (sunken when unchecked, raised when checked)
        if self.checked:
            # Checked - raised
            pygame.draw.rect(surface, constants.GRAY, self.rect)
            pygame.draw.line(surface, constants.WHITE, self.rect.topleft, self.rect.topright, 2)
            pygame.draw.line(surface, constants.WHITE, self.rect.topleft, self.rect.bottomleft, 2)
            pygame.draw.line(surface, (64, 64, 64), self.rect.bottomleft, self.rect.bottomright, 2)
            pygame.draw.line(surface, (64, 64, 64), self.rect.topright, self.rect.bottomright, 2)
            # Draw checkmark
            pygame.draw.line(surface, constants.BLACK, 
                           (self.x + 3, self.y + 8), (self.x + 6, self.y + 11), 2)
            pygame.draw.line(surface, constants.BLACK, 
                           (self.x + 6, self.y + 11), (self.x + 12, self.y + 5), 2)
        else:
            # Unchecked - sunken
            pygame.draw.rect(surface, constants.GRAY, self.rect)
            pygame.draw.line(surface, (64, 64, 64), self.rect.topleft, self.rect.topright, 2)
            pygame.draw.line(surface, (64, 64, 64), self.rect.topleft, self.rect.bottomleft, 2)
            pygame.draw.line(surface, constants.WHITE, self.rect.bottomleft, self.rect.bottomright, 2)
            pygame.draw.line(surface, constants.WHITE, self.rect.topright, self.rect.bottomright, 2)
        
        # Label text
        label_surf = font.render(self.text, True, constants.BRIGHT_GREEN)
        surface.blit(label_surf, (self.x + self.size + 8, self.y))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True  # Toggled
        return False


class RetroSlider:
    """Retro Windows 95 style slider"""
    def __init__(self, x, y, width, min_val, max_val, value, label):
        self.x = x
        self.y = y
        self.width = width
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.label = label
        self.dragging = False
        self.track_rect = pygame.Rect(x, y + 20, width, 8)
        self.update_handle()
    
    def update_handle(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.x + int(ratio * (self.width - 16))
        self.handle_rect = pygame.Rect(handle_x, self.y + 14, 16, 20)
    
    def draw(self, surface, font):
        # Label - centered horizontally over the slider
        label_text = f"{self.label}: {self.value}"
        label_surf = font.render(label_text, True, constants.BRIGHT_GREEN)
        label_rect = label_surf.get_rect()
        label_x = self.x + (self.width - label_rect.width) // 2  # Center over slider
        surface.blit(label_surf, (label_x, self.y))
        
        # Track (sunken)
        pygame.draw.rect(surface, (64, 64, 64), self.track_rect)
        pygame.draw.line(surface, (32, 32, 32), self.track_rect.topleft, self.track_rect.topright, 1)
        pygame.draw.line(surface, (32, 32, 32), self.track_rect.topleft, self.track_rect.bottomleft, 1)
        
        # Handle (raised)
        pygame.draw.rect(surface, constants.GRAY, self.handle_rect)
        pygame.draw.line(surface, constants.WHITE, self.handle_rect.topleft, self.handle_rect.topright, 2)
        pygame.draw.line(surface, constants.WHITE, self.handle_rect.topleft, self.handle_rect.bottomleft, 2)
        pygame.draw.line(surface, (64, 64, 64), self.handle_rect.bottomleft, self.handle_rect.bottomright, 2)
        pygame.draw.line(surface, (64, 64, 64), self.handle_rect.topright, self.handle_rect.bottomright, 2)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.track_rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
    
    def _update_value(self, mouse_x):
        ratio = (mouse_x - self.x) / self.width
        ratio = max(0, min(1, ratio))
        self.value = int(self.min_val + ratio * (self.max_val - self.min_val))
        self.update_handle()


class ConfigDialog:
    """Retro Windows 95 style configuration dialog"""
    def __init__(self):
        pygame.init()
        
        self.width = 450
        self.height = 640
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Screensaver Settings")
        
        # Find and track the Windows screensaver settings dialog
        # so we can close when it closes
        self.parent_hwnd = find_screensaver_settings_window()
        
        # Load current config
        self.config = load_config()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Create UI elements
        # Calculate slider width and position to stretch across panel (with margins)
        panel_width = self.width - 20  # Panel is width - 20
        slider_width = panel_width - 50  # Leave 25px margin on each side
        slider_x = 25  # Centered with margins
        
        self.sliders = [
            RetroSlider(slider_x, 80, slider_width, 1, 150, self.config['num_snakes'], "Number of Snakes"),
            RetroSlider(slider_x, 140, slider_width, 5, 200, self.config['num_food'], "Food Items"),
            RetroSlider(slider_x, 200, slider_width, 5, 120, self.config['speed'], "Speed (FPS)"),
            RetroSlider(slider_x, 260, slider_width, 0, 100, self.config['dodge_chance'], "Dodge Chance %"),
            RetroSlider(slider_x, 320, slider_width, 1, 100, self.config.get('min_starting_length', 4), "Min Starting Length"),
            RetroSlider(slider_x, 380, slider_width, 1, 100, self.config.get('max_starting_length', 4), "Max Starting Length"),
        ]
        
        # Checkbox for showing/hiding leaderboard
        show_leaderboard = self.config.get('show_leaderboard', True)
        self.show_leaderboard_checkbox = RetroCheckbox(slider_x, 440, "Show Scores and Names", show_leaderboard)
        
        # Checkbox for transparent background mode
        transparent_mode = self.config.get('transparent_mode', False)
        self.transparent_mode_checkbox = RetroCheckbox(slider_x, 465, "Desktop Background (trails cover screen)", transparent_mode)
        
        # Slider for trail darkness (only relevant in transparent mode)
        trail_darkness = self.config.get('trail_darkness', self.config.get('trail_fade_rate', 5))
        self.trail_darkness_slider = RetroSlider(slider_x, 495, slider_width, 0, 20, trail_darkness, "Trail Darkness")
        
        # Checkbox for accumulative trails
        accumulative_trails = self.config.get('accumulative_trails', True)
        self.accumulative_trails_checkbox = RetroCheckbox(slider_x, 540, "Accumulative Trails (darker with each pass)", accumulative_trails)
        
        self.ok_button = RetroButton(120, 580, 80, 30, "OK")
        self.cancel_button = RetroButton(220, 580, 80, 30, "Cancel")
        self.preview_button = RetroButton(320, 580, 80, 30, "Preview")
        
        self.running = True
        self.result = None  # 'ok', 'cancel', or 'preview'
        
        self.clock = pygame.time.Clock()
    
    def draw(self):
        # Background - very dark (almost black)
        self.screen.fill((10, 10, 10))
        
        # Title bar
        title_rect = pygame.Rect(0, 0, self.width, 35)
        pygame.draw.rect(self.screen, (0, 0, 128), title_rect)
        title_text = self.title_font.render("🐍 Snake Screensaver Settings", True, constants.WHITE)
        self.screen.blit(title_text, (10, 5))
        
        # Main panel (raised) - dark grey instead of light grey
        panel = pygame.Rect(10, 45, self.width - 20, self.height - 55)
        pygame.draw.rect(self.screen, (20, 20, 20), panel)
        pygame.draw.line(self.screen, constants.WHITE, panel.topleft, panel.topright, 2)
        pygame.draw.line(self.screen, constants.WHITE, panel.topleft, panel.bottomleft, 2)
        pygame.draw.line(self.screen, (64, 64, 64), panel.bottomleft, panel.bottomright, 2)
        pygame.draw.line(self.screen, (64, 64, 64), panel.topright, panel.bottomright, 2)
        
        # Sliders
        for slider in self.sliders:
            slider.draw(self.screen, self.font)
        
        # Checkboxes
        self.show_leaderboard_checkbox.draw(self.screen, self.font)
        self.transparent_mode_checkbox.draw(self.screen, self.font)
        
        # Trail darkness slider
        self.trail_darkness_slider.draw(self.screen, self.font)
        
        # Accumulative trails checkbox
        self.accumulative_trails_checkbox.draw(self.screen, self.font)
        
        # Buttons
        self.ok_button.draw(self.screen, self.font)
        self.cancel_button.draw(self.screen, self.font)
        self.preview_button.draw(self.screen, self.font)
        
        # Version info
        version_text = self.small_font.render("Hack's Retro Snake Screensaver v1.0", True, (64, 64, 64))
        self.screen.blit(version_text, (140, 620))
        
        pygame.display.flip()
    
    def run(self):
        frame_count = 0
        while self.running:
            frame_count += 1
            
            # Check if parent Windows screensaver settings dialog is still open
            # Only check every 30 frames (~1 second) to reduce overhead
            if frame_count % 30 == 0 and self.parent_hwnd:
                if not is_window_valid(self.parent_hwnd):
                    # Parent closed, save and exit
                    self.save_settings()
                    self.result = 'ok'
                    self.running = False
                    break
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result = 'cancel'
                
                # Handle sliders
                for slider in self.sliders:
                    slider.handle_event(event)
                
                # Handle checkboxes
                self.show_leaderboard_checkbox.handle_event(event)
                self.transparent_mode_checkbox.handle_event(event)
                self.accumulative_trails_checkbox.handle_event(event)
                
                # Handle trail darkness slider
                self.trail_darkness_slider.handle_event(event)
                
                # Handle buttons
                if self.ok_button.handle_event(event):
                    self.save_settings()
                    self.result = 'ok'
                    self.running = False
                
                if self.cancel_button.handle_event(event):
                    self.result = 'cancel'
                    self.running = False
                
                if self.preview_button.handle_event(event):
                    self.save_settings()
                    self.result = 'preview'
                    self.running = False
            
            self.draw()
            self.clock.tick(30)
        
        try:
            pygame.display.quit()
        except:
            pass
        
        try:
            pygame.quit()
        except:
            pass
        
        return self.result
    
    def save_settings(self):
        """Save current slider values to config"""
        self.config['num_snakes'] = self.sliders[0].value
        self.config['num_food'] = self.sliders[1].value
        self.config['speed'] = self.sliders[2].value
        self.config['dodge_chance'] = self.sliders[3].value
        self.config['min_starting_length'] = self.sliders[4].value
        self.config['max_starting_length'] = self.sliders[5].value
        self.config['show_leaderboard'] = self.show_leaderboard_checkbox.checked
        self.config['transparent_mode'] = self.transparent_mode_checkbox.checked
        self.config['trail_darkness'] = self.trail_darkness_slider.value
        self.config['accumulative_trails'] = self.accumulative_trails_checkbox.checked
        save_config(self.config)

