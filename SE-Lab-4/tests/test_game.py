import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
import pygame
from game.bird import Bird
from game.pipe import Pipe
from game.game_engine import GameEngine, DIFFICULTIES, circle_hits_pipe


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((500, 700))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.e = GameEngine(500, 700)
        self.e.reset('Medium')
        self.events = []
        self.e.sound.play = self.events.append

    def pipe(self, x=120, top=250, speed=4):
        p = Pipe(x, 700, gap=165, speed=speed)
        p.gap_y = top
        return p

    def test_edge_overlap_outside_center(self):
        b = Bird(125, 260)
        p = self.pipe()
        self.assertFalse(p.top_rect().collidepoint(b.center()))
        self.assertTrue(circle_hits_pipe(b, p))

    def test_tangent_counts_as_collision(self):
        self.assertTrue(circle_hits_pipe(Bird(105, 240), self.pipe(x=120)))

    def test_corner_bounding_box_false_positive_is_avoided(self):
        b = Bird(106, 264)
        p = self.pipe()
        self.assertTrue(b.rect().colliderect(p.top_rect()))
        self.assertFalse(circle_hits_pipe(b, p))

    def test_safe_gap_and_bottom_overlap(self):
        p = self.pipe()
        self.assertFalse(circle_hits_pipe(Bird(125, 330), p))
        self.assertTrue(circle_hits_pipe(Bird(125, 405), p))

    def test_fast_pipe_cannot_tunnel(self):
        self.e.bird.y = 200
        self.e.bird.velocity = -0.5
        self.e.pipes = [self.pipe(x=250, speed=300)]
        self.e.update()
        self.assertTrue(self.e.game_over)
        self.assertEqual(self.e.death_reason, 'Pipe hit')
        self.assertEqual(self.e.score, 0)

    def test_ground_and_ceiling(self):
        for y, velocity, reason in ((684, 1, 'Ground hit'), (16, -3, 'Ceiling hit')):
            with self.subTest(reason=reason):
                self.e.reset('Easy')
                self.e.bird.y, self.e.bird.velocity = y, velocity
                self.e.update()
                self.assertEqual(self.e.death_reason, reason)

    def test_game_over_freezes_and_sound_plays_once(self):
        self.e.die('Pipe hit')
        before = (self.e.bird.y, self.e.pipes[0].x)
        for _ in range(20):
            self.e.update()
            self.e.die('Ground hit')
        self.assertEqual(before, (self.e.bird.y, self.e.pipes[0].x))
        self.assertEqual(self.events, ['death'])

    def test_flap_and_click_events(self):
        for event in (pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
                      pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))):
            self.e.handle_event(event)
            self.assertEqual(self.e.bird.velocity, -8)
        self.assertEqual(self.events, ['flap', 'flap'])

    def test_game_over_space_does_not_flap(self):
        self.e.die('Ground hit')
        velocity = self.e.bird.velocity
        self.e.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        self.assertEqual(self.e.bird.velocity, velocity)

    def test_score_after_full_clear_once(self):
        self.e.bird.y, self.e.bird.velocity = 330, -0.5
        p = self.pipe(x=39, speed=4)
        self.e.pipes = [p]
        self.e.update()  # right edge 105 < bird left edge 110
        self.e.update()
        self.assertEqual(self.e.score, 1)
        self.assertEqual(self.events, ['score'])

    def test_replay_resets_every_difficulty(self):
        for key, difficulty in ((pygame.K_1, 'Easy'), (pygame.K_2, 'Medium'), (pygame.K_3, 'Hard')):
            self.e.die('Pipe hit')
            self.e.score = 7
            self.e.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
            self.assertEqual(self.e.state, 'playing')
            self.assertEqual(self.e.score, 0)
            self.assertEqual(self.e.bird.velocity, 0)
            self.assertEqual(self.e._spawn_timer, 0)
            self.assertEqual((self.e.pipe_speed, self.e.pipe_gap), DIFFICULTIES[difficulty])
            self.assertEqual(len(self.e.pipes), 1)

    def test_menu_mouse_start_and_exit(self):
        self.e.state = 'menu'
        self.e.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                              pos=self.e.buttons()[0][1].center))
        self.assertEqual(self.e.difficulty, 'Easy')
        self.e.die('Ground hit')
        self.e.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                              pos=self.e.exit_button().center))
        self.assertFalse(self.e.running)

    def test_update_with_no_pipes(self):
        self.e.pipes = []
        self.e.update()
        self.assertEqual(self.e.state, "playing")

    def test_regular_spawning_and_cleanup(self):
        self.e._spawn_timer = 89
        p = self.pipe(x=-80)
        self.e.pipes = [p]
        self.e.update()
        self.assertEqual(self.e._spawn_timer, 0)
        self.assertEqual(len(self.e.pipes), 1)
        self.assertEqual(self.e.pipes[0].x, 496)

    def test_escape_and_mute(self):
        self.e.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
        self.assertFalse(self.e.sound.enabled)
        self.e.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertFalse(self.e.running)

    def test_sound_effects_exist(self):
        self.assertTrue(self.e.sound.available)
        self.assertEqual(set(self.e.sound.effects), {'flap', 'score', 'death'})
        self.assertTrue(all(s.get_length() > 0 for s in self.e.sound.effects.values()))

    def test_no_audio_device_fallback(self):
        from unittest.mock import patch
        from game.sound import SoundFeedback
        with patch('pygame.mixer.get_init', return_value=None), patch('pygame.mixer.init', side_effect=pygame.error('no device')):
            sound = SoundFeedback()
            self.assertFalse(sound.available)
            sound.play('flap')

    def test_render_all_states(self):
        screen = pygame.display.get_surface()
        for state in ('menu', 'playing', 'game_over'):
            self.e.state = state
            self.e.render(screen)


if __name__ == '__main__':
    unittest.main()
