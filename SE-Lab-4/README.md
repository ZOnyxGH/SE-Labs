# Lab 4 - Flappy Bird

Completed with ChatGPT assistance from https://github.com/SETAPESU26/40_flappy-bird
Original commit: a6057332daff3c0f10deb4367eb830a12445bd0a
This is an individual lab. Review the code and be able to explain the changes.

## Run on a Mac

Open Terminal inside this Lab-4 folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Python 3.10+ is required. If python3 is unavailable, install Python first.
The game opens a graphical Pygame window; it is not a terminal game.

## Controls

- 1 / 2 / 3 or click a difficulty button: start or replay.
- Space / left mouse click: flap during play.
- M: toggle sound.
- Esc / Q / close the window: exit.

| Difficulty | Pipe speed (pixels/frame at 60 Hz) | Gap (pixels) |
|---|---:|---:|
| Easy | 3 | 200 |
| Medium | 4 | 165 |
| Hard | 6 | 135 |

## Task 1 - Collision repair

The original code tested only the bird's centre. The updated code checks the
actual circle against each pipe rectangle using its closest point. Edge contact
counts as a hit. Float coordinates avoid integer truncation. Motion is subdivided
to at most one pixel per axis per substep so fast pipes cannot skip the bird.

## Task 2 - Game over

Ground, ceiling and pipe collisions freeze play and open a game-over overlay.
It displays the final score and the cause of death, then waits for input.

## Task 3 - Replay and difficulty

The game has explicit menu, playing and game_over states. Choosing a difficulty
creates a fresh bird and pipes and clears score, velocity, spawn timer and death
reason. Keyboard and clickable buttons both work. Exit performs Pygame cleanup.

## Task 4 - Sound

Three effects are synthesized locally: flap, score and death. No downloaded assets
are needed. Death plays once per round and scoring once per pipe. The game continues
silently if an audio device cannot be initialized. M toggles sound.

## Verification

```bash
python -m unittest discover -s tests -v
```

18 tests passed in Python 3.12.14 / Pygame 2.6.1 on Linux with SDL dummy video/audio.
Additional checks: entry-point initialization, QUIT cleanup, compilation and diff
whitespace check. Real Mac display/audio hardware has not been tested here.
Tests cover geometry, high-speed motion, all death causes, input, scoring,
difficulty resets, empty pipe lists, spawning, sound and missing-device fallback.

## Required deliverables

- videos/before.mp4: exactly 10 seconds, original engine.
- videos/after.mp4: exactly 10 seconds, updated engine, with sound.
- main.py, game/, requirements.txt: updated playable code.
- Chat_History.pdf: visible conversation transcript through packaging, plus a
  clearly separated implementation/verification appendix.
- tests/ and test_results.txt: reproducible verification.
- ORIGINAL_README.md: original assignment requirements.

### Video provenance

These are programmatically recorded Pygame renderings with scripted input in a
headless cloud environment, not human-play screen recordings. A controlled pipe
placement exposes the original edge bug and its repair. The scripts use the actual
original/updated engine; they do not fabricate an outcome or draw replacement game
screens. In the after video the soundtrack mixes the same generated effect samples
at their recorded event frames because the cloud uses a dummy audio device.

Before: initial pipes/spawning are suppressed for isolation; normal scripted flaps
are followed by a controlled edge overlap at 3 seconds, then the original engine
continues until game over. After: select Easy at 1 second; controlled pipe placement
shows scoring; the same edge overlap ends the round at 3 seconds; replay Medium at
5 seconds and Hard at 7 seconds; Escape is processed near the end. The recorder
keeps the last rendered frame after the exit request to complete the 10-second clip.

Regenerate videos (ffmpeg must be installed; optional for playing):

```bash
python tools/record_before.py
python tools/record_after.py videos/after.mp4
```

On a Mac, ffmpeg can be installed using `brew install ffmpeg` if Homebrew is installed.
The original source is preserved under tools/original for before-video reproduction.
The after recorder may also produce temporary preview PNGs beside its output.

## Upload to your personal lab repository

Copy this entire Lab-4 folder into your personal lab-repo checkout. From that
checkout's root:

```bash
git add Lab-4
git commit -m "Complete Lab 4 Flappy Bird fixes and features"
git push
```

Check that the repository remote belongs to your personal account before pushing.
Do not push to SETAPESU26 and do not raise a pull request to the class repository.
The source README also asks for a shared ChatGPT conversation link. Use ChatGPT's
Share option on this conversation and add the resulting link to your submission
if required. This package contains the PDF requested by the lab handout; it does
not invent a shared-chat URL. Messages after the PDF was produced are not included
in that export. GitHub publication has not been performed.
