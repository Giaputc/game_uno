import random
import os
import pygame
from .card import Card
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent
IMG_DIR = os.path.join(BASE_PATH, 'data', 'images')

class Deck:
    def __init__(self):
        self.cards = []
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

    def draw(self):
        if not self.cards:
            self.restock_from_discard()
        if self.cards:
            card = self.cards.pop()
            card.curr_x = None
            card.curr_y = None
            return card
        return None

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
            self.shuffle()
            print("Đã xào lại úp bài từ xấp bài đánh.")

    def recycle(self, game_discard_pile):
        if len(game_discard_pile) > 1:
            top = game_discard_pile.pop()
            self.cards = game_discard_pile[:] # copy
            game_discard_pile.clear()
            game_discard_pile.append(top)
            self.shuffle()
            print("Đã tái chế xấp bài đánh thành bộ bài rút.")

    # Ảnh mặt úp để vẽ xấp bài rút
    def get_back_image(self):
        path = os.path.join(IMG_DIR, "back.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (80, 120))
        return None
