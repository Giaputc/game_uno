import pgzrun
import pygame
from settings import WIDTH, HEIGHT, TITLE
from Controller.app_manager import AppManager
import builtins

app = None
virtual_surface = pygame.Surface((WIDTH, HEIGHT))
display_surface = None

class ScreenCapture:
    def __getattr__(self, name):
        return getattr(screen, name)
    @property
    def surface(self):
        return virtual_surface
    def blit(self, *args, **kwargs):
        virtual_surface.blit(*args, **kwargs)
    def fill(self, *args, **kwargs):
        virtual_surface.fill(*args, **kwargs)

def init_display_once():
    global display_surface
    if display_surface is None:
        display_surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

def translate_pos(real_pos):
    real_w, real_h = display_surface.get_size()
    scale = min(real_w / WIDTH, real_h / HEIGHT)
    new_w = int(WIDTH * scale)
    new_h = int(HEIGHT * scale)
    
    offset_x = (real_w - new_w) // 2
    offset_y = (real_h - new_h) // 2
    
    virtual_x = (real_pos[0] - offset_x) / scale
    virtual_y = (real_pos[1] - offset_y) / scale
    return (virtual_x, virtual_y)

# Duck type so that app_manager doesn't need to be changed
builtins.global_zoom_camera = type('obj', (object,), {'translate_pos': lambda self, p: translate_pos(p)})()

def draw():
    global app
    init_display_once()
    
    if app is None:
        app = AppManager(ScreenCapture()) 
    
    app.draw()
    
    real_w, real_h = display_surface.get_size()
    scale = min(real_w / WIDTH, real_h / HEIGHT)
    
    new_w = int(WIDTH * scale)
    new_h = int(HEIGHT * scale)
    
    scaled_surf = pygame.transform.smoothscale(virtual_surface, (new_w, new_h))
    
    offset_x = (real_w - new_w) // 2
    offset_y = (real_h - new_h) // 2
    
    # Tô viền dư bằng màu tối có dải gradient đẹp hơn đen trơn
    screen.surface.fill((15, 25, 45))
    
    # Vẽ viền sáng nhẹ chứa trong game
    if offset_x > 0 or offset_y > 0:
        border_rect = pygame.Rect(offset_x - 2, offset_y - 2, new_w + 4, new_h + 4)
        pygame.draw.rect(screen.surface, (40, 70, 120), border_rect, 2)
    
    screen.surface.blit(scaled_surf, (offset_x, offset_y))

def update(dt):
    if app:
        app.update()

def on_mouse_down(pos, button):
    if app:
        # Lấy toạ độ ảo từ nút bấm trên cửa sổ thật định cỡ
        virtual_pos = translate_pos(pos)
        app.handle_mouse_down(virtual_pos)

# Bắt đầu chạy game
pgzrun.go()