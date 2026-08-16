<!--
Thank you for your PR! Please fill out the sections below.
-->

## Summary

<!-- What does this PR do? -->

## Type of Change

- [ ] New skill
- [ ] Skill improvement/fix
- [ ] Documentation update
- [ ] Tooling/CI improvement
- [ ] Generated file refresh (catalog.json, SKILLS.md)
- [ ] Other: 

## For New Skills

| Field | Value |
|-------|-------|
| Skill name |  |
| Category |  |
| Origin | Original / Adapted / Ported from [URL] |
| License | MIT / Apache-2.0 / Other |
| Original author |  |

## Checklist

- [ ] `SKILL.md` has valid frontmatter (`name`, `description`, `license`)
- [ ] No real secrets, API keys, tokens, or credentials (use `<PLACEHOLDERS>`)
- [ ] Clear activation triggers in `description`
- [ ] Under 500 lines (detail in `references/`)
- [ ] Follows [Agent Skills Specification](https://agentskills.io/specification)
- [ ] Validated locally: `python scripts/validate.py skills/skill-name`
- [ ] If third-party: original `LICENSE` file in skill directory
- [ ] If third-party: `ATTRIBUTION.md` with source details
- [ ] No nested `.git` directories
- [ ] No binary/temporary artifacts

## For Skill Updates

- [ ] What changed and why?
- [ ] Verified against current upstream docs/source
- [ ] Breaking changes noted (if any)

## Testing

Describe how you tested this change:

<!--
- Installed skill locally
- Ran validation script
- Tested with agent (Claude Code/Codex/etc.)
- Verified triggers work correctly
-->