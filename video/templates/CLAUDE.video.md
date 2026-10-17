# Drop-in house rules for a video project (copy to the project root as CLAUDE.md)

## Render contract
- Everything is a pure function of the frame (`useCurrentFrame`). Frame N must render identically every time.
- No CSS transitions, setTimeout, requestAnimationFrame or Date.now in render code. Seeded noise only, never Math.random.
- Say GLOBAL vs scene-local frames; label fps.

## Look
- Banned: centered title on gradient, everything fading in, corner labels, glow on UI, blank space.
- One display face, one UI face, one accent. Something new on screen every 2-4 s. Holds 0.5 s+ after each move.

## Sound
- Score and SFX synthesized in code unless a track is supplied; every sound faded in/out; ducked under speech.

## Before you show me anything
- Render one frame per beat as a contact sheet, score it, fix the worst 3 (see templates/critic-prompt.md).
- Real assets only; never invent a product screen or a metric. If an asset is missing, stop and ask.

## Housekeeping
- Keep TASKS.md with a checklist so a new session can resume. Secrets in .env, referenced by name.
