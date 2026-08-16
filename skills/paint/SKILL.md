---
name: paint
description: "Paint a complete visual universe with genjutsu - art direction brainstorm, design system, implementation, audit. Anti-AI-slop design pipeline. Adapts to Web, Android (Compose), Apple (SwiftUI)."
allowed-tools: Bash, Read, Edit, Write, Grep, Glob, WebSearch, Artifact
---

# Paint - The Master Painter

> Paint a complete visual universe. Brainstorm first, design system second, implement third, audit last.
> This is NOT a quick beautifier - it's a full design pipeline.

---

## Voice

This skill speaks in two registers:

**During execution** - light ninja flair, signature, immersive. Short.
- "Brushing the color palette..."
- "Painting the hero with the unalloyed gold."
- "Setting the spacing tokens."

**In reports / final summaries / audit results** - plain, factual, dev-readable. Drop the flair entirely.
- "Done. Design system generated. Files: MASTER.md, tokens.css, theme.config.ts. 3 pages painted."
- No mystic prose, no metaphors. Just what changed, files touched, next step.

The flair lives at the intro and during work narration. The moment a result lands or a question gets asked, it's gone.

---

## /paint vs /cast

| | `/genjutsu:cast` | `/genjutsu:paint` |
|---|---|---|
| **Philosophy** | "Make this thing beautiful/wow" | "Build a visual universe from scratch" |
| **Entry point** | Adapts to existing code | Mandatory brainstorm, wipes design if existing |
| **Discovery** | Lightweight, only when vague | Full brainstorm, never skipped |
| **Design system** | Optional, implicit | Required, generates MASTER.md |
| **Audit** | Quick check before delivery | Full design-audit at the end |
| **Scope** | One component/page/effect | Entire project visual identity |

`/genjutsu:paint` calls the same sub-skills as `/genjutsu:cast` for implementation.

---

## Iron Rules

1. **Never skip the brainstorm.** Not even if the user says "just make it look good." Especially then. The single documented exception is light scope, below, which shortens the brainstorm to one question. It never removes it.
2. **One question at a time during brainstorm.** Never bundle. The second question depends on the first answer.
3. **Never proceed without both theses validated.** Visual + interaction, both explicitly approved.
4. **Every design token comes from MASTER.md.** No magic numbers, no rogue hex values. On light scope, where no MASTER.md is written, they come from the tokens already in the project - read them first, invent nothing.
5. **Every animation respects the interaction thesis.** Timing, easing, forbidden patterns — no exceptions.
6. **Never install a dependency without asking.**
7. **Work page by page, validate page by page.** Never try to do everything at once.
8. **The audit is not optional.** Phase 5 always runs, even if the user seems happy.
9. **Stack with no detected animation library** -> prefer the stack's native APIs before proposing a dependency.
10. **Animation library detected** (GSAP, Framer Motion, Lottie, Rive, etc.) -> respect the dev's choice. Do not propose a replacement.
11. **Show, don't just describe.** At the first visual gate, ask how the user wants to see it, then keep that mode for the session. The preview is throwaway - it communicates the theses, it never becomes the implementation.

---

## Light scope - the one shortened path

`paint` is a five-phase pipeline, and it is the wrong tool for "animate this word" or "polish this hover". Those belong to `/genjutsu:cast`, which is the default entry point.

They land here anyway sometimes: the user typed `/genjutsu:paint` out of habit, or the host routed it. Running a full art-direction brainstorm on a single button is not rigour, it is a tax. Recognise the case and shorten, out loud.

**It is light scope when all three hold:**

- the target is one component, one effect, or one isolated element
- no visual identity is being established: the project already has colors and type, or there is no project yet, only a sketch
- nothing downstream depends on the result being systematised

If two or more fail, it is not light scope. Run the full pipeline and say in one line why.

**What changes:**

