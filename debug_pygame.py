import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.display.init()
pygame.display.set_mode((1000, 700))
from Controller.app_manager import AppManager

class DummyScreen:
    def __init__(self):
        self.surface = pygame.display.get_surface()
    def blit(self, *args, **kwargs):
        self.surface.blit(*args, **kwargs)

app = AppManager(DummyScreen())
app.controller.game_state = "DIFFICULTY_SELECT"
app.single_player_ctr.view.screen = app.screen
app.single_player_ctr.start_game("EASY")

for i in range(10):
    app.update()
    app.draw()

pygame.image.save(app.screen.surface, "debug_frame.png")
print("Saved debug_frame.png")
