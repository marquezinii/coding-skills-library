<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Wrapping component

Wrap the composition in `<hyperframes-slideshow>` around `<hyperframes-player>` in any embedding context:

```html
<hyperframes-slideshow>
  <hyperframes-player src="deck.html"></hyperframes-player>
</hyperframes-slideshow>
```

`<hyperframes-slideshow>` provides the navigation chrome (Present, Prev / Next, counter, global mute when `sound` is present, fullscreen), keyboard handling (← / →, Space / Backspace, and P for Present), touch swipe, and hotspot overlays.

The slideshow automatically sets the `interactive` attribute on every inner `<hyperframes-player>` at mount time, so clickable controls, links, native media controls, and custom players inside the composition iframe receive pointer events as expected. (Outside a slideshow wrapper, you must add `interactive` manually on `<hyperframes-player>` — the player defaults to `pointer-events: none` on the iframe so clicks on the player host don't get hijacked into toggling timeline playback.)

**Presenter mode:** use the built-in Present icon button in the slideshow nav capsule, or press P. It calls `window.open('?mode=audience')` for a fullscreen audience tab; the originating tab becomes the presenter view (current slide reduced, next-slide preview, notes, elapsed timer). The two tabs sync via `BroadcastChannel('hf-slideshow:' + location.pathname)`. Do not add a custom wrapper-level Present button; the shared component owns its placement, icon, styling, and audience-mode hiding.

**Presenting over Google Meet / Zoom (screen share):** share the _audience_ surface, keep the presenter view on your own screen.

- **Google Meet (or any in-Chrome share):** Present → in Meet choose **Share screen → A tab** → pick the audience tab → switch back to the presenter tab. Chrome keeps a captured tab rendering while backgrounded, so animations and slide nav stay live. Do **not** share "A window" or "Entire screen" — a fully covered window stops rendering (frozen slides for viewers), and entire-screen exposes your notes.
- **Zoom (desktop app):** drag the audience tab out into its own window and share that window. Zoom captures via the OS, so if the audience window becomes _fully_ covered it freezes — use a second monitor, or keep a sliver of the audience window visible behind the presenter view.

Presenter-driven media playback has an autoplay-policy constraint: `BroadcastChannel` can sync intent, time, and state, but it cannot transfer the presenter's user activation to the audience tab. The shared slideshow player mirrors native media events and starts remote audience playback muted first; only fall back to the standalone harness's audience unlock behavior if muted `media.play()` is rejected or if the deck specifically requires audible audience playback. Do not keep applying remote `timeupdate` messages after a rejected play, or the audience will silently seek through the video without playback.

Presenter notes are editable in the presenter view. Edits are stored in `localStorage` per deck and slide, layered over the manifest notes without rewriting the composition file. Do not add one-off note-editing scripts to decks; rely on the shared slideshow player behavior. If a standalone/custom wrapper truly needs to implement this outside the shared player, use the deterministic storage snippet in `skills/slideshow/references/standalone-harness.md`.

### Media cleanup on slide exit

The slideshow controller owns slide-exit media cleanup. When navigation changes slide or sequence, it calls `hyperframes-player.stopMedia()` before entering the next slide. That command:

- posts `stop-media` to the iframe runtime, which stops WebAudio and pauses native `<video>` / `<audio>` elements;
- pauses same-origin iframe media directly as a fallback; and
- pauses parent-frame proxies adopted from iframe media.

Same-slide fragment navigation does **not** stop media. Global/deck-level parent audio, such as a background track wired through `audio-src`, is not treated as slide media.

Do not add per-slide cleanup scripts for normal media players. Keep slide video/audio as normal media in the composition; use `data-has-audio="true"` only when the player should preserve audible native video audio instead of treating it as silent visual media.

If the source page has custom controls or visualizations attached to media, those controls must listen to the same native element the slideshow player stops and mutes. A pause caused by slide exit, presenter sync, native controls, custom controls, or the global mute button should all update the visible custom UI through media events, not through parallel state.

When implementing direct iframe fallback cleanup, treat iframe media as cross-realm DOM. Do not test iframe nodes with the parent page's `el instanceof HTMLMediaElement`; that returns false in real browsers. Use `el.ownerDocument.defaultView.HTMLMediaElement` (or an equivalent tag/duck-type guard) before setting `muted` or calling `pause()`.

### Global nav mute

When `<hyperframes-slideshow sound>` renders the nav mute button, that button is the global mute control for the page. It must mute:

- child `<hyperframes-player>` instances, including same-origin iframe media;
- top-level page `<audio>` / `<video>` elements; and
- wrapper-owned SFX/global `Audio` objects via the `hf-sound` event.

Do not add a second mute button inside the composition. If a wrapper script creates `new Audio(...)` objects that are not attached to the DOM, it must listen for `hf-sound` and set `clip.muted = detail.muted` on each object, not merely skip future plays.

The same cross-realm rule applies here: global mute must reach iframe `<video>` / `<audio>` elements through the child frame's DOM realm. A passing unit test in a single DOM realm is not enough; verify in a browser that the actual iframe media elements report `muted: true` after clicking the nav mute button.

`hyperframes present` serves built bundles from `packages/player/dist`. After changing player or slideshow chrome behavior, run `bun run build` in `packages/player` and restart the present server before testing in a browser.

Presenter notes are editable in the presenter view. Edits are stored in `localStorage` per deck and slide, layered over the manifest notes without rewriting the composition file. Do not add one-off note-editing scripts to decks; rely on the shared slideshow player behavior. If a standalone/custom wrapper truly needs to implement this outside the shared player, use the deterministic storage snippet in `skills/slideshow/references/standalone-harness.md`.

### Media cleanup on slide exit

The slideshow controller owns slide-exit media cleanup. When navigation changes slide or sequence, it calls `hyperframes-player.stopMedia()` before entering the next slide. That command:

- posts `stop-media` to the iframe runtime, which stops WebAudio and pauses native `<video>` / `<audio>` elements;
- pauses same-origin iframe media directly as a fallback; and
- pauses parent-frame proxies adopted from iframe media.

Same-slide fragment navigation does **not** stop media. Global/deck-level parent audio, such as a background track wired through `audio-src`, is not treated as slide media.

Do not add per-slide cleanup scripts for normal media players. Keep slide video/audio as normal media in the composition; use `data-has-audio="true"` only when the player should preserve audible native video audio instead of treating it as silent visual media.

When implementing direct iframe fallback cleanup, treat iframe media as cross-realm DOM. Do not test iframe nodes with the parent page's `el instanceof HTMLMediaElement`; that returns false in real browsers. Use `el.ownerDocument.defaultView.HTMLMediaElement` (or an equivalent tag/duck-type guard) before setting `muted` or calling `pause()`.

### Global nav mute

When `<hyperframes-slideshow sound>` renders the nav mute button, that button is the global mute control for the page. It must mute:

- child `<hyperframes-player>` instances, including same-origin iframe media;
- top-level page `<audio>` / `<video>` elements; and
- wrapper-owned SFX/global `Audio` objects via the `hf-sound` event.

Do not add a second mute button inside the composition. If a wrapper script creates `new Audio(...)` objects that are not attached to the DOM, it must listen for `hf-sound` and set `clip.muted = detail.muted` on each object, not merely skip future plays.

The same cross-realm rule applies here: global mute must reach iframe `<video>` / `<audio>` elements through the child frame's DOM realm. A passing unit test in a single DOM realm is not enough; verify in a browser that the actual iframe media elements report `muted: true` after clicking the nav mute button.

`hyperframes present` serves built bundles from `packages/player/dist`. After changing player or slideshow chrome behavior, run `bun run build` in `packages/player` and restart the present server before testing in a browser.

---

## Running a slideshow standalone (interim)

The **durable answer** is engine-hosted: `hyperframes preview --slideshow` / studio present mode will host the composition over the real HyperFrames engine, which drives seek-timelines, owns the gesture frame, and reads the island from the composition. That path is coming; prefer it once it ships.

Until then, standalone demos (a composition opened via the bare player bundle in a browser, without the engine) require workarounds for three gaps: the composition must expose a seekable root timeline, the island must be duplicated into the wrapper, and wrapper-owned SFX/global audio should live in the parent frame. These patterns are documented in:

```
skills/slideshow/references/standalone-harness.md
```

Do not treat the patterns there as the blessed model — they exist only to bridge the gap until the engine-hosted path lands.

## Handoff

For a public or user-facing slideshow project, the root `index.html` should be a runnable slideshow entrypoint. Opening it in a browser should show slideshow navigation and respond to Next/Prev; it should not expose only the raw composition and require the user to know about Studio or an internal wrapper file. If the raw HyperFrames composition must remain separate for CLI compatibility, put it in a subdirectory such as `composition/index.html` and point scripts/commands at that directory.

The direct-open wrapper must rely on the built-in Present icon button rendered by `<hyperframes-slideshow>`. Do not add a bespoke `#present-btn`, fixed-position button, or wrapper-specific Present styling. The shared component owns the control bar, hides Present in `?mode=audience`, and supports P as a keyboard shortcut.

Validate the direct-open path before handoff. If `file://` browser restrictions break iframe media, local scripts, or same-origin player access, use a self-contained wrapper or make the handoff command start a local server and open the working URL; do not leave `index.html` in a broken or ambiguous state.

For a completed slideshow deck, the primary user-facing next step is presenter mode, not Studio. Run or provide:

```bash
npx hyperframes present <project-dir>
```

Studio/`preview` is useful for editing a composition, but it is not a clear final destination for a slideshow user. If you create a `package.json` for a slideshow project where the raw composition lives in `composition/`, make the default runnable script start presenter mode:

```json
{
  "scripts": {
    "dev": "npx hyperframes present ./composition",
    "studio": "npx hyperframes preview ./composition"
  }
}
```

At handoff, include the local presenter URL printed by the command and the minimal instruction: "Click Present, or press P, to open the audience tab." If the user will present over Google Meet or Zoom, also pass on the screen-share guidance from the Presenting section above (share the audience tab in Meet; a dragged-out audience window in Zoom). Keep the server running if the user asked you to start it.

---

## Validation

After authoring or editing a slideshow composition, run:

```bash
npx hyperframes lint
```

Then run runtime validation:

```bash
npx hyperframes check
```

Treat lint errors and validation `StaticGuard` contract messages as blockers even if a command exits successfully. Fix the file and rerun until lint reports `0 error(s)` and validation reports no runtime errors.

The slideshow lint rule checks:

- Every `slide.sceneId` resolves to an existing scene (by `data-composition-id`).
- Every `hotspot.target` references a defined `slideSequence` id.
- Fragment times fall within each slide's `[start, end]` range.
- No two main-line slides overlap in time.

Fix all violations before previewing. A composition that fails lint will not parse correctly in the player.
