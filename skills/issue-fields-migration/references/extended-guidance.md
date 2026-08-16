<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Important Notes

- **Write endpoint quirk**: the REST API for writing issue field values uses `repository_id` (integer), not `owner/repo`. Always look up the repo ID first with `gh api /repos/{owner}/{repo} --jq .id`.
- **Single-select values**: the REST API accepts option **names** as strings (not option IDs). This makes mapping straightforward for both project fields and labels.
- **Reading values back**: when reading issue field values from the API response, use `.single_select_option.name` for the human-readable value. The `.value` property returns the internal option ID (an integer like `1201`), not the display name.
- **API version header**: all issue fields endpoints require `X-GitHub-Api-Version: 2026-03-10`.
- **Cross-repo items**: a project can contain issues from multiple repositories. Cache the repo ID per-repository to avoid redundant lookups.
- **Preserve existing values**: never overwrite an issue field value that is already set. Skip those items.
- **Iteration fields**: have no issue field equivalent. Always warn the user and skip.
- **Draft items**: project items that are not linked to real issues cannot have issue field values. Skip with a note.
- **Labels are repo-scoped**: unlike project fields, labels exist per-repo. The same label name may exist in multiple repos; migration applies separately to each.
- **Label conflicts**: an issue can have multiple labels that map to the same single_select field. Always detect and resolve these before execution.
- **Label removal is optional**: after migration, the user may want to keep labels as backup or remove them. Always ask before removing.
- **URL-encode label names**: labels with spaces or special characters must be URL-encoded when used in REST API paths (e.g., `good%20first%20issue`).
- **Script generation for scale**: for migrations of 100+ issues, generate a standalone shell script rather than executing API calls one at a time through the agent. This is faster, resumable, and avoids agent timeout issues.
- **Idempotent migrations**: re-running a migration is safe. Issues that already have the target field value set will be skipped. This means you can safely resume a partial migration without duplicating work.
- **`--limit 1000` truncation**: `gh issue list --limit 1000` silently stops at 1000 results. For labels with more issues, paginate with `--jq` and cursor-based pagination or run multiple filtered queries (e.g., by date range).
- **macOS bash version**: macOS ships with bash 3.x, which does not support `declare -A` (associative arrays). Generated scripts should use POSIX-compatible constructs or note the incompatibility and suggest `brew install bash`.
- **Issues vs PRs**: `gh issue list` returns both issues and pull requests. If the migration should only target issues, include `type` in `--json` output and filter for `type == "Issue"`.

## Examples

### Example 1: Full Migration

**User**: "I need to migrate Priority values from our project to the new org Priority issue field"

**Action**: Follow Phases P1-P6. Discover fields, map options, check permissions, scan items, preview, execute.

### Example 2: Dry-Run Only

**User**: "Show me what would happen if I migrated fields from project #42, but don't actually do it"

**Action**: Follow Phases P1-P5 only. Present the full dry-run report with every item listed. Do not execute.

### Example 3: Multiple Fields

**User**: "Migrate Priority and Due Date from project #15 to issue fields"

**Action**: Same workflow, but process both fields in a single pass. During the data scan, collect values for all mapped fields per item. Write all field values in a single API call per issue.

### Example 4: Single Label to Issue Field

**User**: "I want to migrate the 'bug' label to the Type issue field"

**Action**: Route to Label Migration Flow. Ask for org/repo, list labels, confirm mapping: label "bug" → Type field "Bug" option. Scan issues with that label, preview, execute. Ask whether to remove the label after migration.

### Example 5: Multiple Labels to One Field (Bulk)

**User**: "We have p0, p1, p2, p3 labels and want to convert them to the Priority issue field"

**Action**: Route to Label Migration Flow. Map all four labels to Priority field options (p0→P0, p1→P1, p2→P2, p3→P3). Check for conflicts (issues with multiple priority labels). Preview all changes in one summary. Execute in one pass. Optionally remove all four labels from migrated issues.

### Example 6: Cross-Repo Label Migration with Label Removal

**User**: "Migrate the 'frontend' and 'backend' labels to the Team issue field across github/issues, github/memex, and github/mobile, then remove the old labels"

**Action**: Route to Label Migration Flow. Confirm repos and label mappings: "frontend"→Team "Frontend", "backend"→Team "Backend". Scan all three repos for issues with these labels. Detect conflicts (issues with both labels). Preview across repos. Execute field writes, then remove labels from migrated issues. Report per-repo stats.
