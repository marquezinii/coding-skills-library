<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## YARA-X New Features

Key additions from recent releases:

- **Private patterns** (v1.3.0+): `private $helper = "pattern"` — matches but hidden from output
- **Warning suppression** (v1.4.0+): `// suppress: slow_pattern` inline comments
- **Numeric underscores** (v1.5.0+): `filesize < 10_000_000` for readability
- **Built-in formatter**: `yr fmt rules/` to standardize formatting
- **NDJSON output**: `yr scan --output-format ndjson` for tooling

## YARA-X Tooling Workflow

YARA-X provides diagnostic tools legacy YARA lacks:

**Rule development cycle:**
```bash
# 1. Write initial rule
# 2. Check syntax with detailed errors
yr check rule.yar

# 3. Format consistently
yr fmt -w rule.yar

# 4. Dump module output to inspect file structure (no dummy rule needed)
yr dump -m pe sample.exe --output-format yaml

# 5. Scan with timing info
time yr scan -s rule.yar corpus/
```

**When to use `yr dump`:**
- Investigating what PE/ELF/Mach-O fields are available
- Debugging why module conditions aren't matching
- Exploring new modules (crx, lnk, dotnet) before writing rules

**YARA-X diagnostic advantage:** Error messages include precise source locations. If `yr check` points to line 15, the issue is actually on line 15 (unlike legacy YARA).

## Chrome Extension Analysis (crx module)

The `crx` module enables detection of malicious Chrome extensions. Requires YARA-X v1.5.0+ (basic), v1.11.0+ for `permhash()`.

**Key APIs:** `crx.is_crx`, `crx.permissions`, `crx.permhash()`

**Red flags:** `nativeMessaging` + `downloads`, `debugger` permission, content scripts on `<all_urls>`

```yara
import "crx"

rule SUSP_CRX_HighRiskPerms {
    condition:
        crx.is_crx and
        for any perm in crx.permissions : (perm == "debugger")
}
```

See [crx-module.md](../references/crx-module.md) for complete API reference, permission risk assessment, and example rules.

## Android DEX Analysis (dex module)

The `dex` module enables detection of Android malware. Requires YARA-X v1.11.0+. **Not compatible with legacy YARA's dex module** — API is completely different.

**Key APIs:** `dex.is_dex`, `dex.contains_class()`, `dex.contains_method()`, `dex.contains_string()`

**Red flags:** Single-letter class names (obfuscation), `DexClassLoader` reflection, encrypted assets

```yara
import "dex"

rule SUSP_DEX_DynamicLoading {
    condition:
        dex.is_dex and
        dex.contains_class("Ldalvik/system/DexClassLoader;")
}
```

See [dex-module.md](../references/dex-module.md) for complete API reference, obfuscation detection, and example rules.

## Migrating from Legacy YARA

YARA-X has 99% rule compatibility, but enforces stricter validation.

**Quick migration:**
```bash
yr check --relaxed-re-syntax rules/  # Identify issues
# Fix each issue, then:
yr check rules/  # Verify without relaxed mode
```

**Common fixes:**
| Issue | Legacy | YARA-X Fix |
|-------|--------|------------|
| Literal `{` in regex | `/{/` | `/\{/` |
| Invalid escapes | `\R` silently literal | `\\R` or `R` |
| Base64 strings | Any length | 3+ chars required |
| Negative indexing | `@a[-1]` | `@a[#a - 1]` |
| Duplicate modifiers | Allowed | Remove duplicates |

> **Note:** Use `--relaxed-re-syntax` only as a diagnostic tool. Fix issues rather than relying on relaxed mode.

## Quick Reference

### Naming Convention

```
{CATEGORY}_{PLATFORM}_{FAMILY}_{VARIANT}_{DATE}
```

**Common prefixes:** `MAL_` (malware), `HKTL_` (hacking tool), `WEBSHELL_`, `EXPL_`, `SUSP_` (suspicious), `GEN_` (generic)

**Platforms:** `Win_`, `Lnx_`, `Mac_`, `Android_`, `CRX_`

**Example:** `MAL_Win_Emotet_Loader_Jan25`

See [style-guide.md](../references/style-guide.md) for full conventions, metadata requirements, and naming examples.

