---
name: sentry-dotnet-sdk
description: Full Sentry SDK setup for .NET. Use when asked to "add Sentry to .NET", "install Sentry for C#", or configure error monitoring, tracing, profiling, logging, or crons for ASP.NET Core, MAUI, WPF, WinForms, Blazor, Azure Functions, or any other .NET application.
license: Apache-2.0
---

> Sentry SDK setup › .NET

# Sentry .NET SDK

Opinionated wizard that scans your .NET project and guides you through complete Sentry setup: error monitoring, distributed tracing, profiling, structured logging, and cron monitoring across all major .NET frameworks.

## Invoke This Skill When

- User asks to "add Sentry to .NET", "set up Sentry in C#", or "install Sentry for ASP.NET Core"
- User wants error monitoring, tracing, profiling, logging, or crons for a .NET app
- User mentions `SentrySdk.Init`, `UseSentry`, `Sentry.AspNetCore`, or `Sentry.Maui`
- User wants to capture unhandled exceptions in WPF, WinForms, MAUI, or Azure Functions
- User asks about `SentryOptions`, `BeforeSend`, `TracesSampleRate`, or symbol upload

> **Note:** SDK version and APIs below reflect `Sentry` NuGet packages ≥6.1.0 (OTLP export requires ≥6.5.0).
> Always verify against [docs.sentry.io/platforms/dotnet/](https://docs.sentry.io/platforms/dotnet/) before implementing.

---

## Phase 1: Detect

Run these commands to understand the project before making any recommendations:

```bash
# Detect framework type — find all .csproj files
find . -name "*.csproj" | head -20

# Detect framework targets
grep -r "TargetFramework\|Project Sdk" --include="*.csproj" .

# Check for existing Sentry packages
grep -r "Sentry" --include="*.csproj" . | grep "PackageReference"

# Check startup files
ls Program.cs src/Program.cs App.xaml.cs MauiProgram.cs 2>/dev/null

# Check for appsettings
ls appsettings.json src/appsettings.json 2>/dev/null

# Check for logging libraries
grep -r "Serilog\|NLog\|log4net" --include="*.csproj" .

# Check for companion frontend
ls ../frontend ../client ../web 2>/dev/null
cat ../package.json 2>/dev/null | grep -E '"next"|"react"|"vue"' | head -3
```

**What to determine:**

| Question | Impact |
|----------|--------|
| Framework type? | Determines correct package and init pattern |
| .NET version? | .NET 8+ recommended; .NET Framework 4.6.2+ supported |
| Sentry already installed? | Skip install, go to feature config |
| Logging library (Serilog, NLog)? | Recommend matching Sentry sink/target |
| Async/hosted app (ASP.NET Core)? | `UseSentry()` on `WebHost`; no `IsGlobalModeEnabled` needed |
| Desktop app (WPF, WinForms, WinUI)? | Must set `IsGlobalModeEnabled = true` |
| Serverless (Azure Functions, Lambda)? | Must set `FlushOnCompletedRequest = true` |
| Frontend directory found? | Trigger Phase 4 cross-link |

**Framework → Package mapping:**

| Detected | Package to install |
|----------|--------------------|
| `Sdk="Microsoft.NET.Sdk.Web"` (ASP.NET Core) | `Sentry.AspNetCore` |
| `App.xaml.cs` with `Application` base | `Sentry` (WPF) |
| `[STAThread]` in `Program.cs` | `Sentry` (WinForms) |
| `MauiProgram.cs` | `Sentry.Maui` |
| `WebAssemblyHostBuilder` | `Sentry.AspNetCore.Blazor.WebAssembly` |
| `FunctionsStartup` | `Sentry.Extensions.Logging` + `Sentry.OpenTelemetry` |
| `HttpApplication` / `Global.asax` | `Sentry.AspNet` |
| Generic host / Worker Service | `Sentry.Extensions.Logging` |

---

## Phase 2: Recommend

Present a concrete recommendation based on what you found. Lead with a proposal — don't ask open-ended questions.

**Recommended (core coverage):**
- ✅ **Error Monitoring** — always; captures unhandled exceptions, structured captures, scope enrichment
- ✅ **Tracing** — always for ASP.NET Core and hosted apps; auto-instruments HTTP requests and EF Core queries
- ✅ **Logging** — recommended for all apps; routes ILogger / Serilog / NLog entries to Sentry as breadcrumbs and events

**Optional (enhanced observability):**
- ⚡ **Profiling** — CPU profiling; recommend for performance-critical services running on .NET 6+
- ⚡ **Metrics** — counters, gauges, distributions linked to traces; recommend for apps that need custom business metrics
- ⚡ **Crons** — detect missed/failed scheduled jobs; recommend when Hangfire, Quartz.NET, or scheduled endpoints detected

**Recommendation logic:**

| Feature | Recommend when... |
|---------|------------------|
| Error Monitoring | **Always** — non-negotiable baseline |
| Tracing | **Always for ASP.NET Core** — request traces, EF Core spans, HttpClient spans are high-value |
| Logging | App uses `ILogger<T>`, Serilog, NLog, or log4net |
| Profiling | Performance-critical service on .NET 6+ |
| Metrics | App needs custom business metrics (request counts, queue depths, response times) |
| Crons | App uses Hangfire, Quartz.NET, or scheduled Azure Functions |

Propose: *"I recommend setting up Error Monitoring + Tracing + Logging. Want me to also add Profiling or Crons?"*

---

## Phase 3: Guide

### Option 1: Wizard (Recommended)

> **You need to run this yourself** — the wizard opens a browser for login and requires interactive input that the agent can't handle. Copy-paste into your terminal:
>
> ```
> npx @sentry/wizard@latest -i dotnet
> ```
>
> It handles login, org/project selection, DSN configuration, and MSBuild symbol upload setup for readable stack traces in production.
>
> **Once it finishes, come back and skip to [Verification](references/extended-guidance.md#verification).**

If the user skips the wizard, proceed with Option 2 (Manual Setup) below.

---

### Option 2: Manual Setup

#### Install the right package

```bash
# ASP.NET Core
dotnet add package Sentry.AspNetCore -v 6.1.0

# WPF or WinForms or Console
dotnet add package Sentry -v 6.1.0

# .NET MAUI
dotnet add package Sentry.Maui -v 6.1.0

# Blazor WebAssembly
dotnet add package Sentry.AspNetCore.Blazor.WebAssembly -v 6.1.0

# Azure Functions (Isolated Worker)
dotnet add package Sentry.Extensions.Logging -v 6.1.0
dotnet add package Sentry.OpenTelemetry -v 6.1.0

# Classic ASP.NET (System.Web / .NET Framework)
dotnet add package Sentry.AspNet -v 6.1.0
```

---

#### ASP.NET Core — `Program.cs`

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.WebHost.UseSentry(options =>
{
    options.Dsn = Environment.GetEnvironmentVariable("SENTRY_DSN")
                  ?? "___YOUR_DSN___";
    options.Debug = true;                         // disable in production
    options.SendDefaultPii = true;                // captures user IP, name, email
    options.MaxRequestBodySize = RequestSize.Always;
    options.MinimumBreadcrumbLevel = LogLevel.Debug;
    options.MinimumEventLevel = LogLevel.Warning;
    options.TracesSampleRate = 1.0;               // tune to 0.1–0.2 in production
    options.SetBeforeSend((@event, hint) =>
    {
        @event.ServerName = null;                 // scrub hostname from events
        return @event;
    });
});

var app = builder.Build();
app.Run();
```

**`appsettings.json` (alternative configuration):**

```json
{
  "Sentry": {
    "Dsn": "___YOUR_DSN___",
    "SendDefaultPii": true,
    "MaxRequestBodySize": "Always",
    "MinimumBreadcrumbLevel": "Debug",
    "MinimumEventLevel": "Warning",
    "AttachStacktrace": true,
    "Debug": true,
    "TracesSampleRate": 1.0,
    "Environment": "production",
    "Release": "my-app@1.0.0"
  }
}
```

**Environment variables (double underscore as separator):**

```bash
export Sentry__Dsn="https://examplePublicKey@o0.ingest.sentry.io/0"
export Sentry__TracesSampleRate="0.1"
export Sentry__Environment="staging"
```

---

#### WPF — `App.xaml.cs`

> ⚠️ **Critical:** Initialize in the **constructor**, NOT in `OnStartup()`. The constructor fires earlier, catching more failure modes.

```csharp
using System.Windows;
using Sentry;

public partial class App : Application
{
    public App()
    {
        SentrySdk.Init(options =>
        {
            options.Dsn = "___YOUR_DSN___";
            options.Debug = true;
            options.SendDefaultPii = true;
            options.TracesSampleRate = 1.0;
            options.IsGlobalModeEnabled = true;   // required for all desktop apps
        });

        // Capture WPF UI-thread exceptions before WPF's crash dialog appears
        DispatcherUnhandledException += App_DispatcherUnhandledException;
    }

    private void App_DispatcherUnhandledException(
        object sender,
        System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
    {
        SentrySdk.CaptureException(e.Exception);
        // Set e.Handled = true to prevent crash dialog and keep app running
    }
}
```

---

#### WinForms — `Program.cs`

```csharp
using System;
using System.Windows.Forms;
using Sentry;

static class Program
{
    [STAThread]
    static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        // Required: allows Sentry to see unhandled WinForms exceptions
        Application.SetUnhandledExceptionMode(UnhandledExceptionMode.ThrowException);

        using (SentrySdk.Init(new SentryOptions
        {
            Dsn = "___YOUR_DSN___",
            Debug = true,
            TracesSampleRate = 1.0,
            IsGlobalModeEnabled = true,           // required for desktop apps
        }))
        {
            Application.Run(new MainForm());
        } // Disposing flushes all pending events
    }
}
```

---

#### .NET MAUI — `MauiProgram.cs`

```csharp
public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseSentry(options =>
            {
                options.Dsn = "___YOUR_DSN___";
                options.Debug = true;
                options.SendDefaultPii = true;
                options.TracesSampleRate = 1.0;
                // MAUI-specific: opt-in breadcrumbs (off by default — PII risk)
                options.IncludeTextInBreadcrumbs = false;
                options.IncludeTitleInBreadcrumbs = false;
                options.IncludeBackgroundingStateInBreadcrumbs = false;
            });

        return builder.Build();
    }
}
```

---

#### Blazor WebAssembly — `Program.cs`

```csharp
var builder = WebAssemblyHostBuilder.CreateDefault(args);

