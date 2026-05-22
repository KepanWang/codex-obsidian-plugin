# Obsidian Vault Classification

This file is the default classification guide for the `obsidian-vault` skill.

Users should copy this file to a private, user-specific location and edit it for their own vault. Recommended override locations:

- `<vault>/.codex/obsidian-classification.md`
- `~/.codex/obsidian-classification.md`

When archiving new knowledge, Codex should look for a user override first. If no override is available, use this file as the fallback.

## Decision Rules

- Infer the category from the user's request, source title, source content, and existing vault structure.
- Prefer the most specific matching category.
- If multiple categories match, choose the category that describes the user's intended future retrieval path.
- If confidence is low, save to the inbox path and set `classification_status: "needs-review"`.
- Include `category`, `series`, and `classification_confidence` in frontmatter when saving a classified note.

## Default Categories

### CPS

Use for CPS, affiliate marketing, distribution, commission, creator commerce, product selection, traffic, conversion, channel operations, merchant cooperation, campaign review, and related practical experience.

Default path:

```text
01 Sources/CPS/
```

Frontmatter:

```yaml
category: "CPS"
series: "CPS"
```

### Development

Use for software engineering, coding agents, Codex, architecture, tests, CI/CD, developer tools, technical debt, infrastructure, data engineering, and implementation experience.

Default path:

```text
01 Sources/Development/
```

Frontmatter:

```yaml
category: "Development"
series: "Engineering"
```

### Management

Use for company building, enterprise management, AI-native organizations, team collaboration, hiring, process design, strategy, operating rhythm, decision-making, and leadership.

Default path:

```text
01 Sources/Management/
```

Frontmatter:

```yaml
category: "Management"
series: "Company Building"
```

### Documents

Use when the user explicitly provides or asks to archive documents, requirements, specs, manuals, contracts, policies, SOPs, templates, reference files, or formal materials.

Default path:

```text
01 Sources/Documents/
```

Frontmatter:

```yaml
category: "Documents"
series: "Reference"
```

### Knowledge

Use for general articles, concepts, courses, ideas, reading notes, and knowledge summaries that do not fit a more specific category.

Default path:

```text
01 Sources/Knowledge/
```

Frontmatter:

```yaml
category: "Knowledge"
series: "General Knowledge"
```

### Inbox

Use only when no category is clear, when the user asks to defer organization, or when the target category needs review.

Default path:

```text
Inbox/Codex/
```

Frontmatter:

```yaml
classification_status: "needs-review"
classification_confidence: "low"
```
