import os
import math
import pygame
from pathlib import Path
from view.font_helper import draw_text, draw_text_shadow, draw_button

_NAVY      = ( 22,  43,  68)
_RED       = (220,  53,  69)
_RED_H     = (255,  80,  60)
_BLUE      = (  0, 123, 255)
_BLUE_H    = (  0, 105, 217)
_COLOR_MAP = {
    'red':    (220,  53,  69),
    'green':  ( 40, 167,  69),
    'blue':   (  0, 123, 255),
    'yellow': (255, 193,   7),
    'black':  ( 30,  30,  30),
}

# Chiều cao thanh menu trên cùng (chừa không gian cho nút QUIT/Back)
_TOP_BAR_H   = 55
# Lề trái/phải cho vùng bài
_SIDE_MARGIN = 10
# Nút trên cùng bên phải
_BTN_W, _BTN_H = 100, 38
# Kích thước tối thiểu của lá bài khi thu nhỏ
_MIN_CARD_W  = 24
_MIN_SPACING = 12


class MultiGameView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width  = width
        self.height = height

        base_path = Path(__file__).parent.parent.parent
        img_dir   = os.path.join(base_path, 'data', 'images')

        # Backgrounds
        self.bgs = {}
        bg_mapping = {
            'black':  'bgBlack.png', 'red':  'bgR.png',
            'green':  'bgG.png',     'blue': 'bgBlue.png',
            'yellow': 'bgY.png',
        }
        for color, file in bg_mapping.items():
            path = os.path.join(img_dir, file)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.bgs[color] = pygame.transform.scale(img, (width, height))

        # Color-picker images
        self.color_imgs = {}
        for color in ['red', 'green', 'blue', 'yellow']:
            path = os.path.join(img_dir, f"{color}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.color_imgs[color] = pygame.transform.scale(img, (80, 80))

        # Card back
        self.back_image = None
        back_path = os.path.join(img_dir, 'back.png')
        if os.path.exists(back_path):
            img = pygame.image.load(back_path).convert_alpha()
            self.back_image = pygame.transform.scale(img, (60, 90))

        # Nút UNO phía trên-phải của bộ bài 7 lá
        self.uno_btn_rect = pygame.Rect(560, 443, 80, 36)
        # Nút Rút bài (bên trái giữa)
        self.draw_btn_rect = pygame.Rect(
            self.width // 2 - 120, self.height // 2 - 50, 60, 90
        )
        # Nút menu trên cùng (Back, Quit) — vẽ bởi view, không cần controller pass vào
        self.back_btn_rect = pygame.Rect(self.width - _BTN_W - 10,            10, _BTN_W, _BTN_H)
        self.quit_btn_rect = pygame.Rect(self.width - _BTN_W * 2 - 20,        10, _BTN_W, _BTN_H)

        self.human_card_rects = []
        self.human_hit_rects  = []   # hẹp hơn draw rect khi bài chồng nhau
        self.ranking_back_btn = None

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _calc_card_layout(self, hand_len, card_w, card_h):
        """
        Tính spacing và start_x để hand_len lá bài vừa khít trong
        [_SIDE_MARGIN, width - _SIDE_MARGIN].  Card luôn được thu nhỏ
        (cả card_w lẫn spacing) nếu quá nhiều bài.
        Trả về (actual_card_w, actual_card_h, start_x, spacing).
        """
        avail_w = self.width - 2 * _SIDE_MARGIN
        if hand_len <= 1:
            return card_w, card_h, _SIDE_MARGIN + (avail_w - card_w) // 2, card_w

        # Thử spacing bằng card_w (bài không chồng nhau)
        spacing = card_w
        total_w = (hand_len - 1) * spacing + card_w

        if total_w > avail_w:
            # Thu nhỏ spacing trước
            spacing = max(_MIN_SPACING, (avail_w - card_w) // (hand_len - 1))
            total_w = (hand_len - 1) * spacing + card_w

        if total_w > avail_w:
            # Vẫn còn tràn → thu nhỏ cả card_w
            ratio   = avail_w / (card_w + _MIN_SPACING * (hand_len - 1))
            card_w  = max(_MIN_CARD_W, int(card_w * ratio))
            card_h  = int(card_h * card_w / max(1, int(card_w / ratio)))
            spacing = max(_MIN_SPACING, (avail_w - card_w) // (hand_len - 1))
            total_w = (hand_len - 1) * spacing + card_w

        card_h  = int(card_h)
        start_x = max(_SIDE_MARGIN, (self.width - min(total_w, avail_w)) // 2)
        return card_w, card_h, start_x, spacing

    def _draw_top_bar(self, mouse_pos):
        """Vẽ thanh menu Back / Quit ở góc trên bên phải."""
        # Removed dark background bar per user request

        # Nút QUIT
        hov_q = self.quit_btn_rect.collidepoint(mouse_pos)
        draw_button(self.screen.surface, self.quit_btn_rect, "Thoát", 18,
                    _RED_H if hov_q else _RED, _NAVY, (255, 255, 255),
                    hover=hov_q, radius=8)

        # Nút Back
        hov_b = self.back_btn_rect.collidepoint(mouse_pos)
        draw_button(self.screen.surface, self.back_btn_rect, "Quay lại", 18,
                    _BLUE_H if hov_b else _BLUE, _NAVY, (255, 255, 255),
                    hover=hov_b, radius=8)

    # ── Main draw ────────────────────────────────────────────────────────────

    def draw(self, game_logic, mouse_pos, top_buttons=None):
        # 1. Nền
        bg = self.bgs.get(
            game_logic.current_color if game_logic else 'black',
            self.bgs.get('black')
        )
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.surface.fill((10, 80, 10))

        if not game_logic:
            self._draw_top_bar(mouse_pos)
            return

        # 2. Deck (rút bài)
        if game_logic.deck.cards:
            if self.back_image:
                self.screen.blit(self.back_image, self.draw_btn_rect)
            else:
                pygame.draw.rect(self.screen.surface, (255, 255, 255), self.draw_btn_rect)
            draw_text(self.screen.surface, "Rút", 15, (0, 0, 0),
                      center=self.draw_btn_rect.center)

        # (Discard pile moved down to draw AFTER hands for proper z-index)
        # 4. Info BOTs (bên trái/phải/trên)
        num_players = len(game_logic.players)
        if num_players == 3:
            positions = [None, (55, self.height // 2), (self.width - 55, self.height // 2)]
        elif num_players == 4:
            positions = [
                None,
                (55, self.height // 2),
                (self.width // 2, _TOP_BAR_H + 50),
                (self.width - 55, self.height // 2),
            ]
        else:
            positions = [None] * num_players

        for i, pos in enumerate(positions):
            if i == 0 or not pos:
                continue
            bot  = game_logic.players[i]
            x, y = int(pos[0]), int(pos[1])
            
            # Turn Indicator for bot
            if game_logic.current_turn == i:
                pygame.draw.circle(self.screen.surface, (255, 215, 0), (x, y), 50, 4)
                
            pygame.draw.circle(self.screen.surface, (0, 0, 0), (x, y), 42)
            pygame.draw.circle(self.screen.surface, (80, 80, 80), (x, y), 42, 2)
            draw_text(self.screen.surface, bot.name[:6], 17, (200, 200, 200), center=(x, y - 16))
            draw_text(self.screen.surface, f"{len(bot.hand)} lá", 20, (255, 220, 30), center=(x, y + 12))
            if bot.said_uno:
                draw_text_shadow(self.screen.surface, "UNO!", 18, (255, 50, 50),
                                 shadow_color=(0, 0, 0), offset=(1, 1), center=(x, y + 34), bold=True)

        # 5. Bài người chơi (phía dưới)
        human     = game_logic.players[0]
        hand_len  = len(human.hand)
        BASE_W, BASE_H = 60, 90
        card_w, card_h, start_x, spacing = self._calc_card_layout(
            hand_len, BASE_W, BASE_H
        )
        # Đảm bảo tỉ lệ chiều cao
        card_h = int(BASE_H * card_w / BASE_W)
        y_base = self.height - card_h - 10
        hover_lift = min(12, card_h // 7)

        self.human_card_rects = []
        self.human_hit_rects  = []
        # Vùng click của mỗi lá = phần thực sự nhìn thấy khi bài chồng
        hit_w = spacing if spacing < card_w else card_w

        # Turn Indicator for human player
        if game_logic.current_turn == 0 and hand_len > 0:
            total_w = min((hand_len - 1) * spacing + card_w, self.width - 2 * _SIDE_MARGIN)
            pygame.draw.rect(self.screen.surface, (50, 255, 50), (start_x - 8, y_base - 8, total_w + 16, card_h + 16), 4, border_radius=8)

        for i, card in enumerate(human.hand):
            cx = int(start_x + i * spacing)
            cx = min(cx, self.width - _SIDE_MARGIN - card_w)
            cy = y_base

            # Nhấc lá bài lên nếu đang bị dính +2/+4 và lá bài này có thể đem ra đỡ (Stacking)
            if game_logic.current_turn == 0 and game_logic.pending_draw > 0:
                if game_logic.can_play_card(card):
                    cy -= 20

            rect = pygame.Rect(cx, cy, card_w, card_h)

            # Cập nhật trạng thái hover
            card.is_hovered = rect.collidepoint(mouse_pos) and game_logic.current_turn == 0

            self.human_card_rects.append(rect)

            # Hit rect: lá cuối giữ full width, các lá trước thu hẹp
            is_last = (i == hand_len - 1)
            hit_rect = pygame.Rect(cx, cy, card_w if is_last else hit_w, card_h)
            self.human_hit_rects.append(hit_rect)

            # Vẽ bài có hiệu ứng
            card.draw(self.screen.surface, cx, cy, card_w, card_h)

        # 5.5 Vẽ Discard Pile
        top_card    = game_logic.get_top_card()
        discard_rect = pygame.Rect(self.width // 2 + 20, self.height // 2 - 50, 60, 90)
        if top_card:
            top_card.is_hovered = False
            top_card.draw(self.screen.surface, discard_rect.x, discard_rect.y, 60, 90)

        # 5.6 Mũi tên hướng đi + cộng dồn stacking
        arrow_cx = self.width // 2 - 20
        arrow_cy = self.height // 2 - 5
        self._draw_direction_indicator(self.screen.surface, arrow_cx, arrow_cy, game_logic.direction)

        # 5.7 Bỏ text cộng dồn theo yêu cầu

        # 6. Nút UNO (Chỉ hiện khi sắp hết bài)
        if hand_len == 2:
            uno_hov = self.uno_btn_rect.collidepoint(mouse_pos)
            bg_color = (255, 80, 80) if uno_hov else (220, 0, 0)
            if not human.said_uno and (pygame.time.get_ticks() // 150) % 2 == 0:
                bg_color = (255, 100, 100) # Sáng chớp nháy nhắc nhở
                
            draw_button(self.screen.surface, self.uno_btn_rect, "UNO", 18,
                        bg_color, _NAVY, (255, 255, 255), hover=uno_hov, radius=8)

        # 8. Thanh menu trên cùng (vẽ sau cùng để không bị phủ)
        self._draw_top_bar(mouse_pos)

    # ── Winner / Ranking ─────────────────────────────────────────────────────

    def draw_winner(self, winner_name):
        self.screen.surface.fill((0, 0, 0))
        draw_text_shadow(self.screen.surface, f"NGƯỜI CHIẾN THẮNG: {winner_name}",
                         48, (255, 220, 30), shadow_color=(80, 40, 0), offset=(3, 3),
                         center=(self.width // 2, self.height // 2), bold=True)
        draw_text(self.screen.surface, "Chạm để quay về Menu",
                  26, (255, 255, 255),
                  center=(self.width // 2, self.height // 2 + 70))

    def draw_ranking(self, players, win_score=0):
        """Màn hình xếp hạng sau khi game kết thúc (MultiPlayer)."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((10, 10, 30))
        self.screen.blit(overlay, (0, 0))

        title_rect = pygame.Rect(self.width // 2 - 220, 20, 440, 60)
        pygame.draw.rect(self.screen.surface, (60, 30, 120), title_rect, border_radius=14)
        pygame.draw.rect(self.screen.surface, (180, 120, 255), title_rect, 3, border_radius=14)
        draw_text_shadow(self.screen.surface, "BẢNG XẾP HẠNG", 36, (255, 255, 255),
                         shadow_color=(0, 0, 0), offset=(2, 2),
                         center=title_rect.center, bold=True)

        medal_colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
        sorted_players = sorted(players, key=lambda p: len(p.hand))

        card_w, card_h = 420, 62
        start_y, spacing = 110, 75

        for rank, player in enumerate(sorted_players):
            row_y    = start_y + rank * spacing
            row_rect = pygame.Rect(self.width // 2 - card_w // 2, row_y, card_w, card_h)

            if rank == 0:
                bg_color, border_color = (80, 60, 10),  medal_colors[0]
            elif rank == 1:
                bg_color, border_color = (40, 40, 50),  medal_colors[1]
            elif rank == 2:
                bg_color, border_color = (40, 25, 10),  medal_colors[2]
            else:
                bg_color, border_color = (30, 30, 50),  (90, 90, 130)

            pygame.draw.rect(self.screen.surface, bg_color,    row_rect, border_radius=12)
            pygame.draw.rect(self.screen.surface, border_color, row_rect, 3, border_radius=12)

            medal_color = medal_colors[rank] if rank < 3 else (130, 130, 160)
            label       = f"#{rank + 1}"
            draw_text(self.screen.surface, label, 28, medal_color,
                      midleft=(row_rect.x + 14, row_rect.centery), bold=True)

            name_color = (255, 215, 0) if rank == 0 else (220, 220, 255)
            draw_text(self.screen.surface, player.name, 24, name_color,
                      midleft=(row_rect.x + 70, row_rect.centery), bold=(rank == 0))

            cards_left   = len(player.hand)
            penalty_points = 0
            for card in player.hand:
                val = str(getattr(card, "value", ""))
                if val in ["skip", "reverse", "+2"]: penalty_points += 20
                elif val in ["black", "+4"] or getattr(card, "color", "") == "black": penalty_points += 50
                elif val.isdigit(): penalty_points += int(val)

            if rank == 0:
                status_text  = f"0 điểm"
                status_color = (100, 255, 100)
            else:
                status_text  = f"{penalty_points} điểm"
                status_color = (255, 150, 150)

            draw_text(self.screen.surface, status_text, 22, status_color,
                      midright=(row_rect.right - 14, row_rect.centery))

        btn_rect = pygame.Rect(
            self.width // 2 - 130,
            start_y + len(sorted_players) * spacing + 20,
            260, 50
        )
        draw_button(self.screen.surface, btn_rect, "Quay về Menu", 24,
                    (100, 40, 180), (200, 150, 255), (255, 255, 255), radius=12)
        self.ranking_back_btn = btn_rect

    # ── Direction Indicator ────────────────────────────────────────

    def _draw_direction_indicator(self, surface, cx, cy, direction):
        if not hasattr(self, 'dir_angle'):
            self.dir_angle = 0.0
        self.dir_angle += 2.0 * direction
        
        radius = 30  # Thu nhỏ xuống 30px để không che bài
        color = (0, 255, 255) if direction == 1 else (255, 200, 50)
        
        for offset in [0, 180]:
            start_angle = math.radians(self.dir_angle + offset)
            sweep = math.radians(120)
            
            n_seg = 20
            pts = []
            for i in range(n_seg + 1):
                a = start_angle + sweep * (i / n_seg)
                px = cx + radius * math.cos(a)
                py = cy + radius * math.sin(a)
                pts.append((int(px), int(py)))
                
            if len(pts) >= 2:
                pygame.draw.lines(surface, color, False, pts, 4)
                
                head_idx = -1 if direction == 1 else 0
                bg_idx = -2 if direction == 1 else 1
                
                ex, ey = pts[head_idx]
                px, py = pts[bg_idx]
                
                dx, dy = ex - px, ey - py
                length = math.hypot(dx, dy) or 1
                dx /= length; dy /= length
                
                tip = (ex + dx*6, ey + dy*6)
                left = (ex - dx*10 + dy*7, ey - dy*10 - dx*7)
                right = (ex - dx*10 - dy*7, ey - dy*10 + dx*7)
                pygame.draw.polygon(surface, color, [tip, left, right])
        
        try:
            font = pygame.font.SysFont('arial', 12, bold=True)
            txt = "NGƯỢC" if direction == -1 else "XUÔI"
            lbl = font.render(txt, True, color)
            surface.blit(lbl, lbl.get_rect(center=(cx, cy)))
        except Exception:
            pass
