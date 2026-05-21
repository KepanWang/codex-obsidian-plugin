# Codex Obsidian Plugin

Connect Codex to your local Obsidian vault through the [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin.

This plugin is intentionally small: Obsidian owns the vault and REST API, the bundled MCP server exposes a focused tool layer to Codex, and the included Codex skill teaches Codex safer note-taking behavior.

## What It Does

- Searches and reads notes from your local Obsidian vault.
- Creates new Markdown notes.
- Updates existing notes with targeted edits.
- Uses your existing Obsidian Local REST API and Dataview setup.
- Keeps the Obsidian API key out of the repository.

## Requirements

- Codex with local plugin support.
- Obsidian running locally.
- The Obsidian Local REST API community plugin installed and enabled.
- Python 3 available as `python3`.
- An Obsidian Local REST API key.

Dataview is optional for this plugin, but it is useful when your vault already contains Dataview-powered project lists, indexes, and dashboards.

## Installation

Clone this repository into a local plugin directory:

```bash
mkdir -p ~/plugins
git clone git@github.com:KepanWang/codex-obsidian-plugin.git ~/plugins/codex-obsidian-plugin
```

Set your Obsidian Local REST API key:

```bash
export OBSIDIAN_LOCAL_REST_API_KEY="your-api-key"
```

The default Obsidian REST endpoint is:

```text
https://127.0.0.1:27124
```

If you use another endpoint, override it:

```bash
export OBSIDIAN_LOCAL_REST_API_URL="http://127.0.0.1:27123"
```

The bundled MCP server defaults to allowing the Local REST API self-signed HTTPS certificate. If you want strict certificate verification, set:

```bash
export OBSIDIAN_VERIFY_TLS=1
```

## Plugin Files

```text
.codex-plugin/plugin.json       Codex plugin manifest
.mcp.json                       MCP server configuration
scripts/obsidian-mcp.sh         MCP server launcher
scripts/obsidian_mcp_server.py  MCP stdio server backed by Local REST API
skills/obsidian-vault/SKILL.md  Codex behavior guide for vault access
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OBSIDIAN_LOCAL_REST_API_KEY` | Yes | None | API key from Obsidian Local REST API settings. |
| `OBSIDIAN_API_KEY` | No | None | Backward-compatible alias for the API key. |
| `OBSIDIAN_LOCAL_REST_API_URL` | No | `https://127.0.0.1:27124` | Base URL for Obsidian Local REST API. |
| `OBSIDIAN_VERIFY_TLS` | No | None | Set to `1` to verify HTTPS certificates strictly. |
| `OBSIDIAN_MCP_DEBUG` | No | None | Set to `1` to print Python tracebacks to stderr. |

## MCP Tools

The plugin exposes these tools to Codex:

- `obsidian_status`
- `obsidian_list_files`
- `obsidian_get_note`
- `obsidian_put_note`
- `obsidian_append_note`
- `obsidian_patch_note`
- `obsidian_search_simple`
- `obsidian_dataview_query`
- `obsidian_jsonlogic_query`

## Usage Examples

After the plugin is installed and the environment variables are available to Codex, try prompts like:

```text
Search my Obsidian vault for notes about agent workflows.
```

```text
Create an Obsidian note in Inbox/Codex summarizing this conversation.
```

```text
Find my project note for the Codex Obsidian plugin and append today's implementation notes.
```

## Safety Model

The included skill tells Codex to:

- Search before reading when the target note is unknown.
- Read existing notes before editing them.
- Preserve frontmatter, headings, tags, links, aliases, block IDs, and Dataview fields.
- Prefer append or targeted edits over whole-note replacement.
- Avoid deleting notes unless explicitly instructed.
- Ask before bulk edits across many notes.

## Privacy

This plugin talks to your local Obsidian Local REST API endpoint. It does not include a hosted service, and it does not store your Obsidian API key in this repository.

Your vault data is exposed to Codex only when Codex uses the local MCP tools configured by this plugin.

## Troubleshooting

### `Missing Obsidian Local REST API key`

Set `OBSIDIAN_LOCAL_REST_API_KEY` in the environment where Codex launches plugin MCP servers.

### `Missing python3`

Install Python 3 and make sure `python3` is on your `PATH`.

### HTTPS certificate errors

By default the MCP server allows the local self-signed certificate commonly used by Obsidian Local REST API. If you set `OBSIDIAN_VERIFY_TLS=1`, make sure the certificate is trusted by your system, or use the HTTP endpoint:

```bash
export OBSIDIAN_LOCAL_REST_API_URL="http://127.0.0.1:27123"
```

### MCP tools do not appear

Make sure Obsidian is open, Local REST API is enabled, the API key is valid, and the MCP endpoint URL is correct.

## License

MIT
