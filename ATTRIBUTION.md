# Attribution & Third-Party Notices

This repository aggregates Agent Skills from multiple sources. We strive to preserve original authorship and licensing.

## Attribution Policy

- Where the original author/license is known, it is preserved in the skill directory
- Skills ported from public repositories retain their original license files
- Skills adapted from documentation include source references
- Original skill creators are credited in `SKILL.md` frontmatter where possible

## Known Sources

| Skill(s) | Original Source | License | Notes |
|----------|-----------------|---------|-------|
| `code-security/*` | Semgrep Engineering / Trail of Bits | MIT | Adapted from [semgrep-rules](https://github.com/semgrep/semgrep-rules) |
| `sentry-*` | Sentry | MIT | Official Sentry SDK skills |
| `cloudflare/*` | Cloudflare | MIT | Workers, D1, R2, AI Gateway patterns |
| `vercel-*` | Vercel | MIT | Next.js, React, Turbo patterns |
| `github-*` | GitHub | MIT | Copilot, Actions, CLI workflows |
| `aws-*` | AWS | Apache-2.0 | CDK, Serverless, Well-Architected |
| `azure-*` | Microsoft | MIT | Bicep, Azure CLI, DevOps |
| `gstack-*` | gstack project | MIT | Internal tooling, portable subset |
| `qdrant-*` | Qdrant | Apache-2.0 | Vector database operations |
| `supabase-*` | Supabase | MIT/Apache-2.0 | Postgres best practices |
| `terraform-*` | HashiCorp / Community | MPL-2.0 / MIT | Provider patterns, testing |
| `kubernetes-*` | CNCF / Community | Apache-2.0 | Architecture, security, GitOps |
| `react-*` | React Team / Community | MIT | React 18/19 migration, patterns |
| `playwright-*` | Microsoft / Community | Apache-2.0 | E2E testing patterns |
| `ponytail*` | @dietrichgebert | MIT | Code simplification philosophy |
| `caveman*` | @dietrichgebert | MIT | Compressed communication modes |

## License Preservation

For skills with identifiable original licenses:
- The original `LICENSE` file is kept in the skill directory
- `SKILL.md` frontmatter includes `license:` field
- Modifications are noted in skill history

## Unclear Provenance

Some skills have unclear or composite origins (community patterns, folklore, multiple sources). These are marked with `license: MIT` in frontmatter as a default for repository tooling compatibility, **but this does not relicense the underlying knowledge**. Users should treat such skills as "educational patterns" and verify applicability for their use case.

## Requesting Attribution Updates

If you are the original author of a skill and:
- Want your name/project credited differently
- Need license clarification
- Want the skill removed

Please open an issue or email: **attribution@marquezinii.dev**

## Disclaimer

Inclusion in this library does not imply endorsement by original authors. This is a community curation effort. Original authors retain all rights to their work under their chosen licenses.