import pygame
pygame.display.init()
pygame.display.set_mode((800,600))
from settings import WIDTH, HEIGHT
from model.game_logic import GameLogic
from Controller.DonNguoiChoi.single_controller import SinglePlayerController

class DummyController:
    def __init__(self):
        self.screen = pygame.display.get_surface()

c = SinglePlayerController(DummyController())
c.start_game("EASY")
bot = c.game_logic.players[1]
print("Bot hand size:", len(bot.hand))
c.game_logic.current_turn = 1 # Force bot turn
c.last_bot_move_time = 0
c.update()
print("Easy Done")

c.start_game("NORMAL")
c.game_logic.current_turn = 1
c.last_bot_move_time = 0
c.update()
print("Normal Done")

c.start_game("HARD")
c.game_logic.current_turn = 1
c.last_bot_move_time = 0
c.update()
print("Hard Done")
