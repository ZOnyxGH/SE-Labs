"""Game state, accurate collisions, difficulty selection, replay and rendering."""
import math
import pygame
from .bird import Bird
from .pipe import Pipe
from .sound import SoundFeedback

DIFFICULTIES = {'Easy': (3, 200), 'Medium': (4, 165), 'Hard': (6, 135)}
WHITE = (245, 250, 255)


def circle_hits_pipe(bird, pipe):
    """Closest-point circle/rectangle test, using float coordinates.

    Touching an edge counts as a hit. Using the actual drawn circle avoids
    the old center-only misses and square bounding-box corner false positives.
    """
    for top, bottom in ((0, pipe.gap_y),
                        (pipe.gap_y + pipe.gap, pipe.screen_height)):
        x = max(pipe.x, min(bird.x, pipe.x + pipe.width))
        y = max(top, min(bird.y, bottom))
        if (bird.x - x) ** 2 + (bird.y - y) ** 2 <= bird.radius ** 2:
            return True
    return False


class GameEngine:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.font = pygame.font.SysFont('Arial', 30)
        self.small_font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 44, bold=True)
        self.sound = SoundFeedback()
        self.running = True
        self.difficulty = 'Medium'
        self.pipe_interval = 90
        self.reset('Medium')
        self.state = 'menu'

    @property
    def game_over(self):
        return self.state == 'game_over'

    def reset(self, difficulty):
        self.difficulty = difficulty
        self.pipe_speed, self.pipe_gap = DIFFICULTIES[difficulty]
        self.bird = Bird(self.width // 4, self.height // 2)
        self.pipes = [Pipe(self.width + 100, self.height,
                           gap=self.pipe_gap, speed=self.pipe_speed)]
        self._spawn_timer = 0
        self.score = 0
        self.state = 'playing'
        self.death_reason = ''

    def buttons(self):
        return [(name, pygame.Rect(60, 340 + i * 58, self.width - 120, 46))
                for i, name in enumerate(DIFFICULTIES)]

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.running = False
            elif event.key == pygame.K_m:
                self.sound.toggle()
            elif self.state != 'playing':
                choices = {pygame.K_1: 'Easy', pygame.K_2: 'Medium', pygame.K_3: 'Hard'}
                if event.key in choices:
                    self.reset(choices[event.key])
            elif event.key == pygame.K_SPACE:
                self.flap()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == 'playing':
                self.flap()
            else:
                for difficulty, rect in self.buttons():
                    if rect.collidepoint(event.pos):
                        self.reset(difficulty)
                if self.exit_button().collidepoint(event.pos):
                    self.running = False

    def handle_input(self):
        # KEYDOWN/click are edge-triggered; holding Space does not auto-flap.
        pass

    def flap(self):
        self.bird.flap()
        self.sound.play('flap')

    def die(self, reason):
        if self.state == 'playing':
            self.death_reason = reason
            self.state = 'game_over'
            self.sound.play('death')

    def update(self):
        if self.state != 'playing':
            return
        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(Pipe(self.width, self.height,
                                   gap=self.pipe_gap, speed=self.pipe_speed))

        # Subdivide motion to <= 1 pixel per axis so fast objects cannot jump
        # through a pipe between frames. Physics uses one 60 Hz fixed step.
        self.bird.velocity += self.bird.gravity
        steps = max(1, math.ceil(max([abs(self.bird.velocity)] +
                                     [abs(p.speed) for p in self.pipes])))
        for _ in range(steps):
            self.bird.y += self.bird.velocity / steps
            for pipe in self.pipes:
                pipe.x -= pipe.speed / steps
            if self.bird.y - self.bird.radius <= 0:
                self.die('Ceiling hit')
                return
            if self.bird.y + self.bird.radius >= self.height:
                self.die('Ground hit')
                return
            if any(circle_hits_pipe(self.bird, p) for p in self.pipes):
                self.die('Pipe hit')
                return

        for pipe in self.pipes:
            # Score once only after the whole bird clears the pipe.
            if not pipe.scored and pipe.x + pipe.width < self.bird.x - self.bird.radius:
                pipe.scored = True
                self.score += 1
                self.sound.play('score')
        self.pipes = [p for p in self.pipes if not p.off_screen()]

    def exit_button(self):
        return pygame.Rect(60, 530, self.width - 120, 42)

    def centered(self, screen, text, y, font=None, color=WHITE):
        image = (font or self.font).render(text, True, color)
        screen.blit(image, (self.width / 2 - image.get_width() / 2, y))

    def render(self, screen):
        screen.fill((108, 185, 215))
        for pipe in self.pipes:
            for rect in (pipe.top_rect(), pipe.bottom_rect()):
                pygame.draw.rect(screen, (32, 146, 87), rect)
                pygame.draw.rect(screen, (18, 94, 64), rect, 3)
        center = (round(self.bird.x), round(self.bird.y))
        pygame.draw.circle(screen, (255, 220, 75), center, self.bird.radius)
        pygame.draw.circle(screen, (32, 46, 60), (center[0] + 5, center[1] - 4), 3)
        screen.blit(self.font.render(f'Score: {self.score}', True, WHITE), (15, 14))
        sound = ('on' if self.sound.enabled else 'muted') if self.sound.available else 'unavailable'
        screen.blit(self.small_font.render(f'{self.difficulty} | Sound: {sound}', True, WHITE), (15, 51))
        if self.state == 'playing':
            self.centered(screen, 'Space / click: flap    M: sound    Esc: exit', self.height - 32, self.small_font)
            return
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 24, 40, 215))
        screen.blit(overlay, (0, 0))
        self.centered(screen, 'GAME OVER' if self.game_over else 'FLAPPY BIRD', 145, self.title_font)
        if self.game_over:
            self.centered(screen, f'Final score: {self.score}', 215)
            self.centered(screen, self.death_reason, 257, self.small_font)
        else:
            self.centered(screen, 'Space or left click to flap', 220, self.small_font)
        self.centered(screen, 'Choose difficulty to ' + ('replay' if self.game_over else 'start'), 294, self.small_font)
        for i, (difficulty, rect) in enumerate(self.buttons(), 1):
            pygame.draw.rect(screen, (36, 95, 125), rect, border_radius=8)
            speed, gap = DIFFICULTIES[difficulty]
            self.centered(screen, f'{i}  {difficulty} - speed {speed}, gap {gap}', rect.y + 10, self.small_font)
        pygame.draw.rect(screen, (100, 49, 62), self.exit_button(), border_radius=8)
        self.centered(screen, 'Exit (Esc / Q)', 539, self.small_font)
