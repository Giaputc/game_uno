from model.deck import Deck
import random

class GameLogic:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.discard_pile = []
        self.current_color = None
        self.direction = 1 # 1: xuôi kim đồng hồ, -1: ngược
        self.current_turn = 0
        self.game_over = False
        self.winner = None
        self.draw_penalty = 0

        # Rút 7 lá cho mỗi người
        for player in self.players:
            player.draw_n(self.deck, 7)

        # Rút lá bài đầ tiên
        top_card = self.deck.draw()
        # Đảm bảo bài đầu tiên không phải chức năng để dễ chơi (tuỳ quy tắc, nhưng nên làm vậy)
        while top_card.color == "black" or top_card.value in ["skip", "reverse", "+2"]:
            self.deck.cards.insert(0, top_card)
            top_card = self.deck.draw()
            
        self.discard_pile.append(top_card)
        self.current_color = top_card.color

    def get_top_card(self):
        return self.discard_pile[-1]

    def next_turn(self):
        self.current_turn = (self.current_turn + self.direction) % len(self.players)

    def draw_cards_for_current(self, amount):
        player = self.players[self.current_turn]
        for _ in range(amount):
            if len(self.deck.cards) == 0:
                if len(self.discard_pile) > 1:
                    self.deck.recycle(self.discard_pile)
                else:
                    break # Hết bài để rút thật rồi
            player.draw_card(self.deck)

    def play_turn(self, player_index, card_index, chosen_color=None):
        if player_index != self.current_turn:
            return False # Không phải lượt
            
        player = self.players[player_index]
        card = player.hand[card_index]

        if card.is_match(self.get_top_card(), self.current_color):
            # Lấy bài khỏi tay
            player.play_card(card_index)
            self.discard_pile.append(card)
            
            # Cập nhật màu hiện tại
            if card.color == "black":
                self.current_color = chosen_color if chosen_color else random.choice(["red", "blue", "green", "yellow"])
            else:
                self.current_color = card.color

            # Áp dụng chức năng bài
            if card.value == "skip":
                self.next_turn()
            elif card.value == "reverse":
                self.direction *= -1
                if len(self.players) == 2:
                    self.next_turn() # 2 người thì reverse = skip
            elif card.value == "+2":
                self.next_turn()
                self.draw_cards_for_current(2)
            elif card.value == "+4":
                self.next_turn()
                self.draw_cards_for_current(4)

            # Phạt bài nếu quên hô UNO (lá kế cuối)
            if len(player.hand) == 1 and not player.said_uno:
                self.draw_cards_for_current(0) # Logic để tự phạt nếu quy luật khắt khe, nhưng trong code player là hiện tại
                # Wait: người current vừa đánh. Vậy là player hiện tại bị phạt. 
                # Chú ý: Ta nên phạt chính player đang đánh (lúc này current_turn đã bị next nếu dính skip/reverse/draw)
                # Sẽ sửa lại bằng cách phạt trực tiếp player list
                for _ in range(2):
                    if len(self.deck.cards) == 0:
                        self.deck.recycle(self.discard_pile)
                    card = self.deck.draw()
                    if card: player.hand.append(card)
            
            player.reset_uno_status()

            # Kiểm tra game over (nếu vừa đánh lá cuối cùng dù có bị phạt đi nữa cũng không tính vì đã check == 1 ở trên)
            # Dựa theo yêu cầu "nếu phạt thì đánh tiếp":
            if len(player.hand) == 0:
                self.game_over = True
                self.winner = player

            # Chuyển lượt
            if not self.game_over:
                self.next_turn()
            return True
        return False

    def draw_turn(self):
        # Trọng tài bắt người chơi rút 1 lá 
        self.draw_cards_for_current(1)
        # Rút xong sẽ chuyển lượt hoặc có cho đánh tiếp? Luật phổ biến UNO: nếu lá đó đánh được thì có thể đánh.
        # Ở đay đơn giản hóa: Rút xong mất lượt
        self.players[self.current_turn].reset_uno_status()
        self.next_turn()

    def check_empty_deck_winner(self):
        # Khi không còn bài rút (deck rỗng và discard pile rỗng)
        if len(self.deck.cards) == 0 and len(self.discard_pile) <= 1:
            winner = min(self.players, key=lambda p: len(p.hand))
            self.game_over = True
            self.winner = winner
            return True
        return False
