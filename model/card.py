import pygame
import os
from pathlib import Path

# Thư mục chứa hình ảnh
BASE_PATH = Path(__file__).parent.parent
IMG_DIR = os.path.join(BASE_PATH, 'data', 'images')

class Card:
    def __init__(self, color, value, filename):
        self.color = color
        self.value = value
        self.filename = filename
        self.rect = pygame.Rect(0, 0, 80, 120)  # Kích thước mặc định của thẻ bài
        self.image = None
        self.is_hovered = False
        
        # Phục vụ Animation di chuyển
        self.curr_x = None
        self.curr_y = None

    def load_image(self):
        if not self.image:
            path = os.path.join(IMG_DIR, self.filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Resize để vừa vặn
                    self.image = pygame.transform.scale(img, (80, 120))
                except Exception as e:
                    print(f"Error loading {path}: {e}")
            else:
                print(f"Warning: Missing image file for {self.filename}")

    def draw(self, screen, target_x, target_y):
        if not self.image:
            self.load_image()
            
        # Áp dụng Hover nâng bài lên
        if self.is_hovered:
            target_y -= 15
            
        # Nội suy toạ độ (Lerp) để tạo chuyển động mượt
        if self.curr_x is None or self.curr_y is None:
            self.curr_x = target_x
            self.curr_y = target_y
        else:
            self.curr_x += (target_x - self.curr_x) * 0.2
            self.curr_y += (target_y - self.curr_y) * 0.2
            
        # Cập nhật rect thực tế phục vụ click
        self.rect.topleft = (self.curr_x, self.curr_y)
        
        if self.image:
            screen.blit(self.image, (self.curr_x, self.curr_y))
        else:
            surface = screen.surface if hasattr(screen, 'surface') else screen
            pygame.draw.rect(surface, (200, 200, 200), self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
            
    def update_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_match(self, other_card, current_color):
        if self.color == "black":
            return True
        if self.color == current_color:
            return True
        if hasattr(other_card, "value") and self.value == other_card.value:
            return True
        return False

    def __repr__(self):
        return f"{self.color} {self.value}"
