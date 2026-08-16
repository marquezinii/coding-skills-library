---
name: notebooklm
description: Complete API for Google NotebookLM - full programmatic access including features not in the web UI. Create notebooks, add sources, generate all artifact types, download in multiple formats. Activates on explicit /notebooklm or intent like "create a podcast about X"
---

# NotebookLM Automation

Complete programmatic access to Google NotebookLM—including capabilities not exposed in the web UI. Create notebooks, add sources (URLs, YouTube, PDFs, audio, video, images), chat with content, generate all artifact types, and download results in multiple formats.

## Installation

**From PyPI (Recommended for AI agents — Python-version-aware):**
```bash
pip install "notebooklm-py[browser]"   # mandatory; errors must propagate

# [cookies] (rookiepy) is optional and known to FAIL TO BUILD on Python 3.13+.
# Skip it deliberately on 3.13+ rather than swallowing the error — that lets
# *real* install failures (typos, network, PyPI outages) surface for the agent.
if python -c "import sys; sys.exit(0 if sys.version_info < (3, 13) else 1)"; then
    pip install "notebooklm-py[cookies]"   # errors propagate
else
    echo "Skipping [cookies] on Python 3.13+ (rookiepy unavailable). Use 'notebooklm login' interactively."
fi
```

> Full install matrix (extras, headless servers, contributor flow): [Installation guide on GitHub](https://github.com/teng-lin/notebooklm-py/blob/main/docs/installation.md).

**From GitHub (use latest release tag, NOT main branch):**
```bash
# Get the latest release tag (requires curl + jq)
if ! command -v jq >/dev/null; then
    echo "jq is required to read the latest release tag" >&2
    exit 1
fi
LATEST_TAG=$(
    curl -fsSL https://api.github.com/repos/teng-lin/notebooklm-py/releases/latest |
    jq -r '.tag_name'
)
# Includes [browser] so the interactive `notebooklm login` flow works.
pip install "notebooklm-py[browser] @ git+https://github.com/teng-lin/notebooklm-py@${LATEST_TAG}"
```

⚠️ **DO NOT install from main branch** (`pip install git+https://github.com/teng-lin/notebooklm-py`). The main branch may contain unreleased/unstable changes. Always use PyPI or a specific release tag, unless you are testing unreleased features.

**Skill install methods:**

- `notebooklm skill install` installs this skill into the supported local agent directories managed by the CLI.
- `npx skills add teng-lin/notebooklm-py` installs this skill from the GitHub repository into compatible agent skill directories.
- If you are already reading this file inside an agent skill directory, the skill is already installed. You only need the Python package and authentication below.

**CLI-managed install:**
```bash
notebooklm skill install
```

## Prerequisites

**IMPORTANT:** Before using any command, you MUST authenticate:

```bash
notebooklm login          # Opens browser for Google OAuth
notebooklm list           # Verify authentication works
```

If commands fail with authentication errors, re-run `notebooklm login`.

### CI/CD, Multiple Accounts, and Parallel Agents

For automated environments, multiple accounts, or parallel agent workflows:

| Variable | Purpose |
|----------|---------|
| `NOTEBOOKLM_HOME` | Custom config directory (default: `~/.notebooklm`) |
| `NOTEBOOKLM_PROFILE` | Active profile name (default: `default`) |
| `NOTEBOOKLM_AUTH_JSON` | Inline auth JSON - no file writes needed |

**CI/CD setup:** Set `NOTEBOOKLM_AUTH_JSON` from a secret containing your `storage_state.json` contents.

**Multiple accounts:** Use named profiles (`notebooklm profile create work`, then `notebooklm -p work login`). Alternatively, use different `NOTEBOOKLM_HOME` directories per account.

**Parallel agents:** The CLI stores notebook context per profile (`~/.notebooklm/profiles/<profile>/context.json`, with a legacy fallback to `~/.notebooklm/context.json` for the implicit default profile). Multiple concurrent agents that share a profile and use `notebooklm use` can overwrite each other's context — use one of the isolation strategies below.

**Solutions for parallel workflows:**
1. **Always use explicit notebook ID** (recommended): Pass `-n <notebook_id>` / `--notebook <notebook_id>` on notebook-scoped commands instead of relying on `use`
2. **Per-agent isolation via profiles:** `export NOTEBOOKLM_PROFILE=agent-$ID` (each profile gets its own context file)
3. **Per-agent isolation via home:** Set unique `NOTEBOOKLM_HOME` per agent: `export NOTEBOOKLM_HOME=/tmp/agent-$ID`
4. **Use full UUIDs:** Avoid partial IDs in automation (they can become ambiguous)

### Sandboxed Agents (Claude Cowork / Headless)

Sandboxed, no-display agent environments — **Claude Cowork** (Anthropic's desktop agent for non-developers) and similar headless sandboxes — can't run `notebooklm login` (it needs a browser), and they reset between sessions. Everything else works with two adjustments:

1. **Bootstrap each session.** The sandbox resets, so install at the start of every session. You do **not** need `[browser]`/Playwright here — that extra exists only for the interactive `login` flow, which you run on a host machine, not in the sandbox. Chat, sources, generation, and download all run on the base install:
   ```bash
   pip install notebooklm-py   # no [browser] needed for queries/generation
   ```
   (This is the one place the mandatory `[browser]` install at the top of this file does not apply — you are reusing auth, not logging in here.)
2. **Reuse a host-generated `storage_state.json`.** Log in once on a machine with a display (`notebooklm login`), then bring the resulting `storage_state.json` into a sandbox-accessible folder and point at it either way:
   ```bash
   # Per-invocation root flag (a persistent, sandbox-accessible path):
   notebooklm --storage /path/to/storage_state.json list
   # OR inline via env var (no file needed — e.g. from a Cowork-stored secret):
   export NOTEBOOKLM_AUTH_JSON="$(cat /path/to/storage_state.json)"
   notebooklm list
   ```

   > ⚠️ **`storage_state.json` / `NOTEBOOKLM_AUTH_JSON` are bearer credentials** — anyone holding them can act as your Google account. Keep the file `0600`, load it from the sandbox's secret store rather than a committed file, never print or log it, and `unset NOTEBOOKLM_AUTH_JSON` when finished.

**Verify** as in [Agent Setup Verification](#agent-setup-verification) below — e.g. `notebooklm --storage <path> auth check --test --json` (require `"status": "ok"` AND `"checks.token_fetch": true`).

**Context does not survive a reset** either: the selected-notebook context (`context.json`) is gone each session, so pass an explicit `-n/--notebook <id>` on notebook-scoped commands instead of relying on `notebooklm use`.

If Cowork reads `~/.claude/skills/`, `notebooklm skill install` registers this skill there automatically; otherwise build the uploadable archive on the host with `notebooklm skill package` (writes `notebooklm-skill.zip`) and add it via **Claude Settings → Capabilities**. Full recipe (extras matrix, headless auth, CI env-var notes): [installation.md § AI Agent](https://github.com/teng-lin/notebooklm-py/blob/main/docs/installation.md#a-ai-agent-primary-persona).

## Agent Setup Verification

Before starting workflows, verify auth is in place. **Use `--test --json` (not bare `--json`)** — bare `--json` only proves the cookie file parses; `--test` makes a network call and proves the cookies still authenticate against Google.

1. `notebooklm auth check --test --json` → require BOTH `"status": "ok"` AND `"checks.token_fetch": true`. Bare `"status": "ok"` (without `--test`) is a false-positive trap — a stale cookie file passes the parse check.
2. `notebooklm list --json` → expect valid JSON (may be empty for new accounts).
3. **If auth fails or is missing → run `notebooklm login` first.** This is the primary auth path: opens a browser, the user signs in to Google once, and the resulting `storage_state.json` is reused on every subsequent run. Works on any environment with a display.
   - For headless contexts where opening a browser is not feasible, use `notebooklm login --browser-cookies <browser>` instead — extracts the user's already-logged-in cookies from Chrome/Firefox/etc. (requires the `[cookies]` extra; rookiepy may not install on Python 3.13+). Use `chrome::<profile-name-or-directory>` to target one Chromium user-profile, or `firefox::<container-name>` / `firefox::none` to target one Firefox container.
   - To survey signed-in Google accounts before picking one: `notebooklm auth inspect --browser <browser>` (read-only; pass `-v` to see which Chromium user-profile each account came from, or `--json` for tooling). Scoped forms such as `notebooklm auth inspect --browser 'chrome::Profile 1'` inspect only that browser profile.
   - Re-run step 1 after login to confirm.
4. **If auth was working but cookies went stale** (Google rotated SIDTS, or you signed in fresh in the browser) **→ refresh the active profile in place instead of full re-login:**
   - `notebooklm auth refresh` — server-side SIDTS refresh against the existing `storage_state.json`. Cheap and silent; safe to run on a schedule (cron / launchd / systemd) at 15–20 min cadence to keep an unattended profile warm.
   - `notebooklm auth refresh --browser-cookies <browser>` — re-extract cookies from a running browser and match them back to the profile's recorded email in `context.json`. Use when the on-disk `storage_state.json` is too stale for the server-side refresh path but you've just signed back into Google in the browser. For Chromium-family browsers with multiple user-profiles (Chrome's `Default`, `Profile 1`, …), refresh fans out across all profiles to find the email — same path as `auth inspect` (issue #571). Use `chrome::<profile-name-or-directory>` when you already know the exact browser profile.
   - Both forms preserve the same `--profile` (no new profile is created).

> **Note:** `notebooklm status` reports *context state* (selected notebook); do not use it to verify auth.

## When This Skill Activates

**Explicit:** User says "/notebooklm", "use notebooklm", or mentions the tool by name

**Intent detection:** Recognize requests like:
- "Create a podcast about [topic]"
- "Summarize these URLs/documents"
- "Generate a quiz from my research"
- "Turn this into an audio overview"
- "Create flashcards for studying"
- "Generate a video explainer"
- "Make an infographic"
- "Create a mind map of the concepts"
- "Download the quiz as markdown"
- "Add these sources to NotebookLM"

## Autonomy Rules

**Run automatically (no confirmation):**
- `notebooklm status` - check context
- `notebooklm auth check` - diagnose auth issues
- `notebooklm auth inspect` - list Google accounts visible to a browser (read-only)
- `notebooklm auth refresh` - server-side SIDTS refresh of the active profile (no new profile, no destructive writes)
- `notebooklm auth refresh --browser-cookies <browser>` - re-extract cookies from a browser into the active profile (rebuilds `storage_state.json` for the same `--profile`, not a new one)
- `notebooklm list` - list notebooks
- `notebooklm source list` - list sources
- `notebooklm artifact list` - list artifacts
- `notebooklm language list` - list supported languages
- `notebooklm language get` - get current language
- `notebooklm language set` - set language (global setting)
- `notebooklm artifact wait` - wait for artifact completion (in subagent context)
- `notebooklm source wait` - wait for source processing (in subagent context)
- `notebooklm research status` - check research status
- `notebooklm research wait` - wait for research (in subagent context)
- `notebooklm use <id>` - set context (⚠️ SINGLE-AGENT ONLY - use `-n` flag in parallel workflows)
- `notebooklm create` - create notebook
- `notebooklm ask "..."` - chat queries (without `--save-as-note`)
- `notebooklm suggest-prompts` - AI-suggested prompts for a notebook (read-only, no state change)
- `notebooklm history` - display conversation history (read-only)
- `notebooklm source add` - add sources
- `notebooklm profile list` - list profiles
- `notebooklm profile create` - create profile
- `notebooklm profile switch` - switch active profile
- `notebooklm doctor` - check environment health

**Ask before running:**
- `notebooklm delete`, `source delete`, `source delete-by-title`, `source clean`, `note delete`, `artifact delete`, `label delete`, `share remove`, `auth logout`, `clear`, `profile delete`, or `ask --new` - destructive or state-changing. Once approved, pass `--yes`/`-y` where the command supports it. Most destructive `--json` commands still require explicit `--yes` and otherwise return a structured confirmation error (`CONFIRM_REQUIRED` or `VALIDATION_ERROR`, depending on the command family); current exceptions include `share remove --json` and `ask --new --json`, which skip the prompt for non-interactive callers.
- `notebooklm generate *` - long-running, may fail
- `notebooklm download *` - writes to filesystem
- `notebooklm artifact wait` - long-running (when in main conversation)
- `notebooklm source wait` - long-running (when in main conversation)
- `notebooklm research wait` - long-running (when in main conversation)
- `notebooklm research cancel <run_id>` - state-changing; cancels a running research job (an in-progress job transitions to FAILED). Fire-and-forget: it does not confirm success — re-check with `notebooklm research status`.
- `notebooklm ask "..." --save-as-note` - writes a note
- `notebooklm history --save` - writes a note

## Quick Reference

| Task | Command |
|------|---------|
| Authenticate | `notebooklm login` |
| Authenticate from browser cookies | `notebooklm login --browser-cookies <browser>` |
| Authenticate from one Chromium profile | `notebooklm login --browser-cookies 'chrome::Profile 1'` |
| Authenticate from one Firefox container | `notebooklm login --browser-cookies 'firefox::Work'` |
| Import every signed-in account into its own profile | `notebooklm login --browser-cookies <browser> --all-accounts` |
| Inspect signed-in accounts (read-only, by email) | `notebooklm auth inspect --browser <browser>` |
| Inspect one browser profile/container | `notebooklm auth inspect --browser 'chrome::Profile 1'` |
| Diagnose auth issues | `notebooklm auth check` |
| Diagnose auth (full) | `notebooklm auth check --test` |
| Refresh active profile in place (server-side) | `notebooklm auth refresh` |
| Refresh active profile from a re-signed-in browser | `notebooklm auth refresh --browser-cookies <browser>` |
| Refresh from one Chromium profile | `notebooklm auth refresh --browser-cookies 'chrome::Profile 1'` |
| One-shot cookie keepalive (for cron) | `notebooklm auth refresh --quiet` |
| List notebooks | `notebooklm list` |
| Create notebook | `notebooklm create "Title"` |
| Set context | `notebooklm use <notebook_id>` |
| Show context | `notebooklm status` |
| Add URL source | `notebooklm source add "https://..."` |
| Add file | `notebooklm source add ./file.pdf` |
| Add YouTube | `notebooklm source add "https://youtube.com/..."` |
| List sources | `notebooklm source list` |
| List sources in a label | `notebooklm source list --label <label_id_or_name>` |
| Delete source by ID | `notebooklm source delete <source_id>` |
| Delete source by exact title | `notebooklm source delete-by-title "Exact Title"` |
| Wait for source processing | `notebooklm source wait <source_id>` |
| List labels | `notebooklm label list` |
| Expand label to sources | `notebooklm label sources <label_id_or_name>` |
| Generate labels | `notebooklm label generate --scope unlabeled` |
| Create label | `notebooklm label create "Topic"` |
| Add sources to label | `notebooklm label add <label_id_or_name> <source_id>...` |
| Remove sources from label | `notebooklm label remove <label_id_or_name> <source_id>...` |
| Delete label | `notebooklm label delete <label_id_or_name> --yes` |
| Web research (fast) | `notebooklm source add-research "query"` |
| Web research (deep) | `notebooklm source add-research "query" --mode deep --no-wait` |
| Web research (query from file) | `notebooklm source add-research --prompt-file research_query.txt --mode deep` |
| Check research status | `notebooklm research status` |
| Wait for research | `notebooklm research wait --import-all` |
| Cancel research | `notebooklm research cancel <run_id>` (run_id = the `task_id` from `research status`) |
| Suggest questions to ask | `notebooklm suggest-prompts` |
| Chat | `notebooklm ask "question"` |
| Chat (long prompt from file) | `notebooklm ask --prompt-file question.txt` |
| Chat (specific sources) | `notebooklm ask "question" -s src_id1 -s src_id2` |
| Chat (with references) | `notebooklm ask "question" --json` |
| Chat (save answer as note) | `notebooklm ask "question" --save-as-note` |
| Chat (save with title) | `notebooklm ask "question" --save-as-note --note-title "Title"` |
| Show conversation history | `notebooklm history` |
| Save all history as note | `notebooklm history --save` |
| Continue specific conversation | `notebooklm ask "question" -c <conversation_id>` |
| Save history with title | `notebooklm history --save --note-title "My Research"` |
| Get source fulltext | `notebooklm source fulltext <source_id>` |
| Get source guide | `notebooklm source guide <source_id>` |
| Generate podcast | `notebooklm generate audio "instructions"` |
| Generate (long prompt from file) | `notebooklm generate audio --prompt-file instructions.txt` |
| Generate podcast (JSON) | `notebooklm generate audio --json` |
| Generate podcast (specific sources) | `notebooklm generate audio -s src_id1 -s src_id2` |
| Generate video | `notebooklm generate video "instructions"` |
| Generate report | `notebooklm generate report --format briefing-doc` |
| Generate report (append instructions) | `notebooklm generate report --format study-guide --append "Target audience: beginners"` |
| Generate quiz | `notebooklm generate quiz` |
| Revise a slide | `notebooklm generate revise-slide "prompt" --artifact <id> --slide 0` |
| Check artifact status | `notebooklm artifact list` |
| Wait for completion | `notebooklm artifact wait <artifact_id>` |
| Delete artifact | `notebooklm artifact delete <artifact_id> --yes` |
| Download audio | `notebooklm download audio ./output.mp3` |
| Download video | `notebooklm download video ./output.mp4` |
| Download cinematic video | `notebooklm download cinematic-video ./cinematic.mp4` (alias for `download video`) |
| Download infographic | `notebooklm download infographic ./infographic.png` |
| Download slide deck (PDF) | `notebooklm download slide-deck ./slides.pdf` |
| Download slide deck (PPTX) | `notebooklm download slide-deck ./slides.pptx --format pptx` |
| Download report | `notebooklm download report ./report.md` |
| Download mind map | `notebooklm download mind-map ./map.json` |
| Download data table | `notebooklm download data-table ./data.csv` |
| Download quiz | `notebooklm download quiz quiz.json` |
| Download quiz (markdown) | `notebooklm download quiz --format markdown quiz.md` |
| Download flashcards | `notebooklm download flashcards cards.json` |
| Download flashcards (markdown) | `notebooklm download flashcards --format markdown cards.md` |
| Delete notebook | `notebooklm delete -n <id>` (add `--yes` to skip the prompt non-interactively) |
| List languages | `notebooklm language list` |
| Get language | `notebooklm language get` |
| Set language | `notebooklm language set zh_Hans` |
| List profiles | `notebooklm profile list` |
| Create profile | `notebooklm profile create work` |
| Switch profile | `notebooklm profile switch work` |
| Delete profile | `notebooklm profile delete old --yes` (`-y`; `--confirm` is a deprecated alias) |
| Rename profile | `notebooklm profile rename old new` |
| Use profile (one-off) | `notebooklm -p work list` |
| Health check | `notebooklm doctor` |
| Health check (auto-fix) | `notebooklm doctor --fix` |

**Parallel safety:** Use explicit notebook IDs in parallel workflows. Notebook-scoped commands broadly support `-n/--notebook` (ask/history, source, artifact, generate, download, note, label, share, research, and notebook delete/rename/summary/metadata). Download commands also support `-a/--artifact`. For chat, use `-c <conversation_id>` to target a specific conversation.

**Partial IDs:** Use first 6+ characters of UUIDs. Must be unique prefix (fails if ambiguous). Works for ID-based commands such as `use`, `source delete`, and `wait`. For exact source-title deletion, use `source delete-by-title "Title"`. For automation, prefer full UUIDs to avoid ambiguity.

## Command Output Formats

Commands with `--json` return structured data for parsing:

**Create notebook:**
```bash
$ notebooklm create "Research" --json
{"notebook": {"id": "abc123de-...", "title": "Research", "created_at": null}}
# parse with: jq -r .notebook.id
```

**Add source:**
```bash
$ notebooklm source add "https://example.com" --json
{"source": {"id": "def456...", "title": "Example", "type": "web_page", "url": "https://example.com"}}
# parse with: jq -r .source.id
# Note: no `status` field on add — use `source list --json` or `source wait` to check processing state.
```

**Generate artifact:**
```bash
$ notebooklm generate audio "Focus on key points" --json
{"task_id": "xyz789...", "status": "pending"}
# When run with --wait, completed status also includes a `url` field.
```

**Chat with references:**
```bash
$ notebooklm ask "What is X?" --json
{"answer": "X is... [1] [2]", "conversation_id": "...", "turn_number": 1, "is_follow_up": false, "references": [{"source_id": "abc123...", "citation_number": 1, "cited_text": "Relevant passage from source..."}, {"source_id": "def456...", "citation_number": 2, "cited_text": "Another passage..."}]}
```

**Source fulltext (get indexed content):**
```bash
$ notebooklm source fulltext <source_id> --json
{"source_id": "...", "title": "...", "kind": "web_page", "content": "Full indexed text...", "url": null, "char_count": 12345}
```

**Understanding citations:** The `cited_text` in references is often a snippet or section header, not the full quoted passage. The `start_char`/`end_char` positions reference NotebookLM's internal chunked index, not the raw fulltext. Use `SourceFulltext.find_citation_context()` to locate citations:
```python
fulltext = await client.sources.get_fulltext(notebook_id, ref.source_id)
matches = fulltext.find_citation_context(ref.cited_text)  # Returns list[(context, position)]
if matches:
    context, pos = matches[0]  # First match; check len(matches) > 1 for duplicates
```

**Extract IDs:** Singular endpoints wrap their result in an envelope —
parse `.notebook.id` (from `create`), `.source.id` (from `source add`),
or `.task_id` (from `generate *`). The chat `--json` references list uses
`.references[].source_id`.


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Generation Types](references/extended-guidance.md#generation-types)
- [Features Beyond the Web UI](references/extended-guidance.md#features-beyond-the-web-ui)
- [Common Workflows](references/extended-guidance.md#common-workflows)
- [Output Style](references/extended-guidance.md#output-style)
- [Error Handling](references/extended-guidance.md#error-handling)
- [Exit Codes](references/extended-guidance.md#exit-codes)
- [Long Prompts](references/extended-guidance.md#long-prompts)
- [Known Limitations](references/extended-guidance.md#known-limitations)
- [Language Configuration](references/extended-guidance.md#language-configuration)
- [Troubleshooting](references/extended-guidance.md#troubleshooting)

