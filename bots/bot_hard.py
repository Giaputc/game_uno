import random
from model.player import Player

class BotHard(Player):
    def __init__(self, name):
        super().__init__(name, is_human=False)

    def decide_move(self, top_card, current_color):
        valid_moves = self.get_valid_moves(top_card, current_color)
        
        # Bot Hard 100% hô UNO
        if len(self.hand) == 2:
            self.yell_uno()
            
        if valid_moves:
            # 1. Tìm màu phổ biến nhất trên tay để ưu tiên
            color_counts = {"red": 0, "green": 0, "blue": 0, "yellow": 0}
            for card in self.hand:
                if card.color in color_counts:
                    color_counts[card.color] += 1
            best_color = max(color_counts, key=color_counts.get)
            if color_counts[best_color] == 0:
                best_color = random.choice(list(color_counts.keys()))

            # 2. Phân loại bài đánh được
            normal_moves = [i for i in valid_moves if self.hand[i].color != "black" and self.hand[i].value not in ["+2", "skip", "reverse"]]
            action_moves = [i for i in valid_moves if self.hand[i].value in ["+2", "skip", "reverse"]]
            black_moves = [i for i in valid_moves if self.hand[i].color == "black"]

            # Ưu tiên đánh action moves (phạt, skip, reverse) nếu có để ép đối thủ, hoặc chọn màu best_color
            if action_moves:
                # Nếu có action trùng màu best_color thì đánh, không thì đánh đại action
                best_actions = [i for i in action_moves if self.hand[i].color == best_color]
                if best_actions:
                    return best_actions[0], None
                return action_moves[0], None
                
            if normal_moves:
                best_normals = [i for i in normal_moves if self.hand[i].color == best_color]
                if best_normals:
                    return best_normals[0], None
                return normal_moves[0], None

            if black_moves:
                # Ép dùng +4 nếu có, nếu không thì wildcard
                plus4 = [i for i in black_moves if self.hand[i].value == "+4"]
                if plus4:
                    return plus4[0], best_color
                return black_moves[0], best_color
                
        return None, None
