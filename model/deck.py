import random
<<<<<<< HEAD
from model.card import Card
=======
import os
import pygame
from .card import Card
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent
IMG_DIR = os.path.join(BASE_PATH, 'data', 'images')
>>>>>>> wicky

class Deck:
    def __init__(self):
        self.cards = []
<<<<<<< HEAD
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
=======
        self.discard_pile = []
        self.build()

    def build(self):
        colors = ["red", "green", "blue", "yellow"]
        values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "skip", "reverse", "+2"]
        
        self.cards = []
        for color in colors:
            for value in values:
                img_name = f"{color}_{value}.png"
                self.cards.append(Card(color, value, img_name))
                # 1 đến 9, skip, reverse, +2 có 2 lá mỗi màu
                if value != "0":
                    self.cards.append(Card(color, value, img_name))
        
        # 4 lá Wild, 4 lá Wild Draw 4
        for i in range(4):
            self.cards.append(Card("black", "wild", "black_wildcard.png"))
            self.cards.append(Card("black", "+4", "black_+4.png"))
        
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count=1):
        drawn = []
        for _ in range(count):
            if not self.cards:
                self.restock_from_discard()
            if self.cards:
                drawn.append(self.cards.pop())
        return drawn

    def discard(self, card):
        self.discard_pile.append(card)

    def get_top_card(self):
        if self.discard_pile:
            return self.discard_pile[-1]
        return None

    def restock_from_discard(self):
        if len(self.discard_pile) > 1:
            # Giữ lại lá trên cùng
            top = self.discard_pile.pop()
            self.cards = self.discard_pile
            self.discard_pile = [top]
            self.shuffle()
            print("Đã xào lại úp bài từ xấp bài đánh.")

    # Ảnh mặt úp để vẽ xấp bài rút
    def get_back_image(self):
        path = os.path.join(IMG_DIR, "back.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (80, 120))
        return None
>>>>>>> wicky
