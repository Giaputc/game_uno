import os
import pygame
from pathlib import Path

class MenuView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        # Thiết lập đường dẫn chính xác
        base_path = Path(__file__).parent.parent
        img_dir = os.path.join(base_path, 'data', 'images')
        
        # 1. Load Logo
        self.logo = None
        logo_path = os.path.join(img_dir, 'logo.png')
        if os.path.exists(logo_path):
            try:
                original_logo = pygame.image.load(logo_path).convert_alpha()
                self.logo = pygame.transform.scale(original_logo, (250, 250))
                self.logo_rect = self.logo.get_rect(center=(self.width/2, self.height/2))
            except Exception as e:
                print(f"Lỗi load logo: {e}")

        # 2. Load ảnh nền Menu chính (bgG.png)
        self.bg_menu = None
        bg_path = os.path.join(img_dir, 'bgG.png')
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert_alpha()
                self.bg_menu = pygame.transform.scale(img, (self.width, self.height))
            except Exception as e:
                print(f"Lỗi load bgG.png: {e}")

    def draw_splash(self, gif_model):
        # Vẽ nền GIF
        frame = gif_model.get_current_frame()
        self.screen.blit(pygame.transform.scale(frame, (self.width, self.height)), (0, 0))
        
        # Vẽ Logo chính giữa
        if self.logo:
            self.screen.blit(self.logo, self.logo_rect)
            
        # Dòng chữ nhỏ dưới logo
        self.screen.draw.text(
            "Chạm bất kỳ để tiếp tục", 
            center=(self.width/2, self.height/2 + 150), 
            fontsize=22, 
            color="white",
            shadow=(1, 1)
        )


    def draw_main_menu(self, buttons, mouse_pos):
        # 1. Vẽ nền bgG.png
        if self.bg_menu:
            self.screen.blit(self.bg_menu, (0, 0))
        else:
            self.screen.fill((30, 30, 30))

        # 2. Vẽ tiêu đề Menu (Sử dụng font Arial)
        self.screen.draw.text(
            "DANH MỤC GAME", 
            center=(self.width/2, 100), 
            fontsize=55, 
            color="yellow", 
            fontname="arial"  
        )

        # 3. Vẽ các nút bấm
        for btn in buttons:
            color = btn.get_color(mouse_pos)
            self.screen.draw.filled_rect(btn.rect, color)
            
            # Vẽ chữ trên nút (Sử dụng font Arial để hiện tiếng Việt)
            self.screen.draw.text(
                btn.text, 
                center=btn.rect.center, 
                fontsize=25, 
                color="white",
                fontname="arial" 
            )