---
name: sentry-node-sdk
description: Full Sentry SDK setup for Node.js, Bun, and Deno. Use when asked to "add Sentry to Node.js", "add Sentry to Bun", "add Sentry to Deno", "install @sentry/node", "@sentry/bun", or "@sentry/deno", or configure error monitoring, tracing, logging, profiling, metrics, crons, or AI monitoring for server-side JavaScript/TypeScript runtimes.
license: Apache-2.0
---

> Sentry SDK setup › Node.js / Bun / Deno

# Sentry Node.js / Bun / Deno SDK

Opinionated wizard that scans your project and guides you through complete Sentry setup for server-side JavaScript and TypeScript runtimes: Node.js, Bun, and Deno.

## Invoke This Skill When

- User asks to "add Sentry to Node.js", "Bun", or "Deno"
- User wants to install or configure `@sentry/node`, `@sentry/bun`, or `@sentry/deno`
- User wants error monitoring, tracing, logging, profiling, crons, metrics, or AI monitoring for a backend JS/TS app
- User asks about `instrument.js`, `--import ./instrument.mjs`, `bun --preload`, or `npm:@sentry/deno`
- User wants to monitor Express, Fastify, Koa, Hapi, Connect, Bun.serve(), or Deno.serve()

> **NestJS?** Follow the [official Sentry NestJS guide](https://docs.sentry.io/platforms/javascript/guides/nestjs/) instead — it uses `@sentry/nestjs` with NestJS-native decorators and filters.
> **Next.js?** Use [`sentry-nextjs-sdk`](../sentry-nextjs-sdk/SKILL.md) instead — it handles the three-runtime architecture (browser, server, edge).

> **Note:** SDK versions below reflect current Sentry docs at time of writing (`@sentry/node` ≥10.42.0, `@sentry/bun` ≥10.42.0, `@sentry/deno` ≥10.42.0).
> Always verify against [docs.sentry.io/platforms/javascript/guides/node/](https://docs.sentry.io/platforms/javascript/guides/node/) before implementing.

---

## Phase 1: Detect

Run these commands to identify the runtime, framework, and existing Sentry setup:

```bash
# Detect runtime
bun --version 2>/dev/null && echo "Bun detected"
deno --version 2>/dev/null && echo "Deno detected"
node --version 2>/dev/null && echo "Node.js detected"

# Detect existing Sentry packages
cat package.json 2>/dev/null | grep -E '"@sentry/'
cat deno.json deno.jsonc 2>/dev/null | grep -i sentry

# Detect Node.js framework
cat package.json 2>/dev/null | grep -E '"express"|"fastify"|"@hapi/hapi"|"koa"|"@nestjs/core"|"connect"'

# Detect Bun-specific frameworks
cat package.json 2>/dev/null | grep -E '"elysia"|"hono"'

# Detect Deno frameworks (deno.json imports)
cat deno.json deno.jsonc 2>/dev/null | grep -E '"oak"|"hono"|"fresh"'

# Detect module system (Node.js)
cat package.json 2>/dev/null | grep '"type"'
ls *.mjs *.cjs 2>/dev/null | head -5

# Detect existing instrument file
ls instrument.js instrument.mjs instrument.ts instrument.cjs 2>/dev/null

# Detect logging libraries
cat package.json 2>/dev/null | grep -E '"winston"|"pino"|"bunyan"'

# Detect cron / scheduling
cat package.json 2>/dev/null | grep -E '"node-cron"|"cron"|"agenda"|"bull"|"bullmq"'

# Detect AI / LLM usage
cat package.json 2>/dev/null | grep -E '"openai"|"@anthropic-ai"|"@langchain"|"@vercel/ai"|"@google/generative-ai"'

# Detect OpenTelemetry tracing
cat package.json 2>/dev/null | grep -E '"@opentelemetry/sdk-node"|"@opentelemetry/sdk-trace-node"|"@opentelemetry/sdk-trace-base"'
grep -rn "NodeTracerProvider\|trace\.getTracer\|startActiveSpan" \
  --include="*.ts" --include="*.js" --include="*.mjs" 2>/dev/null | head -5

# Check for companion frontend
ls frontend/ web/ client/ ui/ 2>/dev/null
cat package.json 2>/dev/null | grep -E '"react"|"vue"|"svelte"|"next"'
```

**What to determine:**

| Question | Impact |
|----------|--------|
| Which runtime? (Node.js / Bun / Deno) | Determines package, init pattern, and preload flag |
| Node.js: ESM or CJS? | ESM requires `--import ./instrument.mjs`; CJS uses `require("./instrument")` |
| Framework detected? | Determines which error handler to register |
| `@sentry/*` already installed? | Skip install, go straight to feature config |
| `instrument.js` / `instrument.mjs` already exists? | Merge into it rather than overwrite |
| Logging library detected? | Recommend Sentry Logs |
| Cron / job scheduler detected? | Recommend Crons monitoring |
| AI library detected? | Recommend AI Monitoring |
| OpenTelemetry tracing detected? | Use OTLP path instead of native tracing |
| Companion frontend found? | Trigger Phase 4 cross-link |

---

## Phase 2: Recommend

Present a concrete recommendation based on what you found. Don't ask open-ended questions — lead with a proposal:

**Route from OTel detection:**
- **OTel tracing detected** (`@opentelemetry/sdk-node` or `@opentelemetry/sdk-trace-node` in `package.json`, or `NodeTracerProvider` in source) → use OTLP path: `otlpIntegration()` via `@sentry/node-core/light`; do **not** set `tracesSampleRate`; Sentry links errors to OTel traces automatically

**Recommended (core coverage):**
- ✅ **Error Monitoring** — always; captures unhandled exceptions, promise rejections, and framework errors
- ✅ **Tracing** — automatic HTTP, DB, and queue instrumentation via OpenTelemetry

**Optional (enhanced observability):**
- ⚡ **Logging** — structured logs via `Sentry.logger.*`; recommend when `winston`/`pino`/`bunyan` or log search is needed
- ⚡ **Profiling** — continuous CPU profiling (Node.js only; not available on Bun or Deno); **not available with OTLP path**
- ⚡ **AI Monitoring** — OpenAI, Anthropic, LangChain, Vercel AI SDK; recommend when AI/LLM calls detected
- ⚡ **Crons** — detect missed or failed scheduled jobs; recommend when node-cron, Bull, or Agenda is detected
- ⚡ **Metrics** — custom counters, gauges, distributions; recommend when custom KPIs needed
- ⚡ **Runtime Metrics** — automatic collection of memory, CPU, and event loop metrics; `nodeRuntimeMetricsIntegration()` (Node.js) / `bunRuntimeMetricsIntegration()` (Bun)

**Recommendation logic:**

| Feature | Recommend when... |
|---------|------------------|
| Error Monitoring | **Always** — non-negotiable baseline |
| OTLP Integration | OTel tracing detected — **replaces** native Tracing |
| Tracing | **Always for server apps** — HTTP spans + DB spans are high-value; **skip if OTel tracing detected** |
| Logging | App uses winston, pino, bunyan, or needs log-to-trace correlation |
| Profiling | **Node.js only** — performance-critical service; native addon compatible; **skip if OTel tracing detected** (requires `tracesSampleRate`, incompatible with OTLP) |
| AI Monitoring | App calls OpenAI, Anthropic, LangChain, Vercel AI, or Google GenAI |
| Crons | App uses node-cron, Bull, BullMQ, Agenda, or any scheduled task pattern |
| Metrics | App needs custom counters, gauges, or histograms |
| Runtime Metrics | Any Node.js or Bun service wanting automatic memory/CPU/event-loop visibility |

**OTel tracing detected:** *"I see OpenTelemetry tracing in the project. I recommend Sentry's OTLP integration for tracing (via your existing OTel setup) + Error Monitoring + Sentry Logging [+ Metrics/Crons/AI Monitoring if applicable]. Shall I proceed?"*

**No OTel:** *"I recommend setting up Error Monitoring + Tracing. Want me to also add Logging or Profiling?"*

---


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Phase 3: Guide](references/extended-guidance.md#phase-3-guide)
- [Configuration Reference](references/extended-guidance.md#configuration-reference)
- [Verification](references/extended-guidance.md#verification)
- [Phase 4: Cross-Link](references/extended-guidance.md#phase-4-cross-link)
- [Troubleshooting](references/extended-guidance.md#troubleshooting)

