import pygame
import time
from model.game_logic import GameLogic
from model.player import Player
from bots.bot_easy import BotEasy
from bots.bot_normal import BotNormal
from bots.bot_hard import BotHard
from view.DonNguoiChoi.single_game_view import SingleGameView
from view.font_helper import draw_text_shadow
from settings import WIDTH, HEIGHT

_COLOR_MAP = {'red':(220,53,69),'green':(40,167,69),'blue':(0,123,255),'yellow':(255,193,7)}

class SinglePlayerController:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.difficulty = None
        self.game_logic = None
        self.view = SingleGameView(self.main_controller.screen if hasattr(self.main_controller, 'screen') else None, WIDTH, HEIGHT)
        self.last_bot_move_time = 0
        self.color_picker_active = False

    def get_screen(self):
        # Fallback to get screen if it wasn't passed during init
        import __main__
        return getattr(__main__, 'screen', None)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.main_controller.game_state = "PLAYING_SINGLE"
        self.color_picker_active = False
        
        # Tạo player
        human = Player("You", is_human=True)
        bot = None
        if difficulty == "EASY":
            bot = BotEasy("Bot (Easy)")
        elif difficulty == "NORMAL":
            bot = BotNormal("Bot (Normal)")
        else:
            bot = BotHard("Bot (Hard)")
            
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
            self.main_controller.game_state = "MENU"
            return

        # Nút Back / Quit (thanh menu trên cùng — liên kết với view)
        if self.view.back_btn_rect.collidepoint(pos):
            self.main_controller.game_state = "MENU"
            return
        if self.view.quit_btn_rect.collidepoint(pos):
            self.main_controller.safe_exit()
            return

        if self.game_logic.current_turn != 0:
            return # Không phải lượt ng chơi
            
        if self.color_picker_active:
            # Chọn màu cho lá Wild (Sử dụng 4 nút ảo ngay chính giữa màn hình)
            # red at WIDTH/2 - 100, Y
            # green at WIDTH/2 - 20, Y
            # blue at WIDTH/2 + 60, Y
            # yellow at WIDTH/2 + 140, Y
            # Mỗi nút 80x80
            colors = ["red", "green", "blue", "yellow"]
            for i, c in enumerate(colors):
                rect = pygame.Rect(WIDTH/2 - 180 + i*90, HEIGHT/2 - 40, 80, 80)
                if rect.collidepoint(pos):
                    self.game_logic.play_turn(0, self.pending_card_idx, c)
                    self.color_picker_active = False
                    return
            return

        # Nút Rút Bài
        if self.view.draw_btn_rect.collidepoint(pos):
            self.game_logic.draw_turn()
            return

        # Nút UNO
        if self.view.uno_btn_rect.collidepoint(pos):
            self.game_logic.players[0].yell_uno()
            return
            
        # Click bài trên tay
        # Dùng human_hit_rects: mỗi lá chỉ nhận click ở phần nhìn thấy
        # reversed() để lá nằm trên cùng (phải nhất) ưu tiên
        for i in reversed(range(len(self.view.human_hit_rects))):
            rect = self.view.human_hit_rects[i]
            if rect.collidepoint(pos):
                card = self.game_logic.players[0].hand[i]
                if card.is_match(self.game_logic.get_top_card(), self.game_logic.current_color):
                    if card.color == "black":
                        self.color_picker_active = True
                        self.pending_card_idx = i
                    else:
                        self.game_logic.play_turn(0, i)
                return

    def update(self):
        if self.game_logic and not self.game_logic.game_over:
            # Check empty deck win
            if self.game_logic.check_empty_deck_winner():
                return
                
            # Đợi bot đánh (1.5 giây độ trễ)
            if self.game_logic.current_turn == 1:
                if time.time() - self.last_bot_move_time > 1.5:
                    self.last_bot_move_time = time.time()
                    bot = self.game_logic.players[1]
                    card_idx, picked_color = bot.decide_move(self.game_logic.get_top_card(), self.game_logic.current_color)
                    
                    if card_idx is not None:
                        self.game_logic.play_turn(1, card_idx, picked_color)
                    else:
                        self.game_logic.draw_turn()

    def draw(self, mouse_pos):
        if not self.view.screen: # Init safe passing
            self.view.screen = self.get_screen()
            
        if self.game_logic.game_over:
            self.view.draw_winner(self.game_logic.winner.name)
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
        self.main_controller.game_state = "PLAYING"
    
    def handle_click(self, pos, diff_buttons):
        for key, btn in diff_buttons.items():
            if btn.rect.collidepoint(pos):
                if key == 'BACK':
                    self.main_controller.game_state = "MENU"
                elif key in ['EASY', 'NORMAL', 'HARD']:
                    self.main_controller.game_state = "PLAYING"
                    return key
                return "HANDLED"
        return None
