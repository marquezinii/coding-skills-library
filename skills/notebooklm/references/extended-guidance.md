<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Generation Types

Common generate options vary by subcommand:
- `-n, --notebook` targets the notebook.
- `-s, --source` limits generation to specific source(s) on content generators (not `revise-slide`).
- `--language` sets output language where supported (defaults to configured language or `en`).
- `--wait`, `--timeout`, and `--interval` are shared polling controls where waiting is supported.
- `--json` returns machine-readable output.
- `--retry N` automatically retries rate limits on supported subcommands (not `mind-map`).
- `--prompt-file PATH` reads description/query text from a file on `ask`, generation subcommands except `mind-map`, and `source add-research`.

| Type | Command | Options | Download |
|------|---------|---------|----------|
| Podcast | `generate audio` | `--format [deep-dive\|brief\|critique\|debate]`, `--length [short\|default\|long]` | .mp3 |
| Video | `generate video` | `--format [explainer\|brief\|cinematic\|short]` (⁴), `--style [auto\|custom\|classic\|whiteboard\|kawaii\|anime\|watercolor\|retro-print\|heritage\|paper-craft]`, `--style-prompt` with `--style custom` | .mp4 |
| Slide Deck | `generate slide-deck` | `--format [detailed\|presenter]`, `--length [default\|short]` (²) | .pdf / .pptx |
| Slide Revision | `generate revise-slide "prompt" --artifact <id> --slide N` | `--wait`, `--notebook` | *(re-downloads parent deck)* |
| Infographic | `generate infographic` | `--orientation [landscape\|portrait\|square]`, `--detail [concise\|standard\|detailed]`, `--style [auto\|sketch-note\|professional\|bento-grid\|editorial\|instructional\|bricks\|clay\|anime\|kawaii\|scientific]` | .png |
| Report | `generate report` | `--format [briefing-doc\|study-guide\|blog-post\|custom]`, `--append "extra instructions"` (¹) | .md |
| Mind Map | `generate mind-map` | `--kind [interactive\|note-backed]` (³) *(default: interactive)* | .json |
| Data Table | `generate data-table` | description required | .csv |
| Quiz | `generate quiz` | `--difficulty [easy\|medium\|hard]`, `--quantity [fewer\|standard\|more]` | .json/.md/.html |
| Flashcards | `generate flashcards` | `--difficulty [easy\|medium\|hard]`, `--quantity [fewer\|standard\|more]` | .json/.md/.html |

¹ `--append` only customizes the built-in templates. With `--format custom`, pass the prompt as the positional `DESCRIPTION` argument (`notebooklm generate report "PROMPT" --format custom`); `--append` is silently ignored in that mode (the CLI prints a warning).

