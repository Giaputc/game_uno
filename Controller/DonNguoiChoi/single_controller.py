import pygame
import time
from model.game_logic import GameLogic
from model.player import Player
from bots.easy_bot import EasyBot
from bots.normal_bot import NormalBot
from bots.hard_bot import HardBot
from view.DonNguoiChoi.single_game_view import SingleGameView
from view.font_helper import draw_text_shadow
from settings import WIDTH, HEIGHT
import view.sfx_manager as sfx

_COLOR_MAP = {'red':(220,53,69),'green':(40,167,69),'blue':(0,123,255),'yellow':(255,193,7)}


class SinglePlayerController:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.difficulty = None
        self.game_logic = None
        self.view = SingleGameView(
            self.main_controller.screen if hasattr(self.main_controller, 'screen') else None,
            WIDTH, HEIGHT
        )
        self.last_bot_move_time = 0
        self.color_picker_active = False
        self._win_sfx_played = False

    def get_screen(self):
        import __main__
        return getattr(__main__, 'screen', None)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.main_controller.game_state = "PLAYING_SINGLE"
        self.color_picker_active = False
        self._win_sfx_played = False

        from model.player import AIPlayer
        human = Player("Bạn", is_human=True)
        if difficulty == "EASY":
            bot = AIPlayer("Bot (Dễ)", EasyBot())
        elif difficulty == "NORMAL":
            bot = AIPlayer("Bot (Vừa)", NormalBot())
        else:
            bot = AIPlayer("Bot (Khó)", HardBot())

        self.game_logic = GameLogic([human, bot])

    def handle_click(self, pos, diff_buttons=None):
        if self.main_controller.game_state == "DIFFICULTY_SELECT":
            for key, btn in diff_buttons.items():
                if btn.rect.collidepoint(pos):
                    if key == 'BACK':
                        self.main_controller.game_state = "MENU"
                    elif key in ['EASY', 'NORMAL', 'HARD']:
                        self.start_game(key)
                    return True
            return False

    def handle_game_click(self, pos):
        if self.game_logic.game_over:
            back_btn = getattr(self.view, 'ranking_back_btn', None)
            if back_btn is None or back_btn.collidepoint(pos):
                self.main_controller.game_state = "MENU"
            return

        # Nút Back / Quit
        if self.view.back_btn_rect.collidepoint(pos):
            self.main_controller.game_state = "MENU"
            return
        if self.view.quit_btn_rect.collidepoint(pos):
            self.main_controller.safe_exit()
            return

        # Chỉ cho phép click nếu là lượt của người chơi số 1 VÀ người đó là con người
        if self.game_logic.current_turn != 0 or not self.game_logic.players[0].is_human:
            return  

        # ── Chọn màu cho lá Wild ──────────────────────────────────────────────
        if self.color_picker_active:
            colors = ["red", "green", "blue", "yellow"]
            for i, c in enumerate(colors):
                rect = pygame.Rect(WIDTH/2 - 180 + i*90, HEIGHT/2 - 40, 80, 80)
                if rect.collidepoint(pos):
                    self.game_logic.play_turn(0, self.pending_card_idx, chosen_color=c)
                    sfx.play('card_play')
                    self.color_picker_active = False
                    self.pending_card_idx = None
                    self.last_move_time = time.time()
                    return
            return

        # ── Nút Rút bài ──────────────────────────────────────────────────────
        if self.view.draw_btn_rect.collidepoint(pos):
            self.game_logic.draw_turn()
            sfx.play('card_draw')
            self.last_move_time = time.time()
            return

        # ── Nút UNO ──────────────────────────────────────────────────────────
        if self.view.uno_btn_rect.collidepoint(pos):
            self.game_logic.players[0].yell_uno()
            sfx.play('uno_call')
            return

        # ── Click bài trên tay ───────────────────────────────────────────────
        for i in reversed(range(len(self.view.human_hit_rects))):
            rect = self.view.human_hit_rects[i]
            if rect.collidepoint(pos):
                card = self.game_logic.players[0].hand[i]
                # Dùng can_play_card để tôn trọng Stacking Rule
                if self.game_logic.can_play_card(card):
                    if card.color == "black":
                        self.color_picker_active = True
                        self.pending_card_idx = i
                    else:
                        self.game_logic.play_turn(0, i)
                        sfx.play('card_play')
                        self.last_move_time = time.time()
                return

    def update(self):
        if self.game_logic and not self.game_logic.game_over:
            if self.game_logic.check_empty_deck_winner():
                return

            # Lấy người chơi hiện tại
            curr_idx = self.game_logic.current_turn
            curr_player = self.game_logic.players[curr_idx]

            # ── Auto-Draw cho người chơi khi bị phạt +2/+4 mà KHÔNG CÓ BÀI ĐỠ ──
            if curr_player.is_human and self.game_logic.pending_draw > 0:
                has_stack_card = any(
                    str(getattr(c, "value", "")) == self.game_logic.pending_draw_type 
                    for c in curr_player.hand
                )
                if not has_stack_card:
                    if time.time() - self.last_bot_move_time > 1.5:
                        self.game_logic.draw_turn()
                        sfx.play('card_draw')
                        self.last_bot_move_time = time.time()
                    return

            # Nếu là Bot (không phải con người), thực hiện nước đi tự động
            if not curr_player.is_human:
                if time.time() - self.last_bot_move_time > 1.2:
                    self.last_bot_move_time = time.time()
                    
                    # Lấy thông tin bài của mọi người để bot nhắm mục tiêu
                    all_hands = [len(p.hand) for p in self.game_logic.players]
                    
                    card_idx, picked_color = curr_player.decide_move(
                        self.game_logic.get_top_card(),
                        self.game_logic.current_color,
                        next_player_hand_size=all_hands[1 - curr_idx],
                        pending_draw_type=self.game_logic.pending_draw_type,
                        all_players_info=all_hands
                    )

                    if card_idx is not None:
                        self.game_logic.play_turn(curr_idx, card_idx, picked_color)
                        sfx.play('card_play')
                    else:
                        self.game_logic.draw_turn()
                        sfx.play('card_draw')

    def draw(self, mouse_pos):
        if not self.view.screen:
            self.view.screen = self.get_screen()

        if self.game_logic.game_over:
            # Phát âm thanh chiến thắng một lần
            if not self._win_sfx_played:
                sfx.play('win')
                self._win_sfx_played = True

            # Hiển thị bảng xếp hạng với điểm số
            score = getattr(self.game_logic, 'win_score', 0)
            self.view.draw_ranking(self.game_logic.players, win_score=score)
        else:
            self.view.draw(self.game_logic, mouse_pos)

            if self.color_picker_active:
                surf = self.view.screen.surface
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                surf.blit(overlay, (0, 0))
                draw_text_shadow(surf, "CHỌN MÀU", 50, (255, 165, 0),
                                 shadow_color=(0,0,0), offset=(3,3),
                                 center=(WIDTH/2, HEIGHT/2 - 100), bold=True)
                colors = ["red", "green", "blue", "yellow"]
                for i, c in enumerate(colors):
                    x = int(WIDTH/2 - 180 + i*90)
                    y = int(HEIGHT/2 - 40)
                    img = self.view.color_imgs.get(c)
                    if img:
                        self.view.screen.blit(img, (x, y))
                    else:
                        pygame.draw.rect(surf, _COLOR_MAP.get(c, (128,128,128)), pygame.Rect(x, y, 80, 80))
