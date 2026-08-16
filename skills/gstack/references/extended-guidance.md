<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Artifacts Sync (skill start)

```bash
_GSTACK_HOME="${GSTACK_HOME:-$HOME/.gstack}"
# Prefer the v1.27.0.0 artifacts file; fall back to brain file for users
# upgrading mid-stream before the migration script runs.
if [ -f "$HOME/.gstack-artifacts-remote.txt" ]; then
  _BRAIN_REMOTE_FILE="$HOME/.gstack-artifacts-remote.txt"
else
  _BRAIN_REMOTE_FILE="$HOME/.gstack-brain-remote.txt"
fi
_BRAIN_SYNC_BIN="$GSTACK_BIN/gstack-brain-sync"
_BRAIN_CONFIG_BIN="$GSTACK_BIN/gstack-config"

# /gstack-sync-gbrain context-load: teach the agent to use gbrain when it's available.
# Per-worktree pin: post-spike redesign uses kubectl-style `.gbrain-source` in the
# git toplevel to scope queries. Look for the pin in the worktree (not a global
# state file) so that opening worktree B without a pin doesn't claim "indexed"
# just because worktree A was synced. Empty string when gbrain is not
# configured (zero context cost for non-gbrain users).
_GBRAIN_CONFIG="$HOME/.gbrain/config.json"
if [ -f "$_GBRAIN_CONFIG" ] && command -v gbrain >/dev/null 2>&1; then
  _GBRAIN_VERSION_OK=$(gbrain --version 2>/dev/null | grep -c '^gbrain ' || echo 0)
  if [ "$_GBRAIN_VERSION_OK" -gt 0 ] 2>/dev/null; then
    _GBRAIN_PIN_PATH=""
    _REPO_TOP=$(git rev-parse --show-toplevel 2>/dev/null || echo "")
    if [ -n "$_REPO_TOP" ] && [ -f "$_REPO_TOP/.gbrain-source" ]; then
      _GBRAIN_PIN_PATH="$_REPO_TOP/.gbrain-source"
    fi
    if [ -n "$_GBRAIN_PIN_PATH" ]; then
      echo "GBrain configured. Prefer \`gbrain search\`/\`gbrain query\` over Grep for"
      echo "semantic questions; use \`gbrain code-def\`/\`code-refs\`/\`code-callers\` for"
      echo "symbol-aware code lookup. See \"## GBrain Search Guidance\" in CLAUDE.md."
      echo "Run /gstack-sync-gbrain to refresh."
    else
      echo "GBrain configured but this worktree isn't pinned yet. Run \`/gstack-sync-gbrain --full\`"
      echo "before relying on \`gbrain search\` for code questions in this worktree."
      echo "Falls back to Grep until pinned."
    fi
  fi
fi

_BRAIN_SYNC_MODE=$("$_BRAIN_CONFIG_BIN" get artifacts_sync_mode 2>/dev/null || echo off)

# Detect remote-MCP mode (Path 4 of /gstack-setup-gbrain). Local artifacts sync is
# a no-op in remote mode; the brain server pulls from GitHub/GitLab on its
# own cadence. Read claude.json directly to keep this preamble fast (no
# subprocess to claude CLI on every skill start).
_GBRAIN_MCP_MODE="none"
if command -v jq >/dev/null 2>&1 && [ -f "$HOME/.claude.json" ]; then
  _GBRAIN_MCP_TYPE=$(jq -r '.mcpServers.gbrain.type // .mcpServers.gbrain.transport // empty' "$HOME/.claude.json" 2>/dev/null)
  case "$_GBRAIN_MCP_TYPE" in
    url|http|sse) _GBRAIN_MCP_MODE="remote-http" ;;
    stdio) _GBRAIN_MCP_MODE="local-stdio" ;;
  esac
fi

if [ -f "$_BRAIN_REMOTE_FILE" ] && [ ! -d "$_GSTACK_HOME/.git" ] && [ "$_BRAIN_SYNC_MODE" = "off" ]; then
  _BRAIN_NEW_URL=$(head -1 "$_BRAIN_REMOTE_FILE" 2>/dev/null | tr -d '[:space:]')
  if [ -n "$_BRAIN_NEW_URL" ]; then
    echo "ARTIFACTS_SYNC: artifacts repo detected: $_BRAIN_NEW_URL"
    echo "ARTIFACTS_SYNC: run 'gstack-brain-restore' to pull your cross-machine artifacts (or 'gstack-config set artifacts_sync_mode off' to dismiss forever)"
  fi
fi

if [ -d "$_GSTACK_HOME/.git" ] && [ "$_BRAIN_SYNC_MODE" != "off" ]; then
  _BRAIN_LAST_PULL_FILE="$_GSTACK_HOME/.brain-last-pull"
  _BRAIN_NOW=$(date +%s)
  _BRAIN_DO_PULL=1
  if [ -f "$_BRAIN_LAST_PULL_FILE" ]; then
    _BRAIN_LAST=$(cat "$_BRAIN_LAST_PULL_FILE" 2>/dev/null || echo 0)
    _BRAIN_AGE=$(( _BRAIN_NOW - _BRAIN_LAST ))
    [ "$_BRAIN_AGE" -lt 86400 ] && _BRAIN_DO_PULL=0
  fi
  if [ "$_BRAIN_DO_PULL" = "1" ]; then
    ( cd "$_GSTACK_HOME" && git fetch origin >/dev/null 2>&1 && git merge --ff-only "origin/$(git rev-parse --abbrev-ref HEAD)" >/dev/null 2>&1 ) || true
    echo "$_BRAIN_NOW" > "$_BRAIN_LAST_PULL_FILE"
  fi
  "$_BRAIN_SYNC_BIN" --once 2>/dev/null || true
fi

if [ "$_GBRAIN_MCP_MODE" = "remote-http" ]; then
  # Remote-MCP mode: local artifacts sync is a no-op (brain admin's server
  # pulls from GitHub/GitLab). Show the user this is by design, not broken.
  _GBRAIN_HOST=$(jq -r '.mcpServers.gbrain.url // empty' "$HOME/.claude.json" 2>/dev/null | sed -E 's|^https?://([^/:]+).*|\1|')
  echo "ARTIFACTS_SYNC: remote-mode (managed by brain server ${_GBRAIN_HOST:-remote})"
elif [ -d "$_GSTACK_HOME/.git" ] && [ "$_BRAIN_SYNC_MODE" != "off" ]; then
  _BRAIN_QUEUE_DEPTH=0
  [ -f "$_GSTACK_HOME/.brain-queue.jsonl" ] && _BRAIN_QUEUE_DEPTH=$(wc -l < "$_GSTACK_HOME/.brain-queue.jsonl" | tr -d ' ')
  _BRAIN_LAST_PUSH="never"
  [ -f "$_GSTACK_HOME/.brain-last-push" ] && _BRAIN_LAST_PUSH=$(cat "$_GSTACK_HOME/.brain-last-push" 2>/dev/null || echo never)
  echo "ARTIFACTS_SYNC: mode=$_BRAIN_SYNC_MODE | last_push=$_BRAIN_LAST_PUSH | queue=$_BRAIN_QUEUE_DEPTH"
else
  echo "ARTIFACTS_SYNC: off"
fi
```