| Phase | Full | Light |
|---|---|---|
| 1 BRAINSTORM | five domains, one question at a time | **one question**, the least obvious one, then stop |
| 2 THESIS | visual + interaction, both validated | interaction thesis only, still validated |
| 3 DESIGN SYSTEM | generate MASTER.md and the stack token files | **skipped.** Read the tokens already in the project and use them. Write no MASTER.md. |
| 4 IMPLEMENT | page by page, validate page by page | the one component |
| 5 AUDIT | full design-audit sub-skill | the quick check: reduced-motion, exit animation, 60fps |

**Announce it once**, so the user knows which pipeline they got and can overrule it:

> "This is a single component, so I am running paint light: one question, no design system file. Say so if you want the full pipeline."

**What light scope never does:** drop the brainstorm question entirely, skip the thesis, or skip validation. Every gate stays. Only their number goes down.

---

<!-- genjutsu:shared:preview:start -->
## Showing Your Work - The Preview Gate

Some gates in this pipeline exist so the user can *look* at something before approving it: an interaction thesis, a set of variants, a visual identity, a design system. Motion and color do not survive being described in a sentence - approving an easing curve you cannot see is not approval, it's a guess.

So before the first gate of that kind, ask how they want to see it. Then never ask again.

**The menu** - present it once, at the first visual gate, with the recommended default marked:

> Before I show you this - how do you want to see it?
>
> **A. Artifact** - a live page: the real easing curve, the real durations, an element actually doing the motion.
> **B. Live preview** - a throwaway route in your project, real stack, real tokens. Native: a `@Preview` / `#Preview` scratch file.
> **C. Inline** - written out here in the conversation.

**Recommended default** - state it in the menu, never apply it silently:

| Situation | Default |
|---|---|
| Scope is light (a hover, one transition) | C - inline |
| Scope is medium or full, web stack | A - artifact |
| Scope is medium or full, Compose / SwiftUI | B - live preview, A as second choice |
| A full visual identity or design system is on the table | A - artifact |
| No dev server, or the repo must not be written to | A - artifact |
| Host is Cowork and there is no project checkout to write into | A - artifact, B is unavailable |

**The choice sticks for the whole session.** At every later gate, announce the mode in one line ("Variants in artifact.") and go. Do not reopen the menu. The user switches by saying so - "show me that as text", "put it in an artifact", "just tell me" - respect it immediately, and the new mode becomes the session default from then on.

**Which host is this?** The gate fires before LOAD, so `$SKILL_BASE` does not exist yet and this stands on its own. Detect once, cheaply, then map:

```bash
if [ -d /mnt/skills/user ]; then
  GENJUTSU_HOST=claude-ai
elif [ -d /mnt/.claude/skills ] \
  || [ -n "$(find /sessions -maxdepth 6 -type d -path '*/.claude/skills' 2>/dev/null | head -1)" ]; then
  GENJUTSU_HOST=cowork
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || [ -d "$HOME/.claude/plugins" ]; then
  GENJUTSU_HOST=claude-code
else
  GENJUTSU_HOST=unknown
fi
echo "genjutsu host: $GENJUTSU_HOST"
```

Cowork is tested before Claude Code on purpose: both can have a `~/.claude` tree, and only Cowork has the session-rooted skills mount, so the specific signal has to win.

**Producing the preview** - resolve the host, degrade, never fail:

| Host | A - artifact | C - inline |
|---|---|---|
| claude.ai | Rendered natively. Just produce one. | Written out in the conversation. |
| Cowork | The host's persistent artifact. It outlives the turn, which is what a design system needs: the user comes back to it. | The host's inline widget, rendered in place. Right default for a short task. |
| Claude Code | The `Artifact` tool, when it is available. | Written out in the conversation. |
| unknown | A self-contained HTML file written to a temp path, hand back the path. | Written out in the conversation. |

Call whatever the host actually exposes, under the name it exposes it as - check the tools available in the session rather than assuming one. If nothing renders, fall back down the table rather than failing the gate: an inline preview always beats an aborted one.

**B - live preview needs a project to write into.** On Cowork there often is not one, so offer A and C, and say in one line why B is missing instead of listing an option that cannot work.

