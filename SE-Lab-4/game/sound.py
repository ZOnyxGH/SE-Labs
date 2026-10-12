"""Self-contained synthesized effects; continue silently without audio hardware."""
import math
from array import array
import pygame


class SoundFeedback:
    def __init__(self):
        self.enabled = True
        self.effects = {}
        self.samples = {}
        self.available = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2)
            rate, sample_format, channels = pygame.mixer.get_init()
            if sample_format != -16:
                return
            for name, frequencies, duration in (
                ('flap', (650, 950), 0.09),
                ('score', (880, 1320), 0.18),
                ('death', (220, 70), 0.30),
            ):
                values = array('h')
                count = int(rate * duration)
                phase = 0.0
                for i in range(count):
                    t = i / count
                    frequency = frequencies[0] + (frequencies[1] - frequencies[0]) * t
                    phase += 2 * math.pi * frequency / rate
                    envelope = min(1, i / max(1, rate * 0.005)) * (1 - t)
                    sample = int(7500 * math.sin(phase) * envelope)
                    values.extend([sample] * channels)
                self.samples[name] = values
                self.effects[name] = pygame.mixer.Sound(buffer=values)
            self.available = True
        except pygame.error:
            self.available = False

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled and self.available:
            pygame.mixer.stop()

    def play(self, name):
        if self.enabled and self.available:
            self.effects[name].play()
