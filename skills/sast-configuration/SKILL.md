---
name: sast-configuration
description: Configure and govern static application security testing with Semgrep, CodeQL, SARIF, and CI quality gates. Use when selecting SAST tools, establishing a baseline, adding CI scans, tuning false positives, writing scanning policy, or designing a remediation workflow. Do not use for DAST-only testing or a manual penetration test.
---

# Configure SAST

Build the smallest scanning system that covers the repository's languages and risk profile. Reuse the dedicated scanner skills instead of inventing commands, versions, or rule packs here.

## 1. Establish scope

Inspect:

- languages, generated code, vendored code, build systems, and monorepo boundaries;
- pull-request and default-branch CI workflows;
- existing Semgrep, CodeQL, SonarQube, SARIF, suppression, or policy files;
- data-handling constraints for source code and scan artifacts;
- the team's ability to triage and remediate findings.

Record what is in scope, which paths are excluded, who owns findings, and whether external scanning services are approved. Do not upload private source or findings to a third party without authorization.

## 2. Select analyzers

| Need | Route |
|---|---|
| Fast, customizable pattern and taint analysis | [Semgrep](../semgrep/SKILL.md) |
| Deep interprocedural data-flow analysis | [CodeQL](../codeql/SKILL.md) |
| Organization-specific detections | [Semgrep rule creator](../semgrep-rule-creator/SKILL.md) |
| Normalize or deduplicate scanner output | [SARIF parsing](../sarif-parsing/SKILL.md) |
| Dependency and supply-chain analysis | [Dependency audit](../dependency-management-deps-audit/SKILL.md) |
| Secret detection and push protection | [Secret scanning](../secret-scanning/SKILL.md) |
| Docker or runtime-container hardening | [Container security hardening](../container-security-hardening/SKILL.md) |
| API design and implementation controls | [API security practices](../api-security-best-practices/SKILL.md) |

Use multiple analyzers only when their coverage is complementary and the team can triage the combined output.

## 3. Baseline before blocking

1. Run the chosen analyzers without a merge-blocking gate.
2. Save tool version, configuration, ruleset identity, scope, and output format with the result.
3. Deduplicate findings and separate confirmed vulnerabilities from noise.
4. Assign an owner and remediation decision to every accepted finding.
5. Define a baseline so historical debt does not hide or block review of newly introduced findings.

Never mark a finding as a false positive only to make CI green. Record the technical reason, scope, reviewer, and review date for every suppression.

## 4. Add CI policy

Use two deliberate modes:

- **Pull requests:** scan changed code or compare against the approved baseline; block only on policy-defined new findings.
- **Default branch or schedule:** run broader coverage and publish a durable report for backlog and trend review.

For CI configuration:

- pin third-party actions or images to an immutable version accepted by the repository policy;
- grant the workflow only the permissions required to read code and publish results;
- keep tokens in the platform's secret store and out of logs, artifacts, and command arguments;
- bound runtime, memory, file size, and generated/vendor directories;
- retain raw output long enough to reproduce a decision, subject to data-retention policy;
- fail clearly when the scanner crashes or its configuration cannot load; do not report that as a clean scan.

## 5. Define the gate

Write the gate as an auditable rule, for example:

```text
Block when a new finding is high confidence and high severity,
unless an unexpired, reviewed suppression matches its stable fingerprint.
Scanner failure is an infrastructure failure, not a passing security result.
```

Use stable fingerprints or SARIF identities where the analyzer supports them. Avoid gating on raw finding counts, because line movement, duplicate rules, and analyzer upgrades can change counts without changing risk.

## 6. Tune and extend

- Reproduce noisy findings on the smallest representative sample.
- Prefer a narrower rule, path constraint, or typed/data-flow condition over a broad ignore.
- Add positive and negative tests for custom rules.
- Review suppressions after framework, dependency, or analyzer upgrades.
- Treat a ruleset update as a policy change: preview the delta before enabling it on protected branches.

Load [Semgrep rule creator](../semgrep-rule-creator/SKILL.md) for custom rules and [SARIF parsing](../sarif-parsing/SKILL.md) for cross-tool result processing.

## 7. Validate the system

Before declaring the SAST setup complete, demonstrate:

- the configuration loads successfully;
- a known safe test fixture does not create unexpected findings;
- a controlled vulnerable fixture or repository-approved test rule is detected;
- the CI job distinguishes clean scan, policy violation, configuration failure, and infrastructure failure;
- suppressions expire or have a review mechanism;
- developers can reproduce the scan locally with documented, repository-owned commands;
- the output contains no secrets or prohibited source excerpts.

Report the analyzers selected, coverage boundaries, gate logic, baseline location, validation evidence, and any capability intentionally deferred.
