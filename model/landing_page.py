import os
from PIL import Image, ImageSequence
import pygame

class LandingPageGIF:
    def __init__(self, gif_filename):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.gif_path = os.path.join(base_path, 'data', 'images', gif_filename)
        self.frames = []
        self.current_frame_index = 0
        self.timer = 0
        self.load_gif_frames()

    def load_gif_frames(self):
        try:
            with Image.open(self.gif_path) as im:
                for frame in ImageSequence.Iterator(im):
                    # Chuyển đổi tối ưu cho Pygame
                    frame_surf = pygame.image.fromstring(
                        frame.convert('RGBA').tobytes(), frame.size, 'RGBA'
                    ).convert_alpha()
                    self.frames.append(frame_surf)
            self.frame_count = len(self.frames)
        except Exception as e:
            print(f"Lỗi: {e}")
            self.frames = [pygame.Surface((800, 600))]
            self.frame_count = 1

    def update(self):
        if self.frame_count > 1:
            self.timer += 1
            if self.timer >= 4: # Tăng số này nếu muốn GIF chạy chậm lại
                self.timer = 0
                self.current_frame_index = (self.current_frame_index + 1) % self.frame_count

    def get_current_frame(self):
        return self.frames[self.current_frame_index]