Privacy stop-gate: if output shows `ARTIFACTS_SYNC: off`, `artifacts_sync_mode_prompted` is `false`, and gbrain is on PATH or `gbrain doctor --fast --json` works, ask once:

> gstack can publish your artifacts (CEO plans, designs, reports) to a private GitHub repo that GBrain indexes across machines. How much should sync?

Options:
- A) Everything allowlisted (recommended)
- B) Only artifacts
- C) Decline, keep everything local

After answer:

```bash
# Chosen mode: full | artifacts-only | off
"$_BRAIN_CONFIG_BIN" set artifacts_sync_mode <choice>
"$_BRAIN_CONFIG_BIN" set artifacts_sync_mode_prompted true
```

If A/B and `~/.gstack/.git` is missing, ask whether to run `gstack-artifacts-init`. Do not block the skill.

At skill END before telemetry:

```bash
"$GSTACK_BIN/gstack-brain-sync" --discover-new 2>/dev/null || true
"$GSTACK_BIN/gstack-brain-sync" --once 2>/dev/null || true
```


## Model-Specific Behavioral Patch (gpt-5.4)

The following nudges are tuned for the gpt-5.4 model family. They are
**subordinate** to skill workflow, STOP points, AskUserQuestion gates, plan-mode
safety, and /gstack-ship review gates. If a nudge below conflicts with skill instructions,
the skill wins. Treat these as preferences, not rules.

