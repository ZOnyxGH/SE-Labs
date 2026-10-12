"""Run with python main.py. Importing this module does not open a window."""
import pygame
from game.game_engine import GameEngine

WIDTH, HEIGHT, FPS = 500, 700, 60


def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Flappy Bird - Lab 4')
        clock = pygame.time.Clock()
        engine = GameEngine(WIDTH, HEIGHT)
        while engine.running:
            for event in pygame.event.get():
                engine.handle_event(event)
            if not engine.running:
                break
            engine.update()
            engine.render(screen)
            pygame.display.flip()
            clock.tick(FPS)
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
