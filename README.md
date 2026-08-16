# Coding Skills Library

A curated library of **1,110+ portable Agent Skills** for coding agents such as **Claude Code**, **OpenAI Codex**, **Manus**, **OpenCode**, and similar systems.

## What Are Agent Skills?

Agent Skills are structured markdown files (`SKILL.md`) that teach AI coding agents how to perform specialized tasks — from writing secure code and designing APIs to debugging production issues and optimizing database queries. Each skill encapsulates domain expertise, best practices, and actionable workflows that agents can invoke on demand.

## Quick Stats

| Metric | Count |
|--------|-------|
| Skills | 1,110 |
| SKILL.md files | 1,111 |
| Categories | 30+ |
| Total files | ~9,000 |

## Supported Agents

| Agent | Installation Path | Notes |
|-------|-------------------|-------|
| **Claude Code** | `~/.claude/skills/` or project `.claude/skills/` | Auto-discovered |
| **OpenAI Codex** | `~/.codex/skills/` or project `.codex/skills/` | See [Codex Skills Docs](https://learn.chatgpt.com/docs/build-skills) |
| **Manus** | Project `.manus/skills/` | Manual setup |
| **OpenCode** | `~/.config/opencode/skills/` or project `.opencode/skills/` | Auto-discovered |
| **Generic** | Any directory | Use `skillctl.py install` |

## Installation

### Option 1: Clone Entire Repository (Recommended)

```bash
git clone https://github.com/marquezinii/coding-skills-library.git
```

Then link to your agent's skill directory:

```bash
# Claude Code (global)
ln -s "$PWD/coding-skills-library/skills" ~/.claude/skills

# Codex (global)
ln -s "$PWD/coding-skills-library/skills" ~/.codex/skills

# OpenCode (global)
ln -s "$PWD/coding-skills-library/skills" ~/.config/opencode/skills
```

### Option 2: Download ZIP

1. Download the latest release ZIP from [Releases](https://github.com/marquezinii/coding-skills-library/releases)
2. Extract to your preferred location
3. Link as shown above

### Option 3: Install Individual Skills

```bash
# Using the helper CLI (see scripts/skillctl.py)
python scripts/skillctl.py install ponytail --target ~/.claude/skills

# Or manually copy a skill directory
cp -r skills/ponytail ~/.claude/skills/
```

### Option 4: Install Multiple Skills

```bash
# Install all skills
python scripts/skillctl.py install-all --target ~/.claude/skills

# Install by category
python scripts/skillctl.py install-category security --target ~/.claude/skills
```

## Repository Structure

```
coding-skills-library/
├── .github/
│   ├── workflows/          # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md
├── scripts/
│   ├── skillctl.py         # Skill management CLI
│   └── validate.py         # Validation utilities
├── skills/
│   ├── api-design/         # Each skill is a directory
│   │   ├── SKILL.md        # Main skill definition
│   │   └── references/     # Optional supporting files
│   ├── security-audit/
│   └── ...                 # 1,110+ skill directories
├── catalog.json            # Machine-readable skill catalog
├── SKILLS.md               # Human-readable skill index
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── ATTRIBUTION.md
└── README.md
```

## Using Skills

Once installed, skills are automatically discovered by compatible agents. You can invoke them by name:

```
# In your agent conversation
"Use the ponytail skill to simplify this code"
"Apply the security-audit skill to review this PR"
"Load the api-design skill for this endpoint"
```

Skills with `metadata.selection-policy: explicit-only` require explicit invocation:

```
"Use the writing-skills skill explicitly"
"/skill writing-skills"
```

## Categories

Skills are organized into categories (also reflected in `catalog.json`):

- **AI/ML**: `rag-architect`, `llm-evaluation`, `fine-tuning-expert`, `embedding-strategies`
- **API/Backend**: `api-design`, `graphql-architect`, `backend-architect`, `microservices-architect`
- **Security**: `security-audit`, `code-security`, `security-reviewer`, `secret-scanning`
- **Frontend/UI**: `frontend-design`, `ui-design`, `react-expert`, `vue-expert`, `animate`
- **Database**: `postgres-pro`, `database-optimizer`, `mongodb-schema-design`, `supabase`
- **DevOps/Cloud**: `terraform-specialist`, `kubernetes-architect`, `aws-serverless`, `cloudflare`
- **Testing**: `playwright-expert`, `test-master`, `e2e-testing-patterns`, `pytest-coverage`
- **Code Quality**: `code-review`, `refactor`, `ponytail`, `lint-and-validate`
- **Architecture**: `architecture-designer`, `domain-driven-design`, `event-sourcing-architect`
- **And 20+ more categories...**

See [SKILLS.md](SKILLS.md) for a complete categorized index, or [catalog.json](catalog.json) for programmatic access.

## Skill Format

Each skill follows the [Agent Skills Specification](https://agentskills.io/specification):

```yaml
---
name: skill-name
description: When to use this skill (triggers, use cases)
license: MIT
metadata:
  selection-policy: automatic  # or explicit-only
  category: security
  tags: [audit, vulnerability, owasp]
---

# Skill Name

Detailed instructions, workflows, and reference material...
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Submitting new skills
- Improving existing skills
- Reporting issues
- Code of conduct

## Security

**Important**: This repository is a **collection** of third-party skills. Inclusion does not imply security endorsement.

- Skills may contain shell commands, code patterns, or instructions that execute in your environment
- Always inspect third-party skills before using them in production
- Report security concerns via [SECURITY.md](SECURITY.md) process
- CI validates structure but cannot guarantee runtime safety

## Licensing

This repository's tooling and documentation are licensed under **MIT** (see [LICENSE](LICENSE)).

Individual skills remain under their **original licenses**. We preserve attribution and license information where available. See [ATTRIBUTION.md](ATTRIBUTION.md) for details.

**Absence of an explicit license does NOT mean public domain or MIT.** Contributors must respect upstream licensing terms.

## Related Projects

- [Agent Skills Specification](https://agentskills.io/specification)
- [OpenAI Codex Skills](https://learn.chatgpt.com/docs/build-skills)
- [OpenCode Skills](https://opencode.ai/docs/skills)
- [Awesome Copilot](https://github.com/github/awesome-copilot)

---

**Repository**: https://github.com/marquezinii/coding-skills-library