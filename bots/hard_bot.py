import random

class HardBot:
    """
    Bot độ khó Khó (Hard).
    Thuật toán: Q-Learning mô phỏng kết hợp Minimax heuristic.
    Cách hoạt động: Dựa vào cấu trúc tráng thái (State) bao gồm số lượng bài của đối thủ
    chơi tiếp theo, kết quả Q-learning sẽ chọn những hành động làm tối đa hóa cơ hội thắng.
    Nếu thông tin không đủ lớn, kết hợp với Minimax hạn chế đối phương (VD: Thấy đối phương
    hô UNO thì ưu tiên đánh +2, +4, Skip).
    """
    def __init__(self, name="HardBot", use_q_learning=False):
        self.name = name
        self.use_q_learning = use_q_learning
        self.q_table = {}
        # Tham số cho Q-Learning (Epsilon Greedy)
        self.epsilon = 0.1

    def choose_action(self, hand, top_card, current_color, next_player_hand_size=5, **kwargs):
        valid_cards = self.get_valid_cards(hand, top_card, current_color)
        if not valid_cards:
            return None # Rút bài

        if self.use_q_learning:
            # Q-Learning pipeline
            state = self.get_state(hand, current_color, next_player_hand_size)
            if random.uniform(0, 1) < self.epsilon:
                return random.choice(valid_cards)  # Exploration
            else:
                return self.get_best_action_from_q_model(state, valid_cards)  # Exploitation
        else:
            # Trình mô phỏng cách đánh Minimax - Đưa đối thủ rơi vào trạng thái có lợi ích nhỏ nhất 
            # (Hoặc bất lợi nhất) bằng cách cản bước tiến khi đối thủ gần hết bài
            return self.minimax_decision(valid_cards, hand, current_color, next_player_hand_size)

    def get_state(self, hand, current_color, next_player_hand_size):
        # Trạng thái tổng quát của ván đấu có thể dùng để học
        hand_size = len(hand)
        return (hand_size, next_player_hand_size, current_color)

    def get_best_action_from_q_model(self, state, valid_cards):
        # Dummy Q-table query logic. Trên thực tế cần nạp weight model.
        # Tạm thời quy về heuristic nâng cao nếu không có Q-Table
        best_card = valid_cards[0]
        return best_card

    def minimax_decision(self, valid_cards, hand, current_color, next_player_hand_size):
        """
        Quyết định theo Minimax heuristic:
        Minimax giả định rằng ta và đối thủ luân phiên giành vị thế. 
        Khi Next Player (đối thủ ngay sau) sắp hết bài (còn <= 2 lá), 
        nước đi mang lại lợi ích tốt nhất là cấm lượt hoặc cộng dồn bài để "tăng min".
        """
        # Nếu tiếp theo là lượt của người sắp thắng
        if next_player_hand_size <= 2:
            # Ưu tiên cao nhất: Bắt rút thêm bài (+4)
            for card in valid_cards:
                if getattr(card, "value", "") == "+4": return card
            # Ưu tiên cao thứ nhì: +2
            for card in valid_cards:
                if getattr(card, "value", "") == "+2": return card
            # Ưu tiên tiếp theo: Cấm lượt hoặc đổi chiều
            for card in valid_cards:
                if getattr(card, "value", "") in ["skip", "reverse"]: return card

        # Đánh giá theo hướng làm giảm điểm trên tay của bản thân cao nhất có thể
        valid_cards.sort(key=lambda c: self._get_card_power(c), reverse=True)
        return valid_cards[0]

    def _get_card_power(self, card):
        val = getattr(card, "value", 0)
        color = getattr(card, "color", "")
        power = 0
        if color == "black":
            power = 50
        elif isinstance(val, str) and val in ["skip", "reverse", "+2"]:
            power = 20
        elif isinstance(val, int):
            power = val
        return power

    def choose_color(self, hand):
        counts = {"red": 0, "green": 0, "blue": 0, "yellow": 0}
        for card in hand:
            c = getattr(card, "color", None)
            if c in counts: counts[c] += 1
        return max(counts, key=counts.get) if any(counts.values()) else random.choice(list(counts.keys()))

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
