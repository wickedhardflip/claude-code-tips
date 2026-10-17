# Style guide: <video name>

Gate 2: approve this and shotlist.md before code. Written from a reference frame/clip
(`ffmpeg -i ref.mp4 -vf fps=2,scale=960:-2 refs/f_%03d.png`). Take the grammar, never the subjects, logos or copy.
Report measured vs estimated vs proposed values separately; pixel estimates are approximate, verify against the frame.

- Palette (hex):
- Type: one display face, one UI face, one accent
- Shot lengths / pacing:
- Transitions:
- Camera:
- Texture (grain, shadows):

## Banned defaults
Centered title on a gradient, everything fading in, corner labels, glow on UI, a dead beat with nothing new on screen for >4 s.
Never two accent-color emphases at once. One focus per screen.

## Motion rules (by object class)
- Small UI snaps, minimal overshoot. Panels settle. Camera glides almost invisibly.
- Headlines land hard and HOLD long enough to read (captions 3-5 s).
- Ease: movement power2.inOut, arrivals power2/3.out, linear for typing/ticks/pans.
- Overlap chained beats ~0.3 s. Hold every finished state >= 0.5 s.
- Springs (stay a pure function of time): `track(t) = v0 + sum (v_i - v_(i-1)) * spring(t - t_i)`; one spring per retarget.
- Beat-synced motion is GENTLE: one smooth swell per bar, soft hits on drops. No per-beat whole-frame bounce.
- No blank space or empty backgrounds in any frame.
