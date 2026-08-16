---
name: scroll-world
description: "Use only when explicitly requested by name. Build an immersive scroll-scrubbed \"fly through the world\" landing page for any industry or brand using Higgsfield. As the visitor scrolls, a pre-rendered camera flies from outside each scene into its interior, then flows on to the next scene with NO cuts — one continuous connected flight (Emons-style isometric diorama world, or any art direction you pick). The skill interviews the user for the topic, the story beats/sections, and brand kit, then generates cohesive scenes + seamless camera clips with Higgsfield and wires a portable, framework-agnostic scroll-scrub engine. The video chain renders through Monid by default (Seedance 2.0, pay-per-clip USD — capability re-checked each build, see Step 4) with Higgsfield credits as the fallback biller. Use when the user wants a \"3D world\" / \"browse-through-the-industry\" hero, a scroll cinematic, a diorama landing, or to turn a business into a scrollable world."
allowed-tools: Bash, Read, Write, Edit, AskUserQuestion, Skill
metadata:
  selection-policy: explicit-only
  opencode/autoinvoke: "false"
---

# scroll-world

Produces a landing page where **scroll drives a camera**: it dives from outside a scene
into its interior, then flies out and into the next scene, continuously, with no visible
cuts. The visuals are AI-generated — stills via Higgsfield (or Codex), the video chain
via **Monid by default** (pay-per-clip Seedance 2.0; Higgsfield credits as fallback) —
and the page just scrubs pre-rendered video by scroll position. This is the same technique behind Apple's scroll-through product
pages — the camera genuinely moves, scroll only drives time.

**What you generate:** N scene stills → N "dive-in" camera clips → N-1 "connector" clips
that join consecutive scenes seamlessly → a portable scrub engine that plays the whole
chain as one flight.

