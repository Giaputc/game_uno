import random
from model.player import Player

class BotNormal(Player):
    def __init__(self, name):
        super().__init__(name, is_human=False)

    def decide_move(self, top_card, current_color):
        valid_moves = self.get_valid_moves(top_card, current_color)
        
        # Bot Normal tỉ lệ quên hô UNO cực thấp (chỉ ~10%)
        if len(self.hand) == 2 and random.random() > 0.1: 
            self.yell_uno()
            
        if valid_moves:
            # Thuật toán: Ưu tiên giữ lại bài "black" (++4/wild), đánh lôi thẻ bình thường cùng màu
            normal_moves = [i for i in valid_moves if self.hand[i].color != "black"]
            if normal_moves:
                choice_idx = random.choice(normal_moves)
                return choice_idx, None
            else:
                # Bắt buộc đánh black
                choice_idx = random.choice(valid_moves)
                # Thông minh hơn chút: Chọn màu mình đang có nhiều nhất trên tay
                color_counts = {"red": 0, "green": 0, "blue": 0, "yellow": 0}
                for card in self.hand:
                    if card.color in color_counts:
                        color_counts[card.color] += 1
                best_color = max(color_counts, key=color_counts.get)
                # Nếu không có màu (chỉ toàn đen) 
                if color_counts[best_color] == 0:
                    best_color = random.choice(list(color_counts.keys()))
                
                return choice_idx, best_color
                
        return None, None
