import random

class EasyBot:
    """
    Bot độ khó Dễ (Easy).
    Thuật toán: Random (Ngẫu nhiên).
    Cách hoạt động: Trong số các lá bài hợp lệ có thể chơi, bot sẽ chọn ngẫu nhiên một lá bất kỳ.
    Nếu không có lá nào hợp lệ, bot bắt buộc phải rút bài.
    """
    def __init__(self, name="Dễ"):
        self.name = name

    def choose_action(self, hand, top_card, current_color, **kwargs):
        """
        Chọn lá bài để đánh.
        """
        valid_cards = self.get_valid_cards(hand, top_card, current_color)
        if valid_cards:
            return random.choice(valid_cards)
        return None  # Rút bài

    def choose_color(self):
        """
        Dùng khi bot đánh lá Đổi màu (Wild) hoặc +4 (Wild Draw 4)
        """
        return random.choice(["red", "yellow", "green", "blue"])

    def get_valid_cards(self, hand, top_card, current_color):
        return [c for c in hand if self.is_valid(c, top_card, current_color)]

    def is_valid(self, card, top_card, current_color):
        if getattr(card, "color", None) == "black": return True
        if getattr(card, "color", None) == current_color: return True
        if hasattr(card, "value") and hasattr(top_card, "value") and card.value == top_card.value: return True
        return False