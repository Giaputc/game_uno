import os
import pygame
from pathlib import Path

class RoleView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        # Đường dẫn thư mục ảnh
        base_path = Path(__file__).parent.parent
        img_dir = os.path.join(base_path, 'data', 'images')
        
        # Load nền bgY.png
        self.bg_role = None
        bg_path = os.path.join(img_dir, 'bgY.png')
        if os.path.exists(bg_path):
            img = pygame.image.load(bg_path).convert_alpha()
            self.bg_role = pygame.transform.scale(img, (self.width, self.height))

    def draw(self, buttons, mouse_pos):
        # 1. Vẽ nền vàng bgY.png
        if self.bg_role:
            self.screen.blit(self.bg_role, (0, 0))
        else:
            self.screen.fill((255, 204, 0))

        # 2. Vẽ tiêu đề chính
        self.screen.draw.text(
            "Hướng dẫn chơi", 
            center=(self.width/2, 80), 
            fontsize=60, 
            color="#1a2a4e", 
            fontname="arial", 
            bold=True
        )

        # 3. Vẽ khung nội dung (Panel)
        # Viền đen bên ngoài
        self.screen.draw.filled_rect(pygame.Rect(65, 145, 670, 410), "black")
        # Nền xanh nhạt bên trong
        self.screen.draw.filled_rect(pygame.Rect(70, 150, 660, 400), "#a5b4fc")

        # 4. Nội dung quy tắc chơi
        content = (
            "[1] NGUYÊN TẮC ĐÁNH BÀI:\n"
            "• Đánh hợp lệ nếu: Cùng hệ màu, Cùng con số, hoặc Cùng chức năng với lá bài cũ.\n"
            "• Nếu bí bài: Bắt buộc bấm Rút Bài 1 lá. Hệ thống cho phép đánh luôn lá vừa rút hoặc Bỏ Qua lượt.\n\n"
            "[2] QUYỀN NĂNG THẺ ĐẶC BIỆT THẦN THÁNH:\n"
            "• Đổi Màu (Wild): Được thả bất cứ lúc nào để chuyển màu ván bài.\n"
            "• +4 (Wild Draw 4): Bắt đối thủ ôm 4 lá! ĐƯỢC ĐÁNH TỰ DO bất chấp trên tay bạn đang có bài hay không!\n\n"
            "[3] KHẮC CỐT GHI TÂM HÔ UNO! TRÁNH ĂN PHẠT:\n"
            "• Nhấn gấp nút UNO khi chuẩn bị đánh lá bài kế cuối (nghĩa là trên tay sẽ xót lại đúng 1 thẻ).\n"
            "• Nếu quên nói mà đánh lá bài xuống báo hại bản thân sẽ bị phạt bốc 2 lá.\n"
            "• Ván chơi sẽ tự kết thúc nếu ai đó may mắn xả sạch tụ bài của mình trước!"
        )
        self.screen.draw.text(
            content, 
            (85, 170),
            width=620, 
            fontsize=17, 
            color="#1a2a4e", 
            fontname="arial", 
            lineheight=1.2
        )

        # 5. Vẽ các nút chức năng (QUIT, BACK, SOUND...)
        for btn in buttons:
            btn_color = btn.get_color(mouse_pos)
            self.screen.draw.filled_rect(btn.rect, btn_color)
            self.screen.draw.text(
                btn.text, 
                center=btn.rect.center, 
                fontsize=20, 
                color="white", 
                fontname="arial"
            )