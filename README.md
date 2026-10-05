# Claude Code Tips & Tricks

Practical shortcuts, configs, and workflows for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — the CLI for Claude from Anthropic.

These aren't just documentation repackaged. They're patterns we've developed and refined through daily use — things that actually changed how we work.

> **Contributions welcome** — open a PR to add your own tips.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- **Setup & Launch**
  - [1. Quick Launch with `cc`](#1-quick-launch-with-cc)
  - [2. Custom Status Line](#2-custom-status-line)
  - [3. Workspace Folder Pattern](#3-workspace-folder-pattern)
- **Configuration**
  - [4. Project Instructions with `CLAUDE.md`](#4-project-instructions-with-claudemd)
  - [5. Security Policy in `CLAUDE.md`](#5-security-policy-in-claudemd)
  - [6. Permission Allowlists](#6-permission-allowlists)
  - [7. Useful Settings](#7-useful-settings)
- **Workflow**
  - [8. Memory System](#8-memory-system)
  - [9. Pipe Anything into Claude](#9-pipe-anything-into-claude)
  - [10. `/wrap`: Checkpoint a Session](#10-wrap-checkpoint-a-session)
  - [12. Mods: Info That Doesn't Scroll Away](#12-mods-info-that-doesnt-scroll-away)
  - [13. Lazy Senior Dev: Write Less Code](#13-lazy-senior-dev-write-less-code)
- [Quick Reference](#quick-reference)
- [Resources](#resources)

---

## Prerequisites

| Tool | Install | Verify |
|---|---|---|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | `claude --version` |
| **Node.js** (v18+) | [nodejs.org](https://nodejs.org) | `node --version` |
| **PowerShell 7+** (Windows tips) | `winget install Microsoft.PowerShell` | `pwsh --version` |
| **GitHub CLI** (optional) | `winget install GitHub.cli` | `gh --version` |

Already have Claude Code running? Skip to [Tips](#1-quick-launch-with-cc).

---

## Setup & Launch

### 1. Quick Launch with `cc`

Launch Claude Code in your project folder from anywhere in your terminal. When the session ends, you're back where you started.

<details>
<summary><strong>PowerShell (Windows)</strong></summary>

1. Open your profile:

   ```powershell
   notepad $PROFILE
   ```

   If the file doesn't exist, say yes when prompted to create it.

2. Add this function — **change the path** to your own project folder:

   ```powershell
   function CC {
     Push-Location "C:\Users\YourName\YourProjectFolder"
     claude @args
     Pop-Location
   }
   ```

3. Reload:

   ```powershell
   . $PROFILE
   ```

</details>

<details>
<summary><strong>Bash / Zsh (macOS, Linux)</strong></summary>

Add to `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`:

```bash
cc() {
  pushd ~/your-project-folder > /dev/null
  claude "$@"
  popd > /dev/null
}
```

Then reload: `source ~/.bashrc` (or `~/.zshrc`).

</details>

**Usage:**

```
cc                          # Interactive session in your project folder
cc "fix the login bug"      # Start with a prompt
cc --resume                 # Resume last session
cc --continue               # Continue last conversation
```

All `claude` flags work — `cc` just forwards everything.

**Why a dedicated folder?** Claude Code reads `CLAUDE.md` from the working directory for project-specific instructions. A consistent launch folder means your preferences, conventions, and context load every time.

---

### 2. Custom Status Line

Replace the default status line with one that shows your model, directory, and rate-limit usage at a glance — with color-coded meters and reset countdowns.

```
Claude Opus 4.6 | my-project | 5h ████░ 78% ↻2:15p | 7d ██░░░ 42% ↻Mon 8a
```

| Color | Usage |
|---|---|
| Green | Under 50% |
| Yellow | 50–74% |
| Red | 75–89% |
| Bright red | 90%+ |

**Setup (PowerShell / Windows):**

1. Copy [`scripts/statusline.ps1`](scripts/statusline.ps1) to your Claude config folder:

   ```powershell
   Copy-Item scripts\statusline.ps1 "$HOME\.claude\statusline.ps1"
   ```

2. Open your Claude Code settings:

   ```
   claude /config
   ```

   Or edit `~/.claude/settings.json` directly. Add:

   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "pwsh -NoProfile -File \"C:/Users/YourName/.claude/statusline.ps1\""
     }
   }
   ```

   Replace `YourName` with your Windows username.

3. Restart Claude Code. The new status line appears at the bottom.

> **Bash/Zsh port:** Not yet available — the same logic applies using `jq` for JSON parsing and standard ANSI escapes. PRs welcome!

---

### 3. Workspace Folder Pattern

Instead of scattering projects everywhere, create a single workspace folder that Claude always launches into. This becomes your hub — projects, logs, config, and context all live here.

**Recommended structure:**

```
~/claude-workspace/
├── CLAUDE.md           # Global instructions (loaded every session)
├── .claude/            # Claude-specific config
├── logs/
│   └── journal.md      # Decision log — key choices, not every detail
├── screenshots/        # Visual documentation
├── project-a/          # Your projects as subdirectories
│   └── CLAUDE.md       # Project-specific instructions (layered on top)
├── project-b/
│   └── CLAUDE.md
└── docs/               # Shared references, conventions
```

**Why this works:**
- Your root `CLAUDE.md` applies to everything — security policies, coding style, deployment conventions
- Each project gets its own `CLAUDE.md` that layers on top with project-specific rules
- The journal captures decisions you'd otherwise forget between sessions
- Screenshots land in a known place instead of your desktop

Pair this with the [`cc` shortcut](#1-quick-launch-with-cc) and you're always one command away from a fully-configured session.

---

## Configuration

### 4. Project Instructions with `CLAUDE.md`

Drop a `CLAUDE.md` in any project root. Claude reads it automatically at session start and follows the instructions every time.

```markdown
# Project Instructions

- Use TypeScript strict mode
- Tests live in __tests__/ next to source files
- Run `npm run lint` before committing
- Deploy flow: staging first, then production
- Never commit .env files
```

**The hierarchy:** Claude reads `CLAUDE.md` files at multiple levels and merges them:

1. `~/.claude/CLAUDE.md` — your personal global defaults
2. Your workspace root `CLAUDE.md` — shared team conventions
3. Subdirectory `CLAUDE.md` files — project-specific overrides

Lower levels override higher ones. Use this to set broad rules at the top and get specific as you go deeper.

---

### 5. Security Policy in `CLAUDE.md`

If you work with databases, APIs, servers, or anything with credentials, put a security policy in your `CLAUDE.md`. Claude follows it every session without you having to remind it.

**Example — credential management:**

```markdown
## Security Policy

### Rules
1. NEVER include passwords, API keys, or tokens in commands or output
2. ALWAYS use environment variables — `$env:PGPASSWORD`, not the actual value
3. ALWAYS redact credentials with `***` or `[REDACTED]` in examples
4. NEVER echo, print, or display credential values

### Credential Storage
- Use **Windows Credential Manager** (or your OS keychain) for secrets
- Access via PowerShell cmdlets / `security` CLI without exposing values
- Store with `cmdkey` or your platform's secure storage
```

**Why this matters:** Without this, Claude will sometimes put credentials in plain text in commands it shows you — especially database connection strings, API keys in curl commands, etc. One line in `CLAUDE.md` prevents it permanently.

---

### 6. Permission Allowlists

Tired of approving `git status` and `ls` every time? Add a permission allowlist so safe, read-only commands run without prompting.

Edit `.claude/settings.local.json` in your project (or `~/.claude/settings.json` for global):

```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(gh *)",
      "Bash(npm:*)",
      "Bash(node:*)",
      "Bash(python:*)",
      "Bash(ls:*)",
      "Bash(find:*)",
      "Bash(grep *)",
      "Bash(curl:*)",
      "Bash(ssh:*)",
      "Bash(scp:*)",
      "PowerShell(Test-Path *)",
      "PowerShell(Get-Content *)",
      "PowerShell(Get-ChildItem *)",
      "WebSearch"
    ]
  }
}
```

**Start conservative.** Add commands as you notice yourself approving the same ones repeatedly. You can always remove entries later.

**Pro tip:** Use `.claude/settings.local.json` (project-level, gitignored) for personal preferences and `.claude/settings.json` (committed) for team-shared permissions.

---

### 7. Useful Settings

Edit with `/config` inside a session or directly in `~/.claude/settings.json`:

```jsonc
{
  // Dark theme
  "theme": "dark",

  // Default to a specific model
  "model": "claude-sonnet-5",

  // Use fullscreen TUI mode
  "tui": "fullscreen",

  // Get push notifications when background tasks finish
  "agentPushNotifEnabled": true
}
```

---

## Workflow

### 8. Memory System

Claude Code has a built-in auto-memory feature that persists information across sessions. Instead of re-explaining who you are and how you work every time, teach it once.

**What to save:**
- Your role and expertise level (so explanations match your depth)
- Feedback on how Claude should work ("don't do X", "always do Y")
- Project context that isn't in the code (who's doing what, deadlines, decisions)
- Pointers to external resources (where bugs are tracked, which dashboards matter)

**What NOT to save:**
- Code patterns or architecture (derive from the code itself)
- Git history (use `git log`)
- Fix recipes (they're in the commits)
- Anything already in `CLAUDE.md`

**How it works:** Memory files live in `~/.claude/projects/<project>/memory/` with a `MEMORY.md` index. Each memory is a small markdown file with frontmatter for type and description.

**Example memories:**

```markdown
# feedback: no trailing summaries
Don't summarize what you just did at the end of every response — I can read the diff.

# feedback: delegate research
Always look for opportunities to offload research and brainstorming to local
models or free-tier APIs to save tokens.

# project: merge freeze
Merge freeze begins 2026-03-05 for mobile release cut. Flag any non-critical
PR work scheduled after that date.
```

**Pro tip:** Tell Claude to remember things as you go — "remember that I prefer single PRs for refactors" — and it saves a memory file automatically. Over time you build up a profile that makes every session start smarter.

---

### 9. Pipe Anything into Claude

Use `-p` (print mode) to send one-shot prompts and pipe in files, diffs, or logs:

```bash
# Explain a file
cat app.py | claude -p "explain this"

# Code review a diff
git diff | claude -p "review for bugs"

# Debug failing tests
npm test 2>&1 | claude -p "why are these failing?"

# Summarize recent logs
tail -100 errors.log | claude -p "what's going wrong?"
```

PowerShell equivalents:

```powershell
Get-Content app.py | claude -p "explain this"
git diff | claude -p "review for bugs"
Get-Content errors.log -Tail 100 | claude -p "what's going wrong?"
```

### 10. `/wrap`: Checkpoint a Session

Long sessions end with reboots, context limits, or "I'll finish tomorrow." `/wrap` is a custom skill that saves everything a fresh session needs to pick up where you left off:

- **Memory:** updates or creates memory files for new decisions and preferences, and keeps the `MEMORY.md` index in sync
- **Resume docs:** updates the `NEXT.md` / `TASKS.md` / `CONTEXT.md` files the project already has, and moves the "start here" marker
- **Journal:** appends a dated entry to `logs/journal.md` if you keep one
- **Git:** commits this session's files in every repo touched, staged by explicit path with a secrets check. **It never pushes.**
- **Loose ends:** stops background servers or watchers and lists anything waiting on you (reboot, login)
- **Report:** a fixed summary ending with the exact phrase to resume with

**Install** (works in every project):

```bash
mkdir -p ~/.claude/skills/wrap
curl -o ~/.claude/skills/wrap/SKILL.md https://raw.githubusercontent.com/wickedhardflip/claude-code-tips/master/skills/wrap/SKILL.md
```

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills\wrap" | Out-Null
Invoke-WebRequest https://raw.githubusercontent.com/wickedhardflip/claude-code-tips/master/skills/wrap/SKILL.md -OutFile "$HOME\.claude\skills\wrap\SKILL.md"
```

Then type `/wrap` at the end of a session. The skill sets `disable-model-invocation: true`, so it only runs when you ask for it.

### 12. Mods: Info That Doesn't Scroll Away

Mods are small plugins of function hooks that run inside Claude Code and put information in a fixed spot: the status line, or a band above the prompt. Three of ours are public in [claude-code-mods](https://github.com/wickedhardflip/claude-code-mods) (MIT), each written with Claude's help.

| Mod | What it shows | Where | Tokens? |
| --- | --- | --- | --- |
| `subagent-models` | Which model each subagent runs on, e.g. `agents: haiku-4-5 ✓, sonnet-5-5` | Status line | No |
| `session-recap` | 2-5 bullets on what the last prompt did, plus questions Claude is still waiting on | Band above prompt | One small Haiku call per prompt |
| `run-breakdown` | After a long run: model and effort for the main session, each subagent, and Gemini/Ollama calls | Band above prompt | No |

**Why:** a long run buries the question or result you need. Mixed model setups make it easy to lose track of what ran where.

**Requirements:** a Claude Code build with hook modules turned on. Built and tested on 2.1.287 on Windows.

**Try one for a session** (nothing saved):

```powershell
git clone https://github.com/wickedhardflip/claude-code-mods.git
claude --plugin-dir .\claude-code-mods\subagent-models
```

Repeat `--plugin-dir` to load several.

**Load them every session:** add `CLAUDE_CODE_PLUGIN_DIRS` to the `env` block of `~/.claude/settings.json`, folders separated by `;` on Windows or `:` on macOS/Linux, then open a new terminal.

```json
{
  "env": {
    "CLAUDE_CODE_PLUGIN_DIRS": "C:\path\to\claude-code-mods\subagent-models;C:\path\to\claude-code-mods\session-recap;C:\path\to\claude-code-mods\run-breakdown"
  }
}
```

Use your user settings, not a project's; project settings are ignored for this.

**Tips:**
- Try a mod with `--plugin-dir` first and add it to the always-on list only after it behaves.
- `run-breakdown` only appears after runs longer than `MIN_MS` (in `hooks/register.tsx`), and its Gemini/Ollama tool prefixes are specific to our setup, so change them to yours.
- To undo, remove the folder from `CLAUDE_CODE_PLUGIN_DIRS`.

Each mod's README in the repo has the details.

### 13. Lazy Senior Dev: Write Less Code

Agents tend to over-build: extra abstractions, new dependencies for five lines, helpers that already exist two files over. This `CLAUDE.md` section makes them check a short ladder before writing anything. It is adapted from [ponytail](https://github.com/DietrichGebert/ponytail) (MIT) by Dietrich Gebert, a full plugin for the same idea. We took only the prompt rules, with no hooks, and softened its output limit into a 4-line prose cap.

```markdown
## Code Style: Lazy Senior Dev

The best code is the code never written. Before adding code, stop at the first rung that holds:

1. **Needed at all?** Speculative need → skip it and say so in one line.
2. **Already in this codebase?** Reuse the existing helper/util/pattern. Grep before writing.
3. **Stdlib does it?** Use it.
4. **Native feature covers it?** HTML/CSS/HTMX over JS, DB constraint over app code.
5. **Installed dependency does it?** Use it. Never add a new one for a few lines.
6. **One line?** Write one line.
7. **Only then** write the minimum that works.

Understand the task and trace the real flow first; the ladder runs after that, not instead of it.

- **Bug fix = root cause.** Grep every caller before editing; fix once in the shared place, not per caller.
- **No unrequested abstractions:** no interface with one implementation, no config for a constant, no scaffolding "for later."
- **Ship the simple version** and question it in the same message ("Did X; Y covers it. Need full X?") instead of stalling.
- **Mark deliberate corner-cutting** with `# simplified: <ceiling>, <upgrade path>` so it's greppable later.
- Never trade away validation, error handling, security, or accessibility for brevity.
- **Prose cap: max 4 short lines** after code or a result. Longer only when I ask for a walkthrough, review, or report.
```

**Why each part helps:**
- **The ladder:** the cheapest code is the code you don't write, and reuse beats new code.
- **Root cause:** one fix in the shared function beats a patch in every caller.
- **`# simplified:` tags:** known shortcuts stay findable instead of becoming surprises.
- **Prose cap:** shorter replies cost fewer output tokens and are faster to read. Change the number to taste.

**Subagents:** add this to every subagent brief, since they don't always read your `CLAUDE.md`: "Reuse existing helpers; add no new dependencies or abstractions beyond what's asked; mark deliberate simplifications with `# simplified:`."

**Want the full thing?** ponytail adds hooks, intensity levels (`lite`/`full`/`ultra`), and `/ponytail-review`, `/ponytail-audit`, and `/ponytail-debt` commands, and works with many agents. See its [README](https://github.com/DietrichGebert/ponytail) and benchmarks. Its hooks run on every prompt and subagent start, so read them before installing.

**Try it:** paste this into Claude Code:

```text
Add the "Code Style: Lazy Senior Dev" section from section 13 of
https://github.com/wickedhardflip/claude-code-tips to my user-level CLAUDE.md
(~/.claude/CLAUDE.md). Show me the exact text before you write it, and don't
change anything else.
```

To undo, delete the section.

---

## Quick Reference

### Session Management

| Command | What it does |
|---|---|
| `claude --resume` | Pick up your most recent session |
| `claude --continue` | Continue last conversation (no selection prompt) |
| `/clear` | Reset conversation context mid-session |
| `/compact` | Compress context to free up token space |
| `/cost` | Show token usage and cost for this session |
| `/model` | Switch model mid-session |
| `/fast` | Toggle fast mode (same model, faster output) |
| `/config` | Open settings |

### Running Modes

| Command | What it does |
|---|---|
| `claude` | Interactive mode |
| `claude "prompt"` | Start with an initial prompt |
| `claude -p "prompt"` | One-shot — runs and exits |
| `claude -p "prompt" < file.txt` | One-shot with piped input |

---

## File Structure

```
claude-code-tips/
├── README.md              # This file
├── scripts/
│   └── statusline.ps1     # Custom status line script (PowerShell)
├── skills/
│   └── wrap/SKILL.md      # /wrap session checkpoint skill
└── LICENSE
```

---

## Resources

- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code) — Official documentation
- [Claude Code GitHub](https://github.com/anthropics/claude-code) — Report issues, check releases
- [claude-code-mods](https://github.com/wickedhardflip/claude-code-mods) — The mods from section 12
- [ponytail](https://github.com/DietrichGebert/ponytail) — Source of the ladder in section 13


---

## Contributing

Found a tip that saves you time? Open a PR. Keep it practical — show the problem, then the solution.

## License

[MIT](LICENSE)
