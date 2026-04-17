import os
from model.button import MenuButton

# --- CẤU HÌNH HỆ THỐNG ---
os.environ['SDL_VIDEO_CENTERED'] = '1'
WIDTH  = 800
HEIGHT = 600
TITLE  = "Uno Game - UTC Project"

# ── Màu sắc chuẩn theo reference design ────────────────────────────────────
_ORANGE  = (239, 100,  72)
_HOVER   = (255, 130, 100)
_NAVY    = ( 22,  43,  68)
_GREEN   = ( 40, 167,  69)
_GREEN_H = ( 33, 136,  56)
_BLUE    = (  0, 123, 255)
_BLUE_H  = (  0, 105, 217)
_YELLOW  = (255, 193,   7)
_YELLOW_H= (224, 168,   0)
_RED     = (220,  53,  69)
_RED_H   = (200,  35,  51)
_GRAY    = (108, 117, 125)
_GRAY_H  = ( 90,  98, 104)

# Vị trí nút: căn giữa màn hình, cách đều nhau
_BW = 300   # button width
_BH =  56   # button height
_BX = WIDTH // 2 - _BW // 2

menu_buttons_config = {
    'SINGLE': MenuButton("Đơn người chơi", _BX, 270, _BW, _BH, _ORANGE, _HOVER),
    'MULTI':  MenuButton("Đa người chơi",  _BX, 345, _BW, _BH, _ORANGE, _HOVER),
    'GUIDE':  MenuButton("Hướng dẫn chơi", _BX, 420, _BW, _BH, _ORANGE, _HOVER),
    'QUIT':   MenuButton("Thoát",           _BX, 495, _BW, _BH, _RED,    _RED_H),
}

role_buttons_config = {
    'BACK':      MenuButton("Back", 710, 20, 70, 35, _BLUE,  _BLUE_H),
    'QUIT_MINI': MenuButton("Quit", 630, 20, 70, 35, _RED,   _RED_H),
}

difficulty_buttons = {
    'EASY':   MenuButton("Dễ",      _BX, 250, _BW, _BH, _ORANGE, _HOVER),
    'NORMAL': MenuButton("Vừa",     _BX, 325, _BW, _BH, _ORANGE, _HOVER),
    'HARD':   MenuButton("Khó",     _BX, 400, _BW, _BH, _ORANGE, _HOVER),
    'BACK':   MenuButton("Quay lại",_BX, 475, _BW, _BH, _GRAY,   _GRAY_H),
}

multi_buttons = {
    'P3':   MenuButton("Chơi 3 người", _BX, 300, _BW, _BH, _ORANGE, _HOVER),
    'P4':   MenuButton("Chơi 4 người", _BX, 390, _BW, _BH, _ORANGE, _HOVER),
    'BACK': MenuButton("Quay lại",      _BX, 475, _BW, _BH, _GRAY,   _GRAY_H),
}

def init_buttons():
    return menu_buttons_config, role_buttons_config, difficulty_buttons, multi_buttons