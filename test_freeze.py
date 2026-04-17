import pygame
pygame.display.init()
pygame.display.set_mode((800,600))
from Controller.app_manager import AppManager

class DummyScreen:
    def __init__(self):
        self.surface = pygame.display.get_surface()

try:
    print("Initializing AppManager")
    app = AppManager(DummyScreen())

    print("Setting state")
    app.controller.game_state = "DIFFICULTY_SELECT"

    print("Starting single player EASY")
    app.single_player_ctr.start_game("EASY")

    print("Running updates")
    for i in range(100):
        app.update()
        
    print("Testing draw")
    app.draw()
        
    print("It did not freeze!")
except Exception as e:
    import traceback
    traceback.print_exc()

