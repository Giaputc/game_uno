from .deck import Deck
from bots.easy_bot import EasyBot
from bots.normal_bot import NormalBot
from bots.hard_bot import HardBot
import random

class UnoGame:
    def __init__(self, difficulty="EASY"):
        self.deck = Deck()
        self.player_hand = self.deck.draw(7)
        self.bot_hand = self.deck.draw(7)
        
        # Khởi tạo thuật toán bot
        if difficulty == "EASY":
            self.bot = EasyBot("Bot (Dễ)")
        elif difficulty == "NORMAL":
            self.bot = NormalBot("Bot (Thường)")
        elif difficulty == "HARD":
            self.bot = HardBot("Bot (Khó)")
        else:
            self.bot = EasyBot("Bot")

        self.difficulty = difficulty

        # Lấy lá bài đầu tiên
        first_card = self.deck.draw(1)[0]
        while first_card.color == "black" or first_card.value in ["+2", "skip", "reverse", "+4", "wild"]:
            # Rút lại nếu lá đầu là lá đặc biệt (luật dễ)
            self.deck.discard(first_card)
            first_card = self.deck.draw(1)[0]
            
        self.deck.discard(first_card)
        self.current_color = first_card.color
        
        self.current_turn = "PLAYER" # hoặc "BOT"
        self.winner = None
        self.uno_called = {"PLAYER": False, "BOT": False}
        self.player_has_drawn = False
        self.messsage = f"Trò chơi bắt đầu! (Độ khó: {difficulty})"

    def is_valid_move(self, card, hand):
        top_card = self.deck.get_top_card()
        
        # Thẻ bài màu đen (Wild, +4) cho phép đánh bất chấp trạng thái
        if getattr(card, "color", "") == "black":
            return True
            
        if getattr(card, "color", "") == self.current_color:
            return True
        if hasattr(card, "value") and hasattr(top_card, "value") and card.value == top_card.value:
            return True
        return False

    def play_turn(self, card_index=None, selected_color=None):
        if self.winner: return

        if self.current_turn == "PLAYER":
            if card_index is not None:
                card = self.player_hand[card_index]
                if self.is_valid_move(card, self.player_hand):
                    self.player_hand.pop(card_index)
                    self.process_played_card(card, selected_color, "PLAYER")
                else:
                    self.messsage = "Lá bài không hợp lệ!"
        elif self.current_turn == "BOT":
            top_card = self.deck.get_top_card()
            # Bot gọi hành động
            all_players_info = [len(self.player_hand), len(self.bot_hand)]
            card_to_play = self.bot.choose_action(
                self.bot_hand, 
                top_card, 
                self.current_color, 
                next_player_hand_size=len(self.player_hand),
                all_players_info=all_players_info
            )
            if card_to_play:
                self.bot_hand.remove(card_to_play)
                
                # Logic chọn màu cho lá black
                bot_color = None
                if card_to_play.color == "black":
                    bot_color = self.bot.choose_color(self.bot_hand) if hasattr(self.bot, 'choose_color') else random.choice(["red", "blue", "green", "yellow"])
                
                self.process_played_card(card_to_play, bot_color, "BOT")
            else:
                # Bot rút bài
                drawn = self.deck.draw(1)
                if drawn: self.bot_hand.extend(drawn)
                self.messsage = f"{self.bot.name} rút 1 lá."
                self.switch_turn()

    def process_played_card(self, card, selected_color, player):
        self.deck.discard(card)
        
        # Cập nhật trí nhớ cho bot (nếu có hỗ trợ)
        if hasattr(self.bot, "update_knowledge_discard"):
            self.bot.update_knowledge_discard(card)
        
        
        if card.color == "black":
            self.current_color = selected_color if selected_color else "red"
        else:
            self.current_color = card.color

        msg = f"{'Bạn' if player == 'PLAYER' else self.bot.name} đánh {card.color} {card.value}."
        if card.color == "black":
            msg += f" Đổi màu thành: {self.current_color}."
        self.messsage = msg

        # Kiểm tra thắng
        if player == "PLAYER" and len(self.player_hand) == 0:
            self.winner = "PLAYER"
            self.messsage = "Bạn đã thắng!"
            return
        elif player == "BOT" and len(self.bot_hand) == 0:
            self.winner = "BOT"
            self.messsage = f"{self.bot.name} đã thắng!"
            return

        # Gọi UNO
        if len(self.player_hand) == 1 and not self.uno_called["PLAYER"] and player == "PLAYER":
            # Phạt quên hô UNO
            self.player_hand.extend(self.deck.draw(2))
            self.messsage += " Quên hô UNO! Phạt rút 2 lá."
        
        if len(self.bot_hand) == 1 and player == "BOT":
            self.uno_called["BOT"] = True # Bot mặc định tự hô
            self.messsage += " Bot hô UNO!"

        # Chức năng đặc biệt
        val = str(card.value)
        next_turn = "BOT" if player == "PLAYER" else "PLAYER"
        
        if val == "skip" or val == "reverse":
            self.messsage += " Mất lượt!"
            # Vẫn giữ nguyên lượt của player đánh (vì chỉ có 2 người)
        elif val == "+2":
            target_hand = self.bot_hand if next_turn == "BOT" else self.player_hand
            target_hand.extend(self.deck.draw(2))
            self.messsage += f" {next_turn} rút 2 lá và mất lượt!"
        elif val == "+4":
            target_hand = self.bot_hand if next_turn == "BOT" else self.player_hand
            target_hand.extend(self.deck.draw(4))
            self.messsage += f" {next_turn} rút 4 lá và mất lượt!"
        else:
            self.switch_turn()

    def end_turn(self):
        self.switch_turn()

    def switch_turn(self):
        self.current_turn = "BOT" if self.current_turn == "PLAYER" else "PLAYER"
        self.uno_called[self.current_turn] = False
        self.player_has_drawn = False

    def draw_card(self):
        if self.current_turn == "PLAYER" and not self.player_has_drawn:
            drawn = self.deck.draw(1)
            if drawn: 
                self.player_hand.extend(drawn)
                self.messsage = "Bạn rút 1 lá. Đánh luôn hoặc Bỏ qua."
                self.player_has_drawn = True
                
                # Báo cho bot biết bạn có thể đang thiếu màu hiện tại
                if hasattr(self.bot, "update_knowledge_draw"):
                    self.bot.update_knowledge_draw("PLAYER", self.current_color)