### Required Metadata

Every rule needs: `description` (starts with "Detects"), `author`, `reference`, `date`.

```yara
meta:
    description = "Detects Example malware via unique mutex and C2 path"
    author = "Your Name <email@example.com>"
    reference = "https://example.com/analysis"
    date = "2025-01-29"
```

### String Selection

**Good:** Mutex names, PDB paths, C2 paths, stack strings, configuration markers
**Bad:** API names, common executables, format specifiers, generic paths

See [strings.md](../references/strings.md) for the full decision tree and examples.

### Condition Patterns

**Order conditions for short-circuit:**
1. `filesize < 10MB` (instant)
2. `uint16(0) == 0x5A4D` (nearly instant)
3. String matches (cheap)
4. Module checks (expensive)

See [performance.md](../references/performance.md) for detailed optimization patterns.

## Workflow

1. **Gather samples** — Multiple samples; single-sample rules are brittle
2. **Extract candidates** — `yarGen -m samples/ --excludegood`
3. **Validate quality** — Use decision tree; yarGen needs 80% filtering
4. **Write initial rule** — Follow template with proper metadata
5. **Lint and test** — `yr check`, `yr fmt`, linter script
6. **Goodware validation** — VirusTotal corpus or local clean files
7. **Deploy** — Add to repo with full metadata, monitor for FPs

See [testing.md](../references/testing.md) for detailed validation workflow and FP investigation.

For a comprehensive step-by-step guide covering all phases from sample collection to deployment, see [rule-development.md](../workflows/rule-development.md).

## Common Mistakes

| Mistake | Bad | Good |
|---------|-----|------|
| API names as indicators | `"VirtualAlloc"` | Hex pattern of call site + unique mutex |
| Unbounded regex | `/https?:\/\/.*/` | `/https?:\/\/[a-z0-9]{8,12}\.onion/` |
| Missing file type filter | `pe.imports(...)` first | `uint16(0) == 0x5A4D and filesize < 10MB` first |
| Short strings | `"abc"` (3 bytes) | `"abcdef"` (4+ bytes) |
| Unescaped braces (YARA-X) | `/config{key}/` | `/config\{key\}/` |

## Performance Optimization

**Quick wins:** Put `filesize` first, avoid `nocase`, bounded regex `{1,100}`, prefer hex over regex.

**Red flags:** Strings <4 bytes, unbounded regex (`.*`), modules without file-type filter.

See [performance.md](../references/performance.md) for atom theory and optimization details.

## Reference Documents

| Topic | Document |
|-------|----------|
| Naming and metadata conventions | [style-guide.md](../references/style-guide.md) |
| Performance and atom optimization | [performance.md](../references/performance.md) |
| String types and judgment | [strings.md](../references/strings.md) |
| Testing and validation | [testing.md](../references/testing.md) |
| Chrome extension module (crx) | [crx-module.md](../references/crx-module.md) |
| Android DEX module (dex) | [dex-module.md](../references/dex-module.md) |

## Workflows

| Topic | Document |
|-------|----------|
| Complete rule development process | [rule-development.md](../workflows/rule-development.md) |

## Example Rules

The `examples/` directory contains real, attributed rules demonstrating best practices:

| Example | Demonstrates | Source |
|---------|--------------|--------|
| [MAL_Win_Remcos_Jan25.yar](../examples/MAL_Win_Remcos_Jan25.yar) | PE malware: graduated string counts, multiple rules per family | Elastic Security |
| [MAL_Mac_ProtonRAT_Jan25.yar](../examples/MAL_Mac_ProtonRAT_Jan25.yar) | macOS: Mach-O magic bytes, multi-category grouping | Airbnb BinaryAlert |
| [MAL_NPM_SupplyChain_Jan25.yar](../examples/MAL_NPM_SupplyChain_Jan25.yar) | npm supply chain: real attack patterns, ERC-20 selectors | Stairwell Research |
| [SUSP_JS_Obfuscation_Jan25.yar](../examples/SUSP_JS_Obfuscation_Jan25.yar) | JavaScript: obfuscator detection, density-based matching | imp0rtp3, Nils Kuhnert |
| [SUSP_CRX_SuspiciousPermissions.yar](../examples/SUSP_CRX_SuspiciousPermissions.yar) | Chrome extensions: crx module, permissions | Educational |

