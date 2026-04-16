"""
font_helper.py — Render Vietnamese text via pygame.font (Arial.ttf).
pgzero's screen.draw.text() does NOT reliably support Unicode/Vietnamese, so
all text rendering in this project goes through these helpers instead.
"""
import os
import pygame
from pathlib import Path

_font_cache: dict = {}

def _get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        font_path = os.path.join(Path(__file__).parent.parent, 'fonts', 'Arial.ttf')
        if os.path.exists(font_path):
            font = pygame.font.Font(font_path, size)
            font.bold = bold
        else:
            font = pygame.font.SysFont('arial', size, bold=bold)
        _font_cache[key] = font
    return _font_cache[key]


def draw_text(
    surface,
    text: str,
    size: int,
    color,
    center=None,
    topleft=None,
    midleft=None,
    midright=None,
    bold: bool = False,
    alpha: int = 255,
):
    """Render `text` onto `surface` at a given anchor position."""
    font = _get_font(size, bold)
    img = font.render(text, True, color)
    if alpha != 255:
        img.set_alpha(alpha)
    rect = img.get_rect()
    if center:
        rect.center = (int(center[0]), int(center[1]))
    elif topleft:
        rect.topleft = (int(topleft[0]), int(topleft[1]))
    elif midleft:
        rect.midleft = (int(midleft[0]), int(midleft[1]))
    elif midright:
        rect.midright = (int(midright[0]), int(midright[1]))
    surface.blit(img, rect)
    return rect


def draw_text_shadow(
    surface,
    text: str,
    size: int,
    color,
    shadow_color=(0, 0, 0),
    offset=(2, 2),
    center=None,
    topleft=None,
    bold: bool = False,
):
    """Render text with a drop-shadow for legibility."""
    sx = (center[0] + offset[0], center[1] + offset[1]) if center else None
    stl = (topleft[0] + offset[0], topleft[1] + offset[1]) if topleft else None
    draw_text(surface, text, size, shadow_color, center=sx, topleft=stl, bold=bold)
    return draw_text(surface, text, size, color, center=center, topleft=topleft, bold=bold)


def draw_button(surface, rect: pygame.Rect, text: str, font_size: int,
                bg_color, border_color, text_color=(30, 30, 30),
                hover=False, radius: int = 28):
    """Draw a rounded pill-style button matching the reference design."""
    # Shadow
    shadow_rect = rect.move(0, 4)
    pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=radius)
    # Fill
    fill_color = tuple(min(c + 20, 255) for c in bg_color) if hover else bg_color
    pygame.draw.rect(surface, fill_color, rect, border_radius=radius)
    # Border
    pygame.draw.rect(surface, border_color, rect, 3, border_radius=radius)
    # Text
    draw_text(surface, text, font_size, text_color, center=rect.center, bold=True)
