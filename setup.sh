#!/usr/bin/env sh
# Cognis guided setup wizard — one-line bootstrap (POSIX / macOS / Linux / WSL / git-bash).
#
#   ./setup.sh                 # launch the guided, numbered-menu wizard
#   ./setup.sh --dry-run       # show every command, never run it
#   ./setup.sh --manifest URL  # point at a specific MANIFEST.json (path or http(s) URL)
#
# Stdlib-only Python — nothing to install. Picks the first available interpreter.
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
WIZARD="$DIR/cognis_setup.py"

# Pick the first interpreter that actually runs (skip the Windows Store shim,
# which is on PATH as `python`/`python3` but only prints an install nag).
PY=""
for c in python3 python py "/c/Python314/python.exe" "/c/Python313/python.exe"; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; sys.exit(0)" >/dev/null 2>&1; then
    PY="$c"; break
  fi
done

if [ -z "$PY" ]; then
  echo "Cognis setup needs Python 3 (stdlib only). Install Python and re-run ./setup.sh" >&2
  exit 1
fi

exec "$PY" "$WIZARD" "$@"
