"""
Snake class with AI logic for Retro Snake Screensaver
"""

import pygame
import random
from collections import deque
from retro_snake import constants
from retro_snake.config import DODGE_CHANCE


class Snake:
    def __init__(self, start_x, start_y, color, name=None):
        self.body = deque([(start_x, start_y)])
        self.direction = random.choice(list(constants.Direction))
        self.color = color
        self.name = name  # Name for this snake
        self.grow_pending = 0
        self.turn_timer = 0
        self.turn_interval = random.randint(15, 40)  # Frames between possible turns
        self.min_turn_interval = 15
        self.max_turn_interval = 50
        self.score = 0  # Individual score for this snake
        self.alive = True  # Whether snake is active (not in death animation)
        
    def get_head(self):
        return self.body[0]
    
    def get_body_set(self):
        return set(self.body)
    
    def can_turn(self):
        """Check if enough time has passed for a turn"""
        return self.turn_timer >= self.turn_interval
    
    def reset_turn_timer(self):
        self.turn_timer = 0
        self.turn_interval = random.randint(self.min_turn_interval, self.max_turn_interval)
    
    def get_possible_directions(self):
        """Get directions that won't cause immediate reversal"""
        opposite = {
            constants.Direction.UP: constants.Direction.DOWN,
            constants.Direction.DOWN: constants.Direction.UP,
            constants.Direction.LEFT: constants.Direction.RIGHT,
            constants.Direction.RIGHT: constants.Direction.LEFT
        }
        return [d for d in constants.Direction if d != opposite[self.direction]]
    
    def get_safe_directions(self, obstacles):
        """Get directions that won't cause collision in next move"""
        head_x, head_y = self.get_head()
        safe = []
        
        for direction in self.get_possible_directions():
            dx, dy = direction.value
            new_x = (head_x + dx) % constants.GRID_WIDTH
            new_y = (head_y + dy) % constants.GRID_HEIGHT
            
            # Check if this position is safe (not in obstacles)
            if (new_x, new_y) not in obstacles:
                safe.append(direction)
        
        return safe
    
    def look_ahead(self, direction, obstacles, depth=5):
        """Look ahead to see how many safe moves in a direction"""
        head_x, head_y = self.get_head()
        dx, dy = direction.value
        safe_count = 0
        
        # Create a copy of body positions for simulation
        simulated_body = set(self.body)
        
        for i in range(depth):
            head_x = (head_x + dx) % constants.GRID_WIDTH
            head_y = (head_y + dy) % constants.GRID_HEIGHT
            
            if (head_x, head_y) in obstacles or (head_x, head_y) in simulated_body:
                break
            safe_count += 1
        
        return safe_count
    
    def check_approaching_snakes(self, other_snakes_info, proximity_threshold=3):
        """Check if any other snake's head is nearby and moving toward this snake
        other_snakes_info: list of dicts with 'head', 'direction', 'body_set' keys
        Returns True if an approaching snake is detected
        """
        my_head = self.get_head()
        my_x, my_y = my_head
        
        for other_info in other_snakes_info:
            other_head = other_info['head']
            other_dir = other_info['direction']
            other_x, other_y = other_head
            
            # Calculate distance (accounting for toroidal wrapping)
            dx = min(abs(other_x - my_x), constants.GRID_WIDTH - abs(other_x - my_x))
            dy = min(abs(other_y - my_y), constants.GRID_HEIGHT - abs(other_y - my_y))
            distance = max(dx, dy)  # Chebyshev distance (max of x and y)
            
            if distance <= proximity_threshold:
                # Check if other snake is moving toward this snake
                other_dx, other_dy = other_dir.value
                other_next_x = (other_x + other_dx) % constants.GRID_WIDTH
                other_next_y = (other_y + other_dy) % constants.GRID_HEIGHT
                
                # Calculate distance after other snake moves
                next_dx = min(abs(other_next_x - my_x), constants.GRID_WIDTH - abs(other_next_x - my_x))
                next_dy = min(abs(other_next_y - my_y), constants.GRID_HEIGHT - abs(other_next_y - my_y))
                next_distance = max(next_dx, next_dy)
                
                # If distance is decreasing, snake is approaching
                if next_distance < distance:
                    return True
        
        return False
    
    def choose_direction(self, obstacles, other_snakes_info=None):
        """AI decision making for direction
        other_snakes_info: optional list of dicts with 'head', 'direction', 'body_set' keys for proximity checking
        """
        self.turn_timer += 1
        
        # Get currently safe directions
        safe_directions = self.get_safe_directions(obstacles)
        
        if not safe_directions:
            # No safe direction - try any non-reversing direction
            safe_directions = self.get_possible_directions()
        
        # Check for approaching snakes (proximity check)
        approaching_danger = False
        if other_snakes_info:
            approaching_danger = self.check_approaching_snakes(other_snakes_info, proximity_threshold=3)
        
        # Check if look-ahead detects collision in current direction
        look_ahead_danger = False
        if self.direction in safe_directions:
            look_ahead_score = self.look_ahead(self.direction, obstacles, depth=5)
            # If look-ahead finds very few safe moves, there's danger ahead
            if look_ahead_score < 3:
                look_ahead_danger = True
        
        # Current direction is still valid?
        if self.direction in safe_directions:
            # Check if we should dodge due to approaching snake or look-ahead danger
            should_dodge = approaching_danger or look_ahead_danger
            
            if should_dodge and self.can_turn():
                # Force a dodge - evaluate all safe directions
                best_directions = []
                best_score = -1
                
                for d in safe_directions:
                    score = self.look_ahead(d, obstacles, depth=8)
                    if score > best_score:
                        best_score = score
                        best_directions = [d]
                    elif score == best_score:
                        best_directions.append(d)
                
                if best_directions:
                    new_direction = random.choice(best_directions)
                    if new_direction != self.direction:
                        self.reset_turn_timer()
                    self.direction = new_direction
            # Only consider turning if timer allows (normal behavior)
            elif self.can_turn():
                # Sometimes turn randomly, sometimes continue
                if random.random() < 0.3:  # 30% chance to turn when timer allows
                    # Evaluate all safe directions
                    best_directions = []
                    best_score = -1
                    
                    for d in safe_directions:
                        score = self.look_ahead(d, obstacles, depth=8)
                        if score > best_score:
                            best_score = score
                            best_directions = [d]
                        elif score == best_score:
                            best_directions.append(d)
                    
                    if best_directions:
                        new_direction = random.choice(best_directions)
                        if new_direction != self.direction:
                            self.reset_turn_timer()
                        self.direction = new_direction
            # Else keep going straight
        else:
            # Must turn - choose best safe direction
            if safe_directions:
                best_directions = []
                best_score = -1
                
                for d in safe_directions:
                    score = self.look_ahead(d, obstacles, depth=8)
                    if score > best_score:
                        best_score = score
                        best_directions = [d]
                    elif score == best_score:
                        best_directions.append(d)
                
                # 50% chance to actually dodge, 50% chance to crash anyway
                if random.random() < DODGE_CHANCE:
                    self.direction = random.choice(best_directions) if best_directions else random.choice(safe_directions)
                    self.reset_turn_timer()
                # else: keep going straight into danger!
    
    def move(self):
        """Move the snake in current direction"""
        head_x, head_y = self.get_head()
        dx, dy = self.direction.value
        
        # Wrap around screen (toroidal)
        new_head = ((head_x + dx) % constants.GRID_WIDTH, (head_y + dy) % constants.GRID_HEIGHT)
        
        self.body.appendleft(new_head)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
    
    def grow(self, amount=3):
        """Schedule growth"""
        self.grow_pending += amount
    
    def check_self_collision(self):
        """Check if head collides with body"""
        head = self.get_head()
        body_without_head = list(self.body)[1:]
        return head in body_without_head
    
    def draw(self, surface, screen_saver=None):
        """Draw the snake with retro style"""
        for i, (x, y) in enumerate(self.body):
            px, py = x * constants.CELL_SIZE, y * constants.CELL_SIZE
            rect = pygame.Rect(px, py, constants.CELL_SIZE - 1, constants.CELL_SIZE - 1)
            
            if i == 0:
                # Head - brighter
                pygame.draw.rect(surface, self.color, rect)
                # Eyes
                eye_color = constants.BLACK
                eye_size = 3
                dx, dy = self.direction.value
                
                if self.direction == constants.Direction.RIGHT:
                    pygame.draw.rect(surface, eye_color, (x * constants.CELL_SIZE + 12, y * constants.CELL_SIZE + 4, eye_size, eye_size))
                    pygame.draw.rect(surface, eye_color, (x * constants.CELL_SIZE + 12, y * constants.CELL_SIZE + 12, eye_size, eye_size))
                elif self.direction == constants.Direction.LEFT:
                    pygame.draw.rect(surface, eye_color, (x * constants.CELL_SIZE + 4, y * constants.CELL_SIZE + 4, eye_size, eye_size))
                    pygame.draw.rect(surface, eye_color, (x * constants.CELL_SIZE + 4, y * constants.CELL_SIZE + 12, eye_size, eye_size))
                elif self.direction == constants.Direction.UP:
                    pygame.draw.rect(surface, eye_color, (x * constants.CELL_SIZE + 4, y * constants.CELL_SIZE + 4, eye_size, eye_size))
                    pygame.draw.rect(surface, eye_color, (x * constants.CELL_SIZE + 12, y * constants.CELL_SIZE + 4, eye_size, eye_size))
                else:  # DOWN
                    pygame.draw.rect(surface, eye_color, (x * constants.CELL_SIZE + 4, y * constants.CELL_SIZE + 12, eye_size, eye_size))
                    pygame.draw.rect(surface, eye_color, (x * constants.CELL_SIZE + 12, y * constants.CELL_SIZE + 12, eye_size, eye_size))
            else:
                # Body segments - slightly darker for depth effect
                segment_color = tuple(max(0, c - 40) for c in self.color)
                pygame.draw.rect(surface, segment_color, rect)
                # Inner highlight for retro 3D effect
                inner_rect = pygame.Rect(x * constants.CELL_SIZE + 2, y * constants.CELL_SIZE + 2, constants.CELL_SIZE - 5, constants.CELL_SIZE - 5)
                pygame.draw.rect(surface, self.color, inner_rect)
    
    def draw_on_monitor(self, surface, monitor):
        """Draw the snake segments that are visible on a specific monitor"""
        mon_x = monitor['x']
        mon_y = monitor['y']
        mon_w = monitor['width']
        mon_h = monitor['height']
        
        for i, (x, y) in enumerate(self.body):
            px, py = x * constants.CELL_SIZE, y * constants.CELL_SIZE
            # Check if this segment is visible on this monitor
            if not (mon_x <= px < mon_x + mon_w and mon_y <= py < mon_y + mon_h):
                continue
            
            # Convert to monitor-local coordinates
            local_x = px - mon_x
            local_y = py - mon_y
            rect = pygame.Rect(local_x, local_y, constants.CELL_SIZE - 1, constants.CELL_SIZE - 1)
            
            if i == 0:
                # Head - brighter
                pygame.draw.rect(surface, self.color, rect)
                # Eyes
                eye_color = constants.BLACK
                eye_size = 3
                dx, dy = self.direction.value
                
                if self.direction == constants.Direction.RIGHT:
                    pygame.draw.rect(surface, eye_color, (local_x + 12, local_y + 4, eye_size, eye_size))
                    pygame.draw.rect(surface, eye_color, (local_x + 12, local_y + 12, eye_size, eye_size))
                elif self.direction == constants.Direction.LEFT:
                    pygame.draw.rect(surface, eye_color, (local_x + 4, local_y + 4, eye_size, eye_size))
                    pygame.draw.rect(surface, eye_color, (local_x + 4, local_y + 12, eye_size, eye_size))
                elif self.direction == constants.Direction.UP:
                    pygame.draw.rect(surface, eye_color, (local_x + 4, local_y + 4, eye_size, eye_size))
                    pygame.draw.rect(surface, eye_color, (local_x + 12, local_y + 4, eye_size, eye_size))
                else:  # DOWN
                    pygame.draw.rect(surface, eye_color, (local_x + 4, local_y + 12, eye_size, eye_size))
                    pygame.draw.rect(surface, eye_color, (local_x + 12, local_y + 12, eye_size, eye_size))
            else:
                # Body segments - slightly darker for depth effect
                segment_color = tuple(max(0, c - 40) for c in self.color)
                pygame.draw.rect(surface, segment_color, rect)
                # Inner highlight for retro 3D effect
                inner_rect = pygame.Rect(local_x + 2, local_y + 2, constants.CELL_SIZE - 5, constants.CELL_SIZE - 5)
                pygame.draw.rect(surface, self.color, inner_rect)

