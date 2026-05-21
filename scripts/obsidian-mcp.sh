#!/usr/bin/env bash
set -euo pipefail

api_key="${OBSIDIAN_LOCAL_REST_API_KEY:-${OBSIDIAN_API_KEY:-}}"

if [[ -z "$api_key" ]]; then
  cat >&2 <<'EOF'
Missing Obsidian Local REST API key.

Set one of:
  OBSIDIAN_LOCAL_REST_API_KEY
  OBSIDIAN_API_KEY

Find the key in Obsidian Settings -> Local REST API.
EOF
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  cat >&2 <<'EOF'
Missing python3.

Install Python 3 first, then try again.
EOF
  exit 1
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$script_dir/obsidian_mcp_server.py"