builder.UseSentry(options =>
{
    options.Dsn = "___YOUR_DSN___";
    options.Debug = true;
    options.SendDefaultPii = true;
    options.TracesSampleRate = 0.1;
});

// Hook logging pipeline without re-initializing the SDK
builder.Logging.AddSentry(o => o.InitializeSdk = false);

await builder.Build().RunAsync();
```

---

#### Azure Functions (Isolated Worker) — `Program.cs`

> **Recommended:** Install `Sentry.OpenTelemetry.Exporter` (≥6.5.0) for OTLP export. Alternatively, use `Sentry.OpenTelemetry` for the bridge pattern.

```csharp
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using OpenTelemetry.Trace;

// Package: Sentry.OpenTelemetry.Exporter
var host = new HostBuilder()
    .ConfigureFunctionsWorkerDefaults()
    .ConfigureLogging(logging =>
    {
        logging.AddSentry(options =>
        {
            options.Dsn = "___YOUR_DSN___";
            options.Debug = true;
            options.TracesSampleRate = 1.0;
            options.UseOtlp(); // send OTel spans via OTLP (requires 6.5.0+)
        });
    })
    .ConfigureServices(services =>
    {
        services.AddOpenTelemetry().WithTracing(builder =>
        {
            builder
                .AddHttpClientInstrumentation()
                .AddSentryOtlpExporter("___YOUR_DSN___"); // route spans to Sentry OTLP endpoint
        });
    })
    .Build();

