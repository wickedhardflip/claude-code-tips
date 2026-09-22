# Claude Code custom status line (PowerShell)
# Shows: model | directory | 5-hour usage | 7-day usage | spend limit
# Color-coded: green < 50%, yellow 50-74%, red 75-89%, bright red 90%+
#
# Install:
#   1. Copy this file to ~/.claude/statusline.ps1
#   2. Add to ~/.claude/settings.json:
#      "statusLine": {
#        "type": "command",
#        "command": "pwsh -NoProfile -File \"C:/Users/YourName/.claude/statusline.ps1\""
#      }

$ErrorActionPreference = 'SilentlyContinue'
$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }
try { $d = $raw | ConvertFrom-Json } catch { exit 0 }

[Console]::OutputEncoding = New-Object Text.UTF8Encoding $false
$e = [char]27
function Paint([string]$code, [string]$text) { "$e[${code}m$text$e[0m" }

function UsageColor([double]$p) {
  if ($p -ge 90) { '1;31' }
  elseif ($p -ge 75) { '31' }
  elseif ($p -ge 50) { '33' }
  else { '32' }
}

function Bar([double]$p) {
  $filled = [math]::Min(5, [math]::Max(0, [math]::Round($p / 20)))
  ([string][char]0x2588 * $filled) + ([string][char]0x2591 * (5 - $filled))
}

function ResetLabel([double]$epoch) {
  $t   = [DateTimeOffset]::FromUnixTimeSeconds([long]$epoch).ToLocalTime().DateTime
  $now = Get-Date
  if ($t -le $now) { return 'now' }
  $clock = $t.ToString('h:mmtt').ToLower() -replace 'm$', ''
  if ($t.Date -eq $now.Date) { return $clock }
  if ($t.Date -eq $now.Date.AddDays(1)) { return "tmrw $clock" }
  return "$($t.ToString('ddd')) $clock"
}

function Window([string]$label, $w) {
  if ($null -eq $w) { return $null }
  $p = [double]$w.used_percentage
  $txt = "$label $(Bar $p) $([math]::Round($p))%"
  if ($w.resets_at) { $txt += " " + [char]0x21BB + (ResetLabel $w.resets_at) }
  Paint (UsageColor $p) $txt
}

$parts = @()

if ($d.model.display_name) { $parts += Paint '36' $d.model.display_name }

if ($d.workspace.current_dir) {
  $dir = Split-Path -Leaf $d.workspace.current_dir
  if ($dir) { $parts += Paint '34' $dir }
}

$rl = $d.rate_limits
if ($rl) {
  $s = Window '5h' $rl.five_hour;     if ($s) { $parts += $s }
  $w = Window '7d' $rl.seven_day;     if ($w) { $parts += $w }
  $l = Window '$'  $rl.spend_limit;   if ($l) { $parts += $l }
}
if (-not $rl -or (-not $rl.five_hour -and -not $rl.seven_day -and -not $rl.spend_limit)) {
  $parts += Paint '90' 'usage n/a'
}

[Console]::Out.Write(($parts -join (Paint '90' ' | ')))
