import os
import math
import pygame
from pathlib import Path
from view.font_helper import draw_text, draw_text_shadow, draw_button

# ── Bảng màu chuẩn theo reference design ────────────────────────────────────
BTN_ORANGE  = (239, 100,  72)   # coral-orange nút bấm
BTN_HOVER   = (255, 130, 100)   # hover sáng hơn
BTN_BORDER  = ( 22,  43,  68)   # navy viền
BTN_TEXT    = ( 20,  20,  20)   # text màu đậm trên nút
TITLE_COLOR = (255, 220,  30)   # tiêu đề vàng
WHITE       = (255, 255, 255)


class MenuView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width  = width
        self.height = height
        self._surf  = screen.surface          # pygame.Surface gốc

        base_path = Path(__file__).parent.parent
        img_dir   = os.path.join(base_path, 'data', 'images')

        # ── Logo ────────────────────────────────────────────────────────────
        self.logo = None
        logo_path = os.path.join(img_dir, 'logo.png')
        if os.path.exists(logo_path):
            try:
                raw = pygame.image.load(logo_path).convert_alpha()
                self.logo = pygame.transform.smoothscale(raw, (220, 220))
            except Exception as e:
                print(f"[MenuView] logo load error: {e}")

        # ── Background bgG (sunburst comic green) ───────────────────────────
        self.bg_menu = None
        bg_path = os.path.join(img_dir, 'bgG.png')
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert_alpha()
                self.bg_menu = pygame.transform.smoothscale(img, (width, height))
            except Exception as e:
                print(f"[MenuView] bgG load error: {e}")

        # ── Splash screen: animated "press any key" alpha ───────────────────
        self._splash_alpha = 255
        self._splash_dir   = -2          # fade direction

    # ── Private helpers ──────────────────────────────────────────────────────

    def _blit_bg(self):
        if self.bg_menu:
            self._surf.blit(self.bg_menu, (0, 0))
        else:
            self._surf.fill((28, 90, 50))

    def _draw_title(self, text: str, y: int = 90):
        """Tiêu đề lớn có bóng đổ ở trên cùng màn hình."""
        draw_text_shadow(
            self._surf, text, 52, TITLE_COLOR,
            shadow_color=(40, 20, 0), offset=(3, 3),
            center=(self.width / 2, y), bold=True,
        )

    def _draw_rounded_button(self, btn, mouse_pos):
        """Vẽ 1 nút kiểu pill với hover effect."""
        hovered = btn.rect.collidepoint(mouse_pos)
        draw_button(
            self._surf,
            pygame.Rect(btn.rect.x, btn.rect.y, btn.rect.width, btn.rect.height),
            btn.text,
            font_size=26,
            bg_color=BTN_HOVER if hovered else BTN_ORANGE,
            border_color=BTN_BORDER,
            text_color=BTN_TEXT,
            hover=hovered,
            radius=30,
        )

    # ── Public API ───────────────────────────────────────────────────────────

    def draw_splash(self, gif_model):
        """Màn hình giật title / intro."""
        frame = gif_model.get_current_frame()
        self._surf.blit(pygame.transform.smoothscale(frame, (self.width, self.height)), (0, 0))

        if self.logo:
            logo_rect = self.logo.get_rect(center=(self.width // 2, self.height // 2 - 30))
            self._surf.blit(self.logo, logo_rect)

        # Hiệu ứng nhấp nháy "Chạm bất kỳ để tiếp tục"
        self._splash_alpha = max(60, min(255, self._splash_alpha + self._splash_dir * 3))
        if self._splash_alpha in (60, 255):
            self._splash_dir *= -1

        draw_text(
            self._surf,
            "Chạm bất kỳ để tiếp tục",
            22, (*WHITE, self._splash_alpha),
            center=(self.width / 2, self.height / 2 + 140),
        )

    def draw_main_menu(self, buttons, mouse_pos):
        """Menu chính: nền bgG + logo + 4 nút pill."""
        self._blit_bg()

        # Logo trên cùng
        if self.logo:
            lr = self.logo.get_rect(center=(self.width // 2, 110))
            self._surf.blit(self.logo, lr)

        # Tiêu đề bên dưới logo
        draw_text_shadow(
            self._surf, "UNO GAME", 48, TITLE_COLOR,
            shadow_color=(80, 30, 0), offset=(3, 3),
            center=(self.width / 2, 240), bold=True,
        )

        # Các nút bấm
        for btn in buttons:
            self._draw_rounded_button(btn, mouse_pos)

    def draw_difficulty(self, title: str, buttons, mouse_pos):
        """Màn chọn độ khó - dùng chung cho đơn người chơi."""
        self._blit_bg()
        self._draw_title(title)
        for btn in buttons:
            self._draw_rounded_button(btn, mouse_pos)

    def draw_multi_select(self, title: str, buttons, mouse_pos):
        """Màn chọn số người - đa người chơi."""
        self._blit_bg()
        self._draw_title(title)
        for btn in buttons:
            self._draw_rounded_button(btn, mouse_pos)