import pygame
import sys
from settings import WIDTH, HEIGHT, init_buttons
from model.landing_page import LandingPageGIF
from view.menu_view import MenuView
from view.role_view import RoleView
from view.DonNguoiChoi.difficulty_view import DifficultyView
from view.DaNguoiChoi.multi_select_view import MultiSelectView
from Controller.game_controller import GameController
from Controller.DonNguoiChoi.single_controller import SinglePlayerController
from Controller.DaNguoiChoi.multi_controller import MultiPlayerController
import view.sfx_manager as sfx

class AppManager:
    def __init__(self, screen):
        self.screen = screen
        self.gif_bg = LandingPageGIF("Landing-Page.gif")
        self.controller = GameController()
        # Đính kèm screen vào controller để Single/Multi có thể truy cập
        self.controller.screen = screen

        # Khởi tạo SFX
        sfx.init()

        self.single_player_ctr = SinglePlayerController(self.controller)
        self.multi_player_ctr = MultiPlayerController(self.controller)
        self.menu_buttons, self.role_buttons, self.diff_buttons, self.multi_buttons, self.credit_buttons = init_buttons()
        #View
        self.menu_view = MenuView(screen, WIDTH, HEIGHT)
        self.role_view = RoleView(screen, WIDTH, HEIGHT)
        self.diff_view = DifficultyView(screen, WIDTH, HEIGHT)
        self.multi_select_view = MultiSelectView(screen, WIDTH, HEIGHT)


    def update(self):
        state = self.controller.game_state
        if state == "SPLASH":
            self.gif_bg.update()
        elif state == "PLAYING_SINGLE":
            self.single_player_ctr.update()
        elif state == "PLAYING_MULTI":
            self.multi_player_ctr.update()
            
    def draw(self):
        state = self.controller.game_state
        
        real_pos = pygame.mouse.get_pos()
        import builtins
        if hasattr(builtins, 'global_zoom_camera') and builtins.global_zoom_camera:
            mouse_pos = builtins.global_zoom_camera.translate_pos(real_pos)
        else:
            mouse_pos = real_pos

        if state == "SPLASH":
            self.menu_view.draw_splash(self.gif_bg)
        elif state == "MENU":
            self.menu_view.draw_main_menu(self.menu_buttons.values(), mouse_pos)
        elif state == "GUIDE":
            self.role_view.draw(self.role_buttons.values(), mouse_pos)
        elif state == "CREDITS":
            self.menu_view.draw_credits(self.credit_buttons.values(), mouse_pos)
        elif state == "DIFFICULTY_SELECT":
            self.diff_view.draw(self.diff_buttons.values(), mouse_pos)
        elif state == "MULTI_SELECT":
            self.multi_select_view.draw(self.multi_buttons.values(), mouse_pos)
        elif state == "PLAYING_SINGLE":
            self.single_player_ctr.draw(mouse_pos)
        elif state == "PLAYING_MULTI":
            self.multi_player_ctr.draw(mouse_pos)

    def handle_mouse_down(self, pos):
        state = self.controller.game_state

        if state == "SPLASH":
            self.controller.game_state = "MENU"
        
        elif state == "MENU":
            action = self.controller.handle_click(pos, self.menu_buttons)
            if action == 'SINGLE':
                self.controller.game_state = "DIFFICULTY_SELECT"
            elif action == 'MULTI':
                self.controller.game_state = "MULTI_SELECT"
            elif action == 'GUIDE':
                self.controller.game_state = "GUIDE"
            elif action == 'CREDIT':
                self.controller.game_state = "CREDITS"
            elif action == 'QUIT':
                self.safe_exit()
        
        elif state == "DIFFICULTY_SELECT":
            self.single_player_ctr.handle_click(pos, self.diff_buttons)
            
        elif state == "MULTI_SELECT":
            self.multi_player_ctr.handle_click(pos, self.multi_buttons)

        elif state == "PLAYING_SINGLE":
            self.single_player_ctr.handle_game_click(pos)
            
        elif state == "PLAYING_MULTI":
            self.multi_player_ctr.handle_game_click(pos)

        elif state == "GUIDE":
            if self.role_buttons['BACK'].rect.collidepoint(pos):
                self.controller.game_state = "MENU"
            elif self.role_buttons['QUIT_MINI'].rect.collidepoint(pos):
                self.safe_exit()

        elif state == "CREDITS":
            for key, btn in self.credit_buttons.items():
                if btn.rect.collidepoint(pos):
                    if key == 'BACK':
                        self.controller.game_state = "MENU"

    def safe_exit(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()