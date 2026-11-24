#!/usr/bin/env bash
# Check the code and protocol files against the hashes recorded just before the locked IDD-3D test run.
set -euo pipefail
cd "$(dirname "$0")"
MAN=results/idd3d/out_idd_test_freeze/FROZEN.txt
SUM=$(command -v sha256sum || echo "shasum -a 256")
ok=0; bad=0
while read -r h f; do
  [[ "$h" =~ ^[0-9a-f]{64}$ ]] || continue
  if [ "$($SUM "$f" | awk '{print $1}')" = "$h" ]; then echo "OK       $f"; ok=$((ok+1)); else echo "CHANGED  $f"; bad=$((bad+1)); fi
done < "$MAN"
echo "$ok unchanged, $bad changed (paths edited for your machine count as changed)"
