import pygame
from model.uno_game import UnoGame
from view.DonNguoiChoi.play_view import PlayView

class PlayController:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.game = None
        self.view = None
        self.pending_card_idx = None # Dùng lưu index bài chờ chọn màu
        self.bot_wait_start = 0

    def start_game(self, screen, width, height, difficulty):
        self.game = UnoGame(difficulty)
        self.view = PlayView(screen, width, height)

    def update(self):
        if not self.game: return
        
        # Logic đánh tự động của bot với 1 chút delay non-blocking
        if self.game.current_turn == "BOT" and not self.game.winner:
            current_time = pygame.time.get_ticks()
            if self.bot_wait_start == 0:
                self.bot_wait_start = current_time
            elif current_time - self.bot_wait_start > 1000:
                self.game.play_turn()
                self.bot_wait_start = 0

    def draw(self):
        if self.game and self.view:
            mouse_pos = pygame.mouse.get_pos()
            self.view.draw(self.game, mouse_pos)

    def handle_click(self, pos):
        if not self.game or not self.view: return

        # Nút Back luôn cho phép nhấn
        if self.view.btn_back.rect.collidepoint(pos):
            self.main_controller.game_state = "MENU"
            self.game = None
            return

        # Nếu game đã kết thúc, nhấn bất kỳ đâu cũng thoát về Menu
        if self.game.winner:
            self.main_controller.game_state = "MENU"
            self.game = None
            return

        # Chọn màu khi đánh bài đổi màu
        if self.view.show_color_picker:
            for color, rect in self.view.color_rects.items():
                if rect.collidepoint(pos):
                    self.game.play_turn(self.pending_card_idx, selected_color=color)
                    self.view.show_color_picker = False
                    self.pending_card_idx = None
            return

        if self.game.current_turn == "PLAYER":
            # Nút hô UNO
            if self.view.btn_uno.rect.collidepoint(pos):
                if len(self.game.player_hand) <= 2: # Nhấn trước khi đánh lá kế cuối
                    self.game.uno_called["PLAYER"] = True
                    self.game.messsage = "Bạn đã hô UNO!"
                return
            # Nút rút bài hoặc Bỏ qua
            if getattr(self.game, "player_has_drawn", False):
                if self.view.btn_pass.rect.collidepoint(pos):
                    self.game.end_turn()
                    return
            else:
                if self.view.btn_draw.rect.collidepoint(pos):
                    self.game.draw_card()
                    return

            # Click chọn bài trên tay
            player_start_x = self.view.width/2 - (len(self.game.player_hand) * 45) / 2
            for i in range(len(self.game.player_hand) - 1, -1, -1):
                base_y = self.view.height - 150
                is_hovered = getattr(self.game.player_hand[i], 'is_hovered', False)
                render_y = base_y - 10 if is_hovered else base_y
                card_rect = pygame.Rect(player_start_x + i * 45, render_y, 80, 120)
                
                if card_rect.collidepoint(pos):
                    actual_card = self.game.player_hand[i]
                    if self.game.is_valid_move(actual_card, self.game.player_hand):
                        if actual_card.color == "black":
                            self.view.show_color_picker = True
                            self.pending_card_idx = i
                        else:
                            self.game.play_turn(i)
                    else:
                        self.game.messsage = "Lá bài vi phạm luật!"
                    return # Ngăn chặn bắt click qua các lá bị đè bên dưới
