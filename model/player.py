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

    def decide_move(self, game_state):
        # Override ở các loại Bot khác nhau
        raise NotImplementedError("This method should be overridden.")
