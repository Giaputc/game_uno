from pgzero.rect import Rect

class MenuButton:  # Kiểm tra kỹ tên này
    def __init__(self, text, x, y, width, height, color, hover_color):
        self.text = text
        self.rect = Rect((x, y), (width, height))
        self.color = color
        self.hover_color = hover_color

    def get_color(self, mouse_pos):
        return self.hover_color if self.rect.collidepoint(mouse_pos) else self.color