await host.RunAsync();
```

---

#### AWS Lambda — `LambdaEntryPoint.cs`

```csharp
public class LambdaEntryPoint : APIGatewayProxyFunction
{
    protected override void Init(IWebHostBuilder builder)
    {
        builder
            .UseSentry(options =>
            {
                options.Dsn = "___YOUR_DSN___";
                options.TracesSampleRate = 1.0;
                options.FlushOnCompletedRequest = true; // REQUIRED for Lambda
            })
            .UseStartup<Startup>();
    }
}
```

---

#### Classic ASP.NET — `Global.asax.cs`

```csharp
public class MvcApplication : HttpApplication
{
    private IDisposable _sentry;

    protected void Application_Start()
    {
        _sentry = SentrySdk.Init(options =>
        {
            options.Dsn = "___YOUR_DSN___";
            options.TracesSampleRate = 1.0;
            options.AddEntityFramework(); // EF6 query breadcrumbs
            options.AddAspNet();          // Classic ASP.NET integration
        });
    }

    protected void Application_Error() => Server.CaptureLastError();

    protected void Application_BeginRequest() => Context.StartSentryTransaction();
    protected void Application_EndRequest() => Context.FinishSentryTransaction();

    protected void Application_End() => _sentry?.Dispose();
}
```

---

### Symbol Upload (Readable Stack Traces)

Without debug symbols, stack traces show only method names — no file names or line numbers. The SDK uploads PDB files (and optionally sources) via MSBuild properties on Release builds:

```xml
<PropertyGroup Condition="'$(Configuration)' == 'Release'">
  <SentryOrg>___ORG_SLUG___</SentryOrg>
  <SentryProject>___PROJECT_SLUG___</SentryProject>
  <SentryUploadSymbols>true</SentryUploadSymbols>
  <SentryUploadSources>true</SentryUploadSources>
  <SentryCreateRelease>true</SentryCreateRelease>
  <SentrySetCommits>true</SentrySetCommits>
