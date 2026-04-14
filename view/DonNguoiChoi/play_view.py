import pygame
import os
from pathlib import Path
from model.button import MenuButton

class PlayView:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("arial", 20, bold=True)
        self.big_font = pygame.font.SysFont("arial", 40, bold=True)
        
        # Ảnh nền động
        base_path = Path(__file__).parent.parent.parent
        img_dir = os.path.join(base_path, 'data', 'images')
        
        self.bg_images = {}
        bg_config = {
            "red": "bgR.png",
            "green": "bgG.png",
            "blue": "bgBlue.png",
            "yellow": "bgY.png",
            "black": "bgBlack.png"
        }
        for map_color, fname in bg_config.items():
            path = os.path.join(img_dir, fname)
            if os.path.exists(path):
                img = pygame.image.load(path).convert()
                self.bg_images[map_color] = pygame.transform.scale(img, (self.width, self.height))

        # Nút chức năng
        self.btn_uno = MenuButton("UNO!", self.width - 120, self.height - 100, 100, 40, (220, 53, 69), (200, 35, 51))
        self.btn_draw = MenuButton("RÚT BÀI", self.width - 120, self.height - 50, 100, 40, (0, 123, 255), (0, 105, 217))
        self.btn_pass = MenuButton("BỎ QUA", self.width - 120, self.height - 50, 100, 40, (255, 193, 7), (224, 168, 0))
        self.btn_back = MenuButton("🔴 Thoát", 20, 20, 100, 35, (108, 117, 125), (90, 98, 104))
        
        # Popup chọn màu khi đánh wild card
        self.show_color_picker = False
        self.color_rects = {
            "red": pygame.Rect(self.width/2 - 60, self.height/2 - 20, 50, 50),
            "green": pygame.Rect(self.width/2 + 10, self.height/2 - 20, 50, 50),
            "blue": pygame.Rect(self.width/2 - 60, self.height/2 + 40, 50, 50),
            "yellow": pygame.Rect(self.width/2 + 10, self.height/2 + 40, 50, 50)
        }
        self.color_values = {
            "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0)
        }

    def draw(self, game, mouse_pos):
        # 1. Nền
        current_bg = self.bg_images.get(game.current_color, self.bg_images.get("black", None))
        if current_bg:
            self.screen.blit(current_bg, (0, 0))
        else:
            self.screen.fill((50, 150, 50))

        # 2. Thông tin chung
        self.draw_text_pgz(f"Độ khó: {game.difficulty}", 20, 60, "white", 20)
        self.draw_text_pgz(f"Lượt của: {'BẠN' if game.current_turn == 'PLAYER' else game.bot.name}", 20, 90, "yellow", 25)
        self.draw_text_pgz(f"Màu hiện tại: {game.current_color.upper()}", 20, 120, game.current_color if game.current_color != "white" else "black", 25)
        self.draw_text_pgz(f"Thông báo: {game.messsage}", self.width/2, 20, "white", 25, center=True)

        # 3. Bài của Bot (Mặt úp)
        self.draw_text_pgz(f"{game.bot.name} - Còn: {len(game.bot_hand)} lá", self.width/2, 80, "white", 20, center=True)
        bot_start_x = self.width/2 - (len(game.bot_hand) * 20) / 2
        back_img = game.deck.get_back_image()
        for i in range(len(game.bot_hand)):
            if back_img:
                self.screen.blit(back_img, (bot_start_x + i * 20, 110))
            else:
                pygame.draw.rect(self.screen.surface if hasattr(self.screen, 'surface') else self.screen, (100, 0, 0), (bot_start_x + i * 20, 110, 60, 90))

        # 4. Xấp bài ở giữa
        # Bài bỏ (Top card)
        top_card = game.deck.get_top_card()
        if top_card:
            top_card.draw(self.screen, self.width/2 - 90, self.height/2 - 60)
        
        # Bài bốc
        if back_img:
            self.screen.blit(back_img, (self.width/2 + 10, self.height/2 - 60))
            self.draw_text_pgz(f"({len(game.deck.cards)})", self.width/2 + 50, self.height/2 + 65, "white", 20, center=True)

        # 5. Bài của Người chơi
        self.draw_text_pgz("Bài của bạn", self.width/2, self.height - 180, "white", 20, center=True)
        player_start_x = self.width/2 - (len(game.player_hand) * 45) / 2
        
        hovered_idx = -1
        # Tìm lá bài được hover từ trên xuống dưới (đảo ngược mảng)
        for i in range(len(game.player_hand) - 1, -1, -1):
            rect = pygame.Rect(player_start_x + i * 45, self.height - 150, 80, 120)
            if rect.collidepoint(mouse_pos):
                hovered_idx = i
                break

        for i, card in enumerate(game.player_hand):
            card.is_hovered = (i == hovered_idx)
            card.draw(self.screen, player_start_x + i * 45, self.height - 150)

        # 6. Các nút
        # Highlight nút UNO khi người có 2 lá (chuẩn bị đánh còn 1 lá)
        uno_override = None
        if len(game.player_hand) == 2 and not game.uno_called.get("PLAYER", False):
            if (pygame.time.get_ticks() // 150) % 2 == 0:
                uno_override = (255, 80, 80) # Sáng đỏ rực
                
        self.draw_button(self.btn_uno, mouse_pos, override_color=uno_override)
        
        if getattr(game, "player_has_drawn", False):
            self.draw_button(self.btn_pass, mouse_pos)
        else:
            self.draw_button(self.btn_draw, mouse_pos)
            
        self.draw_button(self.btn_back, mouse_pos)

        # 7. Vẽ Popup chọn màu
        if self.show_color_picker:
            pygame.draw.rect(self.screen.surface if hasattr(self.screen, 'surface') else self.screen, (0, 0, 0), (self.width/2 - 80, self.height/2 - 50, 160, 160))
            pygame.draw.rect(self.screen.surface if hasattr(self.screen, 'surface') else self.screen, (255, 255, 255), (self.width/2 - 80, self.height/2 - 50, 160, 160), 2)
            self.draw_text_pgz("Chọn màu", self.width/2, self.height/2 - 40, "white", 20, center=True)
            for color, rect in self.color_rects.items():
                pygame.draw.rect(self.screen.surface if hasattr(self.screen, 'surface') else self.screen, self.color_values[color], rect)
        
        # 8. Màn hình thắng thua
        if game.winner:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface = self.screen.surface if hasattr(self.screen, 'surface') else self.screen
            surface.blit(overlay, (0, 0))
            msg = "BẠN ĐÃ CHIẾN THẮNG!" if game.winner == "PLAYER" else "BOT ĐÃ CHIẾN THẮNG!"
            color = "green" if game.winner == "PLAYER" else "red"
            self.draw_text_pgz(msg, self.width/2, self.height/2 - 50, color, 50, center=True)
            self.draw_text_pgz("Nhấn phím/chuột bất kỳ để về Menu", self.width/2, self.height/2 + 20, "white", 30, center=True)

    def draw_button(self, btn, mouse_pos, override_color=None):
        color = override_color if override_color else btn.get_color(mouse_pos)
        surface = self.screen.surface if hasattr(self.screen, 'surface') else self.screen
        pygame.draw.rect(surface, color, btn.rect)
        self.draw_text_pgz(btn.text, btn.rect.centerx, btn.rect.centery, "white", 20, center=True)

    def draw_text_pgz(self, text, x, y, color, size, center=False):
        if hasattr(self.screen, 'draw') and hasattr(self.screen.draw, 'text'):
            if center:
                self.screen.draw.text(text, center=(x, y), fontsize=size, color=color, fontname="arial", owidth=1, ocolor="black")
            else:
                self.screen.draw.text(text, midleft=(x, y), fontsize=size, color=color, fontname="arial", owidth=1, ocolor="black")
