# Security Policy

## Reporting a Vulnerability

**Do not open public issues for security vulnerabilities.**

Email security concerns to: **security@marquezinii.dev** (or use GitHub's private vulnerability reporting)

Include:
- Affected skill(s) or component
- Description of the issue
- Potential impact
- Suggested fix (if any)

We aim to acknowledge within 48 hours and provide a timeline for resolution.

## Supported Versions

Only the latest `main` branch receives security updates.

## Scope

### In Scope
- Repository infrastructure (CI, tooling, `skillctl.py`)
- Skill validation and sanitization logic
- Generated catalog and index files
- GitHub Actions workflows

### Out of Scope (Third-Party Skills)
Individual skills are **community-contributed content**. We validate structure and scan for obvious secrets, but:

- Skills may contain code patterns, shell commands, or instructions that execute in your environment
- Inclusion in this library is **not a security endorsement**
- Users must inspect skills before using them in production
- Vulnerabilities in third-party skill content should be reported to the skill author/origin

## Secret Handling

- **Never** commit real credentials, API keys, tokens, or private keys
- Examples must use obvious placeholders: `<YOUR_API_KEY>`, `<YOUR_TOKEN>`, `sk_test_<REDACTED>`
- CI runs secret scanning on every PR
- Detected secrets block merge until remediated

## Safe Usage Guidelines

1. **Review before use** — Read the `SKILL.md` and any `references/` files
2. **Understand the triggers** — Skills activate based on keywords; know when they run
3. **Audit permissions** — Some skills suggest commands requiring elevated access
4. **Test in isolation** — Try new skills in a sandbox/non-production environment first
5. **Pin versions** — When skills reference external tools, pin to specific versions

## Known Considerations

| Area | Note |
|------|------|
| Shell commands | Some skills include `bash`/`PowerShell` snippets; validate before running |
| `curl \| bash` patterns | Flagged in security scan; only allowed in explicit educational context |
| `eval` / dynamic code | Educational examples only; marked with warnings |
| Third-party installers | Skills may reference `npx`, `pipx`, `brew`; verify sources |
| Cloud credentials | Skills for AWS/Azure/GCP assume you manage credentials securely |

## Disclosure Timeline

1. Report received → Acknowledgment (48h)
2. Triage → Severity assessment (5 business days)
3. Fix development → Coordinated with reporter
4. Advisory published → After fix merged to `main`
5. CVE requested → If applicable

## Contact

Security team: **security@marquezinii.dev**

For non-security issues, use [GitHub Issues](https://github.com/marquezinii/coding-skills-library/issues).