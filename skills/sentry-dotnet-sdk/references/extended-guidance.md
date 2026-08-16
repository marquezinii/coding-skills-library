<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Configuration Reference

### Core `SentryOptions`

| Option | Type | Default | Env Var | Notes |
|--------|------|---------|---------|-------|
| `Dsn` | `string` | — | `SENTRY_DSN` | Required. SDK disabled if unset. |
| `Debug` | `bool` | `false` | — | SDK diagnostic output. Disable in production. |
| `DiagnosticLevel` | `SentryLevel` | `Debug` | — | `Debug`, `Info`, `Warning`, `Error`, `Fatal` |
| `Release` | `string` | auto | `SENTRY_RELEASE` | Auto-detected from assembly version + git SHA |
| `Environment` | `string` | `"production"` | `SENTRY_ENVIRONMENT` | `"debug"` when debugger attached |
| `Dist` | `string` | — | — | Build variant. Max 64 chars. |
| `SampleRate` | `float` | `1.0` | — | Error event sampling rate 0.0–1.0 |
| `TracesSampleRate` | `double` | `0.0` | — | Transaction sampling. Must be `> 0` to enable. |
| `TracesSampler` | `Func<SamplingContext, double>` | — | — | Per-transaction dynamic sampler; overrides `TracesSampleRate` |
| `ProfilesSampleRate` | `double` | `0.0` | — | Fraction of traced transactions to profile. Requires `Sentry.Profiling`. |
| `SendDefaultPii` | `bool` | `false` | — | Include user IP, name, email |
| `AttachStacktrace` | `bool` | `true` | — | Attach stack trace to all messages |
| `MaxBreadcrumbs` | `int` | `100` | — | Max breadcrumbs stored per event |
| `IsGlobalModeEnabled` | `bool` | `false`* | — | *Auto-`true` for MAUI, Blazor WASM. **Must** be `true` for WPF, WinForms, Console. |
| `AutoSessionTracking` | `bool` | `false`* | — | *Auto-`true` for MAUI. Enable for Release Health. |
| `CaptureFailedRequests` | `bool` | `true` | — | Auto-capture HTTP client errors |
| `CacheDirectoryPath` | `string` | — | — | Offline event caching directory |
| `ShutdownTimeout` | `TimeSpan` | — | — | Max wait for event flush on shutdown |
| `HttpProxy` | `string` | — | — | Proxy URL for Sentry requests |
| `EnableBackpressureHandling` | `bool` | `true` | — | Auto-reduce sample rates on delivery failures |
| `TraceIgnoreStatusCodes` | `IList<HttpStatusCodeRange>` | `[]` | — | Drop transactions whose HTTP response status matches any range; e.g., `[404]` or `[(500, 599)]` |
| `StrictTraceContinuation` | `bool` | `false` | — | When `true`, starts a new trace if exactly one side (SDK or incoming `sentry-org_id` baggage) has an org ID. A full mismatch (both present but different) always starts a new trace regardless of this setting. (requires ≥6.6.0) |
| `OrgId` | `string` | auto | — | Organization ID for trace validation; auto-parsed from DSN subdomain (e.g., `o123.ingest.sentry.io` → `"123"`). Recommended to set explicitly for self-hosted Sentry, local Relay, or custom domains (requires ≥6.6.0) |

### ASP.NET Core Extended Options (`SentryAspNetCoreOptions`)

| Option | Type | Default | Notes |
|--------|------|---------|-------|
| `MaxRequestBodySize` | `RequestSize` | `None` | `None`, `Small` (~4 KB), `Medium` (~10 KB), `Always` |
| `MinimumBreadcrumbLevel` | `LogLevel` | `Information` | Min log level for breadcrumbs |
| `MinimumEventLevel` | `LogLevel` | `Error` | Min log level to send as Sentry event |
| `CaptureBlockingCalls` | `bool` | `false` | Detect `.Wait()` / `.Result` threadpool starvation |
| `FlushOnCompletedRequest` | `bool` | `false` | **Required for Lambda / serverless** |
| `IncludeActivityData` | `bool` | `false` | Capture `System.Diagnostics.Activity` values |

### MAUI Extended Options (`SentryMauiOptions`)

| Option | Type | Default | Notes |
|--------|------|---------|-------|
| `IncludeTextInBreadcrumbs` | `bool` | `false` | Text from `Button`, `Label`, `Entry` elements. ⚠️ PII risk. |
| `IncludeTitleInBreadcrumbs` | `bool` | `false` | Titles from `Window`, `Page` elements. ⚠️ PII risk. |
| `IncludeBackgroundingStateInBreadcrumbs` | `bool` | `false` | `Window.Backgrounding` event state. ⚠️ PII risk. |

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `SENTRY_DSN` | Project DSN |
| `SENTRY_RELEASE` | App version (e.g. `my-app@1.2.3`) |
| `SENTRY_ENVIRONMENT` | Deployment environment name |
| `SENTRY_AUTH_TOKEN` | MSBuild / `sentry-cli` symbol upload auth token |

