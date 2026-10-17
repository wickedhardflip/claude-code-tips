# Render checklist

Gates (an agent can run for hours between them; a missing asset or unclear reference is a blocker, ask first):

- [ ] GATE 1  references + real assets approved (brief.md)
- [ ] GATE 2  style_guide.md + shotlist.md approved
- [ ] GATE 3  stills for every shot, critiqued (`bash scripts/stills.sh sheet1 0 90 180 ...`)
- [ ] GATE 4  rough animatic (small size, placeholder audio) watched
- [ ] GATE 5  full pass, polish, sound
- [ ] GATE 6  formats, QA, poster frame, README

## QA before showing anything
- [ ] `bash scripts/determinism.sh 300`: same frame twice, same hash
- [ ] `python scripts/qa.py blank out/video.mp4`: no flat/empty frames, last frame not black
- [ ] `python scripts/qa.py sheet out/video.mp4` then run critic-prompt.md on it, fix the worst 3
- [ ] `python scripts/qa.py phone out/video.mp4`: still readable at 360 px wide
- [ ] `python scripts/qa.py loop out/video.mp4` (loops only)
- [ ] Blindfold test: listen with eyes closed; audio should have shape on its own
- [ ] No ticking on hits (every sound faded in/out); music ducked under speech

## Deliver
ONE 1080p file, H.264 + AAC 192k, yuv420p, `-movflags +faststart`, about 20 MB (crf 24-26 for 16:9, 21 for 1:1).
Keep approved render + brief + timeline + cue list together. X videos: 10 s max, scrubbed sample data only.
