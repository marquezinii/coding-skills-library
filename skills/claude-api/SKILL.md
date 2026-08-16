---
name: claude-api
description: |-
  Authoritative Claude API and Anthropic SDK reference for model IDs, pricing, parameters, streaming, tool use, MCP, agents, prompt caching, token counting, and model migration. Use whenever the request names Claude, Anthropic, Opus, Sonnet, Haiku, Anthropic packages, or Bedrock Anthropic model IDs, or asks provider-unstated questions about LLM agents, MCP, tool calling, RAG, caching, tokens, streaming, refusals, or model selection. Verify current facts instead of answering from memory. Do not use when the request or project clearly targets OpenAI, Gemini, Llama, Mistral, Cohere, Ollama, or another named provider.
license: Complete terms in LICENSE.txt
---

# Building LLM-Powered Applications with Claude

This skill helps you build LLM-powered applications with Claude. Choose the right surface based on your needs, detect the project language, then read the relevant language-specific documentation.

## Before You Start

Scan the target file (or, if no target file, the prompt and project) for non-Anthropic provider markers — `import openai`, `from openai`, `langchain_openai`, `OpenAI(`, `gpt-4`, `gpt-5`, file names like `agent-openai.py` or `*-generic.py`, or any explicit instruction to keep the code provider-neutral. If you find any, stop and tell the user that this skill produces Claude/Anthropic SDK code; ask whether they want to switch the file to Claude or want a non-Claude implementation. Do not edit a non-Anthropic file with Anthropic SDK calls.

## Output Requirement

When the user asks you to add, modify, or implement a Claude feature, your code must call Claude through one of:

1. **The official Anthropic SDK** for the project's language (`anthropic`, `@anthropic-ai/sdk`, `com.anthropic.*`, etc.). This is the default whenever a supported SDK exists for the project.
2. **Raw HTTP** (`curl`, `requests`, `fetch`, `httpx`, etc.) — only when the user explicitly asks for cURL/REST/raw HTTP, the project is a shell/cURL project, or the language has no official SDK.

Never mix the two — don't reach for `requests`/`fetch` in a Python or TypeScript project just because it feels lighter. Never fall back to OpenAI-compatible shims.

**Never guess SDK usage.** Function names, class names, namespaces, method signatures, and import paths must come from explicit documentation — either the `{lang}/` files in this skill or the official SDK repositories or documentation links listed in `shared/live-sources.md`. If the binding you need is not explicitly documented in the skill files, WebFetch the relevant SDK repo from `shared/live-sources.md` before writing code. Do not infer Ruby/Java/Go/PHP/C# APIs from cURL shapes or from another language's SDK.

