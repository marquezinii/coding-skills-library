# Contributing to Coding Skills Library

Thank you for contributing! This library thrives on community expertise.

## Ways to Contribute

1. **Submit a new skill** — Package your domain knowledge as a portable `SKILL.md`
2. **Improve an existing skill** — Fix bugs, update examples, expand coverage
3. **Report issues** — Bugs, outdated patterns, broken links, missing skills
4. **Curate categories** — Organize skills, write category overviews
5. **Improve tooling** — Enhance `skillctl.py`, validation, CI

## Skill Submission Requirements

### Required
- `SKILL.md` with valid frontmatter (`name`, `description`, `license`)
- Clear activation triggers in `description` (when should an agent use this?)
- No real secrets, API keys, or credentials (use placeholders like `<YOUR_API_KEY>`)
- Original authorship or explicit permission + preserved attribution
- Compatible with [Agent Skills Specification](https://agentskills.io/specification)

### Strongly Recommended
- `metadata.category` and `metadata.tags` for discoverability
- `metadata.selection-policy: automatic` or `explicit-only`
- Supporting files in `references/` (kept minimal)
- Examples that are demonstrably safe (no `curl \| bash`, no `eval` on user input)

### File Structure
```
skills/your-skill-name/
├── SKILL.md
└── references/          # optional
    ├── best-practices.md
    └── examples/
```

## Submission Process

1. Fork the repository
2. Create your skill in `skills/your-skill-name/`
3. Run validation locally: `python scripts/validate.py skills/your-skill-name`
4. Submit a PR with:
   - Skill name and category
   - Source/origin (your work, adapted from X, ported from Y)
   - Original license and author (if third-party)
   - Confirmation: "No secrets included. Validated locally."

## Skill Quality Guidelines

### Do
- Write for **agents**, not humans (imperative, structured, actionable)
- Include concrete patterns: **Incorrect** → **Correct** code blocks
- Define clear boundaries: when NOT to use the skill
- Keep `SKILL.md` under 500 lines; offload detail to `references/`
- Use consistent formatting: headings, code fences, tables

### Don't
- Include executable scripts that modify state without confirmation
- Hardcode credentials (even examples — use `<PLACEHOLDERS>`)
- Duplicate existing skills — check catalog first
- Assume specific frameworks unless in skill scope
- Write prose essays; agents need instructions, not tutorials

## Third-Party Skills

If submitting a skill from another project:
- Verify the original license permits redistribution
- Preserve the original `LICENSE` file in the skill directory
- Add `ATTRIBUTION.md` with source URL, author, license
- Note any adaptations made for portability

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be respectful, constructive, and inclusive.

## Review Process

1. Automated checks: structure, frontmatter, secret scan, no nested `.git`
2. Maintainer review: triggers, clarity, duplication, licensing
3. Merge → CI regenerates `catalog.json` and `SKILLS.md`

## Questions?

Open a [Discussion](https://github.com/marquezinii/coding-skills-library/discussions) or [Issue](https://github.com/marquezinii/coding-skills-library/issues/new/choose).