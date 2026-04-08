import pygame
import sys
from settings import WIDTH, HEIGHT, init_buttons
from model.landing_page import LandingPageGIF
from view.menu_view import MenuView
from view.role_view import RoleView
from view.DonNguoiChoi.difficulty_view import DifficultyView
from Controller.game_controller import GameController
from .DonNguoiChoi.single_controller import SinglePlayerController

class AppManager:
    def __init__(self, screen):
        self.screen = screen
        self.gif_bg = LandingPageGIF("Landing-Page.gif")
        self.controller = GameController()
        
        self.single_player_ctr = SinglePlayerController(self.controller)
        
        self.menu_buttons, self.role_buttons, self.diff_buttons = init_buttons()
        
        self.menu_view = MenuView(screen, WIDTH, HEIGHT)
        self.role_view = RoleView(screen, WIDTH, HEIGHT)
        self.diff_view = DifficultyView(screen, WIDTH, HEIGHT)

    def update(self):
        if self.controller.game_state == "SPLASH":
            self.gif_bg.update()
    def draw(self):
        state = self.controller.game_state
        mouse_pos = pygame.mouse.get_pos()

        if state == "SPLASH":
            self.menu_view.draw_splash(self.gif_bg)
        elif state == "MENU":
            self.menu_view.draw_main_menu(self.menu_buttons.values(), mouse_pos)
        elif state == "GUIDE":
            self.role_view.draw(self.role_buttons.values(), mouse_pos)
        elif state == "DIFFICULTY_SELECT":
            self.diff_view.draw(self.diff_buttons.values(), mouse_pos)

    def handle_mouse_down(self, pos):
        state = self.controller.game_state

        if state == "SPLASH":
            self.controller.game_state = "MENU"
        
        elif state == "MENU":
            action = self.controller.handle_click(pos, self.menu_buttons)
            if action == 'SINGLE':
                self.controller.game_state = "DIFFICULTY_SELECT"
            elif action == 'GUIDE':
                self.controller.game_state = "GUIDE"
            elif action == 'QUIT':
                self.safe_exit()
        
        elif state == "DIFFICULTY_SELECT":
            self.single_player_ctr.handle_click(pos, self.diff_buttons)

        elif state == "GUIDE":
            if self.role_buttons['BACK'].rect.collidepoint(pos):
                self.controller.game_state = "MENU"
            elif self.role_buttons['QUIT_MINI'].rect.collidepoint(pos):
                self.safe_exit()

    def safe_exit(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()