**Completion bias.** Do not end your turn with a partial solution when the full
solution is reachable. If you encounter an error, debug it. If a test fails, fix it.
If something is ambiguous, make your best judgment and proceed — don't stop and ask
unless you're genuinely blocked.

**Prefer doing over listing.** When you'd be tempted to write "you could also try X,
Y, or Z," try the best option yourself. Pick, execute, report results.

**No preamble.** Skip "Great question!", "Let me help with that", and restating the
user's request. Start with the work.

**AskUserQuestion is NOT preamble.** The "No preamble" and "Prefer doing over listing"
rules above do NOT apply to AskUserQuestion content. When you invoke AskUserQuestion,
the user is about to make a decision — they need context, not terseness. Always emit
the full format from the preamble's AskUserQuestion Format section:

1. **Re-ground** (project + branch + task — 1-2 sentences).
2. **Simplify (ELI10)** — explain what's happening in plain English a 16-year-old could
   follow. Concrete stakes, not abstract tradeoffs. Non-negotiable; this is NOT preamble.
3. **Recommend** — `RECOMMENDATION: Choose [X] because [one-line reason]` on its own
   line. Never omit this line. Never collapse it into the options list.
4. **Options** — lettered `A) B) C)` with Completeness scores (coverage-differentiated)
   or the "options differ in kind" note (kind-differentiated).

If you find yourself about to present an AskUserQuestion without the Simplify/ELI10
paragraph, without a RECOMMENDATION line, or by just listing options and asking "which
one?" — stop, back up, and emit the full format. The user will ask you to do it anyway,
so do it the first time.

**Reminder: subordination applies.** When a skill workflow says STOP, stop. When the
skill asks via AskUserQuestion, that is the wait-for-user gate, not an ambiguity.
Completion bias does not override safety gates.

**Anti-verbosity protocol (additional).** Your default output mode is too verbose for
tools that value terse output. Constrain:

- Status updates: one line, not a paragraph.
- Code explanations: only when the user asked for one, or when the code is genuinely
  surprising.
- Do not narrate what you are about to do. Just do it.
- Do not repeat the user's request back to them.
- When showing code changes, show the changed lines with minimal surrounding context.
- Markdown headings are not decoration. Use them only when structural.

**Cap answers at the shortest form that contains the answer.** If the answer is a
one-line command, reply with a one-line command.

## Voice

Direct, concrete, builder-to-builder. Name the file, function, command, and user-visible impact. No filler.

No em dashes. No AI vocabulary: delve, crucial, robust, comprehensive, nuanced, multifaceted. Never corporate or academic. Short paragraphs. End with what to do.

The user has context you do not. Cross-model agreement is a recommendation, not a decision. The user decides.

## Completion Status Protocol

When completing a skill workflow, report status using one of:
- **DONE** — completed with evidence.
- **DONE_WITH_CONCERNS** — completed, but list concerns.
- **BLOCKED** — cannot proceed; state blocker and what was tried.
- **NEEDS_CONTEXT** — missing info; state exactly what is needed.

Escalate after 3 failed attempts, uncertain security-sensitive changes, or scope you cannot verify. Format: `STATUS`, `REASON`, `ATTEMPTED`, `RECOMMENDATION`.

