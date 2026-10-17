# Critic prompt

Run this in a FRESH session or subagent (the builder doesn't grade itself). Give it brief.md, shotlist.md and the
contact sheet / phone sheet / boundary stills. Not the source code.

```
Judge only the rendered frames; ignore what the author meant to make.
Score 1-10: hook in 2 s, phone readability, motion, variety, sound sync, brand accuracy.
List the 3 worst defects, each with timestamp, evidence and a local fix. Max 5 frame-specific corrections.
Look for: overlapping text, blurry scaled type, elements sliding that should ease, corner labels,
a dead beat with nothing happening, blank/empty frames, a stutter at the loop point, a black last frame.
```

Builder then patches ONLY those seconds, re-renders them, and repeats until every score is 8+.

## Edit requests use 4 fields
where (frames) / what's wrong / what changes / WHAT STAYS FIXED. Build one scene, then stop for feedback.
