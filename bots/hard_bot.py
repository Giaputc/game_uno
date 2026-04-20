import random

class HardBot:
    """
    Advanced Hard Bot - "The Grandmaster"
    Áp dụng chiến thuật Pro Player: Quản lý Stack, 3-Phase Strategy, và Target Modeling.
    Hỗ trợ tối ưu hóa riêng biệt cho chế độ 1v1 và Multiplayer (1vN).
    """
    def __init__(self, name="Siêu Khó"):
        self.name = name
        self.discarded_history = []
        # drought: màu mà đối thủ KHÔNG có. Dạng {str_id: set(colors)}
        self.player_droughts = {}

    def update_knowledge_discard(self, card):
        """Ghi nhớ lá bài vừa đánh ra (Phục vụ cho Counting sau này)"""
        self.discarded_history.append(card)

    def update_knowledge_draw(self, player_turn_idx, current_color):
        """Ghi nhớ đối thủ vừa phải rút bài vì thiếu màu current_color"""
        p_id = str(player_turn_idx)
        if p_id not in self.player_droughts:
            self.player_droughts[p_id] = set()
        if current_color:
            self.player_droughts[p_id].add(current_color)

    def _get_card_power(self, card):
        """Hệ thống tính điểm chuẩn của UNO (Official Scoring)"""
        val = getattr(card, "value", 0)
        val_str = str(val).lower()
        if val_str in ["wild", "+4", "wildcard"]: 
            return 50
        if val_str in ["+2", "skip", "reverse"]: 
            return 20
        return int(val) if str(val).isdigit() else 0

    def _get_color_counts(self, hand):
        """Đếm số lượng từng màu trên tay"""
        counts = {"red": 0, "green": 0, "blue": 0, "yellow": 0}
        for card in hand:
            c = getattr(card, "color", None)
            if c in counts: 
                counts[c] += 1
        return counts

    def get_valid_cards(self, hand, top_card, current_color):
        """Lọc danh sách bài hợp lệ có thể đánh"""
        return [c for c in hand if self.is_valid(c, top_card, current_color)]

    def is_valid(self, card, top_card, current_color):
        """Kiểm tra luật đánh bài cơ bản"""
        if getattr(card, "color", None) == "black": return True
        if getattr(card, "color", None) == current_color: return True
        if hasattr(card, "value") and hasattr(top_card, "value") and card.value == top_card.value: return True
        return False

    def choose_color(self, hand, next_player_hand_size=5):
        """
        Chọn màu thông minh khi đánh lá Wild / +4
        Ưu tiên: Màu đối thủ sắp thắng KHÔNG có -> Màu Bot có nhiều nhất.
        """
        my_colors = self._get_color_counts(hand)
        
        # Tìm tất cả các màu mà đối thủ kỵ (Droughts)
        all_droughts = set()
        for d in self.player_droughts.values():
            all_droughts.update(d)
            
        # Chọn màu mình có mà đối thủ kỵ
        best_candidates = [c for c in my_colors if my_colors[c] > 0 and c in all_droughts]
        if best_candidates:
            return max(best_candidates, key=lambda c: my_colors[c])
            
        # Nếu không, chọn màu mình có nhiều nhất để dễ xả bài
        if any(my_colors.values()):
            return max(my_colors, key=my_colors.get)
            
        return random.choice(["red", "green", "blue", "yellow"])

    def choose_action(self, hand, top_card, current_color, next_player_hand_size=5, all_players_info=None, **kwargs):
        """
        Bộ não chính của Bot (Decision Tree)
        all_players_info: list chứa số lượng bài của tất cả người chơi [p0, p1, p2, p3]
        """
        valid_cards = self.get_valid_cards(hand, top_card, current_color)
        if not valid_cards: 
            return None # Bắt buộc rút bài

        # ---------------------------------------------------------
        # BƯỚC 1: PHÂN TÍCH TRẠNG THÁI BÀN CHƠI (STATE ANALYSIS)
        # ---------------------------------------------------------
        my_hand_size = len(hand)
        num_opponents = len(all_players_info) - 1 if all_players_info else 1
        is_1v1 = (num_opponents == 1)

        # Xác định mối đe dọa (Kẻ có ít bài nhất)
        if all_players_info:
            opponents_hands = list(all_players_info)
            # Lấy số lượng bài của người ít nhất (đề phòng bot tự lấy chính nó)
            min_opponent_cards = min(opponents_hands)
            if min_opponent_cards == my_hand_size and len(opponents_hands) > 1:
                sorted_hands = sorted(opponents_hands)
                min_opponent_cards = sorted_hands[1]
        else:
            min_opponent_cards = next_player_hand_size

        # Tính Delta (Độ chênh lệch bài để xác định bị Stack)
        delta = my_hand_size - min_opponent_cards

        # ---------------------------------------------------------
        # BƯỚC 2: PHÂN LOẠI VŨ KHÍ (WEAPON CATEGORIZATION)
        # ---------------------------------------------------------
        wild_cards = [c for c in valid_cards if getattr(c, "color", "") == "black"]
        action_cards = [c for c in valid_cards if str(getattr(c, "value", "")) in ["+2", "skip", "reverse"]]
        number_cards = [c for c in valid_cards if c not in wild_cards and c not in action_cards]

        # Sắp xếp bài số theo giá trị (To -> Nhỏ)
        number_cards.sort(key=lambda c: self._get_card_power(c), reverse=True)

        # ---------------------------------------------------------
        # BƯỚC 3: CÂY QUYẾT ĐỊNH CHIẾN THUẬT (DECISION TREE)
        # ---------------------------------------------------------

        # 🔴 ƯU TIÊN 1: PANIC MODE (Sinh tồn tuyệt đối)
        if min_opponent_cards <= 2:
            # 1. Tung vũ khí hạng nặng (+4, Wild) để chặn 100%
            if wild_cards: return wild_cards[0]
            # 2. Tung Action Cards (+2, Skip, Reverse)
            if action_cards: 
                # Trong 1v1, Skip/Reverse là vô giá. Trong 1vN, +2 ưu tiên hơn để ép rút bài.
                action_cards.sort(key=lambda c: 100 if str(getattr(c, "value", "")) == "+2" else 50, reverse=True)
                return action_cards[0]
            # 3. Ép màu (Nếu có thông tin) hoặc đánh số to nhất
            return number_cards[0] if number_cards else valid_cards[0]

        # 🟠 ƯU TIÊN 2: CATCH-UP MODE (Bị Stack nặng, Delta >= 3)
        if delta >= 3:
            # Bị bỏ lại phía sau -> Ưu tiên xả điểm rủi ro và phá nhịp độ
            if action_cards: return action_cards[0]
            if wild_cards: return wild_cards[0] # Chấp nhận xả Wild để đổi màu xả rác
            if number_cards: return number_cards[0]

        # 🟢 ƯU TIÊN 3: CHIẾN THUẬT 3 PHASE (Nhịp độ bình thường)
        
        # --- PHASE 3: DỨT ĐIỂM (Bot còn <= 2 lá) ---
        if my_hand_size <= 2:
            # Tung đòn kết liễu: Khóa mõm bằng Action hoặc chốt bằng Wild
            if is_1v1 and action_cards: return action_cards[0]
            if wild_cards: return wild_cards[0]
            if action_cards: return action_cards[0]
            return number_cards[0] if number_cards else valid_cards[0]

        # --- PHASE 2: SETUP/LÊN ĐẠN (Bot còn 3 - 4 lá) ---
        if 3 <= my_hand_size <= 4:
            # Mục tiêu: Găm bài chức năng, xả nốt bài số.
            if number_cards: return number_cards[0]
            # Nếu hết bài số, buộc phải dùng Action, giữ Wild lại cuối cùng
            if action_cards: return action_cards[0]
            return wild_cards[0] if wild_cards else valid_cards[0]

        # --- PHASE 1: DỌN RÁC & ĐỊNH HÌNH MÀU (Bot còn >= 5 lá) ---
        if my_hand_size >= 5:
            # 1. Action Cards: Không xả bừa, trừ khi là +2 để rỉa máu nhẹ, giữ Skip/Reverse lại.
            # (Được hiệu chỉnh cho mượt hơn so với Catch-up mode)
            if action_cards and random.random() < 0.4: # 40% cơ hội đánh Action để giữ Tempo
                return action_cards[0]

            # 2. Xả bài số to nhất để giảm rủi ro điểm số
            if number_cards:
                # Kỹ thuật bẻ màu (Color Unlocking): 
                # Đánh lá số có màu mà Bot đang sở hữu nhiều nhất.
                color_counts = self._get_color_counts(hand)
                number_cards.sort(key=lambda c: color_counts.get(getattr(c, "color", ""), 0), reverse=True)
                return number_cards[0]

            # 3. Nếu kẹt (chỉ đánh được Wild/+4): Chấp nhận bẻ màu
            if wild_cards:
                return wild_cards[0]

        # Fallback an toàn (không bao giờ xảy ra nếu logic trên bao phủ hết)
        return random.choice(valid_cards)