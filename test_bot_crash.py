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

# Force draw until deck is empty
gl = app.single_player_ctr.game_logic
print(f"Deck count: {len(gl.deck.cards)}")
for i in range(120):
    gl.discard_pile.append(gl.deck.draw())

print(f"Deck count after exhaustion: {len(gl.deck.cards)}")
print(f"Discard pile: {len(gl.discard_pile)}")

gl.draw_cards_for_current(2)
print("No crash!")
print(f"Deck count after recycle: {len(gl.deck.cards)}")

