import os
from model.button import MenuButton

# --- CẤU HÌNH HỆ THỐNG ---
os.environ['SDL_VIDEO_CENTERED'] = '1'
WIDTH = 800
HEIGHT = 600
TITLE = "Uno Game - UTC Project"#

menu_buttons_config = {
    'SINGLE': MenuButton("DON NGUOI CHOI", WIDTH/2 - 125, 220, 250, 50, (40, 167, 69), (33, 136, 56)),
    'MULTI':  MenuButton("DA NGUOI CHOI", WIDTH/2 - 125, 300, 250, 50, (0, 123, 255), (0, 105, 217)),
    'GUIDE':  MenuButton("HUONG DAN", WIDTH/2 - 125, 380, 250, 50, (255, 193, 7), (224, 168, 0)),
    'QUIT':   MenuButton("THOÁT", WIDTH/2 - 125, 460, 250, 50, (220, 53, 69), (200, 35, 51))
}

role_buttons_config = {
    'BACK': MenuButton("Back", 710, 20, 70, 35, (59, 130, 246), (37, 99, 235)),
    'QUIT_MINI': MenuButton("QUIT", 630, 20, 70, 35, (239, 68, 68), (220, 38, 38))
}

difficulty_buttons = {
    'EASY':   MenuButton("DE", WIDTH/2 - 125, 220, 250, 50, (40, 167, 69), (33, 136, 56)),
    'NORMAL': MenuButton("THUONG", WIDTH/2 - 125, 300, 250, 50, (0, 123, 255), (0, 105, 217)),
    'HARD':   MenuButton("KHO", WIDTH/2 - 125, 380, 250, 50, (220, 53, 69), (200, 35, 51)),
    'BACK':   MenuButton("QUAY LAI", WIDTH/2 - 125, 460, 250, 50, (108, 117, 125), (90, 98, 104))
}

def init_buttons():
    return menu_buttons_config, role_buttons_config, difficulty_buttons