import random
from model.card import Card

class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        self.shuffle()
        
    def build(self):
        self.cards = []
        colors = ["red", "green", "blue", "yellow"]
        
        for color in colors:
            # 0
            self.cards.append(Card(color, "0", f"{color}_0.png"))
            
            # 1-9 (2 copies each)
            for val in range(1, 10):
                self.cards.append(Card(color, str(val), f"{color}_{val}.png"))
                self.cards.append(Card(color, str(val), f"{color}_{val}.png"))
                
            # Action cards (+2, skip, reverse) (2 copies each)
            self.cards.append(Card(color, "skip", f"{color}_skip.png"))
            self.cards.append(Card(color, "skip", f"{color}_skip.png"))
            self.cards.append(Card(color, "reverse", f"{color}_reverse.png"))
            self.cards.append(Card(color, "reverse", f"{color}_reverse.png"))
            self.cards.append(Card(color, "+2", f"{color}_+2.png"))
            self.cards.append(Card(color, "+2", f"{color}_+2.png"))
            
        # Wild cards (+4, wildcard) (4 copies each)
        for _ in range(4):
            self.cards.append(Card("black", "wildcard", "black_wildcard.png"))
            self.cards.append(Card("black", "+4", "black_+4.png"))
            
    def shuffle(self):
        random.shuffle(self.cards)
        
    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None
        
    def recycle(self, discard_pile):
        # Giữ lại lá bài trên cùng
        top_card = discard_pile.pop()
        
        # Những lá bài còn lại dùng để xáo bài
        self.cards.extend(discard_pile)
        discard_pile.clear()
        discard_pile.append(top_card)
        self.shuffle()
