import pygame

class SinglePlayerController:
    def __init__(self, main_controller):
        self.main_controller = main_controller # Giữ liên kết với controller chính để đổi state
        self.difficulty = None
        
    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.main_controller.game_state = "PLAYING"
    
    def handle_click(self, pos, diff_buttons):
        for key, btn in diff_buttons.items():
            if btn.rect.collidepoint(pos):
                if key == 'BACK':
                    self.main_controller.game_state = "MENU"
                elif key in ['EASY', 'NORMAL', 'HARD']:
                    self.start_game(key)
                return True
        return False