---
name: obsidian-vault
description: Use when the user asks to search, read, write, summarize, reorganize, or update their local Obsidian vault as a knowledge base.
---

# Obsidian Vault

Use the bundled Obsidian MCP server whenever the user asks about their Obsidian notes, vault, knowledge base, projects, daily notes, tags, backlinks, Dataview-backed lists, or wants Codex to save information into Obsidian.

## Connection

- The MCP server is named `obsidian`.
- If the tools are unavailable, ask the user to confirm that Obsidian is running, Local REST API is enabled, and `OBSIDIAN_LOCAL_REST_API_KEY` is set.
- Use `OBSIDIAN_LOCAL_REST_API_URL` only when the user uses a non-default Local REST API base URL.

## Reading

- Search before reading when the target note path is unknown.
- Prefer focused reads over loading broad folders.
- When answering from notes, mention which note paths were used.
- For Dataview-style requests, prefer `obsidian_dataview_query` instead of guessing from filenames alone.

## Writing

- Read an existing note before editing it.
- Preserve YAML frontmatter, existing headings, block IDs, aliases, tags, links, and Dataview fields.
- Prefer appending or targeted patching over replacing a whole note.
- Do not delete notes or large sections unless the user explicitly asks.
- For new captures without a specified destination, create notes under `Inbox/Codex/`.
- Use Markdown that is idiomatic for Obsidian: wiki links when helpful, standard fenced code blocks, and simple frontmatter.

## Safety

- Treat the vault as the user's source of truth.
- Ask before bulk edits across many notes.
- If a requested write could overwrite substantial human-written content, summarize the intended edit first and wait for confirmation.
