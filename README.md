# Codex Obsidian Plugin

Connect Codex to your local Obsidian vault through the [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin and its MCP endpoint.

This plugin is intentionally small: Obsidian owns the vault and API, `mcp-remote` bridges Codex to the local MCP endpoint, and the included Codex skill teaches Codex safer note-taking behavior.

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
- Node.js with `npx` available.
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

The default MCP endpoint is:

```text
https://127.0.0.1:27124/mcp/
```

If you use another endpoint, override it:

```bash
export OBSIDIAN_LOCAL_REST_API_URL="http://127.0.0.1:27123/mcp/"
```

For the HTTP endpoint, the wrapper automatically passes `--allow-http` to `mcp-remote`.

If you use the HTTPS endpoint and your local certificate is self-signed, either trust the Local REST API certificate on your machine or set:

```bash
export OBSIDIAN_ALLOW_SELF_SIGNED_CERT=1
```

## Plugin Files

```text
.codex-plugin/plugin.json       Codex plugin manifest
.mcp.json                       MCP server configuration
scripts/obsidian-mcp.sh         Local wrapper around mcp-remote
skills/obsidian-vault/SKILL.md  Codex behavior guide for vault access
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OBSIDIAN_LOCAL_REST_API_KEY` | Yes | None | API key from Obsidian Local REST API settings. |
| `OBSIDIAN_API_KEY` | No | None | Backward-compatible alias for the API key. |
| `OBSIDIAN_LOCAL_REST_API_URL` | No | `https://127.0.0.1:27124/mcp/` | MCP endpoint exposed by Obsidian Local REST API. |
| `OBSIDIAN_ALLOW_SELF_SIGNED_CERT` | No | None | Set to `1` to allow the default HTTPS self-signed certificate. |

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

### `Missing npx`

Install Node.js and make sure `npx` is on your `PATH`.

### HTTPS certificate errors

Use the HTTP endpoint from Obsidian Local REST API, or set:

```bash
export OBSIDIAN_ALLOW_SELF_SIGNED_CERT=1
```

### MCP tools do not appear

Make sure Obsidian is open, Local REST API is enabled, the API key is valid, and the MCP endpoint URL is correct.

## License

MIT
