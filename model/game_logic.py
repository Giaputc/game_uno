from model.deck import Deck
import random


class GameLogic:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.discard_pile = []
        self.current_color = None
        self.direction = 1      # 1: xuôi kim đồng hồ, -1: ngược
        self.current_turn = 0
        self.game_over = False
        self.winner = None
        self.draw_penalty = 0

        # ── Stacking Rule ─────────────────────────────────────────────────────
        self.pending_draw = 0           # Số bài cộng dồn chưa rút
        self.pending_draw_type = None   # "+2" hoặc "+4"

        # Rút 7 lá cho mỗi người
        for player in self.players:
            player.draw_n(self.deck, 7)

        # Rút lá bài đầu tiên (không phải lá chức năng)
        top_card = self.deck.draw()
        while top_card.color == "black" or top_card.value in ["skip", "reverse", "+2"]:
            self.deck.cards.insert(0, top_card)
            top_card = self.deck.draw()

        self.discard_pile.append(top_card)
        self.current_color = top_card.color

    # ── Core helpers ─────────────────────────────────────────────────────────

    def get_top_card(self):
        return self.discard_pile[-1]

    def next_turn(self):
        self.current_turn = (self.current_turn + self.direction) % len(self.players)

    def can_play_card(self, card):
        """Kiểm tra lá bài có thể đánh không, tính đến Stacking Rule."""
        if self.pending_draw > 0:
            # Khi đang cộng dồn, chỉ được đánh cùng loại lá draw để chồng
            return str(getattr(card, "value", "")) == self.pending_draw_type
        return card.is_match(self.get_top_card(), self.current_color)

    def draw_cards_for_current(self, amount):
        player = self.players[self.current_turn]
        for _ in range(amount):
            if len(self.deck.cards) == 0:
                if len(self.discard_pile) > 1:
                    self.deck.recycle(self.discard_pile)
                else:
                    break
            player.draw_card(self.deck)

    # ── Main game actions ─────────────────────────────────────────────────────

    def play_turn(self, player_index, card_index, chosen_color=None):
        if player_index != self.current_turn:
            return False

        player = self.players[player_index]
        card = player.hand[card_index]

        if not self.can_play_card(card):
            return False

        # Lấy bài khỏi tay
        player.play_card(card_index)
        self.discard_pile.append(card)

        # Cập nhật màu hiện tại
        if card.color == "black":
            self.current_color = chosen_color if chosen_color else random.choice(["red", "blue", "green", "yellow"])
        else:
            self.current_color = card.color

        # Thông báo cho HardBots biết bài vừa được đánh
        for p in self.players:
            if hasattr(p, "bot_logic") and hasattr(p.bot_logic, "update_knowledge_discard"):
                p.bot_logic.update_knowledge_discard(card)

        # ── Áp dụng chức năng bài (Stacking-aware) ───────────────────────────
        val = str(card.value)
        skip_final_advance = False

        if val == "skip":
            self.next_turn()    # Qua người bị bỏ lượt
            self.next_turn()    # Đến người tiếp theo
            skip_final_advance = True

        elif val == "reverse":
            self.direction *= -1
            if len(self.players) == 2:
                # 2 người: Reverse = Skip → quay lại người đánh
                self.next_turn()
                self.next_turn()
                skip_final_advance = True
            # Nếu > 2 người: để final next_turn() tự chạy với direction mới

        elif val == "+2":
            # Cộng dồn stacking
            self.pending_draw += 2
            if not self.pending_draw_type:
                self.pending_draw_type = "+2"
            self.next_turn()            # Chuyển đến người bị phạt → họ được quyền phản ứng
            skip_final_advance = True   # KHÔNG advance nữa, giữ lượt của người bị phạt

        elif val == "+4":
            self.pending_draw += 4
            if not self.pending_draw_type:
                self.pending_draw_type = "+4"
            self.next_turn()
            skip_final_advance = True

        else:
            # Lá thường: Reset pending nếu có (an toàn fallback)
            self.pending_draw = 0
            self.pending_draw_type = None

        # ── Phạt quên hô UNO ─────────────────────────────────────────────────
        # Người chơi đánh lá bài kế cuối (từ 2 xuống 1) nhưng chưa hô UNO
        if len(player.hand) == 1 and not player.said_uno:
            for _ in range(2):
                if len(self.deck.cards) == 0:
                    if len(self.discard_pile) > 1:
                        self.deck.recycle(self.discard_pile)
                    else:
                        break
                c = self.deck.draw()
                if c:
                    player.hand.append(c)

        player.reset_uno_status()

        # ── Kiểm tra thắng ───────────────────────────────────────────────────
        if len(player.hand) == 0:
            self.game_over = True
            self.winner = player
            self.win_score = self.calculate_score()

        # ── Chuyển lượt ──────────────────────────────────────────────────────
        if not self.game_over and not skip_final_advance:
            self.next_turn()

        return True

    def draw_turn(self):
        """Người chơi rút bài (chủ động hoặc bị buộc khi bị stacking)."""
        if self.pending_draw > 0:
            # Rút toàn bộ số bài bị cộng dồn
            self.draw_cards_for_current(self.pending_draw)
            self.pending_draw = 0
            self.pending_draw_type = None
        else:
            self.draw_cards_for_current(1)

        # Báo cho HardBot biết ai đó vừa phải rút bài
        for p in self.players:
            if hasattr(p, "bot_logic") and hasattr(p.bot_logic, "update_knowledge_draw"):
                p.bot_logic.update_knowledge_draw(self.current_turn, self.current_color)

        self.players[self.current_turn].reset_uno_status()
        self.next_turn()

    def calculate_score(self):
        """Tính điểm cho người thắng dựa trên bài còn lại của các người chơi khác."""
        score = 0
        if not self.winner:
            return 0
        for p in self.players:
            if p != self.winner:
                for card in p.hand:
                    val = str(getattr(card, "value", ""))
                    if val in ["skip", "reverse", "+2"]:
                        score += 20
                    elif val in ["black", "+4"] or card.color == "black":
                        score += 50
                    elif val.isdigit():
                        score += int(val)
        return score

    def check_empty_deck_winner(self):
        """Khi xấp bài rút và xấp bỏ đều rỗng — người ít bài nhất thắng."""
        if len(self.deck.cards) == 0 and len(self.discard_pile) <= 1:
            winner = min(self.players, key=lambda p: len(p.hand))
            self.game_over = True
            self.winner = winner
            self.win_score = self.calculate_score()
            return True
        return False
