"""
sfx_manager.py — Hệ thống âm thanh cho game UNO.
Sinh âm thanh procedural bằng stdlib (math, wave, struct) — không cần file ngoài.
Tự động tạo file WAV vào data/sounds/ khi khởi động lần đầu.
"""
import pygame
import math
import wave
import struct
import os
from pathlib import Path


class SFXManager:
    def __init__(self):
        self._sounds = {}
        self._enabled = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self._enabled = True
        except Exception as e:
            print(f"SFX: Mixer init failed — sound disabled. ({e})")
            return

        sounds_dir = os.path.join(Path(__file__).parent.parent, 'data', 'sounds')
        os.makedirs(sounds_dir, exist_ok=True)

        self._generate_all(sounds_dir)
        self._load_all(sounds_dir)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _write_wav(self, path, data, sample_rate=22050):
        """Ghi danh sách int16 samples vào file WAV."""
        clamped = [max(-32767, min(32767, int(v))) for v in data]
        try:
            with wave.open(path, 'w') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(sample_rate)
                f.writeframes(struct.pack(f'{len(clamped)}h', *clamped))
        except Exception as e:
            print(f"SFX: Failed to write {path}: {e}")

    def _apply_envelope(self, data, attack_ms=8, release_ms=20, sample_rate=22050):
        """Áp fade-in/out để tránh tiếng click."""
        n = len(data)
        atk = max(1, int(sample_rate * attack_ms / 1000))
        rel = max(1, int(sample_rate * release_ms / 1000))
        out = list(data)
        for i in range(min(atk, n)):
            out[i] = int(out[i] * (i / atk))
        for i in range(min(rel, n)):
            out[n - 1 - i] = int(out[n - 1 - i] * (i / rel))
        return out

    def _gen_tone(self, path, freq, duration=0.08, volume=0.45, sample_rate=22050):
        """Tiếng click ngắn — dùng cho đặt bài."""
        if os.path.exists(path):
            return
        n = int(sample_rate * duration)
        data = [int(volume * math.sin(2 * math.pi * freq * i / sample_rate) * 32767)
                for i in range(n)]
        self._write_wav(path, self._apply_envelope(data), sample_rate)

    def _gen_sweep(self, path, freq_start, freq_end, duration=0.15, volume=0.4, sample_rate=22050):
        """Tiếng sweep (tần số thay đổi) — dùng cho rút bài và hô UNO."""
        if os.path.exists(path):
            return
        n = int(sample_rate * duration)
        phase = 0.0
        data = []
        for i in range(n):
            freq = freq_start + (freq_end - freq_start) * (i / n)
            phase += 2 * math.pi * freq / sample_rate
            data.append(int(volume * math.sin(phase) * 32767))
        self._write_wav(path, self._apply_envelope(data, attack_ms=5, release_ms=30), sample_rate)

    def _gen_fanfare(self, path, sample_rate=22050):
        """Nhạc chiến thắng — gam C major C5-E5-G5-C6."""
        if os.path.exists(path):
            return
        notes = [(523, 0.10), (659, 0.10), (784, 0.10), (1047, 0.22)]  # C5 E5 G5 C6
        all_data = []
        for freq, dur in notes:
            n = int(sample_rate * dur)
            chunk = [int(0.5 * math.sin(2 * math.pi * freq * i / sample_rate) * 32767)
                     for i in range(n)]
            all_data.extend(self._apply_envelope(chunk, attack_ms=5, release_ms=15))
        self._write_wav(path, all_data, sample_rate)

    # ── Generation & Loading ─────────────────────────────────────────────────

    def _generate_all(self, sounds_dir):
        fp = lambda name: os.path.join(sounds_dir, name)
        # Đặt bài: tiếng click cao, ngắn
        self._gen_tone(fp('card_play.wav'),  freq=900,  duration=0.065, volume=0.40)
        # Rút bài: tiếng whoosh xuống thấp
        self._gen_sweep(fp('card_draw.wav'), freq_start=550, freq_end=200, duration=0.14, volume=0.30)
        # Hô UNO: alert tăng dần
        self._gen_sweep(fp('uno_call.wav'),  freq_start=440, freq_end=880, duration=0.22, volume=0.55)
        # Chiến thắng: fanfare
        self._gen_fanfare(fp('win.wav'))

    def _load_all(self, sounds_dir):
        for name in ('card_play', 'card_draw', 'uno_call', 'win'):
            path = os.path.join(sounds_dir, f'{name}.wav')
            try:
                self._sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"SFX: Could not load '{name}': {e}")

    # ── Public API ───────────────────────────────────────────────────────────

    def play(self, name: str):
        if not self._enabled:
            return
        s = self._sounds.get(name)
        if s:
            try:
                s.play()
            except Exception:
                pass


# ── Singleton API ─────────────────────────────────────────────────────────────
_manager: "SFXManager | None" = None


def init():
    """Khởi tạo SFXManager singleton — gọi 1 lần khi app start."""
    global _manager
    _manager = SFXManager()


def play(name: str):
    """Phát âm thanh theo tên. An toàn ngay cả khi SFX không khởi động được."""
    if _manager:
        _manager.play(name)