## Scripts

```bash
uv run {baseDir}/scripts/yara_lint.py rule.yar      # Validate style/metadata
uv run {baseDir}/scripts/atom_analyzer.py rule.yar  # Check string quality
```

See [README.md](../../../README.md#scripts) for detailed script documentation.

## Quality Checklist

Before deploying any rule:

- [ ] Name follows `{CATEGORY}_{PLATFORM}_{FAMILY}_{VARIANT}_{DATE}` format
- [ ] Description starts with "Detects" and explains what/how
- [ ] All required metadata present (author, reference, date)
- [ ] Strings are unique (not API names, common paths, or format strings)
- [ ] All strings have 4+ bytes with good atom potential
- [ ] Base64 modifier only on strings with 3+ characters
- [ ] Regex patterns have escaped `{` and valid escape sequences
- [ ] Condition starts with cheap checks (filesize, magic bytes)
- [ ] Rule matches all target samples
- [ ] Rule produces zero matches on goodware corpus
- [ ] `yr check` passes with no errors
- [ ] `yr fmt --check` passes (consistent formatting)
- [ ] Linter passes with no errors
- [ ] Peer review completed

## Resources

### Quality YARA Rule Repositories

Learn from production rules. These repositories contain well-tested, properly attributed rules:

| Repository | Focus | Maintainer |
|------------|-------|------------|
| [Neo23x0/signature-base](https://github.com/Neo23x0/signature-base) | 17,000+ production rules, multi-platform | Florian Roth |
| [Elastic/protections-artifacts](https://github.com/elastic/protections-artifacts) | 1,000+ endpoint-tested rules | Elastic Security |
| [reversinglabs/reversinglabs-yara-rules](https://github.com/reversinglabs/reversinglabs-yara-rules) | Threat research rules | ReversingLabs |
| [imp0rtp3/js-yara-rules](https://github.com/imp0rtp3/js-yara-rules) | JavaScript/browser malware | imp0rtp3 |
| [InQuest/awesome-yara](https://github.com/InQuest/awesome-yara) | Curated index of resources | InQuest |

### Style & Performance Guides

| Guide | Purpose |
|-------|---------|
| [YARA Style Guide](https://github.com/Neo23x0/YARA-Style-Guide) | Naming conventions, metadata, string prefixes |
| [YARA Performance Guidelines](https://github.com/Neo23x0/YARA-Performance-Guidelines) | Atom optimization, regex bounds |
| [Kaspersky Applied YARA Training](https://yara.readthedocs.io/) | Expert techniques from production use |

### Tools

| Tool | Purpose |
|------|---------|
| [yarGen](https://github.com/Neo23x0/yarGen) | Extract candidate strings from samples |
| [FLOSS](https://github.com/mandiant/flare-floss) | Extract obfuscated and stack strings |
| [YARA-CI](https://yara-ci.cloud.virustotal.com/) | Automated goodware testing |
| [YaraDbg](https://yaradbg.dev) | Web-based rule debugger |

### macOS-Specific Resources

| Resource | Purpose |
|----------|---------|
| Apple XProtect | Production macOS rules at `/System/Library/CoreServices/XProtect.bundle/` |
| [objective-see](https://objective-see.org/) | macOS malware research and samples |
| [macOS Security Tools](https://github.com/0xmachos/macos-security-tools) | Reference list |

### Multi-Indicator Clustering Pattern

Production rules often group indicators by type:

```yara
strings:
    // Category A: Library indicators
    $a1 = "SRWebSocket" ascii
    $a2 = "SocketRocket" ascii

    // Category B: Behavioral indicators
    $b1 = "SSH tunnel" ascii
    $b2 = "keylogger" ascii nocase

    // Category C: C2 patterns
    $c1 = /https:\/\/[a-z0-9]{8,16}\.onion/

condition:
    filesize < 10MB and
    any of ($a*) and any of ($b*)  // Require evidence from BOTH categories
```

**Why this works:** Different indicator types have different confidence levels. A single C2 domain might be definitive, while you need multiple library imports to be confident. Grouping by `$a*`, `$b*`, `$c*` lets you express graduated requirements.
