import os
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
_BTN_W, _BTN_H = 80, 38   # kích thước nút
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

        # Nút UNO (góc phải dưới)
        self.uno_btn_rect  = pygame.Rect(self.width - 110, self.height - 70, 90, 45)
        # Nút Rút bài (bên trái giữa, dưới bot cards)
        self.draw_btn_rect = pygame.Rect(self.width // 2 - 130, self.height // 2 - 55, 70, 105)
        # Nút Back / Quit — vẽ ngay trong view
        self.back_btn_rect = pygame.Rect(self.width - _BTN_W - 10,       10, _BTN_W, _BTN_H)
        self.quit_btn_rect = pygame.Rect(self.width - _BTN_W * 2 - 20,   10, _BTN_W, _BTN_H)

        self.human_card_rects = []
        self.human_hit_rects  = []   # hẹp hơn draw rect khi bài chồng nhau

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
        bar = pygame.Surface((self.width, _TOP_BAR_H), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 90))
        self.screen.surface.blit(bar, (0, 0))

        hov_q = self.quit_btn_rect.collidepoint(mouse_pos)
        draw_button(self.screen.surface, self.quit_btn_rect, "Quit", 18,
                    _RED_H if hov_q else _RED, _NAVY, (255, 255, 255),
                    hover=hov_q, radius=8)

        hov_b = self.back_btn_rect.collidepoint(mouse_pos)
        draw_button(self.screen.surface, self.back_btn_rect, "Back", 18,
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

        # 4. Discard pile
        top_card     = game_logic.get_top_card()
        discard_rect = pygame.Rect(self.width // 2 + 50, self.height // 2 - 55, 70, 105)
        if top_card and getattr(top_card, 'image', None):
            self.screen.blit(top_card.image, discard_rect)
        else:
            c = _COLOR_MAP.get(top_card.color if top_card else 'black', (120, 120, 120))
            pygame.draw.rect(self.screen.surface, c, discard_rect, border_radius=6)

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

        for i, card in enumerate(human.hand):
            cx   = int(start_x + i * spacing)
            # Clamp x: lá bài không vượt lề phải
            cx   = min(cx, self.width - _SIDE_MARGIN - card_w)
            cy   = y_base
            rect = pygame.Rect(cx, cy, card_w, card_h)

            # Hover effect — không cho nhô lên quá màn hình
            if rect.collidepoint(mouse_pos) and game_logic.current_turn == 0:
                rect.y = max(_TOP_BAR_H, rect.y - hover_lift)

            self.human_card_rects.append(rect)

            # Hit rect: lá cuối dùng full width, các lá trước thu hẹp
            is_last = (i == hand_len - 1)
            hit_rect = pygame.Rect(cx, cy, card_w if is_last else hit_w, card_h)
            self.human_hit_rects.append(hit_rect)

            if card.image:
                self.screen.blit(
                    pygame.transform.scale(card.image, (card_w, card_h)), rect
                )
            else:
                col = _COLOR_MAP.get(card.color, (120, 120, 120))
                lbl_size = max(10, min(15, card_w // 4))
                pygame.draw.rect(self.screen.surface, col, rect, border_radius=5)
                draw_text(self.screen.surface, str(card.value), lbl_size,
                          (255, 255, 255) if card.color == 'black' else (0, 0, 0),
                          center=rect.center)

        # 6. Nút UNO
        uno_hov = self.uno_btn_rect.collidepoint(mouse_pos)
        draw_button(self.screen.surface, self.uno_btn_rect, "UNO", 26,
                    (255, 80, 80) if uno_hov else (220, 0, 0),
                    _NAVY, (255, 255, 255), hover=uno_hov, radius=10)

        # 7. Trạng thái lượt (góc trái — dưới thanh menu)
        turn_text = "Lượt của bạn" if game_logic.current_turn == 0 else f"Lượt của {game_logic.players[1].name}"
        draw_text_shadow(self.screen.surface, turn_text, 24, (255, 255, 255),
                         shadow_color=(0, 0, 0), offset=(2, 2),
                         topleft=(12, _TOP_BAR_H + 4), bold=True)

        # 8. Thanh menu (vẽ cuối để không bị phủ)
        self._draw_top_bar(mouse_pos)

    # ── Winner screen ────────────────────────────────────────────────────────

    def draw_winner(self, winner_name):
        self.screen.surface.fill((0, 0, 0))
        draw_text_shadow(self.screen.surface, f"NGƯỜI CHIẾN THẮNG: {winner_name}",
                         48, (255, 220, 30), shadow_color=(80, 40, 0), offset=(3, 3),
                         center=(self.width // 2, self.height // 2), bold=True)
        draw_text(self.screen.surface, "Chạm để quay về Menu",
                  26, (255, 255, 255),
                  center=(self.width // 2, self.height // 2 + 70))
