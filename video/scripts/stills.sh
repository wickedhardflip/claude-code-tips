#!/usr/bin/env bash
# usage: bash stills.sh <sheetname> <frame> [frame...]
# Renders single Remotion frames to out/f<N>.png, then tiles them into out/<sheetname>.png.
# Env: ENTRY (default src/index.ts), COMP (default Reel)
name=$1; shift
for f in "$@"; do
  npx remotion still "${ENTRY:-src/index.ts}" "${COMP:-Reel}" "out/f$f.png" --frame="$f" --gl=angle --log=error 2>&1 | grep -v "^$" | tail -2
done
python "$(dirname "$0")/sheet.py" "$name" "$@"
