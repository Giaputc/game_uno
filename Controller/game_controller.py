# File: Controller/game_controller.py
import pygame
import sys

class GameController:
    def __init__(self):
        self.game_state = "SPLASH"

    def handle_click(self, pos, buttons):
        if self.game_state == "SPLASH":
            self.game_state = "MENU"
            return None
        
        if self.game_state == "MENU":
            for key, btn in buttons.items():
                if btn.rect.collidepoint(pos):
                    return key 
        return None

    def safe_exit(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()