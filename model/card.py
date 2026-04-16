import pygame
import os
from pathlib import Path

class Card:
    def __init__(self, color, value, image_filename):
        self.color = color
        self.value = value
        self.image_filename = image_filename
        self.image = None
        
        # Load image
        base_path = Path(__file__).parent.parent
        img_path = os.path.join(base_path, 'data', 'images', self.image_filename)
        if os.path.exists(img_path):
            try:
                # We retain original size but standard UNO cards roughly 1:1.5
                original_img = pygame.image.load(img_path).convert_alpha()
                # Scale typical card image, let's say 80x120
                self.image = pygame.transform.scale(original_img, (80, 120))
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
        else:
            print(f"Not found: {img_path}")

    def is_match(self, other_card, current_color):
        if self.color == "black":
            return True
        if self.color == current_color:
            return True
        if self.value == other_card.value:
            return True
        return False
    
    def __str__(self):
        return f"{self.color} {self.value}"
