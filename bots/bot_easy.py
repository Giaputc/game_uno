import random
from model.player import Player

class BotEasy(Player):
    def __init__(self, name):
        super().__init__(name, is_human=False)

    def decide_move(self, top_card, current_color):
        valid_moves = self.get_valid_moves(top_card, current_color)
        
        # Ở chế độ Dễ, bot ngẫu nhiên quên hô UNO
        if len(self.hand) == 2 and random.choice([True, False]): 
            self.yell_uno()
            
        if valid_moves:
            # Chọn ngẫu nhiên 1 lá hợp lệ
            choice_idx = random.choice(valid_moves)
            chosen_color = None
            if self.hand[choice_idx].color == "black":
                chosen_color = random.choice(["red", "blue", "green", "yellow"])
            return choice_idx, chosen_color
        
        return None, None # Không có bài thì trả về None để rút
