#!/usr/bin/env bash
# usage: bash determinism.sh [frame]  - render the same frame twice; the hashes must match.
f=${1:-300}
for n in a b; do
  npx remotion still "${ENTRY:-src/index.ts}" "${COMP:-Reel}" "out/det_$n.png" --frame="$f" --gl=angle --log=error >/dev/null 2>&1
done
if [ "$(sha256sum out/det_a.png | cut -d' ' -f1)" = "$(sha256sum out/det_b.png | cut -d' ' -f1)" ]; then
  echo "OK: frame $f is deterministic"
else
  echo "FAIL: frame $f differs between renders (look for Math.random, Date.now, CSS transitions, setTimeout)"
  exit 1
fi
