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
  - [8. Offload to Local Models with Ollama](#8-offload-to-local-models-with-ollama)
  - [9. Prompt Contract for Delegated Work](#9-prompt-contract-for-delegated-work)
  - [10. Memory System](#10-memory-system)
  - [11. Pipe Anything into Claude](#11-pipe-anything-into-claude)
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

### 8. Offload to Local Models with Ollama

If you run [Ollama](https://ollama.com) locally, you can connect it to Claude Code via an MCP server and delegate token-heavy tasks to a free local model — file reading, code review, boilerplate generation, test scaffolding.

**The savings are real:** Delegating a file read to Ollama instead of having Claude read it directly saves ~75–90% of tokens on that task. The file contents never enter Claude's context window.

**What to delegate:**

| Send to Ollama | Keep in Claude |
|---|---|
| File reading/summarizing | Architecture & design decisions |
| Boilerplate generation (CRUD, models, templates) | Multi-step debugging |
| First-pass code review / lint | Anything needing Claude's tools (git, search, edit) |
| Test scaffolding | Security-sensitive analysis |
| Mechanical refactors | Final review of Ollama's output |
| Verbose explanations | Complex logic where reasoning quality matters |

**Key rule:** Ollama output is always a draft. Review it before committing — in our experience, early on it needed corrections every time. With the prompt contract below, it improved to near-mergeable on first pass.

**Setup:** Install an MCP server that bridges Claude to Ollama (like [OllamaClaude](https://github.com/search?q=ollama+claude+mcp)). Configure it in your Claude settings and test with a simple file review.

---

### 9. Prompt Contract for Delegated Work

When delegating to a local model, inconsistent output wastes more time than it saves. We developed a rules preamble through trial and error — each rule exists because we hit that specific failure mode.

**Paste this into every delegated task:**

```
RULES:
1. Output ONLY what was asked. No preamble, no "Here is...", no closing summary.
2. Code output: a single fenced block, no prose. Prose output: bullets only.
3. NEVER invent imports, function names, fixtures, or attributes. If you need
   something not in the context, write TODO(claude): <what you need> instead.
4. Match the existing file's style exactly: import order, quote style, type hints.
5. Yes/no questions: verdict line FIRST, then at most 5 supporting bullets.
6. Do not restate my question back to me.
7. If less than 80% confident, say UNCERTAIN: <why> instead of bluffing.
8. When I say "prefer X over Y", use X. Don't substitute Y because it's familiar.
9. When monkeypatching, capture the original in a local variable FIRST.
10. List every import your generated code needs. Re-read and check each name.
11. For each test, re-read the spec and confirm the assertion matches —
    especially fallback cases and dict-vs-list fixture shapes.
```

**Why each rule exists:**

| Rule | Failure it prevents |
|---|---|
| 3 | Invented imports that don't exist in the repo |
| 7 | Confident-sounding wrong answers |
| 8 | Ignored explicit "prefer X" instructions |
| 9 | Self-recursive monkeypatch (patched `time.time` referencing `time.time`) |
| 10 | Generated code missing critical imports |
| 11 | Test assertions contradicting the spec |

**Track your own failures.** When the local model makes a new mistake, add a rule. The preamble is a living document — ours went from 7 rules to 11 in two days, and the correction rate dropped to near zero.

---

### 10. Memory System

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

### 11. Pipe Anything into Claude

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
└── LICENSE
```

---

## Resources

- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code) — Official documentation
- [Claude Code GitHub](https://github.com/anthropics/claude-code) — Report issues, check releases
- [Ollama](https://ollama.com) — Run local models for delegation

---

## Contributing

Found a tip that saves you time? Open a PR. Keep it practical — show the problem, then the solution.

## License

[MIT](LICENSE)
