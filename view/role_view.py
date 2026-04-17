import os
import pygame
from pathlib import Path
from view.font_helper import draw_text, draw_text_shadow, draw_button

_NAVY     = ( 22,  43,  68)
_NAVYLT   = ( 30,  60, 110)
_PANEL_BG = (165, 180, 252)   # indigo-200 giữ nguyên như design
_BLUE     = (  0, 123, 255)
_BLUE_H   = (  0, 105, 217)
_RED      = (220,  53,  69)
_RED_H    = (200,  35,  51)
_YELLOW   = (255, 220,  30)


class RoleView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width  = width
        self.height = height
        self._surf  = screen.surface

        base_path = Path(__file__).parent.parent
        img_dir   = os.path.join(base_path, 'data', 'images')

        self.bg_role = None
        bg_path = os.path.join(img_dir, 'bgY.png')
        if os.path.exists(bg_path):
            img = pygame.image.load(bg_path).convert_alpha()
            self.bg_role = pygame.transform.smoothscale(img, (width, height))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _wrap_text(self, text: str, font_size: int, max_width: int):
        """Tự ngắt dòng — trả về list các dòng."""
        import view.font_helper as fh
        font = fh._get_font(font_size)
        lines = []
        for paragraph in text.split('\n'):
            if paragraph.strip() == '':
                lines.append('')
                continue
            words = paragraph.split(' ')
            current = ''
            for word in words:
                test = current + (' ' if current else '') + word
                if font.size(test)[0] <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    def draw(self, buttons, mouse_pos):
        # 1. Nền
        if self.bg_role:
            self._surf.blit(self.bg_role, (0, 0))
        else:
            self._surf.fill((255, 204, 0))

        # 2. Tiêu đề
        draw_text_shadow(
            self._surf, "Hướng dẫn chơi", 50, _NAVY,
            shadow_color=(0, 0, 0), offset=(2, 2),
            center=(self.width / 2, 70), bold=True,
        )

        # 3. Panel nội dung
        panel = pygame.Rect(65, 130, 670, 400)
        pygame.draw.rect(self._surf, (0, 0, 0), panel, border_radius=12)
        inner = pygame.Rect(70, 135, 660, 390)
        pygame.draw.rect(self._surf, _PANEL_BG, inner, border_radius=10)

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

        lines = self._wrap_text(rules, 16, 630)
        y = 148
        for line in lines:
            if line == '':
                y += 8
                continue
            bold = line.startswith('QUY TẮC') or line.startswith("HÔ ") or line.startswith("KẾT ")
            color = _NAVYLT if bold else _NAVY
            draw_text(self._surf, line, 16, color, topleft=(82, y), bold=bold)
            y += 22

        # 5. Nút Back / Quit
        for btn in buttons:
            hovered = btn.rect.collidepoint(mouse_pos)
            is_quit = 'quit' in btn.text.lower()
            bg      = (_RED if is_quit else _BLUE)
            bg_h    = (_RED_H if is_quit else _BLUE_H)
            draw_button(
                self._surf,
                pygame.Rect(btn.rect.x, btn.rect.y, btn.rect.width, btn.rect.height),
                btn.text, 18,
                bg_h if hovered else bg,
                _NAVY, (255, 255, 255),
                hover=hovered, radius=8,
            )