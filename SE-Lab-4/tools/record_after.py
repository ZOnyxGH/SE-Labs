"""Reproducible 10-second scripted evidence, not a human-play recording.

Sets controlled pipe positions at frames 100/180 to show scoring and an edge
collision without waiting for random gameplay. All game updates and rendering
use the unmodified submitted engine. Requires ffmpeg only for recording.
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import random
import subprocess
import sys
import tempfile
import wave
from array import array
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pygame
from game.game_engine import GameEngine
from game.pipe import Pipe


def main():
    output = Path(sys.argv[1] if len(sys.argv) > 1 else 'after.mp4').resolve()
    pygame.mixer.pre_init(44100, -16, 2)
    pygame.init()
    random.seed(40)
    screen = pygame.display.set_mode((500, 700))
    engine = GameEngine(500, 700)
    font = pygame.font.SysFont('Arial', 18)
    audio = array('h', [0]) * (44100 * 10 * 2)
    events = []
    original_play = engine.sound.play
    def record_sound(name):
        original_play(name)
        events.append((frame, name))
        start = round(frame / 60 * 44100) * 2
        for i, sample in enumerate(engine.sound.samples[name]):
            if start + i < len(audio):
                audio[start + i] = max(-32768, min(32767, audio[start + i] + sample))
    engine.sound.play = record_sound
    with tempfile.TemporaryDirectory() as temp:
        video = Path(temp) / 'video.mp4'
        encoder = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo',
            '-pixel_format', 'rgb24', '-video_size', '500x700', '-framerate', '60',
            '-i', '-', '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(video)], stdin=subprocess.PIPE)
        for frame in range(600):
            if frame in (60, 300, 420):
                key = {60: pygame.K_1, 300: pygame.K_2, 420: pygame.K_3}[frame]
                engine.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
                if frame == 60:
                    engine.pipes = []
                    engine._spawn_timer = -10000
            if 60 <= frame < 180 and (frame - 60) % 38 == 0:
                engine.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            if frame == 100:
                pipe = Pipe(180, 700, gap=200, speed=3)
                pipe.gap_y = 300
                engine.pipes = [pipe]
            if frame == 180:
                engine.bird.y, engine.bird.velocity = 260, -0.5
                pipe = Pipe(engine.bird.x + 14, 700, gap=200, speed=3)
                pipe.gap_y = 250
                engine.pipes = [pipe]
            if frame == 590:
                engine.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
            if engine.running:
                engine.update()
            engine.render(screen)
            label = ('Scripted demo: choose Easy' if frame < 60 else
                     'Scripted flaps + controlled scoring setup' if frame < 180 else
                     'Same edge hit detected; final score + replay' if frame < 300 else
                     'Replay: Medium; ground collision detected' if frame < 420 else
                     'Replay: Hard; ground collision detected' if frame < 590 else
                     'Esc processed: application exit requested')
            pygame.draw.rect(screen, (10, 24, 40), (0, 605, 500, 32))
            screen.blit(font.render(label, True, (255, 255, 255)), (8, 613))
            if frame in (0, 140, 200, 305, 425):
                pygame.image.save(screen, str(output.parent / f'preview_{frame}.png'))
            encoder.stdin.write(pygame.image.tostring(screen, 'RGB'))
        encoder.stdin.close()
        assert encoder.wait() == 0
        sound_file = Path(temp) / 'audio.wav'
        with wave.open(str(sound_file), 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            wav.writeframes(audio.tobytes())
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(video), '-i', str(sound_file),
                        '-c:v', 'copy', '-c:a', 'aac', '-t', '10', str(output)], check=True)
    assert {'flap', 'score', 'death'} <= {name for _, name in events}, events
    print('Recorded 600 frames; sound events:', events)
    pygame.quit()


if __name__ == '__main__':
    main()
