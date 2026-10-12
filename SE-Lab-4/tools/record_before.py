"""Capture the unmodified engine; scripted inputs and setup are disclosed."""
import os, sys, subprocess, random
from pathlib import Path
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools' / 'original'))
output = str(Path(sys.argv[1]).resolve()) if len(sys.argv) > 1 else str(root / 'videos' / 'before.mp4')
import pygame
from game.game_engine import GameEngine
from game.pipe import Pipe
pygame.init()
screen=pygame.display.set_mode((500,700))
engine=GameEngine(500,700)
random.seed(40)
engine.pipes=[]
engine._spawn_timer=-10000
font=pygame.font.SysFont('Arial',18)
encoder=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size','500x700','-framerate','60','-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p',output],stdin=subprocess.PIPE)
for frame in range(600):
    if frame < 180 and frame % 32 == 0:
        engine.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
    if frame == 180:
        engine.bird.y=260
        engine.bird.velocity=-0.5
        pipe=Pipe(engine.bird.x+14,700)
        pipe.gap_y=250
        engine.pipes=[pipe]
    engine.update()
    screen.fill((135,206,235))
    engine.render(screen)
    label='Original code | scripted input' if frame <180 else 'Controlled edge hit: center-only check misses'
    if engine.game_over: label='Game frozen: no game-over screen or replay'
    pygame.draw.rect(screen,(20,35,50),(0,650,500,50))
    screen.blit(font.render(label,True,(255,255,255)),(10,666))
    encoder.stdin.write(pygame.image.tostring(screen,'RGB'))
encoder.stdin.close()
assert encoder.wait()==0
pygame.quit()
