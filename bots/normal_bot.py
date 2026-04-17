import random

class NormalBot:
    """
    Bot độ khó Thường (Normal).
    Thuật toán: Heuristic kết hợp Genetic Algorithm.
    Cách hoạt động: Dùng một tập hợp các trọng số (weights) để đánh giá điểm của từng lá bài
    hợp lệ. Sau đó chọn lá bài có điểm cao nhất. Trọng số này có thể được huấn luyện bằng 
    các thuật toán tối ưu tiến hóa (Genetic Algorithm) trong quá trình huấn luyện offline.
    """
    def __init__(self, name="NormalBot", weights=None):
        self.name = name
        # Các trọng số (nhiễm sắc thể trong Genetic Algorithm) 
        # Có thể được tinh chỉnh bằng Genetic Algorithm
        self.weights = weights if weights else {
            "card_value": 1.0,      # Trọng số khuyến khích đánh bài số lớn để giảm điểm rủi ro
            "color_match": 1.5,     # Khuyến khích đánh màu đang có nhiều trên tay
            "keep_wild": -2.0,      # Trọng số âm để giữ lá bài đen khi chưa cần thiết
            "action_card": 1.2      # Ưu tiên đánh bài chức năng (cấm lượt, +2, đổi chiều) để khống chế đối thủ
        }

    def choose_action(self, hand, top_card, current_color, **kwargs):
        valid_cards = self.get_valid_cards(hand, top_card, current_color)
        if not valid_cards:
            return None # Rút bài
        
        best_card = None
        best_score = float('-inf')
        color_counts = self.get_color_counts(hand)

        for card in valid_cards:
            score = self.evaluate_card(card, color_counts)
            if score > best_score:
                best_score = score
                best_card = card

        return best_card

    def evaluate_card(self, card, color_counts):
        score = 0
        
        # Đặc tính màu sắc - uu tiên đánh màu mà mình có nhiều nhất (Heuristic)
        color = getattr(card, "color", "")
        if color in color_counts:
            score += color_counts[color] * self.weights["color_match"]

        # Đặc tính lá bài Wild (đen)
        if color == "black":
            score += self.weights["keep_wild"]
            
        # Đặc tính bài hành động (+2, skip, reverse)
        val = getattr(card, "value", "")
        if isinstance(val, str) and val in ["+2", "skip", "reverse"]:
            score += self.weights["action_card"]

        # Ưu tiên xả điểm cao
        if isinstance(val, int):
            score += val * self.weights["card_value"]

        return score

    def choose_color(self, hand):
        """
        Khi đánh lá đổi màu, chọn màu mà bot đang giữ nhiều nhất
        """
        color_counts = self.get_color_counts(hand)
        # Loại trừ black
        if "black" in color_counts:
            del color_counts["black"]
        if color_counts:
            return max(color_counts, key=color_counts.get)
        return random.choice(["red", "yellow", "green", "blue"])

    def get_color_counts(self, hand):
        counts = {"red": 0, "green": 0, "blue": 0, "yellow": 0, "black": 0}
        for card in hand:
            c = getattr(card, "color", None)
            if c in counts:
                counts[c] += 1
        return counts

    def get_valid_cards(self, hand, top_card, current_color):
        return [c for c in hand if self.is_valid(c, top_card, current_color, hand)]

    def is_valid(self, card, top_card, current_color, hand):
        if getattr(card, "color", None) == "black":
            return True
        if getattr(card, "color", None) == current_color:
            return True
        if hasattr(card, "value") and hasattr(top_card, "value") and card.value == top_card.value:
            return True
        return False