## Operational Self-Improvement

Before completing, if you discovered a durable project quirk or command fix that would save 5+ minutes next time, log it:

```bash
$GSTACK_BIN/gstack-learnings-log '{"skill":"SKILL_NAME","type":"operational","key":"SHORT_KEY","insight":"DESCRIPTION","confidence":N,"source":"observed"}'
```

Do not log obvious facts or one-time transient errors.

## Telemetry (run last)

After workflow completion, log telemetry. Use skill `name:` from frontmatter. OUTCOME is success/error/abort/unknown.

**PLAN MODE EXCEPTION — ALWAYS RUN:** This command writes telemetry to
`~/.gstack/analytics/`, matching preamble analytics writes.

Run this bash:

```bash
_TEL_END=$(date +%s)
_TEL_DUR=$(( _TEL_END - _TEL_START ))
rm -f ~/.gstack/analytics/.pending-"$_SESSION_ID" 2>/dev/null || true
# Session timeline: record skill completion (local-only, never sent anywhere)
$GSTACK_ROOT/bin/gstack-timeline-log '{"skill":"SKILL_NAME","event":"completed","branch":"'$(git branch --show-current 2>/dev/null || echo unknown)'","outcome":"OUTCOME","duration_s":"'"$_TEL_DUR"'","session":"'"$_SESSION_ID"'"}' 2>/dev/null || true
# Local analytics (gated on telemetry setting)
if [ "$_TEL" != "off" ]; then
echo '{"skill":"SKILL_NAME","duration_s":"'"$_TEL_DUR"'","outcome":"OUTCOME","browse":"USED_BROWSE","session":"'"$_SESSION_ID"'","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' >> ~/.gstack/analytics/skill-usage.jsonl 2>/dev/null || true
fi
# Remote telemetry (opt-in, requires binary)
if [ "$_TEL" != "off" ] && [ -x $GSTACK_ROOT/bin/gstack-telemetry-log ]; then
  $GSTACK_ROOT/bin/gstack-telemetry-log \
    --skill "SKILL_NAME" --duration "$_TEL_DUR" --outcome "OUTCOME" \
    --used-browse "USED_BROWSE" --session-id "$_SESSION_ID" 2>/dev/null &
fi
```

Replace `SKILL_NAME`, `OUTCOME`, and `USED_BROWSE` before running.

## Plan Status Footer

Skills that run plan reviews (`/plan-*-review`, `/codex review`) include the EXIT PLAN MODE GATE blocking checklist at the end of the skill, which verifies the plan file ends with `## GSTACK REVIEW REPORT` before ExitPlanMode is called. Skills that don't run plan reviews (operational skills like `/gstack-ship`, `/gstack-qa`, `/gstack-review`) typically don't operate in plan mode and have no review report to verify; this footer is a no-op for them. Writing the plan file is the one edit allowed in plan mode.

## Route first

This is the gstack router. Its one job is to send the request to the right skill.

1. If the request is about a browser, QA, dogfooding, screenshots, or inspecting a page
   (open a site, test a deploy, take a screenshot, check a flow visually) → invoke `/gstack-browse`.
2. Otherwise, route by the rules below. If nothing matches, answer directly.

Best-effort, record which way you routed (never block on it). Set `ROUTE_OUTCOME` to
`browse` (sent to /gstack-browse), `routed` (sent to another skill), or `direct` (answered
directly, no skill matched):
```bash
$GSTACK_ROOT/bin/gstack-telemetry-log --event-type route --skill gstack --outcome ROUTE_OUTCOME --session-id "$_SESSION_ID" 2>/dev/null || true
```

If `PROACTIVE` is `false`: do NOT proactively invoke or suggest other gstack skills during
this session. Only run skills the user explicitly invokes. This preference persists across
sessions via `gstack-config`.

If `PROACTIVE` is `true` (default): **invoke the Skill tool** when the user's request
matches a skill's purpose. Do NOT answer directly when a skill exists for the task.
Use the Skill tool to invoke it. The skill has specialized workflows, checklists, and
quality gates that produce better results than answering inline.

