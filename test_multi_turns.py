import pygame
import time
pygame.display.init()
pygame.display.set_mode((1000, 700))
from Controller.app_manager import AppManager

class DummyScreen:
    def __init__(self):
        self.surface = pygame.display.get_surface()
    def blit(self, *args, **kwargs):
        pass

app = AppManager(DummyScreen())
app.controller.game_state = "MULTI_SELECT"
app.multi_player_ctr.view.screen = app.screen
app.multi_player_ctr.start_game("P4")

gl = app.multi_player_ctr.game_logic
print("--- TEST MULTIPLAYER TURN PROGRESSION ---")

for i in range(15):
    print(f"Current Turn: {gl.current_turn} (Direction {gl.direction})")
    
    if gl.current_turn == 0:
        # Human simulates a regular play
        playable = False
        for idx, card in enumerate(gl.players[0].hand):
            if card.is_match(gl.get_top_card(), gl.current_color):
                print(f"Human (0) plays {card.color}_{card.value}")
                gl.play_turn(0, idx)
                playable = True
                break
        if not playable:
            print("Human (0) draws")
            gl.draw_turn()
            
    else:
        # Bot's turn
        app.multi_player_ctr.last_move_time = 0 # Force wait bypass
        app.multi_player_ctr.update()