**What goes in it.** A preview that restates the sentence in a nicer font is worthless. Carry what a sentence cannot:

| Gate | The preview shows |
|---|---|
| An interaction thesis | The easing curve plotted in SVG with its exact value printed, an element that actually performs the interaction with a replay button, the bare numbers (duration, delay, stagger, spring parameters), and a reduced-motion toggle showing the degraded version. |
| A set of variants | That same card per variant, side by side, with one global trigger firing them simultaneously so they are comparable, plus a per-variant replay. |
| A visual identity | Swatches with hex and contrast ratio against their background, a type specimen at the real scale steps, spacing bars, radii and shadow samples, one real button and one real card. |
| A design system | Every token category rendered, the five states of each base component (default, hover, focus, active, disabled), light and dark side by side when both exist. |

**Rules the preview obeys:**

- **It is throwaway. It never becomes the implementation.** Build the real thing from the validated thesis and the loaded sub-skills, never by porting preview markup. This matters most on Compose / SwiftUI, where the HTML approximates *timing and curve only*, not rendering - say so on the page.
- Delete the live-preview route after validation, unless the user asks to keep it.
- Never install a dependency to build a preview.
- Never start a dev server without asking.
- Only show values that are in the thesis. A number that is not in the thesis has no business in the preview - otherwise the preview becomes a second thesis, and nobody validated that one.
<!-- genjutsu:shared:preview:end -->

---

## Sub-skills Path Detection

