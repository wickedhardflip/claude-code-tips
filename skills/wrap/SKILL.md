---
name: wrap
description: Use when the user types /wrap or asks to wrap up, save progress, or checkpoint the session before stopping, rebooting, or switching tasks.
disable-model-invocation: true
---

# Wrap

Checkpoint the session so a fresh session can resume with no scrollback. Capture state in the places that already exist, commit local repo work, and report.

Work through every step. A step with nothing to do gets one line in the report ("Journal: n/a, no journal in this workspace").

## 1. Inventory (no writes yet)

Note, from this conversation:
- **Projects touched:** each directory where files were created or edited.
- **Decisions:** what was chosen, and why it matters later.
- **State:** what's done, what's in progress, what's blocked (and on what).
- **Next step:** the single concrete action to resume with.
- **Loose ends:** background tasks/servers/downloads still running; actions waiting on the user (reboot, login, approval).

## 2. Memory

Use the memory directory and format from the system prompt.
- Update the existing file for a project or topic. Create a new one only for a genuinely new fact, preference, or project.
- Save user preferences and corrections as `feedback` memories, with **Why** and **How to apply**.
- Store absolute dates, never "today" or "tomorrow".
- Keep the `MEMORY.md` index in sync: one line per file, no duplicates.
- Skip anything the repo, docs, or git history already record.

## 3. Project resume docs

For each project touched, update the resume docs it **already has**: `NEXT.md`, `TASKS.md`, `CONTEXT.md`, plan files with checkboxes, and status sections in a project `CLAUDE.md`.
- Tick finished items and add newly found ones.
- Move the **← START HERE** marker (or equivalent) to the next step.
- Record blockers and exactly how to clear them.

If a project had multi-step work but no resume doc, create `TASKS.md` at its root. Otherwise create nothing new.

## 4. Journal

If the workspace has `logs/journal.md`, append one dated entry (`## YYYY-MM-DD: <topic>`): 3–6 bullets covering decisions, progress, blockers, and the resume pointer.

## 5. Git (every repo touched)

For each touched directory inside a git repo:
1. `git status`. Read `.gitignore` if unsure what belongs.
2. Stage **only files from this session's work**, by explicit path. Never `git add -A`/`.`.
3. Never stage secrets: `.env`, keys, tokens, credential or config files with passwords. If one shows as modified, leave it out and flag it in the report.
4. Commit on the current branch with a clear message and the session's attribution lines.
5. **Never push.** Never force, amend, or rebase.
6. Report unrelated uncommitted changes you left alone.

A repo that is public (per memory or CLAUDE.md) gets an extra secrets check of the staged diff before committing.

## 6. Loose ends

Stop background tasks that shouldn't outlive the session (servers, watchers), unless the user wants them running. Leave user-started processes alone. List everything still running or pending.

## 7. Report (this exact shape)

```
**Wrapped.**
- Memory: <files created/updated, or n/a>
- Docs: <files updated, or n/a>
- Journal: <entry added, or n/a>
- Git: <repo: commit hash + message | nothing to commit | not a repo>
- Still running / needs you: <items, or none>

**To resume:** say "<short phrase>". Starts at <file / next step>.
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Creating a new notes file when a NEXT.md/TASKS.md exists | Update the existing doc |
| `git add .` sweeps in unrelated or secret files | Stage explicit paths from this session only |
| Pushing "since it's committed anyway" | Never push; the user pushes |
| Memory duplicates an existing file | Search the memory dir first; update in place |
| Relative dates ("tomorrow") in memory/docs | Convert to YYYY-MM-DD |
| Skipping a step silently | Every step appears in the report, even as n/a |
