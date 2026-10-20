---
name: tokenwatch
description: Report Claude Code token burn and cost, and say what to change next. Use whenever the user asks how we are doing on tokens, cost, spend, or burn - "how are we doing", "how's our token usage", "are we saving anything", "check spend", "is the autocompact working", "did offload fire". Also use before and after changing any cost-related setting (autoCompactWindow, effort, model, CLAUDE_CODE_SUBAGENT_MODEL) so the change is measured rather than assumed.
---

# Token usage check

Measures what actually happened from Claude Code's own transcripts. Answer first, then
recommend. Do not make up figures: every number comes from the script.

## Run it

```bash
python <path-to>/token-usage-report.py --days 7
```

`--days 1` for a same-day check after a settings change. `--project <name>` to limit it to
one project folder. `--no-log` to skip appending to `token-usage-history.csv`. Every run
without `--no-log` appends rows, and that CSV is the only lasting record: Claude Code deletes
transcripts after `cleanupPeriodDays` (30 by default).

For trend, read `token-usage-history.csv` and compare `usd_per_turn` by `run_date`.
**`$/turn` is the metric that matters**, not total spend. Total moves with how much work got
done that week; `$/turn` shows whether the configuration is working.

## Reading the result

Diagnose from the cost composition, then name one change.

- **cache_read is the largest line and session ctx_avg is high** - context is growing
  unchecked, and every turn re-reads it. Set `autoCompactWindow` in `~/.claude/settings.json`
  (try 300000, then 200000) and use `/clear` between unrelated tasks. `/clear` costs nothing;
  `/compact` is itself a large request.
- **cache_write is high** - new context is written to cache at a premium (1-hour writes cost
  2x input) and then re-read every turn. Split the cause before acting:
  - big rewrites with no idle gap are compaction: the window is too tight; raising it trades
    fewer rewrites for more re-reads, so measure both;
  - big rewrites after an hour or more idle are cache expiry: `/clear` or finish before
    walking away from a large session;
  - steady per-turn growth is tool output: trim with `head`, `--limit`, targeted reads, or
    hand bulky work to a subagent.
- **output above ~25%** - thinking and text. Lower effort for routine work (`/effort`).
- **subagent turns near 0 while work had separable bulk** - offload is not firing. Check
  that `CLAUDE_CODE_SUBAGENT_MODEL` is set (otherwise subagents inherit the main model and
  save nothing) and that `CLAUDE.md` tells Claude when to delegate.
- **expensive-model subagent turns** - usually a fork (forks inherit the parent model) or an
  agent definition that pins a model. Name the sessions and ask whether it was intended.

## When a model is missing

The warning names any model absent from the `PRICES` table in the script; those turns are
left out of totals. Add current rates from the `claude-api` skill or Anthropic's pricing
page, not from memory.