**If WebFetch or repository access fails** (network restricted, timeouts, clone blocked): do not keep retrying — write code from the patterns and namespace/package tables in the `{lang}/` file, run the compiler or interpreter on it, and iterate on the error output. For statically-typed SDKs (C#, Java, Go) a compile-fix loop against local errors reaches working code faster than blocked network research.

## Defaults

Unless the user requests otherwise:

For the Claude model version, please use Claude Opus 5, which you can access via the exact model string `claude-opus-5`. Please default to using adaptive thinking (`thinking: {type: "adaptive"}`) for anything remotely complicated. And finally, please default to streaming for any request that may involve long input, long output, or high `max_tokens` — it prevents hitting request timeouts. Use the SDK's `.get_final_message()` / `.finalMessage()` helper to get the complete response if you don't need to handle individual stream events

## ⚠️ API Drift — Your Training Prior May Be Stale

Several common Claude API shapes changed in 2025–2026. If you recall a pattern from training, verify it against the `{lang}/` files in this skill before writing — the rows below are the most frequent drift points:

| Area | Stale prior | Current API |
|---|---|---|
| Extended thinking | `thinking: {type: "enabled", budget_tokens: N}` | On Claude 4.6+ models: `thinking: {type: "adaptive"}`. `budget_tokens` is deprecated on Opus 4.6 / Sonnet 4.6 and **rejected with a 400** on Fable 5 / Sonnet 5 / Opus 5 / 4.8 / 4.7. Pre-4.6 models still use `budget_tokens`. |
| Web search / web fetch tool type | `web_search_20250305`, `web_fetch_20250910` | `web_search_20260209`, `web_fetch_20260209` (dynamic filtering) on Opus 5/4.8/4.7/4.6, Sonnet 5, and Sonnet 4.6. Older models keep the basic variants; on Vertex AI only basic `web_search_20250305` is available (web fetch is not on Vertex) — see the Server Tools QR below. |
| PHP parameter names | snake_case wire names as named args (`max_tokens`) | Top-level named args are camelCase (`maxTokens`). Nested array keys vary by feature (e.g. `'taskBudget'`, `'skillID'`, `'mcp_server_name'`) — copy the exact key from the documented example; do not bulk-convert. |
| Managed Agents credentials | Keep secrets host-side via custom tools (the only option before vaults shipped) | Vault `environment_variable` credentials — stored by Anthropic, substituted at egress, never visible in the sandbox (`shared/managed-agents-tools.md` → Vaults). Host-side custom tools remain the fallback for self-hosted sandboxes. |

The `{lang}/` files in this skill are authoritative over recalled patterns.

---

## Subcommands

If the User Request at the bottom of this prompt is a bare subcommand string (no prose), search every **Subcommands** table in this document — including any in sections appended below — and follow the matching Action column directly. This lets users invoke specific flows via `/claude-api <subcommand>`. If no table in the document matches, treat the request as normal prose.

| Subcommand | Action |
|---|---|
| `migrate` | Migrate existing Claude API code to a newer model. **Read `shared/model-migration.md` immediately** and follow it in order: Step 0 (confirm scope — ask which files/directories before any edit), Step 1 (classify each file), then the per-target breaking-changes section. Do not summarize the guide — execute it. If the user did not name a target model, ask which model to migrate to in the same turn as the scope question. |

---

## Language Detection

Before reading code examples, determine which language the user is working in:

1. **Look at project files** to infer the language:

   - `*.py`, `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` → **Python** — read from `python/`
   - `*.ts`, `*.tsx`, `package.json`, `tsconfig.json` → **TypeScript** — read from `typescript/`
   - `*.js`, `*.jsx` (no `.ts` files present) → **TypeScript** — JS uses the same SDK, read from `typescript/`
   - `*.java`, `pom.xml`, `build.gradle` → **Java** — read from `java/`
   - `*.kt`, `*.kts`, `build.gradle.kts` → **Java** — Kotlin uses the Java SDK, read from `java/`
   - `*.scala`, `build.sbt` → **Java** — Scala uses the Java SDK, read from `java/`
   - `*.go`, `go.mod` → **Go** — read from `go/`
   - `*.rb`, `Gemfile` → **Ruby** — read from `ruby/`
   - `*.cs`, `*.csproj` → **C#** — read from `csharp/`
   - `*.php`, `composer.json` → **PHP** — read from `php/`

2. **If multiple languages detected** (e.g., both Python and TypeScript files):

   - Check which language the user's current file or question relates to
   - If still ambiguous, ask: "I detected both Python and TypeScript files. Which language are you using for the Claude API integration?"

3. **If language can't be inferred** (empty project, no source files, or unsupported language):

   - Use AskUserQuestion with options: Python, TypeScript, Java, Go, Ruby, cURL/raw HTTP, C#, PHP
   - If AskUserQuestion is unavailable, default to Python examples and note: "Showing Python examples. Let me know if you need a different language."

4. **If unsupported language detected** (Rust, Swift, C++, Elixir, etc.):

   - Suggest cURL/raw HTTP examples from `curl/` and note that community SDKs may exist
   - Offer to show Python or TypeScript examples as reference implementations

5. **If user needs cURL/raw HTTP examples**, read from `curl/`.

### Language-Specific Feature Support

Every SDK language above supports both the beta Tool Runner and Managed Agents (beta) — Python (`@beta_tool` decorator), TypeScript (`betaZodTool` + Zod), Java (annotated classes), Go (`BetaToolRunner` in the `toolrunner` pkg), Ruby (`BaseTool` + `tool_runner`), C# (`BetaToolRunner` + raw JSON schema), PHP (`BetaRunnableTool` + `toolRunner()`); code entry points are in the Tool Use Patterns quick reference below. cURL is raw HTTP (no SDK features) and supports Managed Agents.

> **Managed Agents code examples**: see the reading guide in the `## Managed Agents (Beta)` section below.

---

## Which Surface Should I Use?

> **Start simple.** Default to the simplest tier that meets your needs. Single API calls and workflows handle most use cases — only reach for agents when the task genuinely requires open-ended, model-driven exploration. "Simplest" means the least code you own: for a hosted, scheduled, or memory-backed agent, Managed Agents is usually the simplest option (no loop code, no state files, no scheduler), even though it's a bigger platform.

| Use Case                                        | Tier            | Recommended Surface       | Why                                                          |
| ----------------------------------------------- | --------------- | ------------------------- | ------------------------------------------------------------ |
| Classification, summarization, extraction, Q&A  | Single LLM call | **Claude API**            | One request, one response                                    |
| Batch processing or embeddings                  | Single LLM call | **Claude API**            | Specialized endpoints                                        |
| Multi-step pipelines with code-controlled logic | Workflow        | **Claude API + tool use** | You orchestrate the loop                                     |
| Custom agent with your own tools                | Agent           | **Claude API + tool use** | Maximum flexibility                                          |
| Server-managed stateful agent with workspace    | Agent           | **Managed Agents**        | Anthropic runs the loop and hosts the tool-execution sandbox |
| Persisted, versioned agent configs              | Agent           | **Managed Agents**        | Agents are stored objects; sessions pin to a version         |
| Long-running multi-turn agent with file mounts  | Agent           | **Managed Agents**        | Per-session containers, SSE event stream, Skills + MCP       |
| Agent that runs on a schedule (cron, "every night") | Agent       | **Managed Agents** — scheduled deployments | Deployments fire sessions autonomously; no client-side scheduler |

> **Note:** Managed Agents is the right choice when you want Anthropic to run the agent loop *and* host the container where tools execute — file ops, bash, code execution all run in the per-session workspace. If you want to host the compute yourself or run your own custom tool runtime, Claude API + tool use is the right choice — use the tool runner for the agentic loop — its per-turn hooks still give you approval gates, logging, error interception, and conditional execution (see `shared/tool-use-concepts.md`) — or the manual loop when you want to own the entire loop yourself.

> **Cloud-provider access.** **Claude Platform on AWS** is Anthropic-operated with same-day API parity — see `shared/claude-platform-on-aws.md` for client setup. For per-feature availability on **Claude Platform on AWS**, **Amazon Bedrock**, **Google Vertex AI**, and **Microsoft Foundry**, see `shared/platform-availability.md` — that table is the single source of truth in this skill; do not infer availability from anywhere else.

### Building an Agent: Four Approaches

Once you've decided you actually need an agent (open-ended, model-driven tool use), there are four distinct ways to build one. Two independent questions separate them: **who supplies the harness** (the agent loop + context management) and **who supplies the deployment** (the infra the agent runs on). The Tool Runner and the Claude Agent SDK both supply a *harness only* — you still host and deploy them yourself — which is why they're easy to conflate. Managed Agents (CMA) is the only option that supplies **both** the harness *and* managed deployment; the manual loop supplies neither.

| # | Approach | You write | Harness & deployment | Tools available | Use when |
|---|----------|-----------|----------------------|-----------------|----------|
| 1 | **Claude API — manual loop** | The `while stop_reason == "tool_use"` loop yourself | You build the harness; you host | Only tools you define | You want to own the *entire* loop — no beta dependency, or a control flow the Tool Runner's per-turn hooks don't fit |
| 2 | **Claude API — Tool Runner** (`client.beta.messages.tool_runner` + `@beta_tool` / `betaZodTool`) | Just the tool functions | SDK supplies the loop (**harness only**); you host | Only tools you define | A custom-tool agent without hand-writing the loop (most cases). Per-turn hooks still give you approval gates, error interception, result modification (e.g. `cache_control`), retries, streaming, and compaction |
| 3 | **Managed Agents** (REST, beta) | Agent config + your tool results | Anthropic supplies the harness **and** hosts a per-session sandbox (**harness + deployment**) | Anthropic-hosted sandbox (bash, files, code exec) + Skills/MCP + your tools | You want Anthropic to run the loop *and* host the per-session workspace; persisted/versioned configs; long-running sessions |
| 4 | **Claude Agent SDK** — *separate product* (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) | A prompt + options | SDK supplies the Claude Code harness + built-in tools (**harness only**); you host | Built-in Read/Write/Edit/Bash/Glob/Grep/WebSearch/WebFetch + MCP + subagents | You want a batteries-included coding/filesystem agent running on your own infra |

The harness/deployment split is the key mental model: options 1, 2, and 4 all **leave deployment to you**; only option 3 (CMA) adds managed deployment. Options 1–3 are what this skill generates; option 4 is a different library with its own docs — see the disambiguation below.

> **Tool Runner ≠ Claude Agent SDK.** These sound alike but are different packages:
> - **Tool Runner** is part of the regular Anthropic API SDK (`anthropic` / `@anthropic-ai/sdk`), reached via `client.beta.messages.tool_runner`. It automates the request → execute → loop cycle *for tools you define*. No built-in tools, no filesystem access, no sandbox — you supply every tool and host the compute. It is option 2 above, a thin helper over `POST /v1/messages`.
> - **Claude Agent SDK** (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) is Claude Code packaged as a library. It ships built-in tools (file read/write/edit, bash, grep, web search), the full agent loop, context management, hooks, subagents, permissions, and sessions. You call `query(prompt, options)` and it drives everything.
>
> Both are **harness-only — you host and deploy them.** The difference is scope of harness: the Tool Runner loops over tools *you* define (with per-turn hooks for approval, interception, result modification, and retries — but no built-in tools); the Agent SDK is the full Claude Code harness with built-in tools. Neither provides managed deployment — that's what **Managed Agents (CMA)** adds (Anthropic hosts the loop and a per-session sandbox).
>
> **This skill covers the Claude API and Managed Agents (options 1–3); it does not generate Claude Agent SDK code.** If the user actually wants the Claude Agent SDK, point them to its docs (`code.claude.com/docs/en/agent-sdk`) — don't substitute the API Tool Runner for it, or vice-versa.

### Should I Build an Agent?

Before choosing the agent tier, check all four criteria:

- **Complexity** — Is the task multi-step and hard to fully specify in advance? (e.g., "turn this design doc into a PR" vs. "extract the title from this PDF")
- **Value** — Does the outcome justify higher cost and latency?
- **Viability** — Is Claude capable at this task type?
- **Cost of error** — Can errors be caught and recovered from? (tests, review, rollback)

If the answer is "no" to any of these, stay at a simpler tier (single call or workflow).

---

## Architecture

Everything goes through `POST /v1/messages`. Tools and output constraints are features of this single endpoint — not separate APIs.

**User-defined tools** — You define tools (via decorators, Zod schemas, or raw JSON), and the SDK's tool runner handles calling the API, executing your functions, and looping until Claude is done. For full control, you can write the loop manually.

**Server-side tools** — Anthropic-hosted tools that run on Anthropic's infrastructure. Code execution is fully server-side (declare it in `tools`, Claude runs code automatically). Computer use can be server-hosted or self-hosted.

**Structured outputs** — Constrains the Messages API response format (`output_config.format`) and/or tool parameter validation (`strict: true`). The recommended approach is `client.messages.parse()` which validates responses against your schema automatically. Note: the old `output_format` parameter is deprecated; use `output_config: {format: {...}}` on `messages.create()`.

**Supporting endpoints** — Batches (`POST /v1/messages/batches`), Files (`POST /v1/files`), Token Counting (`POST /v1/messages/count_tokens` — see `shared/token-counting.md`), and Models (`GET /v1/models`, `GET /v1/models/{id}` — live capability/context-window discovery) feed into or support Messages API requests.

---

## Current Models (cached: 2026-06-24)

| Model             | Model ID            | Context        | Input $/1M | Output $/1M |
| ----------------- | ------------------- | -------------- | ---------- | ----------- |
| Claude Fable 5    | `claude-fable-5`      | 1M             | $10.00     | $50.00      |
| Claude Mythos 5 (Project Glasswing only) | `claude-mythos-5` | 1M | $10.00     | $50.00      |
| Claude Opus 5     | `claude-opus-5`       | 1M             | $5.00      | $25.00      |
| Claude Opus 4.8 | `claude-opus-4-8`  | 1M             | $5.00      | $25.00      |
| Claude Opus 4.7   | `claude-opus-4-7`   | 1M             | $5.00      | $25.00      |
| Claude Opus 4.6   | `claude-opus-4-6`   | 1M             | $5.00      | $25.00      |
| Claude Sonnet 5   | `claude-sonnet-5`   | 1M             | $3.00 ($2.00 intro through 2026-08-31) | $15.00 ($10.00 intro) |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | 1M             | $3.00      | $15.00      |
| Claude Haiku 4.5  | `claude-haiku-4-5`  | 200K           | $1.00      | $5.00       |

**Partner pricing:** The prices above are Anthropic first-party API rates — they also apply to Claude on Microsoft Foundry, which is billed through the Microsoft Marketplace at standard API rates. Claude on Amazon Bedrock and Vertex AI is partner-operated with separate pricing — see [Bedrock](https://aws.amazon.com/bedrock/pricing/) or [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/pricing#claude-models). For WebFetch, use the Pricing row in `shared/live-sources.md`.

**ALWAYS use `claude-opus-5` unless the user explicitly names a different model.** This is non-negotiable. Do not use `claude-sonnet-5`, `claude-sonnet-4-6`, or any other model unless the user literally says "use sonnet" or "use haiku". Never downgrade for cost — that's the user's decision, not yours. Use `claude-fable-5` only when the user explicitly asks for Claude Fable 5, "fable", or Anthropic's most capable model — it has different API behavior than the Opus family (see below) and pricing that exceeds Opus-tier. **Use only the exact model ID strings from the table — they are complete as-is; never append date suffixes** (`claude-sonnet-4-6`, never `claude-sonnet-4-6-20251114` or any other date-suffixed variant you might recall from training data). If the user requests an older model not in the table (e.g., "opus 4.5", "sonnet 3.7"), read `shared/models.md` for the exact ID — do not construct one yourself.

### Claude Fable 5 (`claude-fable-5`) — most capable widely released model

Claude Fable 5 is Anthropic's most capable widely released model, for the most demanding reasoning and long-horizon agentic work; everything below also applies to **Claude Mythos 5** (`claude-mythos-5`, Project Glasswing — same capabilities, pricing, and API surface; successor to the invitation-only `claude-mythos-preview`). 1M context window (the maximum is also the default), 128K max output. Key API differences from Opus-tier — see `shared/model-migration.md` → Migrating to Claude Fable 5 for details:

- **Thinking is always on** — omit the `thinking` parameter entirely (or send `{type: "adaptive"}`). Any other explicit configuration is rejected: `{type: "disabled"}` and `{type: "enabled", budget_tokens: N}` both return a 400. Control depth with `output_config.effort` (supports `low` through `xhigh` and `max`).
- **The raw chain of thought is never returned** — responses carry regular `thinking` blocks (not `redacted_thinking`): `display: "summarized"` returns a readable summary, `"omitted"` (the default) leaves the `thinking` field as an empty string. Replay rules: pass thinking blocks back unchanged on the same model; other models drop them silently (unbilled — nothing to strip); details in `shared/model-migration.md`.
- **Tokenizer** — same tokenizer as Opus 4.8 (introduced with Opus 4.7). Token counts are roughly unchanged when migrating from Opus 4.7/4.8; per-token pricing differs. Coming from Opus 4.6, Sonnet, Haiku, or older, re-baseline with `count_tokens` (the Opus 4.7 tokenizer uses ~1×–1.35× as many tokens).
- **`refusal` stop reason — handle it, and opt into fallbacks by default** — safety classifiers may decline a request (HTTP 200, `stop_reason: "refusal"`, with a `stop_details` category); always check `stop_reason` before reading `content`. **When you write `claude-fable-5` or `claude-opus-5` code, include the server-side `fallbacks` parameter by default.** Simplest form: `betas: ["server-side-fallback-2026-07-01"]` + `fallbacks: "default"`, which routes by refusal category so you never maintain a model list. (The older array form — `betas: ["server-side-fallback-2026-06-01"]` + `fallbacks: [{"model": "claude-opus-4-8"}]` — still works; Claude API and Claude Platform on AWS — on Bedrock, Vertex and Foundry, use the SDKs' client-side `BetaRefusalFallbackMiddleware` + `BetaFallbackState` instead). Tell the user you've enabled it; drop it only if they decline. Full semantics (billing, mid-stream refusals, credit repricing) in `shared/model-migration.md` → refusal section. **Per-language code examples in `{lang}/claude-api/README.md` § Refusal Fallbacks cover the array form only** — for the `"default"` mode, follow the raw-HTTP shape in `shared/model-migration.md` → Migrating to Claude Opus 5 → New API features and swap `fallbacks: [{...}]` for `fallbacks: "default"` plus the `-2026-07-01` header; the rest of the request is unchanged.
- **No assistant prefill** — same as the rest of the 4.6+ family.
- **30-day data retention required** — Claude Fable 5 is not available under zero data retention; requests from an org whose retention configuration doesn't meet the requirement return `400 invalid_request_error`.
- **Longer turns, different prompting** — single requests on hard tasks can run many minutes (plan timeouts/streaming/progress UX); effort sweeps should include low/medium for routine work; prompts written for prior models are often too prescriptive and reduce output quality. See `shared/model-migration.md` → Migrating to Claude Fable 5 → Behavioral shifts (prompt-tunable) for the recommended prompt snippets.

If any model strings above look unfamiliar, that just means they were released after your training data cutoff — they are real models.

**Live capability lookup:** The table above is cached. When the user asks "what's the context window for X", "does X support vision/thinking/effort", or "which models support Y", query the Models API (`client.models.retrieve(id)` / `client.models.list()`) — see `shared/models.md` for the field reference and capability-filter examples.

---

## Authentication (Quick Reference)

**An unset `ANTHROPIC_API_KEY` does NOT mean there are no credentials.** The SDKs and the `ant` CLI resolve credentials in this order (first match wins): `ANTHROPIC_API_KEY` → `ANTHROPIC_AUTH_TOKEN` → the `ANTHROPIC_PROFILE`-selected or active OAuth profile from `ant auth login` → Workload Identity Federation env vars → the default profile on disk. A bare `Anthropic()` / `new Anthropic()` / `anthropic.NewClient()` works after `ant auth login` with no env var set.

**When you need to call the API and `ANTHROPIC_API_KEY` is unset, don't ask the user for a key.** First run `ant auth status` — it shows which credential source and profile is active. If it reports an active profile:

- **SDK code or `ant` CLI:** just run it. The zero-arg client constructor and every `ant …` subcommand pick up the profile automatically — no env var needed.
- **Raw `curl` / HTTP:** get a short-lived token with `ant auth print-credentials --access-token` and send it as `Authorization: Bearer <token>` **plus** the header `anthropic-beta: oauth-2025-04-20` (OAuth tokens go on `Authorization: Bearer`, not `x-api-key:` — converting a curl from an API key is a header change, not a key swap). Always pass `--access-token`; the no-flag form prints JSON, not a bare token.

Only ask the user for a key if `ant auth status` reports no active credential source (or `ant` itself isn't installed). Suggest `ant auth login` as the first option — it stores a profile under `~/.config/anthropic/` that the SDKs read automatically — and an exported `ANTHROPIC_API_KEY` as the alternative.

Full auth details (named profiles, scopes, the API-key-shadows-profile trap, refresh-token expiry): `shared/anthropic-cli.md`.

---

## Thinking & Effort (Quick Reference)

Use adaptive thinking (`thinking: {type: "adaptive"}`) on every current model — Claude dynamically decides when and how much to think. Per-model rules:

| Model | Thinking config | Omitting `thinking` | `budget_tokens` | Sampling (`temperature`/`top_p`/`top_k`) | Effort levels |
|---|---|---|---|---|---|
| Fable 5 | `{type: "adaptive"}` or omit; explicit `{type: "disabled"}` returns 400 — omit the param instead | Runs adaptive (thinking is always on) | Removed — `{type: "enabled", budget_tokens: N}` returns 400 | Removed — 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Claude Opus 5 | `{type: "adaptive"}` or omit; `{type: "disabled"}` accepted **only at effort `high` or below** — 400 at `xhigh`/`max`, and see the disabled-thinking pitfall below | Runs **adaptive** (thinking is on by default — unlike Opus 4.8/4.7) | Removed — 400 | Removed — 400 | `low`–`max` (all five) |
| Opus 4.8 / 4.7 | `{type: "adaptive"}` is the only on-mode; `{type: "disabled"}` accepted | Runs **without** thinking — set `{type: "adaptive"}` explicitly | Removed — 400 | Removed — 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Sonnet 5 | `{type: "adaptive"}` is the only on-mode; `{type: "disabled"}` accepted | Runs adaptive | Removed — 400 | Removed — 400 | `low`/`medium`/`high`/`xhigh`/`max` |
| Opus 4.6 / Sonnet 4.6 | `{type: "adaptive"}` (recommended; auto-enables interleaved thinking, no beta header) | Set `{type: "adaptive"}` explicitly | Deprecated — do not use in new code; transitional escape hatch only (see below) | Allowed | `low`/`medium`/`high`/`max` (`xhigh` arrived with Opus 4.7) |
| Older (Sonnet 4.5, Haiku 4.5, …) — only if explicitly requested | `{type: "enabled", budget_tokens: N}` | No thinking | Required for thinking; must be less than `max_tokens`, minimum 1024 — errors otherwise | Allowed | `effort` works on Opus 4.5 (`low`/`medium`/`high` only — no `xhigh`/`max`); errors on Sonnet 4.5 / Haiku 4.5 |

Opus 4.8 keeps the same request surface as 4.7 (no new breaking changes) — see `shared/model-migration.md` → Migrating to Opus 4.8 for the behavioral re-tuning, and → Migrating to Opus 4.7 for the full breaking-change list when coming from 4.6 or earlier. With `thinking` disabled, Opus 4.8 may write longer reasoning into the visible response — leave adaptive thinking on, or add a final-answer-only instruction (see the migration guide).

- **Effort (GA, no beta header):** `output_config: {effort: "low"|"medium"|"high"|"xhigh"|"max"}` — inside `output_config`, not top-level; default `high` (equivalent to omitting it). Controls thinking depth and overall token spend; combine with adaptive thinking for the best cost-quality tradeoffs. `xhigh` (added on Opus 4.7, between `high` and `max`) is the best setting for most coding and agentic use cases on Fable 5 / Opus 4.7/4.8 / Sonnet 5, and the default in Claude Code; effort matters more on those models than on any prior model in their tier — re-tune it when migrating, and run long-horizon/agentic tasks at `high`/`xhigh` with the full task spec given up front. Use a minimum of `high` for intelligence-sensitive work, `max` when correctness matters more than cost, and `low` for subagents or simple tasks — lower effort means fewer and more-consolidated tool calls, less preamble, and terser confirmations (`high` is often the sweet spot balancing quality and token efficiency).
- **Thinking display — `"omitted"` by default on Fable 5 / Mythos 5 / Opus 5 / 4.8 / 4.7 / Sonnet 5:** `display: "summarized"` returns a readable summary of the reasoning; `"omitted"` (the default on all six — a silent change from Opus 4.6 and Sonnet 4.6, where it was `"summarized"`) streams `thinking` blocks with empty text. `display` controls visibility only — thinking happens and is billed the same under every setting; the raw chain of thought is never exposed on any model. If you stream reasoning to users, the default looks like a long pause before output — set `thinking: {type: "adaptive", display: "summarized"}` explicitly. (Independent of display, echo thinking blocks back unchanged when continuing on the same model; other models silently ignore them — see the migration guide.)
- **When the user asks for "extended thinking", a "thinking budget", or `budget_tokens`:** always use Fable 5, Opus 5, 4.8, 4.7, or 4.6 with `thinking: {type: "adaptive"}` — the fixed thinking-token-budget concept is deprecated and adaptive thinking replaces it. Do NOT use `budget_tokens` for new 4.6/4.7/4.8 code and do NOT switch to an older model just because the user mentions it. *Gradual-migration carve-out:* `budget_tokens` is still functional on Opus 4.6 and Sonnet 4.6 only, as a transitional escape hatch for existing code that needs a hard token ceiling before you've tuned `effort` — see `shared/model-migration.md` → Transitional escape hatch. It is fully removed on Fable 5, Opus 5/4.7/4.8, and Sonnet 5.

---

## Compaction (Quick Reference)

**Beta, Fable 5, Opus 5, Opus 4.8, Opus 4.7, Opus 4.6, Sonnet 5, and Sonnet 4.6.** For long-running conversations that may exceed the 1M context window, enable server-side compaction. The API automatically summarizes earlier context when it approaches the trigger threshold (default: 150K tokens). Requires beta header `compact-2026-01-12`.

**Critical:** Append `response.content` (not just the text) back to your messages on every turn. Compaction blocks in the response must be preserved — the API uses them to replace the compacted history on the next request. Extracting only the text string and appending that will silently lose the compaction state.

See `{lang}/claude-api/README.md` (Compaction section) for code examples. Full docs via WebFetch in `shared/live-sources.md`.

---

## Prompt Caching (Quick Reference)

**Prefix match.** Any byte change anywhere in the prefix invalidates everything after it. Render order is `tools` → `system` → `messages`. Keep stable content first (frozen system prompt, deterministic tool list), put volatile content (timestamps, per-request IDs, varying questions) after the last `cache_control` breakpoint.

**Mid-conversation operator instructions** (Claude Opus 5, Claude Opus 4.8, Claude Fable 5, Claude Mythos 5; not Claude Sonnet 5; no beta header): append `{"role": "system", ...}` to `messages[]` instead of editing top-level `system`. Preserves the cached history prefix and is the prompt-injection-safe operator channel. See `shared/prompt-caching.md` § Mid-conversation system messages.

**Top-level auto-caching** (`cache_control: {type: "ephemeral"}` on `messages.create()`) is the simplest option when you don't need fine-grained placement. Max 4 breakpoints per request. Minimum cacheable prefix is ~1024 tokens — shorter prefixes silently won't cache.

**Verify with `usage.cache_read_input_tokens`** — if it's zero across repeated requests, a silent invalidator is at work (`datetime.now()` in system prompt, unsorted JSON, varying tool set).

For placement patterns, architectural guidance, and the silent-invalidator audit checklist: read `shared/prompt-caching.md`. Language-specific syntax: `{lang}/claude-api/README.md` (Prompt Caching section).

---

## Fast Mode (Quick Reference)

**Research preview, Claude Opus 5 / Opus 4.8 only** — Claude API and Managed Agents, not Bedrock / Google Cloud / Foundry. Opus 4.7 fast mode has been removed: `speed: "fast"` on 4.7 returns an error. Fast mode on Claude Opus 5 is priced at $10 / $50 per MTok. Fast mode runs the same model at up to 2.5x higher output tokens per second, at premium pricing. Three things are required on every request: use the **beta** messages endpoint (`client.beta.messages.…`), pass the beta flag `fast-mode-2026-02-01`, and set `speed: "fast"` as a top-level request parameter (not a header, not in `extra_body`).

```python
client.beta.messages.create(
    model="claude-opus-5", max_tokens=4096,
    speed="fast", betas=["fast-mode-2026-02-01"],
    messages=[...],
)
```

| Language | Beta flag | Speed parameter |
|---|---|---|
| Python | `betas=["fast-mode-2026-02-01"]` | `speed="fast"` |
| TypeScript / Ruby | `betas: ["fast-mode-2026-02-01"]` | `speed: "fast"` |
| Go | `[]anthropic.AnthropicBeta{anthropic.AnthropicBetaFastMode2026_02_01}` | `Speed: anthropic.BetaMessageNewParamsSpeedFast` |
| Java | `.addBeta(AnthropicBeta.FAST_MODE_2026_02_01)` | `.speed(MessageCreateParams.Speed.FAST)` |
| C# | `Betas = ["fast-mode-2026-02-01"]` | `Speed = Speed.Fast` (`Anthropic.Models.Beta.Messages`) |
| PHP | `betas: ['fast-mode-2026-02-01']` | `speed: 'fast'` |
| cURL | `anthropic-beta: fast-mode-2026-02-01` header | `"speed": "fast"` in body |

`response.usage.speed` reports which speed was used. Fast mode has its own rate limit separate from standard Opus; on 429, either retry after the `retry-after` delay or drop `speed` and fall back to standard (note: switching speed invalidates prompt cache). Not available with Batch API, Priority Tier, Claude Platform on AWS, or third-party platforms.

**Priority Tier does not cover Claude Opus 5.** It is supported on every other current model, including Claude Fable 5 and Opus 4.8, but Claude Opus 5, Claude Sonnet 5, Claude Mythos 5, and Mythos Preview are excluded — a Priority Tier request naming one of them fails validation.

---

## Task Budgets (Quick Reference)

**Beta, Claude Opus 5 / Fable 5 / Sonnet 5 / Opus 4.8 / 4.7.** A task budget gives Claude a token ceiling for an agentic loop so it paces itself and finishes gracefully instead of being cut off — distinct from `max_tokens`, which is an enforced per-response ceiling the model is not aware of. Minimum `total`: 20,000. Set `task_budget` inside `output_config` on `client.beta.messages.stream(...)` with beta flag `task-budgets-2026-03-13` — use streaming so the large `max_tokens` doesn't hit HTTP timeouts (full details: `shared/model-migration.md` → Task Budgets):

```python
with client.beta.messages.stream(
    model="claude-opus-5", max_tokens=128000,
    output_config={"effort": "high", "task_budget": {"type": "tokens", "total": 64000}},
    betas=["task-budgets-2026-03-13"],
    messages=[...], tools=[...],
) as stream:
    response = stream.get_final_message()
```

`task_budget` fields: `type` (always `"tokens"`), `total`, and optional `remaining` (defaults to `total`). The server injects a countdown marker Claude sees during generation; the budget counts what Claude generates and the tool results it reads this turn — **not** the full history you resend each request. Not the same thing as **Managed Agents session budgets** — those are hard, dollar-denominated, platform-enforced caps on one CMA session (`shared/managed-agents-core.md` § Session budgets); a task budget is advisory and token-denominated.

**Observing spend:** accumulate `response.usage.output_tokens` (plus the token count of the tool-result blocks you append) across loop iterations if you want to display progress. Leave `remaining` unset in the normal loop — the server tracks the countdown itself, and passing a client-computed `remaining` while also resending full history under-reports the budget. **Only pass `remaining`** when you compact or rewrite history between requests and the server can no longer derive prior spend.

---

## Provider Clients (Quick Reference)

When targeting Claude on a third-party platform, use that platform's dedicated client class — not the first-party `Anthropic()` client with a `base_url` override. After construction the client exposes the same `messages.create` / `.stream` surface as the first-party SDK.

### Amazon Bedrock

Use the **Mantle** client (Messages-API Bedrock endpoint). Bedrock model IDs take an `anthropic.` prefix (e.g. `"anthropic.claude-opus-5"`). Region is required.

| Language | Client |
|---|---|
| Python | `from anthropic import AnthropicBedrockMantle` → `AnthropicBedrockMantle(aws_region="…")` |
| TypeScript | `import { AnthropicBedrockMantle } from "@anthropic-ai/bedrock-sdk"` → `new AnthropicBedrockMantle({ awsRegion: "…" })` |
| Go | `bedrock.NewMantleClient(ctx, bedrock.MantleClientConfig{ AWSRegion: "…" })` |
| Java | `AnthropicOkHttpClient.builder().backend(BedrockMantleBackend.fromEnv()).build()` (from `com.anthropic.bedrock.backends`) |
| C# | `new AnthropicBedrockMantleClient(new() { AwsRegion = "…" })` (package `Anthropic.Bedrock`) |
| PHP | `use Anthropic\Bedrock\MantleClient;` → `new MantleClient(awsRegion: '…')` |
| Ruby | `Anthropic::BedrockMantleClient.new(aws_region: "…")` |

`AnthropicBedrock` / `BedrockClient` / `BedrockBackend` (without `Mantle`) are the legacy `bedrock-runtime` InvokeModel path — prefer the Mantle client for new code.

### Microsoft Foundry

| Language | Client |
|---|---|
| Python | `from anthropic import AnthropicFoundry` → `AnthropicFoundry(api_key=…, resource="…")` |
| TypeScript | `import AnthropicFoundry from "@anthropic-ai/foundry-sdk"` → `new AnthropicFoundry({ … })` |
| Java | `AnthropicOkHttpClient.builder().backend(FoundryBackend.fromEnv()).build()` (from `com.anthropic.foundry.backends`) |
| C# | `new AnthropicFoundryClient(new AnthropicFoundryApiKeyCredentials(…))` (package `Anthropic.Foundry`) |
| PHP | `Foundry\Client::withCredentials(…)` |

The Go and Ruby SDKs do not currently support Foundry. For Ruby, use the standard `Anthropic::Client.new(base_url: "<foundry endpoint>")` as a fallback (Entra ID auth is not built in). For Claude Platform on AWS, see `shared/claude-platform-on-aws.md`.

### Google Cloud Vertex AI

Two required constructor args: GCP `project_id` and `region`. Vertex model IDs take **no prefix** — current-generation models (Opus 4.8/4.7/4.6, Sonnet 5, Sonnet 4.6) use the bare first-party ID (e.g. `"claude-opus-5"`); dated-snapshot models use an `@` version separator (e.g. `claude-opus-4-5@20251101`, **not** `claude-opus-4-5-20251101`). Auth is GCP ADC (`gcloud auth application-default login`); no Anthropic API key. `region` can be `"global"` (recommended), a multi-region (`"us"`/`"eu"`), or a specific region. After construction, use the same `messages.create` / `.stream` surface.

| Language | Client |
|---|---|
| Python | `from anthropic import AnthropicVertex` → `AnthropicVertex(project_id="…", region="…")` (install `"anthropic[vertex]"`) |
| TypeScript | `import { AnthropicVertex } from "@anthropic-ai/vertex-sdk"` → `new AnthropicVertex({ projectId, region })` |
| Go | `import "github.com/anthropics/anthropic-sdk-go/vertex"` → `anthropic.NewClient(vertex.WithGoogleAuth(ctx, region, projectID))` |
| Java | `AnthropicOkHttpClient.builder().backend(VertexBackend.builder().region("…").project("…").build()).build()` (from `com.anthropic.vertex.backends`) |
| C# | `new AnthropicClient { Backend = new VertexBackend(projectId, region) }` (package `Anthropic.Vertex`) |
| PHP | `use Anthropic\Vertex;` → `Vertex\Client::fromEnvironment(location: '…', projectId: '…')` — note `location`, not `region` |
| Ruby | `Anthropic::VertexClient.new(region: "…", project_id: "…")` |

---


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Context Editing (Quick Reference)](references/extended-guidance.md#context-editing-quick-reference)
- [Mid-Conversation System Messages (Quick Reference)](references/extended-guidance.md#mid-conversation-system-messages-quick-reference)
- [Managed Agents (Beta)](references/extended-guidance.md#managed-agents-beta)
- [Server Tools (Quick Reference)](references/extended-guidance.md#server-tools-quick-reference)
- [Document & File Input (Quick Reference)](references/extended-guidance.md#document-file-input-quick-reference)
- [Tool Use Patterns (Quick Reference)](references/extended-guidance.md#tool-use-patterns-quick-reference)
- [Other API Surfaces (Quick Reference)](references/extended-guidance.md#other-api-surfaces-quick-reference)
- [Workload Identity Federation (Quick Reference)](references/extended-guidance.md#workload-identity-federation-quick-reference)
- [Reading Guide](references/extended-guidance.md#reading-guide)
- [When to Use WebFetch](references/extended-guidance.md#when-to-use-webfetch)
- [Common Pitfalls](references/extended-guidance.md#common-pitfalls)

