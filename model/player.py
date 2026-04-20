class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.is_human = is_human
        self.hand = []
        self.said_uno = False

    def draw_card(self, deck):
        card = deck.draw()
        if card:
            self.hand.append(card)
        return card

    def draw_n(self, deck, n):
        cards_drawn = []
        for _ in range(n):
            card = self.draw_card(deck)
            if card:
                cards_drawn.append(card)
        return cards_drawn

    def play_card(self, index):
        if 0 <= index < len(self.hand):
            return self.hand.pop(index)
        return None

    def reset_uno_status(self):
        self.said_uno = False
        
    def yell_uno(self):
        self.said_uno = True

    def get_valid_moves(self, top_card, current_color):
        valid = []
        for i, card in enumerate(self.hand):
            if card.is_match(top_card, current_color):
                valid.append(i)
        return valid

    def decide_move(self, *args, **kwargs):
        # Override ở các loại Bot khác nhau
        raise NotImplementedError("This method should be overridden.")


class AIPlayer(Player):
    def __init__(self, name, bot_logic):
        super().__init__(name, is_human=False)
        self.bot_logic = bot_logic

    def decide_move(self, top_card, current_color, next_player_hand_size=5, pending_draw_type=None, **kwargs):
        import random
        from settings import UNO_SHOUT_RATES

        # ── Xử lý Stacking Rule: nếu đang bị cộng dồn, chỉ được đánh cùng loại ──
        if pending_draw_type:
            stack_cards = [c for c in self.hand if str(getattr(c, "value", "")) == pending_draw_type]
            if stack_cards:
                idx = self.hand.index(stack_cards[0])
                return idx, None  # Chồng bài
            else:
                return None, None  # Phải rút

        # ── Tỷ lệ hô UNO theo độ khó ──
        bot_name = getattr(self.bot_logic, "name", "")
        shout_chance = 1.0  # Mặc định Hard
        for key, rate in UNO_SHOUT_RATES.items():
            if key in bot_name:
                shout_chance = rate
                break

        if len(self.hand) == 1:
            if random.random() < shout_chance:
                self.yell_uno()
            # Nếu không vượt qua xác suất: quên hô UNO → bị phạt sau khi đánh

        # ── Uỷ quyền chọn bài cho thuật toán bot ──
        # Truyền thêm all_players_info nếu có (để bot nhắm mục tiêu)
        card = self.bot_logic.choose_action(
            self.hand, top_card, current_color,
            next_player_hand_size=next_player_hand_size,
            all_players_info=kwargs.get("all_players_info")
        )

        if card:
            idx = self.hand.index(card)
            chosen_color = None
            if getattr(card, "color", "") == "black":
                if hasattr(self.bot_logic, "choose_color"):
                    chosen_color = self.bot_logic.choose_color(self.hand)
                else:
                    chosen_color = random.choice(["red", "blue", "green", "yellow"])
            return idx, chosen_color

        return None, None
