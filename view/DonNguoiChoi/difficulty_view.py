# view/difficulty_view.py
import os
import pygame
from pathlib import Path

class DifficultyView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        # --- THIẾT LẬP ĐƯỜNG DẪN ẢNH NỀN (Giống MenuView) ---
        base_path = Path(__file__).parent.parent
        img_dir = os.path.join(base_path, 'data', 'images')
        
        # Load ảnh nền bgG.png
        self.bg_image = None
        bg_path = os.path.join(img_dir, 'bgG.png') # Chỉ định chính xác file bgG.png
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert_alpha()
                # Co giãn ảnh cho vừa khít màn hình
                self.bg_image = pygame.transform.scale(img, (self.width, self.height))
            except Exception as e:
                print(f"Lỗi load bgG.png cho DifficultyView: {e}")

    def draw(self, buttons, mouse_pos):
        # --- 1. VẼ NỀN bgG.png ---
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            # Fallback nếu không load được ảnh: dùng màu nền tối
            self.screen.fill((44, 62, 80)) 
        
        # --- 2. VẼ TIÊU ĐỀ ---
        self.screen.draw.text(
            "CHỌN ĐỘ KHÓ", 
            center=(self.width/2, 100), 
            fontsize=50, 
            color="yellow", # Đổi sang màu vàng cho nổi bật trên nền xanh
            fontname="arial",
            bold=True,
            shadow=(2, 2) # Thêm bóng đổ cho chữ
        )

        # --- 3. VẼ CÁC NÚT BẤM ---
        for btn in buttons:
            btn_color = btn.get_color(mouse_pos)
            self.screen.draw.filled_rect(btn.rect, btn_color)
            
            # Vẽ chữ trên nút (Sử dụng font Arial để hiện tiếng Việt)
            self.screen.draw.text(
                btn.text, 
                center=btn.rect.center, 
                fontsize=25, 
                color="white", 
                fontname="arial"
            )