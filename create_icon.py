#!/usr/bin/env python3
"""
Create a snake-themed icon for the screensaver
"""
from PIL import Image, ImageDraw
import math

def create_snake_icon():
    # Create a 64x64 image with transparent background
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Snake colors - retro green theme
    snake_color = (0, 255, 0, 255)  # Bright green
    snake_outline = (0, 128, 0, 255)  # Darker green
    eye_color = (255, 255, 0, 255)  # Yellow
    background = (0, 0, 0, 255)  # Black background
    
    # Draw black background circle
    margin = 2
    draw.ellipse([margin, margin, size-margin-1, size-margin-1], 
                 fill=background, outline=snake_outline, width=2)
    
    # Draw snake body as a spiral
    center_x, center_y = size // 2, size // 2
    radius_start = 8
    radius_end = 24
    
    # Create snake body segments
    segments = []
    for i in range(60):
        angle = i * 0.3  # Spiral angle
        radius = radius_start + (radius_end - radius_start) * (i / 59)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        segments.append((x, y))
    
    # Draw snake body
    segment_size = 3
    for i, (x, y) in enumerate(segments):
        if i < len(segments) - 1:
            # Draw line segment
            next_x, next_y = segments[i + 1]
            draw.line([x, y, next_x, next_y], fill=snake_color, width=segment_size)
    
    # Draw snake head (larger circle at the end)
    if segments:
        head_x, head_y = segments[-1]
        head_size = 6
        draw.ellipse([head_x - head_size//2, head_y - head_size//2, 
                     head_x + head_size//2, head_y + head_size//2], 
                     fill=snake_color, outline=snake_outline, width=1)
        
        # Draw eyes
        eye_size = 2
        eye_offset = 2
        # Calculate head direction for eye placement
        if len(segments) > 1:
            prev_x, prev_y = segments[-2]
            dx = head_x - prev_x
            dy = head_y - prev_y
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                # Normalize and perpendicular for eye placement
                dx /= length
                dy /= length
                eye1_x = head_x + dy * eye_offset
                eye1_y = head_y - dx * eye_offset
                eye2_x = head_x - dy * eye_offset
                eye2_y = head_y + dx * eye_offset
                
                draw.ellipse([eye1_x - eye_size//2, eye1_y - eye_size//2,
                             eye1_x + eye_size//2, eye1_y + eye_size//2],
                             fill=eye_color)
                draw.ellipse([eye2_x - eye_size//2, eye2_y - eye_size//2,
                             eye2_x + eye_size//2, eye2_y + eye_size//2],
                             fill=eye_color)
    
    return img

def main():
    try:
        # Create the icon
        icon = create_snake_icon()
        
        # Save as ICO file (Windows icon format)
        icon.save('snake_icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
        print("Snake icon created successfully: snake_icon.ico")
        
        # Also save as PNG for preview
        icon.save('snake_icon.png', format='PNG')
        print("Preview saved as: snake_icon.png")
        
    except ImportError:
        print("Error: Pillow (PIL) is required to create the icon.")
        print("Please install it with: pip install Pillow")
        return False
    except Exception as e:
        print(f"Error creating icon: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()