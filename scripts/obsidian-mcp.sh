#!/usr/bin/env bash
set -euo pipefail

api_key="${OBSIDIAN_LOCAL_REST_API_KEY:-${OBSIDIAN_API_KEY:-}}"
server_url="${OBSIDIAN_LOCAL_REST_API_URL:-https://127.0.0.1:27124/mcp/}"

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

if ! command -v npx >/dev/null 2>&1; then
  cat >&2 <<'EOF'
Missing npx.

Install Node.js first, then try again.
EOF
  exit 1
fi

args=("mcp-remote@latest" "$server_url" "--header" "Authorization: Bearer $api_key")

if [[ "$server_url" == http://* ]]; then
  args+=("--allow-http")
fi

if [[ "${OBSIDIAN_ALLOW_SELF_SIGNED_CERT:-}" == "1" ]]; then
  export NODE_TLS_REJECT_UNAUTHORIZED=0
fi

exec npx -y "${args[@]}"
