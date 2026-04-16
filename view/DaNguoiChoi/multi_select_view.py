import os
import pygame
from pathlib import Path
from view.font_helper import draw_text_shadow, draw_button

_ORANGE = (239, 100,  72)
_HOVER  = (255, 130, 100)
_NAVY   = ( 22,  43,  68)
_GRAY   = (108, 117, 125)
_GRAY_H = ( 90,  98, 104)
_YELLOW = (255, 220,  30)


class MultiSelectView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width  = width
        self.height = height
        self._surf  = screen.surface

        base_path = Path(__file__).parent.parent.parent
        img_dir   = os.path.join(base_path, 'data', 'images')

        self.bg_image = None
        bg_path = os.path.join(img_dir, 'bgG.png')
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert_alpha()
                self.bg_image = pygame.transform.smoothscale(img, (width, height))
            except Exception as e:
                print(f"[MultiSelectView] bg load error: {e}")

    def draw(self, buttons, mouse_pos):
        if self.bg_image:
            self._surf.blit(self.bg_image, (0, 0))
        else:
            self._surf.fill((28, 90, 50))

        draw_text_shadow(
            self._surf, "Đa người chơi", 48, _YELLOW,
            shadow_color=(60, 30, 0), offset=(3, 3),
            center=(self.width / 2, 180), bold=True,
        )

        for btn in buttons:
            hovered = btn.rect.collidepoint(mouse_pos)
            bg = _HOVER if hovered else _ORANGE
            draw_button(
                self._surf,
                pygame.Rect(btn.rect.x, btn.rect.y, btn.rect.width, btn.rect.height),
                btn.text, 26, bg, _NAVY, (20, 20, 20), hover=hovered, radius=30,
            )