<!-- genjutsu:shared:skill-base:start -->
```bash
# Environment detection, most specific first:
# - claude.ai: skills are uploaded individually to /mnt/skills/user/<name>/
# - Claude Code: ${CLAUDE_PLUGIN_ROOT} resolves to THIS plugin version's
#   install directory. Claude Code substitutes it anywhere in skill content.
# - Cowork and skills-directory installs: no fixed path exists. The tree is
#   mounted under a session root that changes every run, e.g.
#   /sessions/<id>/mnt/.claude/skills/genjutsu/_jutsu. Probed last, so the two
#   environments above keep resolving exactly as they did before.
# Single-bundle upload (genjutsu.zip) first: sub-skills live under this skill's
# own dir, e.g. /mnt/skills/user/genjutsu/_jutsu/<name>/.

# Probe for a mounted _jutsu when no fixed path applies. Bounded on purpose:
# every root is either shallow or depth-capped, so this never walks the disk.
genjutsu_probe_jutsu() {
  probe_hit=""
  # Walk up from the working directory first: cheapest, and correct whenever
  # the session root is an ancestor of wherever the pipeline is running. Hard
  # bounded, and the case guard catches "." and "": an empty or relative PWD
  # would otherwise never reach "/" and the loop would spin forever.
  probe_dir="${PWD:-$(pwd)}"
  probe_n=0
  while [ "$probe_n" -lt 24 ]; do
    probe_n=$((probe_n + 1))
    probe_hit="$(find "$probe_dir/.claude/skills" -maxdepth 2 -type d -name _jutsu 2>/dev/null | head -1)"
    [ -n "$probe_hit" ] && { printf '%s\n' "$probe_hit"; return 0; }
    case "$probe_dir" in /|.|"") break ;; esac
    probe_dir="$(dirname "$probe_dir")"
  done
  # Then the fixed roots. A skills directory holds _jutsu two levels down, so
  # that is all they get: no reason to traverse a populated one any deeper.
  for probe_root in "$HOME/.claude/skills" /mnt/.claude/skills; do
    [ -d "$probe_root" ] || continue
    probe_hit="$(find "$probe_root" -maxdepth 2 -type d -name _jutsu 2>/dev/null | head -1)"
    [ -n "$probe_hit" ] && { printf '%s\n' "$probe_hit"; return 0; }
  done
  # A session root is the one layout that needs more, for the session id and
  # its mnt/ wrapper. Still capped, and skipped entirely when absent.
  if [ -d /sessions ]; then
    probe_hit="$(find /sessions -maxdepth 8 -type d -path '*/.claude/skills/*/_jutsu' 2>/dev/null | head -1)"
    [ -n "$probe_hit" ] && { printf '%s\n' "$probe_hit"; return 0; }
  fi
  return 1
}

BUNDLE_JUTSU="$(find /mnt/skills/user -maxdepth 2 -type d -name _jutsu 2>/dev/null | head -1)"
if [ -n "$BUNDLE_JUTSU" ]; then
  # claude.ai - single self-contained genjutsu bundle
  SKILL_BASE="$BUNDLE_JUTSU"
elif [ -d "/mnt/skills/user" ]; then
  # claude.ai - each sub-skill is its own uploaded skill (detect the mount, not
  # one specific sub-skill, so a partial upload still resolves the base).
  SKILL_BASE="/mnt/skills/user"
else
  # Claude Code plugin
  SKILL_BASE="${CLAUDE_PLUGIN_ROOT}/skills/_jutsu"
  # Fallback if the placeholder was not substituted: newest installed version.
  # Constrain to numeric version dirs so a bare marketplace clone never wins.
  if [ ! -d "$SKILL_BASE" ]; then
    SKILL_BASE=$(find ~/.claude/plugins/cache -type d -path '*/genjutsu/[0-9]*/skills/_jutsu' 2>/dev/null | sort -V | tail -1)
  fi
  # Cowork / skills-directory install: session-rooted mount, nothing fixed to
  # match, so probe for it only once the two fixed layouts have both missed.
  if [ -z "$SKILL_BASE" ] || [ ! -d "$SKILL_BASE" ]; then
    SKILL_BASE="$(genjutsu_probe_jutsu)"
  fi
fi

# Abort clearly instead of cat-ing bogus paths if resolution failed. Name every
# root that was tried, so a new host layout can be reported instead of guessed.
if [ -z "$SKILL_BASE" ] || [ ! -d "$SKILL_BASE" ]; then
  echo "genjutsu: could not resolve the sub-skills directory." >&2
  echo "  claude.ai   - upload the genjutsu skill ZIP(s) via Customize > Skills." >&2
  echo "  Claude Code - reinstall the plugin, then run /reload-plugins." >&2
  echo "  Cowork      - expected a _jutsu directory under a */.claude/skills/<name>/ mount." >&2
  echo "  Tried: /mnt/skills/user, \$CLAUDE_PLUGIN_ROOT, ~/.claude/plugins/cache," >&2
  echo "         \$PWD ancestors, ~/.claude/skills, /mnt/.claude/skills, /sessions." >&2
fi

# Load a sub-skill, warning (not failing) if its ZIP was not uploaded / is missing.
# The entry filename depends on the artifact, not on the host: a plugin install
# ships SKILL.md, while the claude.ai bundle renames every inner one to GUIDE.md
# at packaging time. Either can end up mounted under a Cowork session root, so
# try both. The name is assembled from parts on purpose - spelled out in full it
# would be rewritten by the same packaging step, defeating the fallback.
load_skill() {
  for jutsu_doc in SKILL GUIDE; do
    if [ -f "$SKILL_BASE/$1/$jutsu_doc.md" ]; then
      cat "$SKILL_BASE/$1/$jutsu_doc.md"
      return 0
    fi
  done
  echo "genjutsu: sub-skill '$1' not found - upload its ZIP (claude.ai) or reinstall the plugin; continuing without it." >&2
}
```
<!-- genjutsu:shared:skill-base:end -->

All sub-skills are loaded via `load_skill <name>` (defined above), which cat's `$SKILL_BASE/<name>/SKILL.md` and warns instead of failing if a sub-skill was not uploaded.

---


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Pipeline](references/extended-guidance.md#pipeline)
- [Existing Project Protocol](references/extended-guidance.md#existing-project-protocol)
- [Red Flags — You're About to Violate This Skill](references/extended-guidance.md#red-flags-youre-about-to-violate-this-skill)

