#!/usr/bin/env bash
set -euo pipefail

echo "[ci] Discovering all package.json projects and running npm test where defined..."

# Find all package.json files and extract their directories, excluding tasks/ (external repos)
# Build a unique list of directories in a robust way (handles spaces in paths)
dirs=()
while IFS= read -r -d '' f; do
  d=$(dirname "$f")
  skip=0
  for x in "${dirs[@]}"; do
    if [ "$x" = "$d" ]; then
      skip=1
      break
    fi
  done
  if [ $skip -eq 0 ]; then
    dirs+=("$d")
  fi
done < <(find . -path "./tasks" -prune -o -name "package.json" -print0)

exit_code=0
for d in "${dirs[@]}"; do
  if [ -f "$d/package.json" ]; then
    if grep -q '"test"' "$d/package.json"; then
      echo "[ci] Running tests in $d"
      (cd "$d" && npm ci --silent && npm test --silent) || {
        echo "[ci] Tests failed in $d";
        exit_code=1
        # do not break the loop immediately; collect all failures
      }
    else
      echo "[ci] No test script found in $d; skipping"
    fi
  fi
done

exit "$exit_code"
