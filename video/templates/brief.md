# Brief: <video name>

Fill this in BEFORE any code. Gate 1: references and real assets approved.

```
FILM      One sentence the viewer keeps. Audience. Duration. Formats (16:9 / 1:1 / 9:16).
ASSETS    Real logo, real UI screenshots or sanitized-data footage, brand type + colors, audio source.
VISUAL    What to keep from the reference (timing/grammar only). Clichés to avoid.
HARD LINE Never invent product screens or metrics. A missing asset is a blocker: stop and ask.
DELIVER   Storyboard, contact sheet, final video, poster (last frame), source, README.
```

## Shot as an event (frame numbers, constants in code, not magic numbers)
start state -> cursor on action -> press -> result -> HOLD (>= 0.5 s)

State FPS and say whether frames are GLOBAL or scene-local (Sequence offset trap): 0.5 s = 15 f @30, 30 f @60.

## Secrets
Keys live in `.env`; refer to them by name in prompts. Never paste a key.
