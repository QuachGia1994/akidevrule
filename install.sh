#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# `python3` may resolve to an old interpreter (seen on a deploy host: 3.7), so pick the newest one meeting the floor rather than whatever is first on PATH.
for _py in python3.14 python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3 python; do
  if command -v "$_py" >/dev/null 2>&1 \
    && "$_py" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)' 2>/dev/null; then
    exec "$_py" "$DIR/install.py" "$@"
  fi
done

echo "akidevrule: Python 3.7+ is required but none was found on PATH." >&2
exit 1
