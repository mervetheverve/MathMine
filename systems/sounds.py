"""Sound effects - synthesized programmatically, no external files needed."""
import io
import math
import struct
import wave
import pygame


SAMPLE_RATE = 44100


def _make_wav(samples):
    """Convert a list of float samples (-1.0 to 1.0) into a pygame Sound."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            w.writeframes(struct.pack('<h', int(clamped * 32767)))
    buf.seek(0)
    return pygame.mixer.Sound(file=buf)


def _envelope(i, total, fade_in_ms=8, fade_out_ms=15):
    """Smooth fade-in / fade-out envelope."""
    fade_in = int(SAMPLE_RATE * fade_in_ms / 1000)
    fade_out = int(SAMPLE_RATE * fade_out_ms / 1000)
    if i < fade_in:
        return i / fade_in
    if i > total - fade_out:
        return (total - i) / fade_out
    return 1.0


def _tone(freq, duration_ms, volume=0.3):
    """Generate a pure sine tone."""
    n = int(SAMPLE_RATE * duration_ms / 1000)
    return [volume * _envelope(i, n) * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
            for i in range(n)]


def _sweep(freq_start, freq_end, duration_ms, volume=0.3):
    """Generate a frequency sweep."""
    n = int(SAMPLE_RATE * duration_ms / 1000)
    samples = []
    for i in range(n):
        t = i / n
        freq = freq_start + (freq_end - freq_start) * t
        env = _envelope(i, n)
        samples.append(volume * env * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
    return samples


def _make_pickup():
    """Short rising chirp when collecting a block."""
    return _make_wav(_sweep(600, 1200, 80, volume=0.25))


def _make_correct():
    """Happy two-note chime: C5 then E5."""
    samples = _tone(523, 120, volume=0.3) + _tone(659, 160, volume=0.35)
    return _make_wav(samples)


def _make_wrong():
    """Soft low buzz — two close frequencies for a gentle wobble."""
    n = int(SAMPLE_RATE * 0.18)
    samples = []
    for i in range(n):
        env = _envelope(i, n, fade_in_ms=10, fade_out_ms=40)
        s = 0.15 * env * (
            math.sin(2 * math.pi * 200 * i / SAMPLE_RATE) +
            0.4 * math.sin(2 * math.pi * 207 * i / SAMPLE_RATE)
        )
        samples.append(s)
    return _make_wav(samples)


def _make_blueprint_complete():
    """Celebratory three-note arpeggio: C5 - E5 - G5."""
    samples = (_tone(523, 100, volume=0.3) +
               _tone(659, 100, volume=0.35) +
               _tone(784, 220, volume=0.4))
    return _make_wav(samples)


def _make_penalty():
    """Descending two-tone warning for wrong answer penalty."""
    samples = _tone(440, 120, volume=0.3) + _tone(300, 200, volume=0.35)
    return _make_wav(samples)


class SoundManager:
    """Manages all game sounds. Call init() after pygame.mixer.init()."""

    def __init__(self):
        self.enabled = True
        self.sounds = {}

    def init(self):
        """Generate all sounds. Must be called after pygame.mixer is ready."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)
            self.sounds['pickup'] = _make_pickup()
            self.sounds['correct'] = _make_correct()
            self.sounds['wrong'] = _make_wrong()
            self.sounds['blueprint_complete'] = _make_blueprint_complete()
            self.sounds['penalty'] = _make_penalty()
        except Exception:
            self.enabled = False

    def play(self, name):
        """Play a sound by name."""
        if self.enabled and name in self.sounds:
            self.sounds[name].play()