**ASP.NET Core:** use double underscore `__` as hierarchy separator:

```bash
export Sentry__Dsn="https://..."
export Sentry__TracesSampleRate="0.1"
```

### MSBuild Symbol Upload Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SentryOrg` | `string` | — | Sentry organization slug |
| `SentryProject` | `string` | — | Sentry project slug |
| `SentryUploadSymbols` | `bool` | `false` | Upload PDB files for line numbers in stack traces |
| `SentryUploadSources` | `bool` | `false` | Upload source files for source context |
| `SentryCreateRelease` | `bool` | `false` | Auto-create a Sentry release during build |
| `SentrySetCommits` | `bool` | `false` | Associate git commits with the release |
| `SentryUrl` | `string` | — | Self-hosted Sentry URL |

---

## Verification

After wizard or manual setup, add a test throw and remove it after verifying:

```csharp
// ASP.NET Core: add a temporary endpoint
app.MapGet("/sentry-test", () =>
{
    throw new Exception("Sentry test error — delete me");
});

// Or capture explicitly anywhere
SentrySdk.CaptureException(new Exception("Sentry test error — delete me"));
```

Then check your [Sentry Issues dashboard](https://sentry.io/issues/) — the error should appear within ~30 seconds.

**Verification checklist:**

| Check | How |
|-------|-----|
| Exceptions captured | Throw a test exception, verify in Sentry Issues |
| Stack traces readable | Check that file names and line numbers appear |
| Tracing active | Check Performance tab for transactions |
| Logging wired | Log an error via `ILogger`, check it appears as Sentry breadcrumb |
| Symbol upload working | Stack trace shows `Controllers/HomeController.cs:42` not `<unknown>` |

---

## Phase 4: Cross-Link

After completing .NET setup, check for companion frontend projects:

```bash
# Check for frontend in adjacent directories
ls ../frontend ../client ../web ../app 2>/dev/null

# Check for JavaScript framework indicators
cat ../package.json 2>/dev/null | grep -E '"next"|"react"|"vue"|"nuxt"' | head -3
```

If a frontend is found, suggest the matching SDK skill:

| Frontend detected | Suggest skill |
|-------------------|--------------|
| Next.js (`"next"` in `package.json`) | `sentry-nextjs-sdk` |
| React SPA (`"react"` without `"next"`) | `@sentry/react` — see [docs.sentry.io/platforms/javascript/guides/react/](https://docs.sentry.io/platforms/javascript/guides/react/) |
| Vue.js | `@sentry/vue` — see [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |
| Nuxt | `@sentry/nuxt` — see [docs.sentry.io/platforms/javascript/guides/nuxt/](https://docs.sentry.io/platforms/javascript/guides/nuxt/) |

Connecting frontend and backend with the same Sentry project enables **distributed tracing** — a single trace view spanning browser, .NET server, and any downstream APIs.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Events not appearing | DSN misconfigured | Set `Debug = true` and check console output for SDK diagnostic messages |
| Stack traces show no file/line | PDB files not uploaded | Add `SentryUploadSymbols=true` to `.csproj`; set `SENTRY_AUTH_TOKEN` in CI |
| WPF/WinForms exceptions missing | `IsGlobalModeEnabled` not set | Set `options.IsGlobalModeEnabled = true` in `SentrySdk.Init()` |
| Lambda/serverless events lost | Container freezes before flush | Set `options.FlushOnCompletedRequest = true` |
| WPF UI-thread exceptions missing | `DispatcherUnhandledException` not wired | Register `App.DispatcherUnhandledException` in constructor (not `OnStartup`) |
| Duplicate HTTP spans in Azure Functions | Both Sentry and OTel instrument HTTP | Set `options.DisableSentryHttpMessageHandler = true` |
| `TracesSampleRate` has no effect | Rate is `0.0` (default) | Set `TracesSampleRate > 0` to enable tracing |
| `appsettings.json` values ignored | Config key format wrong | Use flat key `"Sentry:Dsn"` or env var `Sentry__Dsn` (double underscore) |
| `BeforeSend` drops all events | Hook returns `null` unconditionally | Verify your filter logic; return `null` only for events you want to drop |
| MAUI native crashes not captured | Wrong package | Confirm `Sentry.Maui` is installed (not just `Sentry`) |
