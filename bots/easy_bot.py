import random

class EasyBot:
    """
    Bot độ khó Dễ (Easy).
    Thuật toán: Random (Ngẫu nhiên).
    Cách hoạt động: Trong số các lá bài hợp lệ có thể chơi, bot sẽ chọn ngẫu nhiên một lá bất kỳ.
    Nếu không có lá nào hợp lệ, bot bắt buộc phải rút bài.
    """
    def __init__(self, name="EasyBot"):
        self.name = name

    def choose_action(self, hand, top_card, current_color, **kwargs):
        """
        Chọn lá bài để đánh.
        :param hand: Danh sách các lá bài trên tay bot
        :param top_card: Lá bài nằm trên cùng của xấp bỏ
        :param current_color: Màu sắc hiện tại của ván bài
        :param kwargs: Các tham số tuỳ chọn khác
        :return: Lá bài được chọn để đánh hoặc None nếu phải rút bài
        """
        valid_cards = self.get_valid_cards(hand, top_card, current_color)
        if valid_cards:
            return random.choice(valid_cards)
        return None  # Rút bài

    def choose_color(self, hand):
        """
        Dùng khi bot đánh lá Đổi màu (Wild) hoặc +4 (Wild Draw 4)
        """
        return random.choice(["red", "yellow", "green", "blue"])

    def get_valid_cards(self, hand, top_card, current_color):
        valid_cards = []
        for card in hand:
            if self.is_valid(card, top_card, current_color, hand):
                valid_cards.append(card)
        return valid_cards

    def is_valid(self, card, top_card, current_color, hand):
        if getattr(card, "color", None) == "black":
            return True
        if getattr(card, "color", None) == current_color:
            return True
        if hasattr(card, "value") and hasattr(top_card, "value") and card.value == top_card.value:
            return True
        return False