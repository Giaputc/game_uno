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

_TOP_BAR_H   = 55          # chiều cao thanh menu trên cùng
_SIDE_MARGIN = 10          # lề trái/phải cho vùng bài
_BTN_W, _BTN_H = 100, 38   # kích thước nút
_MIN_CARD_W  = 28          # chiều rộng tối thiểu của lá bài khi thu nhỏ
_MIN_SPACING = 14          # khoảng cách tối thiểu giữa các lá bài


class SingleGameView:
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

        # Color-picker images (Wild card)
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
            self.back_image = pygame.transform.scale(img, (70, 105))

        # Nút UNO phía trên-phải của bộ bài 7 lá (xấp xỉ cạnh phải hand)
        self.uno_btn_rect  = pygame.Rect(560, 443, 80, 36)
        # Nút Rút bài (bên trái giữa, dưới bot cards)
        self.draw_btn_rect = pygame.Rect(self.width // 2 - 130, self.height // 2 - 55, 70, 105)
        # Nút Back / Quit — vẽ ngay trong view
        self.back_btn_rect = pygame.Rect(self.width - _BTN_W - 10,       10, _BTN_W, _BTN_H)
        self.quit_btn_rect = pygame.Rect(self.width - _BTN_W * 2 - 20,   10, _BTN_W, _BTN_H)

        self.human_card_rects = []
        self.human_hit_rects  = []   # hẹp hơn draw rect khi bài chồng nhau
        self.ranking_back_btn = None

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _calc_card_layout(self, hand_len, card_w, card_h):
        """
        Trả về (actual_card_w, actual_card_h, start_x, spacing) đảm bảo
        tất cả lá bài luôn vừa khít trong màn hình.
        Thu nhỏ cả card_w lẫn spacing khi tay nhiều bài.
        """
        avail_w = self.width - 2 * _SIDE_MARGIN
        if hand_len <= 1:
            return card_w, card_h, _SIDE_MARGIN + (avail_w - card_w) // 2, card_w

        # Thử spacing bằng card_w trước (bài không chồng)
        spacing = card_w
        total_w = (hand_len - 1) * spacing + card_w

        if total_w > avail_w:
            # Thu nhỏ spacing trước
            spacing = max(_MIN_SPACING, (avail_w - card_w) // (hand_len - 1))
            total_w = (hand_len - 1) * spacing + card_w

        if total_w > avail_w:
            # Vẫn còn tràn → thu nhỏ cả card_w
            # card_w * 1 + spacing * (n-1) <= avail_w
            # dùng tỉ lệ: spacing = card_w * ratio
            ratio   = avail_w / (card_w + _MIN_SPACING * (hand_len - 1))
            card_w  = max(_MIN_CARD_W, int(card_w * ratio))
            card_h  = int(card_h * (card_w / max(1, int(card_w / ratio))))
            spacing = max(_MIN_SPACING, (avail_w - card_w) // (hand_len - 1))
            total_w = (hand_len - 1) * spacing + card_w

        # Đảm bảo tỉ lệ bài
        card_h = int(card_h)
        start_x = (self.width - min(total_w, avail_w)) // 2
        start_x = max(_SIDE_MARGIN, start_x)
        return card_w, card_h, start_x, spacing

    def _draw_top_bar(self, mouse_pos):
        """Vẽ thanh Quit / Back ở góc trên bên phải, tương tự màn hướng dẫn."""
        # Removed dark background bar per user request

        hov_q = self.quit_btn_rect.collidepoint(mouse_pos)
        draw_button(self.screen.surface, self.quit_btn_rect, "Thoát", 18,
                    _RED_H if hov_q else _RED, _NAVY, (255, 255, 255),
                    hover=hov_q, radius=8)

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
            self.screen.surface.fill((20, 50, 20))

        if not game_logic:
            self._draw_top_bar(mouse_pos)
            return

        # 2. Bài BOT (phía trên, bắt đầu dưới top bar)
        bot_player = game_logic.players[1]
        bot_hand   = len(bot_player.hand)
        bot_cw, bot_ch = 50, 75
        bot_y          = _TOP_BAR_H + 8

        if bot_hand > 0:
            bot_cw, bot_ch, b_start, b_spacing = self._calc_card_layout(bot_hand, bot_cw, bot_ch)
            
            if game_logic.current_turn == 1:
                total_bw = (bot_hand - 1) * b_spacing + bot_cw
                pygame.draw.rect(self.screen.surface, (255, 215, 0), (b_start - 8, bot_y - 8, total_bw + 16, bot_ch + 16), 4, border_radius=8)
                
            for i in range(bot_hand):
                bx   = int(b_start + i * b_spacing)
                bx   = min(bx, self.width - _SIDE_MARGIN - bot_cw)
                brect = pygame.Rect(bx, bot_y, bot_cw, bot_ch)
                if self.back_image:
                    self.screen.blit(
                        pygame.transform.scale(self.back_image, (bot_cw, bot_ch)), brect
                    )
                else:
                    pygame.draw.rect(self.screen.surface, _RED, brect, border_radius=4)

        # 3. Deck (rút bài)
        if game_logic.deck.cards:
            if self.back_image:
                self.screen.blit(self.back_image, self.draw_btn_rect)
            else:
                pygame.draw.rect(self.screen.surface, (255, 255, 255), self.draw_btn_rect)
            draw_text(self.screen.surface, "Rút", 16, (0, 0, 0),
                      center=self.draw_btn_rect.center)

        # (Discard pile moved to draw AFTER human hand for proper z-index)
        # 5. Bài người chơi (phía dưới)
        human    = game_logic.players[0]
        hand_len = len(human.hand)
        BASE_W, BASE_H = 65, 98
        card_w, card_h, start_x, spacing = self._calc_card_layout(
            hand_len, BASE_W, BASE_H
        )
        # Đảm bảo tỉ lệ chiều cao theo chiều rộng thực tế
        card_h = int(BASE_H * card_w / BASE_W)
        y_base = self.height - card_h - 8
        hover_lift = min(16, card_h // 6)  # hover không được bay ra khỏi màn hình

        self.human_card_rects = []
        self.human_hit_rects  = []
        # Khi bài chồng nhau, vùng click của mỗi lá = phần thực sự nhìn thấy
        # (spacing px từ cạnh trái), riêng lá cuối giữ nguyên card_w.
        hit_w = spacing if spacing < card_w else card_w
        
        # Turn Indicator
        if game_logic.current_turn == 0 and hand_len > 0:
            total_w = min((hand_len - 1) * spacing + card_w, self.width - 2 * _SIDE_MARGIN)
            pygame.draw.rect(self.screen.surface, (50, 255, 50), (start_x - 8, y_base - 8, total_w + 16, card_h + 16), 4, border_radius=8)

        for i, card in enumerate(human.hand):
            cx   = int(start_x + i * spacing)
            # Clamp x: lá bài không vượt lề phải
            cx   = min(cx, self.width - _SIDE_MARGIN - card_w)
            cy   = y_base

            # Nhấc lá bài lên nếu đang bị dính +2/+4 và lá bài này có thể đem ra đỡ (Stacking)
            if game_logic.current_turn == 0 and game_logic.pending_draw > 0:
                if game_logic.can_play_card(card):
                    cy -= 20

            rect = pygame.Rect(cx, cy, card_w, card_h)

            # Cập nhật trạng thái hover cho card (bỏ qua rect.y tĩnh)
            card.is_hovered = rect.collidepoint(mouse_pos) and game_logic.current_turn == 0

            self.human_card_rects.append(rect)

            # Hit rect: lá cuối dùng full width, các lá trước thu hẹp
            is_last = (i == hand_len - 1)
            hit_rect = pygame.Rect(cx, cy, card_w if is_last else hit_w, card_h)
            self.human_hit_rects.append(hit_rect)

            # Vẽ bài, hàm draw sẽ lo animation và hover
            card.draw(self.screen.surface, cx, cy, card_w, card_h)

        # 5.5 Vẽ Discard Pile đè lên trên để bài vừa đánh ra luôn nổi lướt qua màn hình
        top_card     = game_logic.get_top_card()
        discard_rect = pygame.Rect(self.width // 2 + 50, self.height // 2 - 55, 70, 105)
        if top_card:
            top_card.is_hovered = False
            top_card.draw(self.screen.surface, discard_rect.x, discard_rect.y, 70, 105)

        # 5.6 Mũi tên hướng đi + thông báo Stacking
        arrow_cx = self.width // 2 - 15
        arrow_cy = self.height // 2 - 5
        self._draw_direction_indicator(self.screen.surface, arrow_cx, arrow_cy, game_logic.direction)

        # Bỏ đi text hiện cộng dồn theo yêu cầu

        # 6. Nút UNO (Chỉ hiện khi sắp hết bài)
        if hand_len == 2:
            uno_hov = self.uno_btn_rect.collidepoint(mouse_pos)
            bg_color = (255, 80, 80) if uno_hov else (220, 0, 0)
            if not human.said_uno and (pygame.time.get_ticks() // 150) % 2 == 0:
                bg_color = (255, 100, 100) # Sáng chớp nháy nhắc nhở
                
            draw_button(self.screen.surface, self.uno_btn_rect, "UNO", 18,
                        bg_color, _NAVY, (255, 255, 255), hover=uno_hov, radius=8)

        # 7. Trạng thái lượt (đã xóa theo yêu cầu)

        # 8. Thanh menu (vẽ cuối để không bị phủ)
        self._draw_top_bar(mouse_pos)

    # ── Winner screen ────────────────────────────────────────────────────────

    def draw_ranking(self, players, win_score=0):
        """Màn hình xếp hạng sau khi game kết thúc (Single Player)."""
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((10, 10, 30))
        self.screen.blit(overlay, (0, 0))

        title_rect = pygame.Rect(self.width // 2 - 220, 20, 440, 60)
        pygame.draw.rect(self.screen.surface, (60, 30, 120), title_rect, border_radius=14)
        pygame.draw.rect(self.screen.surface, (180, 120, 255), title_rect, 3, border_radius=14)
        draw_text_shadow(self.screen.surface, "BẢNG XẾP HẠNG", 36, (255, 255, 255),
                         shadow_color=(0, 0, 0), offset=(2, 2),
                         center=title_rect.center, bold=True)

        medal_colors = [(255, 215, 0), (192, 192, 192)]
        sorted_players = sorted(players, key=lambda p: len(p.hand))

        card_w, card_h = 440, 70
        start_y, spacing = 130, 85

        for rank, player in enumerate(sorted_players):
            row_y    = start_y + rank * spacing
            row_rect = pygame.Rect(self.width // 2 - card_w // 2, row_y, card_w, card_h)

            if rank == 0:
                bg_color, border_color = (80, 60, 10),  medal_colors[0]
            elif rank == 1:
                bg_color, border_color = (40, 40, 50),  medal_colors[1]
            else:
                bg_color, border_color = (30, 30, 50),  (90, 90, 130)

            pygame.draw.rect(self.screen.surface, bg_color,    row_rect, border_radius=12)
            pygame.draw.rect(self.screen.surface, border_color, row_rect, 3, border_radius=12)

            medal_color = medal_colors[rank] if rank < 2 else (130, 130, 160)
            label       = f"#{rank + 1}"
            draw_text(self.screen.surface, label, 30, medal_color,
                      midleft=(row_rect.x + 14, row_rect.centery), bold=True)

            name_color = (255, 215, 0) if rank == 0 else (220, 220, 255)
            draw_text(self.screen.surface, player.name, 26, name_color,
                      midleft=(row_rect.x + 80, row_rect.centery), bold=(rank == 0))

            cards_left = len(player.hand)
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

            draw_text(self.screen.surface, status_text, 24, status_color,
                      midright=(row_rect.right - 14, row_rect.centery))

        btn_rect = pygame.Rect(
            self.width // 2 - 130,
            start_y + len(sorted_players) * spacing + 40,
            260, 50
        )
        draw_button(self.screen.surface, btn_rect, "Quay về Menu", 24,
                    (100, 40, 180), (200, 150, 255), (255, 255, 255), radius=12)
        self.ranking_back_btn = btn_rect

    # ── Direction Indicator ───────────────────────────────────────────────────

    def _draw_direction_indicator(self, surface, cx, cy, direction):
        if not hasattr(self, 'dir_angle'):
            self.dir_angle = 0.0
        self.dir_angle += 2.0 * direction
        
        radius = 30  # Thu nhỏ để không che bài bốc
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

