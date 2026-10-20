# Weekly Maintenance

The weekly maintenance reminder (section 20) reads this file. Each `##` section is one item.
Add or remove items here; the reminder prompt does not need to change.

Rules for every item: ask before running, change nothing beyond what the item says, report
results briefly, close with what needs a decision.

**Local only:** items read memory files and local disk. No SSH, APIs, databases, or other
remote systems unless an item says so. Memory dir = `~/.claude/projects/<project>/memory/`.
Never print secret values; name the credential only.

---

## 1. Context & token review

a) Run the tokenwatch skill (7 days). Compare $/turn by lane, subagent share, and cost
   composition against previous rows in `token-usage-history.csv`.
b) Look at what we have been doing: the heaviest sessions, whether subagents fired where
   they should have, any use of the most expensive model and whether it was intended, and
   the size of `MEMORY.md`.
c) Check the official Claude Code docs for new or changed features relevant to context and
   cost: compaction, caching, subagents, skill and plugin loading, settings, model and effort
   options.
d) Report what moved since last week, then at most 3 concrete improvements, each with the
   expected effect and any function it might cost. Change nothing without approval.

## 2. Due-date sweep

Grep memory files for dates (`YYYY-MM-DD`, "due", "owed", "by", "ends", "expires").
List every item that is overdue or due in the next 14 days: date, what, memory file.
Overdue first. Skip dates that are only history (e.g. "set up on").

## 3. Temporary changes still open

From memory only, list every change marked TEMP, temporary, "revert when", "until", PAUSED,
or PINNED: what it is, why it was left, what ends it, and how long it has been open.

## 4. Credential rotations owed

List rotations still marked owed in memory: credential name, where exposed, date noted.
Names only, never values. One local check: for git repos in the workspace (depth 2), report
which `.git/config` files still contain a credential in a remote URL
(pattern `https://[^/@]+@github.com`). Report the path only, never the matched text.

## 5. Waiting on you

Grep memory for items blocked on you ("waiting on", "your OK", "your decision", "sign-off",
"NOT merged", "owed:"). List each: what, what is needed, since when, memory file. Group by
project.

## 6. Leftover worktrees and branches

For git repos in the workspace (depth 2), run read-only local commands only:
`git worktree list`, `git branch --merged <main>`, `git branch -vv` (look for `: gone]`),
branches with no commits in 30+ days. No fetch, no prune, no removal. Report per repo and say
whether memory marks each leftover as Claude's own (removable with approval) or someone
else's (leave alone).

## 7. Memory hygiene

Compare `MEMORY.md`'s active-project lines with their topic files. Propose archiving any
project whose file says done, closed, parked, or superseded, and any index line that is stale
against its file. Report `MEMORY.md` size against your budget. Propose only; move nothing
without approval, and move rather than delete.
