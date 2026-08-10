#!/usr/bin/env bash
# Transitional Unix wrapper — the Python file is the SSOT (cross-platform, incl. Windows).
# Kept so existing prompts/docs that name "council-open.sh" keep working on Unix during the transition.
exec python3 "$(dirname "$0")/council_open.py" "$@"