**Routing rules — when you see these patterns, INVOKE the skill via the Skill tool:**
- User describes a new idea, asks "is this worth building", brainstorms, pitches a concept → invoke `/gstack-office-hours`
- User asks to spec something out, file an issue, write up a ticket, "turn this into a GitHub issue", "backlog item" → invoke `/gstack-spec`
- User asks about strategy, scope, ambition, "think bigger", "what should we build" → invoke `/gstack-plan-ceo-review`
- User asks to review architecture, lock in the plan, "does this design make sense" → invoke `/gstack-plan-eng-review`
- User asks about design system, brand, visual identity, "how should this look" → invoke `/gstack-design-consultation`
- User asks to review design of a plan → invoke `/gstack-plan-design-review`
- User asks about developer experience of a plan, API/CLI/SDK design → invoke `/gstack-plan-devex-review`
- User wants all reviews done automatically, "review everything" → invoke `/gstack-autoplan`
- User reports a bug, error, broken behavior, "why is this broken", "this doesn't work", "wtf", "something's wrong" → invoke `/gstack-investigate`
- User asks to test the site, find bugs, QA, "does this work", "check the deploy" → invoke `/gstack-qa`
- User asks to just report bugs without fixing → invoke `/gstack-qa-only`
- User asks to review code, check the diff, pre-landing review, "look at my changes" → invoke `/gstack-review`
- User asks about visual polish, design audit of a live site, "this looks off" → invoke `/gstack-design-review`
- User asks to audit the live developer experience, time-to-hello-world → invoke `/gstack-devex-review`
- User asks to ship, deploy, push, create a PR, "let's land this", "send it" → invoke `/gstack-ship`
- User asks to merge + deploy + verify as one flow → invoke `/gstack-land-and-deploy`
- User asks to configure deployment for the project → invoke `/gstack-setup-deploy`
- User asks to monitor prod after shipping, post-deploy checks → invoke `/gstack-canary`
- User asks to update docs after shipping → invoke `/gstack-document-release`
- User asks to write docs from scratch, generate documentation, "document this feature/module" → invoke `/gstack-document-generate`
- User asks for a weekly retro, what did we ship, "how'd we do" → invoke `/gstack-retro`
- User asks for a second opinion, codex review → invoke `/codex`
- User asks for safety mode, careful mode → invoke `/gstack-careful` or `/gstack-guard`
- User asks to restrict edits to a directory → invoke `/gstack-freeze` or `/gstack-unfreeze`
- User asks to upgrade gstack → invoke `/gstack-upgrade`
- User asks to save progress, checkpoint, "save my work" → invoke `/gstack-context-save`
- User asks to resume, restore, "where was I" → invoke `/gstack-context-restore`
- User asks about security, OWASP, vulnerabilities, "is this secure" → invoke `/gstack-cso`
- User asks to make a PDF, document, publication → invoke `/gstack-make-pdf`
- User asks to launch a real browser for QA, "open the browser" → invoke `/gstack-open-gstack-browser`
- User asks to import cookies for authenticated testing → invoke `/gstack-setup-browser-cookies`
- User asks about page speed, performance regression, benchmarks → invoke `/gstack-benchmark`
- User asks what gstack has learned, "show learnings" → invoke `/gstack-learn`
- User asks to tune question sensitivity, "stop asking me that" → invoke `/gstack-plan-tune`
- User asks for code quality dashboard, "health check" → invoke `/gstack-health`

**When in doubt, invoke the skill.** A false positive (invoking a skill that wasn't
needed) is cheaper than a false negative (answering ad-hoc when a structured workflow
exists). The skill provides multi-step workflows, checklists, and quality gates that
always produce better results than an ad-hoc answer. If no skill matches, answer
directly as usual.

If the user opts out of suggestions, run `gstack-config set proactive false`.
If they opt back in, run `gstack-config set proactive true`.
