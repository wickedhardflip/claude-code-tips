# Claude Code Tips & Tricks

Practical shortcuts, configs, and workflows for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — the CLI for Claude from Anthropic.

Whether you're setting up for the first time or looking to level up your workflow, everything here is copy-paste ready.

> **Contributions welcome** — open a PR to add your own tips.

---

## Prerequisites

| Tool | Install | Verify |
|---|---|---|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | `claude --version` |
| **Node.js** (v18+) | [nodejs.org](https://nodejs.org) | `node --version` |
| **PowerShell 7+** (Windows tips) | `winget install Microsoft.PowerShell` | `pwsh --version` |
| **GitHub CLI** (optional) | `winget install GitHub.cli` | `gh --version` |

Already have Claude Code running? Skip to [Tips](#tips).

---

## Tips

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

See your model, directory, and rate-limit usage at a glance with color-coded meters and reset countdowns.

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

### 3. Project Instructions with `CLAUDE.md`

Drop a `CLAUDE.md` in any project root. Claude reads it automatically at session start and follows the instructions every time.

```markdown
# Project Instructions

- Use TypeScript strict mode
- Tests live in __tests__/ next to source files
- Run `npm run lint` before committing
- Deploy flow: staging first, then production
- Never commit .env files
```

You can also nest them — a `CLAUDE.md` in a subdirectory applies when working in that subtree.

---

### 4. Pipe Anything into Claude

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

### 5. Session Management

| Command | What it does |
|---|---|
| `claude --resume` | Pick up your most recent session |
| `claude --continue` | Continue last conversation (no selection prompt) |
| `/clear` | Reset conversation context mid-session |
| `/compact` | Compress context to free up token space |
| `/cost` | Show token usage and cost for this session |

---

### 6. Switch Models on the Fly

```
/model              # Pick from available models
/fast               # Toggle fast mode (same model, faster output)
```

Fast mode uses Opus with optimized output speed — it does not downgrade to a smaller model.

---

### 7. Useful Settings

Edit with `claude /config` or directly in `~/.claude/settings.json`:

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

## Quick Reference

| Action | Command |
|---|---|
| Start interactive session | `claude` |
| Start with a prompt | `claude "do the thing"` |
| One-shot (run and exit) | `claude -p "do the thing"` |
| Resume last session | `claude --resume` |
| Continue last session | `claude --continue` |
| Switch model | `/model` |
| Toggle fast mode | `/fast` |
| Check usage/cost | `/cost` |
| Compress context | `/compact` |
| Clear context | `/clear` |
| Open settings | `/config` |

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

---

## Contributing

Found a tip that saves you time? Open a PR. Keep it practical — show the problem, then the solution.

## License

[MIT](LICENSE)
