# Code-Rendered Video Workflow

Claude writes a program, a headless browser turns it into frames, ffmpeg glues them into a file. Motion graphics, product/UI promos and data stories, all drawn in code. Copy this folder to a new machine and you have the whole workflow.

## Rig (10 minutes)

| Tool | Install |
|---|---|
| Node 18+ | nodejs.org |
| Remotion 4 (React) | `npm i remotion @remotion/cli react react-dom` (bundles Chrome + ffmpeg). Free for individuals and companies of 3 or fewer; check the license before paid/client work |
| 3D (optional) | `@remotion/three three @react-three/fiber`; render with `--gl=angle` |
| Python | `pip install numpy scipy pillow opencv-python librosa soundfile` |
| Claude Code | run on a high effort level for new films; medium is for small fixes |

Remotion's bundled ffmpeg can't write image files or run `afade`. For stills from a finished video use OpenCV (`scripts/qa.py`); do fades in numpy. Playwright is the zero-framework alternative if you'd rather write one `index.html`.

## The one rule: seekable frames

Any frame must render on its own, identically every time. Drive everything from `useCurrentFrame`; no CSS transitions, timers or unseeded random. Check with `scripts/determinism.sh`.

## Pipeline

1. **Brief** (`templates/brief.md`): a production document, not a vibe. Real assets, hard line against invented screens or metrics.
2. **Reference** (`templates/style_guide.md`): extract frames from a clip you like, write down palette/type/timing. Borrow grammar, never subjects or copy.
3. **Shot list** (`templates/shotlist.md`): beats with entry state, exit state and a reason to exist. Write each shot as an event with frame numbers.
4. **Stills first**: `bash scripts/stills.sh sheet1 0 90 180` tiles single frames into a contact sheet. Review order: 3 stills, then boundary frames of a cut, then full playback. Fix order: missing/unreadable info, timing, visual detail.
5. **Sound on the same clock**: `scripts/synth_helpers.py` for a procedural score and SFX (every sound faded in/out), or measure a supplied track with `scripts/beats.py` and put state changes on beats, big moments on downbeats.
6. **Critic loop** (`templates/critic-prompt.md`): a fresh agent scores the contact sheet and phone sheet; fix the worst 3; repeat until every score is 8+.
7. **QA + deliver** (`templates/render-checklist.md`): determinism, blank-frame check, phone test, loop check, one 1080p file.

Drop `templates/CLAUDE.video.md` into the project root as `CLAUDE.md` so the house rules never need repeating. Keep a `TASKS.md` so a new session can resume after a usage limit. One session (or one project folder) per brand: the renderer, audio synth and export pipeline carry over.

## Rules that came out of real cuts

- 30-45 s for a showreel, never rushed: captions 3-5 s, data boards fill then HOLD ~4 s.
- Last frame is a finished poster/lockup, never a fade to black. No blank space in any frame.
- Beat-synced motion must be gentle (one smooth swell per bar). A per-beat scale bounce reads as jarring.
- Ticking on hits means a missing fade. Fade every sound 2 ms in, 8 ms out.
- Voiceover: OS text-to-speech ignores pronunciation hints; use a neural TTS with a style prompt, split lines at pauses, cue each phrase to its visual, duck music under speech.
- X/Twitter autoplays muted: burn in 2-4 word captions; videos 10 s max; scrubbed sample data only.
- Custom three.js ShaderMaterials need `#include <colorspace_fragment>`, linearized hand-written colors and double-sided ribbons, or colors go muddy and geometry vanishes.

## Screen-capture promos (real app footage)

Run the real app on sanitized sample data (never live data). Capture frame-stepped with Playwright on GPU Chrome (virtual clock, step CSS animations via the Web Animations API) so moves are deterministic. Capture each aspect ratio separately (16:9 and 1:1 with their own framing); never crop or letterbox. Compose in Remotion: drawn cursor, click ripples, burned-in captions, logo end card.

Supplied music: measure with ffprobe (files are often mislabeled or too long), find the drop with numpy RMS, cut on a bar boundary, fade out in numpy.

## Motion numbers (1920x1080)

| Effect | Defaults |
|---|---|
| cursor click | curved move 1.1 s, arc 150 px, power2.inOut; press scale 0.94 / 0.12 s; ripple 2.4x over ~0.5 s; land INSIDE the button |
| typing | irregular gaps 0.07-0.17 s, caret half-period 0.24 s, last 0.6 s still |
| count-up | 1.0-2.0 s power2.out, 0.3 s zero-hold first, unit appears ~0.35 s after arrival |
| zoom callout | 3.6-4.5x, circle ~330 px, appear 0.85 s power3.out; magnified value must equal source |
| spotlight | dim others to 0.25 over 0.65 s |
| ken burns | scale 1.12 over ~2.2 s, linear |

## Deliverable

H.264 + AAC 192k, yuv420p, `-movflags +faststart`, ~20 MB. Example:

```
ffmpeg -i raw.mp4 -c:v libx264 -crf 24 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart final.mp4
```

## Where code loses

Photoreal scenes, complex characters and organic movement still want footage or a video model. Code wins for product films, UI motion, data stories, typography and launch explainers.