</PropertyGroup>
```

Upload needs a `SENTRY_AUTH_TOKEN` set in CI as a secret. Follow the current Sentry .NET documentation linked above for token scope, symbol upload, release creation, and commit association. The `SentryCreateRelease` and `SentrySetCommits` properties can create a release with suspect commits.

---

### For Each Agreed Feature

Load the corresponding reference file and follow its steps:

| Feature | Reference file | Load when... |
|---------|---------------|-------------|
| Error Monitoring | `references/error-monitoring.md` | Always — `CaptureException`, scopes, enrichment, filtering |
| Tracing | `references/tracing.md` | Server apps, distributed tracing, EF Core spans, custom instrumentation |
| Profiling | `references/profiling.md` | Performance-critical apps on .NET 6+ |
| Logging | `references/logging.md` | `ILogger<T>`, Serilog, NLog, log4net integration |
| Metrics | `references/metrics.md` | Custom counters, gauges, distributions; `EmitCounter`, `EmitGauge`, `EmitDistribution` |
| Crons | `references/crons.md` | Hangfire, Quartz.NET, or scheduled function monitoring |

For each feature: read the reference file, follow its steps exactly, and verify before moving on.

---


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Configuration Reference](references/extended-guidance.md#configuration-reference)
- [Verification](references/extended-guidance.md#verification)
- [Phase 4: Cross-Link](references/extended-guidance.md#phase-4-cross-link)
- [Troubleshooting](references/extended-guidance.md#troubleshooting)