³ **Two kinds of mind map (issue #1256).** `generate mind-map --kind interactive` (the default) creates the **interactive** studio artifact (what the web app now makes); it is polled to completion. `generate mind-map --kind note-backed` creates the **note-backed** kind — a JSON node tree, generated synchronously. Both emit the same `{mind_map, note_id, kind}` JSON, list under `artifact list --type mind-map`, and export via `download mind-map`. `--instructions` applies only to the note-backed kind.

⁴ **Cinematic video (Veo 3).** `generate video --format cinematic` generates AI documentary footage via Veo 3; it **ignores `--style`**, takes ~30-40 min, and requires a Google AI Ultra subscription. Also exposed as the `generate cinematic-video` alias (which forces `--format cinematic` and a longer default timeout). Download with `download video` or the `download cinematic-video` alias.

² **Portrait / vertical slide decks via prompt.** Slide-deck has no `--orientation` flag (unlike infographic). Treat portrait decks as skill-level prompt guidance, not a typed CLI/API contract: NotebookLM currently honors orientation cues written into the `DESCRIPTION` positional argument. Including phrases like `"9:16 portrait"`, `"vertical layout"`, `"portrait mobile format"`, or `"vertical 9:16 layout"` can make NotebookLM render each slide as a 9:16 portrait image. Empirically:

- The `.pptx` canvas itself may stay 16:9, but each slide's embedded image can be rendered as 9:16 portrait — useful for vertical/mobile video material extracted via `python-pptx`.
- Orientation is steered once at generation time. `generate revise-slide` edits content within an existing slide but does not change its orientation; if a slide falls back to landscape (occasional inconsistency), regenerate the whole deck rather than revising the single page.
- Combine with an explicit page count in the prompt (e.g. `"Create exactly 8 pages, using a vertical 9:16 portrait layout"`) for the most predictable output.

```bash
# Skill prompt hint: ask NotebookLM to render each slide as a 9:16 portrait image
notebooklm generate slide-deck "Create an 8-page deck in 9:16 portrait orientation for mobile viewing" --length default
```

## Features Beyond the Web UI

These capabilities are available via CLI but not in NotebookLM's web interface:

| Feature | Command | Description |
|---------|---------|-------------|
| **Batch downloads** | `download <type> --all` | Download all artifacts of a type at once |
| **Quiz/Flashcard export** | `download quiz --format json` | Export as JSON, Markdown, or HTML (web UI only shows interactive view) |
| **Mind map extraction** | `download mind-map` | Export hierarchical JSON for visualization tools |
| **Data table export** | `download data-table` | Download structured tables as CSV |
| **Slide deck as PPTX** | `download slide-deck --format pptx` | Download slide deck as editable .pptx (web UI only offers PDF) |
| **Slide revision** | `generate revise-slide "prompt" --artifact <id> --slide N` | Modify individual slides with a natural-language prompt |
| **Report template append** | `generate report --format study-guide --append "..."` | Append custom instructions to built-in format templates without losing the format type |
| **Source fulltext** | `source fulltext <id>` | Retrieve the indexed text content of any source |
| **Save chat to note** | `ask "..." --save-as-note` / `history --save` | Save Q&A answers or conversation history as notebook notes |
| **Programmatic sharing** | `share` commands | Manage sharing permissions without the UI |

## Common Workflows

### Research to Podcast (Interactive)
**Time:** 5-10 minutes total

1. `notebooklm create "Research: [topic]"` — *if fails: check auth with `notebooklm login`*
2. `notebooklm source add` for each URL/document — *if one fails: log warning, continue with others*
3. Wait for sources: `notebooklm source list --json` until all status=READY — *required before generation*
4. `notebooklm generate audio "Focus on [specific angle]"` (confirm when asked) — *if rate limited: wait 5 min, retry once*
5. Note the artifact ID returned
6. Check `notebooklm artifact list` later for status
7. `notebooklm download audio ./podcast.mp3` when complete (confirm when asked)

### Research to Podcast (Automated with Subagent)
**Time:** 5-10 minutes, but continues in background

When user wants full automation (generate and download when ready):

1. Create notebook and add sources as usual
2. Wait for sources to be ready (use `source wait` or check `source list --json`)
3. Run `notebooklm generate audio "..." --json` → parse `task_id` from output
4. **Spawn a background agent** using Task tool:
   ```python
   Task(
     prompt="Wait for artifact {task_id} in notebook {notebook_id} to complete, then download.
             Use: notebooklm artifact wait {task_id} -n {notebook_id} --timeout 1200
             Then: notebooklm download audio ./podcast.mp3 -a {task_id} -n {notebook_id}",
     subagent_type="general-purpose"
   )
   ```
5. Main conversation continues while agent waits

**Error handling in subagent:**
- If `artifact wait` returns exit code 2 (timeout): Report timeout, suggest checking `artifact list`
- If download fails: Check if artifact status is COMPLETED first

**Benefits:** Non-blocking, user can do other work, automatic download on completion

### Document Analysis
**Time:** 1-2 minutes

1. `notebooklm create "Analysis: [project]"`
2. `notebooklm source add ./doc.pdf` (or URLs)
3. `notebooklm ask "Summarize the key points"`
4. `notebooklm ask "What are the main arguments?"`
5. Continue chatting as needed

### Bulk Import
**Time:** Varies by source count

1. `notebooklm create "Collection: [name]"`
2. Add multiple sources:
   ```bash
   notebooklm source add "https://url1.com"
   notebooklm source add "https://url2.com"
   notebooklm source add ./local-file.pdf
   ```
3. `notebooklm source list` to verify

**Source limits:** Varies by plan—Standard: 50, Plus: 100, Pro: 300, Ultra: 600 sources per notebook. See [NotebookLM plans](https://support.google.com/notebooklm/answer/16213268) for details. The CLI does not enforce these limits; they are applied by your NotebookLM account.
**Supported types:** PDFs, YouTube URLs, web URLs, Google Docs, text files, Markdown, Word docs, EPUB, audio files, video files, images

### Bulk Import with Source Waiting (Subagent Pattern)
**Time:** Varies by source count

When adding multiple sources and needing to wait for processing before chat/generation:

1. Add sources with `--json` to capture IDs (parse with `jq -r .source.id`):
   ```bash
   notebooklm source add "https://url1.com" --json  # → {"source": {"id": "abc...", ...}}
   notebooklm source add "https://url2.com" --json  # → {"source": {"id": "def...", ...}}
   ```
2. **Spawn a background agent** to wait for all sources:
   ```
   Task(
     prompt="Wait for sources {source_ids} in notebook {notebook_id} to be ready.
             For each: notebooklm source wait {id} -n {notebook_id} --timeout 600
             Report when all ready or if any fail.",
     subagent_type="general-purpose"
   )
   ```
3. Main conversation continues while agent waits
4. Once sources are ready, proceed with chat or generation

**Why wait for sources?** Sources must be indexed before chat or generation. Takes ~30 seconds to several minutes per source (see the processing-times table below).

### Deep Web Research (Subagent Pattern)
**Time:** 15-30+ minutes, runs in background

Deep research finds and analyzes web sources on a topic:

1. Create notebook: `notebooklm create "Research: [topic]"`
2. Start deep research (non-blocking):
   ```bash
   notebooklm source add-research "topic query" --mode deep --no-wait
   ```
3. **Spawn a background agent** to wait and import:
   ```
   Task(
     prompt="Wait for research in notebook {notebook_id} to complete and import sources.
             Use: notebooklm research wait -n {notebook_id} --import-all --timeout 1800
             Report how many sources were imported.",
     subagent_type="general-purpose"
   )
   ```
4. Main conversation continues while agent waits
5. When agent completes, sources are imported automatically

**Alternative (blocking):** For simple cases, omit `--no-wait`:
```bash
notebooklm source add-research "topic" --mode deep --import-all
# Blocks until research completes (deep mode: 15-30+ min)
```

**When to use each mode:**
- `--mode fast`: Specific topic, quick overview needed (5-10 sources, seconds)
- `--mode deep`: Broad topic, comprehensive analysis needed (20+ sources, 15-30+ min)

**Research sources:**
- `--from web`: Search the web (default)
- `--from drive`: Search Google Drive

## Output Style

**Progress updates:** Brief status for each step
- "Creating notebook 'Research: AI'..."
- "Adding source: https://example.com..."
- "Starting audio generation... (task ID: abc123)"

**Fire-and-forget for long operations:**
- Start generation, return artifact ID immediately
- Do NOT poll or wait in main conversation - generation takes 5-45 minutes (see timing table)
- User checks status manually, OR use subagent with `artifact wait`

**JSON output:** Use `--json` flag for machine-readable output:
```bash
notebooklm list --json
notebooklm auth check --test --json   # use --test for network-validated auth (see § Agent Setup Verification)
notebooklm source list --json
notebooklm artifact list --json
```

**JSON schemas (key fields):**

`notebooklm list --json`:
```json
{"notebooks": [{"index": 1, "id": "...", "title": "...", "is_owner": true, "created_at": "..."}], "count": 1}
```

`notebooklm auth check --test --json` (use `--test` to drive the network token-fetch — bare `--json` would leave `"token_fetch": null`):
```json
{"status": "ok", "checks": {"storage_exists": true, "json_valid": true, "cookies_present": true, "sid_cookie": true, "token_fetch": true}, "details": {"storage_path": "...", "auth_source": "file", "cookies_found": ["SID", "HSID", "..."], "cookie_domains": [".google.com"]}}
```

`notebooklm source list --json`:
```json
{"notebook_id": "...", "notebook_title": "...", "sources": [{"index": 1, "id": "...", "title": "...", "type": "web_page", "url": "...", "status": "ready|processing|error", "status_id": 1, "created_at": "..."}], "count": 1}
```

`notebooklm artifact list --json`:
```json
{"notebook_id": "...", "notebook_title": "...", "artifacts": [{"index": 1, "id": "...", "title": "...", "type": "Audio", "type_id": 1, "status": "in_progress|pending|completed|unknown", "status_id": 1, "created_at": "..."}], "count": 1}
```

**Status values:**
- Sources: `processing` → `ready` (or `error`)
- Artifacts: `pending` or `in_progress` → `completed` (or `unknown`)

## Error Handling

**On failure, offer the user a choice:**
1. Retry the operation
2. Skip and continue with something else
3. Investigate the error

**Error decision tree:**

| Error | Cause | Action |
|-------|-------|--------|
| Auth/cookie error | Session expired | Run `notebooklm auth check` then `notebooklm login` |
| "No notebook context" | Context not set | Use `-n <id>` or `--notebook <id>` flag (parallel), or `notebooklm use <id>` (single-agent) |
| "No result found for RPC ID" | Rate limiting | Wait 5-10 min, retry |
| `GENERATION_FAILED` | Google rate limit | Wait and retry later |
| Download fails | Generation incomplete | Check `artifact list` for status |
| Invalid notebook/source ID | Wrong ID | Run `notebooklm list` to verify |
| RPC protocol error | Google changed APIs | May need CLI update |

## Exit Codes

All commands use consistent exit codes:

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1 | Error (not found, processing failed) | Check stderr, see Error Handling |
| 2 | Timeout (wait commands only) | Extend timeout or check status manually |

**Examples:**
- `source wait` returns 1 if source not found or processing failed
- `artifact wait` returns 2 if timeout reached before completion
- `generate` returns 1 if rate limited (check stderr for details)

## Long Prompts

When a prompt or query exceeds shell command-line length limits, use `--prompt-file` to read it from a file:

```bash
notebooklm ask --prompt-file ./long_question.txt
notebooklm generate report --prompt-file ./custom_report_prompt.txt
notebooklm source add-research --prompt-file ./research_query.txt --mode deep
```

`--prompt-file` is mutually exclusive with the positional text argument. The file is read as UTF-8 with trailing whitespace stripped. Supported on: `ask`, all `generate` subcommands (except `mind-map`), and `source add-research`.

> **Note:** `--prompt-file` reads a *prompt/query text file*, not a source document. To upload a file as a notebook source, use `source add ./file.pdf`.

## Known Limitations

**Rate limiting:** Audio, video, quiz, flashcards, infographic, and slide deck generation may fail due to Google's rate limits. This is an API limitation, not a bug.

**Reliable operations:** These always work:
- Notebooks (list, create, delete, rename)
- Sources (add, list, delete)
- Chat/queries
- Mind-map, study-guide, report, data-table generation

**Unreliable operations:** These may fail with rate limiting:
- Audio (podcast) generation
- Video generation
- Quiz and flashcard generation
- Infographic and slide deck generation

**Workaround:** If generation fails:
1. Check status: `notebooklm artifact list`
2. Retry after 5-10 minutes
3. Use the NotebookLM web UI as fallback

**Processing times vary significantly.** Use the subagent pattern for long operations:

| Operation | Typical time | Suggested timeout |
|-----------|--------------|-------------------|
| Source processing | 30s - 10 min | 600s |
| Research (fast) | 30s - 2 min | 180s |
| Research (deep) | 15 - 30+ min | 1800s |
| Notes | instant | n/a |
| Mind-map | instant (sync) | n/a |
| Quiz, flashcards | 5 - 15 min | 900s |
| Report, data-table | 5 - 15 min | 900s |
| Audio generation | 10 - 20 min | 1200s |
| Video generation | 15 - 45 min | 2700s |

**Polling intervals:** When checking status manually, poll every 15-30 seconds to avoid excessive API calls.

## Language Configuration

Language setting controls the output language for generated artifacts (audio, video, etc.).

**Important:** Language is a **GLOBAL** setting that affects all notebooks in your account.

```bash
# List all 80+ supported languages with native names
notebooklm language list

# Show current language setting
notebooklm language get

# Set language for artifact generation
notebooklm language set zh_Hans  # Simplified Chinese
notebooklm language set ja       # Japanese
notebooklm language set en       # English (default)
```

**Common language codes:**
| Code | Language |
|------|----------|
| `en` | English |
| `zh_Hans` | 中文（简体） - Simplified Chinese |
| `zh_Hant` | 中文（繁體） - Traditional Chinese |
| `ja` | 日本語 - Japanese |
| `ko` | 한국어 - Korean |
| `es` | Español - Spanish |
| `fr` | Français - French |
| `de` | Deutsch - German |
| `pt_BR` | Português (Brasil) |

**Override per command:** Use `--language` flag on generate commands:
```bash
notebooklm generate audio --language ja   # Japanese podcast
notebooklm generate video --language zh_Hans  # Chinese video
```

**Offline mode:** Use `--local` flag to skip server sync:
```bash
notebooklm language set zh_Hans --local  # Save locally only
notebooklm language get --local  # Read local config only
```

## Troubleshooting

```bash
notebooklm --help              # Main commands
notebooklm auth check          # Diagnose auth issues
notebooklm auth check --test   # Full auth validation with network test
notebooklm source --help       # Source management
notebooklm research --help     # Research status/wait/cancel
notebooklm generate --help     # Content generation
notebooklm artifact --help     # Artifact management
notebooklm download --help     # Download content
notebooklm language --help     # Language settings
```

**Diagnose auth:** `notebooklm auth check` - shows cookie domains, storage path, validation status
**Re-authenticate:** `notebooklm login`
**Check version:** `notebooklm --version`
**Refresh a CLI-managed install:** `notebooklm skill install`