**The one rule that makes or breaks it:** seams must be *frame-identical*. Read
[The seamless chain](#step-5--the-seamless-chain-the-critical-part) before generating any
connector. Getting this wrong is the single most common failure and produces a visible
"pop" between scenes.

Do not assume a frontend framework. The scrub engine in `references/scrub-engine.js` is
self-contained vanilla JS (it builds its own DOM + injects its own CSS into a container
you give it), so it drops into plain HTML, Next.js, Vue, a Python-served page, anything.
The value of this skill is the Higgsfield pipeline, the prompts, and the seam method —
not the framework.

---

## Step 0 — Bootstrap

1. **Monid CLI — the default video-chain backend.** Check `monid --version`,
   `monid keys list` (active key) and `monid balance` — the chain is billed per
   clip in USD (Step 1.7 has the numbers; a 1080p N=6 chain ≈ $27). If the CLI is
   missing or the balance can't cover the chain, say so and fall back to
   rendering the chain on Higgsfield credits instead — same model, same
   pipeline, different biller (Step 4 → Monid backend).
2. **Higgsfield CLI — still required even on the Monid path**: it renders the
   scene stills (`gpt_image_2`) and is the home of the `kling3_0` NSFW fallback
   and the fallback chain. If `higgsfield` is not on `$PATH`, install per the
   `higgsfield-generate` skill. If `higgsfield workspace list` fails auth, ask the user
   to run `higgsfield auth login` (interactive OAuth — you cannot run it) and, if needed,
   `higgsfield workspace set <id>`. Confirm credits cover the stills (~N image
   gens) — plus `(2N-1)` video gens if the chain falls back here.
3. **ffmpeg / ffprobe** on `$PATH` (frame extraction + encoding).
4. **An image tool** for background knockout if you want floating scenes: PIL
   (`python3 -c "import PIL"`), or `cwebp`/`sips`. Optional — see Step 3.
5. **(Optional) Codex CLI** — if `codex` is on `$PATH` (≥ 0.125) and
   `codex login status` reports a ChatGPT login, the scene stills can be generated
   through Codex's built-in `image_gen` (the same gpt-image-2 model) billed to the
   user's ChatGPT subscription instead of Higgsfield credits — offer it at
   Step 1.7, command in Step 2. Absence just removes the option.
6. Caveats: macOS ships **bash 3.2** (no `declare -A`); don't use associative arrays in
   scripts. Higgsfield generations take **3–8 min each** — always run them detached
   (background) and poll, never a foreground blocking call. Reference-by-job-UUID is
   rejected by media flags — pass **local file paths** to `--image/--start-image/--end-image`.
   Video models differ in accepted params (e.g. Kling has no `--resolution`) and in whether
   they support start/end-image conditioning at all — before batching, confirm the chosen
   model's schema with `higgsfield model get <job_type>` and see the Step 4 model table.

---

## Step 1 — Interview the user

The **subject is the user's to state — ask it as an open question in plain prose**, never a
fabricated multiple-choice. A made-up list of industries biases them and reads as you
deciding their business for them; let them answer in their own words (their real business,
a client's, or any idea). Reserve structured multiple-choice (`AskUserQuestion` in Claude
Code; a plain either/or question elsewhere) for the genuinely
enumerable, lower-stakes choices below — art direction, camera style, and brand-kit
approach — and even
there, signal they can go their own way ("Other"). Ask only what you can't sensibly
default. Cover:

1. **Subject** (ask openly, not multiple-choice) — "What should this world be about? Your
   business, a client's, or any idea — a word or a sentence is fine." Capture the
   industry/product + a one-line pitch (e.g. "a bubble tea company, from leaf to last
   sip"), and a brand name if they have one; otherwise you'll propose one below.
2. **Brand kit** — offer three paths, pick one:
   - Import from a URL: `higgsfield marketing-studio brand-kits fetch --url <site> --wait`
     (pulls name, colours, tone). Then read it back with `brand-kits list --json`.
   - The user hands you palette + name + tone directly.
   - You propose a palette + name and let them approve.
   Capture **4–6 named hex values**, a display name, and a tone word or two.
3. **Art direction** — default is "soft matte low-poly **clay diorama**, isometric,
   tilt-shift miniature, warm light." Offer alternatives (flat papercraft, glossy toy,
   claymation, neon night). Whatever is chosen becomes the shared **style preamble**
   reused verbatim in every scene prompt (this is what makes the world cohesive).
4. **Camera style — ALWAYS ask; it's the film's personality, not a technical
   detail.** Ask by feel (`AskUserQuestion` in Claude Code; a plain question
   elsewhere) and record the answer as `CAMERA`. The options map to the Step 4
   architectures — Step 4 then *implements* the choice, it never re-decides it:
   - **"Fly through the world"** — the camera dives into each scene, pulls up and
     out, and hops across the miniature world to the next; angles change
     constantly, big expressive aerial moves (this is the flagship-demo look).
     → Architecture B. Recommend as the default for diorama/miniature art
     directions.
   - **"One continuous walkthrough"** — a single forward flight that glides
     through each scene straight into the next, never pulling back; expressive
     but always-forward moves per scene (camera grammar table). → Architecture A.
     Recommend as the default for grounded/photoreal art directions.
   - **"Locked isometric glide"** — the camera keeps one fixed angle for the whole
     film, Emons-style; the world slides past/toward it, no rotation, no reveals.
     → Architecture A + the locked-iso clause in every leg prompt (prompts.md).
   State the trade-off in one line each (B reverses direction at seams — charming
   in miniature, jarring in realism; locked-iso is the calmest and cheapest to
   re-roll; walkthrough sits between).
5. **The journey (sections)** — the ordered scenes the camera flies through. Propose a
   set derived from the subject's own value chain and let the user edit. 5–7 works well.
   Boba example: farms → pearl kitchen → flagship shop → delivery → community plaza →
   the hero product. Each section needs: a short subject description (what's IN the
   diorama), an eyebrow, a headline, one line of body, and 0–3 tag pills. The last
   section is usually the hero product + the CTA.
6. **Mobile version — ALWAYS ask this; never silently generate both.** Ask as a
   two-option choice (`AskUserQuestion` in Claude Code; a plain question elsewhere):
   *"Want a mobile-optimized version too? The mobile version is a second camera chain
   rendered natively in **9:16 portrait** — composed for phones, not a crop of the
   landscape film — which roughly doubles the Higgsfield credit spend (state the
   estimated number)."*
   Options: "Desktop only" / "Desktop + mobile (native 9:16 — ~2× credits)". The
   credit cost must be stated to the user, not just implied.
   What the answer gates:
   - **Yes** → render the parallel 9:16 portrait chain and ship it as the mobile variants
     (Step 6 / pipeline.md §6b): portrait start canvases → 9:16 dives + connectors
     frame-locked against their own renders → 720-wide `-m.mp4` encodes → `stillMobile`
     portrait posters. Wire `clipMobile`/`connectorsMobile`/`stillMobile` (Step 7); run
     the full mobile QA (Step 8). Budget ~2N-1 extra video gens + NSFW re-rolls.
     **Never ship the centre-crop as the mobile version by default** — if credits can't
     cover the portrait chain, say so and offer the crop encodes (pipeline.md §6) as an
     explicitly-labelled stopgap the user must approve.
   - **No** → skip the mobile encodes and wiring entirely. The engine's phone hardening
     (seek-coalescing, iOS priming, safe-area CSS) is always on regardless — that's not
     a "mobile version," it's just the page not breaking when a phone visits — so a
     desktop-only build still degrades gracefully.

7. **Budget — engines shown by cost, decided before anything renders.** Present the
   render tiers (`AskUserQuestion`), then compute and state the estimated total for
   the user's N scenes — `N stills + (2N−1) videos [videos ×2 if mobile] + ~15%
   re-roll headroom` — and get a go before generating.
   - **Video tier** (roster only — every option frame-locks seams, Step 4):

     | Tier | Model | Rough cost |
     |---|---|---|
     | Draft / previz | `seedance_2_0_mini` (720p) | ~¼ of Standard |
     | Standard (default) | `seedance_2_0` (1080p) | baseline |
     | Alternate | `kling3_0` (720p native) | ≈ Standard; different look + content filter |

     Draft doubles as the previz path: run the whole chain cheap, approve the
     journey, re-render final legs on Standard (pipeline.md Notes) — suggest it
     unprompted when the balance reads tight.
   - **Backend — Monid is the DEFAULT biller for the chain** (Step 0.1; wiring
     in pipeline.md → Monid backend). Same Seedance 2.0, per-clip USD instead of
     credits. Token-priced `width × height × 24 × seconds / 1024` at $7/1M
     (480p/720p) or $7.7/1M (1080p) — measured: 1080p 8s dive ≈ $2.99, 5s
     connector ≈ $1.87; 720p ≈ $1.21 / $0.76; 480p ≈ $0.28 / $0.35. An N=6
     desktop chain ≈ $27 at 1080p / ~$11 at 720p vs Higgsfield Plus-monthly ≈
     $32 / $16 — ~15% cheaper per clip, parity with Plus-annual; structurally
     better for one-off builds (pay-per-use, no monthly expiry). On Monid the
     Draft/previz tier is simply the **same endpoint at 480p** — no model swap,
     so previz→final stays one-model by construction. State `monid balance`
     against the estimate; **fall back to Higgsfield credits** (per-model tiers
     above) when the user prefers their subscription, the balance is short, or
     the model must be `kling3_0` (Higgsfield-only). It's the same underlying
     model (`seedance_2_0` ≙ Monid's `seedance-2.0`), so finishing a stranded
     chain on the other biller is a reasonable rescue — but the serving stacks
     differ and cross-provider seam character is **untested**: eyeball the first
     rescued seam before rendering the rest, same as any model swap.
   - **Stills source** (only offer if the Codex CLI is present, Step 0.5):
     Higgsfield `gpt_image_2` (spends credits) vs **Codex `image_gen`** — the same
     gpt-image-2 model billed to the ChatGPT subscription (zero credits; counts
     toward Codex usage limits; 1536×1024 output — exactly 3:2, slightly under
     Higgsfield's 2k). Stills are plain PNGs handed to `--start-image`, so the
     video chain is indifferent to their source. Command in Step 2. **One source
     for all N stills of a build** — the two render with slightly different
     character (verified: Codex runs warmer/lighter), and mixing sources across
     scenes reads as style drift, same reason the video chain uses one model.
   - **Calibrate costs, don't guess.** The CLI exposes no pricing and plans differ.
     Run ONE still and ONE video first, diff `higgsfield workspace list` before/
     after, extrapolate to the full run, and warn the user whenever the estimate
     exceeds ~70% of the balance. (Observed on a plus plan, 2026-07: Standard
     video ≈ 40–55 credits, still ≈ 15.) A real `not_enough_credits` mid-run is
     recoverable (finished clips survive; resume after top-up) but ugly — the
     whole point of this step is that the user decides *before* the spend.

If the user names a video model outside the roster, honor it **only if it can
frame-lock seams** (Step 4). This skill only ships seamless output, so a model that
can't frame-lock is declined with a one-line why, not substituted in — use a roster
model instead.

Keep the scroll mechanic fixed (continuous fly-through) — that's the point of the skill.
See `references/prompts.md` for the intake checklist and copy structure.

---

## Step 2 — Generate the scene stills

One image per section, **all sharing the same style preamble** for cohesion. Default
model **`gpt_image_2`** (crisp, great at isometric illustration; returns a solid/white
background which is perfect for floating diorama "islands"). Use `nano_banana_2` only if
the brief is character/cartoon-heavy (note: `nano_banana_2` is a CLI alias — it resolves
to `nano_banana_pro`; it won't appear under that name in `higgsfield model list`).

Prompt shape (full templates in `references/prompts.md`):

```
<STYLE PREAMBLE, identical every time>. On a plain solid <bg> background with a soft
contact shadow. <PALETTE hexes>. No text, no letters, no logos, centered, 3:2.
Subject: <what is in THIS diorama>.
```

- Run all N concurrently, detached. Command per scene:
  `higgsfield generate create gpt_image_2 --prompt "$(cat scene_i.txt)" --aspect_ratio 3:2 --resolution 2k --quality high --wait --wait-timeout 15m --json > scene_i.json 2>scene_i.err`
- Result URL is `.[]0.result_url` in the `--wait --json` output. `curl` it down.
- **Codex stills variant** (if chosen at Step 1.7 — subscription-billed, zero
  credits): same prompt files, same byte-identical preamble, generated by Codex's
  built-in `image_gen`:

  ```bash
  codex exec -C "$WORK" -s workspace-write --skip-git-repo-check \
    'Use the image generation tool ($imagegen) to generate: '"$(cat "$WORK/still_i.txt")"' Wide 3:2 landscape, high resolution. Save it as ./still_i.png. Do not do anything else.' \
    < /dev/null
  ```

  Single-quote the `$imagegen` segment (the shell must not expand it); if editing
  with reference images, the prompt goes BEFORE any `-i` flag (it's variadic).
  ~1–3 min per image; run a few in parallel, not all N at once — and keep the
  `< /dev/null`: parallel `codex exec` calls sharing a script's stdin hang
  waiting for input (Gotchas). Output lands at
  1536×1024 (3:2) — fine for `--start-image` and posters. Everything downstream
  (cohesion review, knockout, dives) is unchanged.
- A generation may fail transiently (HTTP 503) — re-roll that one individually; don't
  restart the batch.
- **Review the stills before continuing.** They must read as one cohesive world (same
  angle, palette, light). If one is off-style, regenerate it, optionally passing an
  approved scene as `--image` to lock style.

See `references/pipeline.md` for the exact batch script.

---

## Step 3 — (Optional) Float the scenes

If you want the dioramas to float over an atmospheric background instead of sitting in a
solid box, knock out the flat background to transparency with
`references/knockout.py` (border-connected flood fill — preserves interior colour that
matches the bg, e.g. cream walls). Then encode to webp. If you'd rather keep it simple,
just make the page background the same colour as the scene background and skip this.

These stills double as **video posters and lazy-load fallbacks**, so keep them.

---


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Step 4 — Camera architecture (implements the Step 1.4 choice)](references/extended-guidance.md#step-4-camera-architecture-implements-the-step-14-choice)
- [Step 5 — Connectors (architecture B only)](references/extended-guidance.md#step-5-connectors-architecture-b-only)
- [Step 6 — Encode for smooth scrubbing](references/extended-guidance.md#step-6-encode-for-smooth-scrubbing)
- [Step 7 — Assemble the page](references/extended-guidance.md#step-7-assemble-the-page)
- [Step 8 — QA the seams (don't skip)](references/extended-guidance.md#step-8-qa-the-seams-dont-skip)
- [Gotchas (hard-won)](references/extended-guidance.md#gotchas-hard-won)
- [References](references/extended-guidance.md#references)

