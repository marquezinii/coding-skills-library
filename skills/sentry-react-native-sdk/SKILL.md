---
name: sentry-react-native-sdk
description: Full Sentry SDK setup for React Native and Expo. Use when asked to "add Sentry to React Native", "install @sentry/react-native", "setup Sentry in Expo", or configure error monitoring, tracing, profiling, session replay, or logging for React Native applications. Supports Expo managed, Expo bare, and vanilla React Native.
license: Apache-2.0
---

# Sentry React Native SDK

Opinionated wizard that scans your React Native or Expo project and guides you through complete Sentry setup — error monitoring, tracing, profiling, session replay, logging, and more.

## Invoke This Skill When

- User asks to "add Sentry to React Native" or "set up Sentry" in an RN or Expo app
- User wants error monitoring, tracing, profiling, session replay, or logging in React Native
- User mentions `@sentry/react-native`, mobile error tracking, or Sentry for Expo
- User wants to monitor native crashes, ANRs, or app hangs on iOS/Android

> **Note:** SDK versions and APIs below reflect current Sentry docs at time of writing (`@sentry/react-native` ≥6.0.0, minimum recommended ≥8.0.0).
> Always verify against [docs.sentry.io/platforms/react-native/](https://docs.sentry.io/platforms/react-native/) before implementing.

---

## Phase 1: Detect

Run these commands to understand the project before making any recommendations:

```bash
# Detect project type and existing Sentry
cat package.json | grep -E '"(react-native|expo|@expo|@sentry/react-native|sentry-expo)"'

# Distinguish Expo managed vs bare vs vanilla RN
ls app.json app.config.js app.config.ts 2>/dev/null
cat app.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('Expo managed' if 'expo' in d else 'Bare/Vanilla')" 2>/dev/null

# Check Expo SDK version (important: Expo SDK 50+ required for @sentry/react-native)
cat package.json | grep '"expo"'

# Detect navigation library
grep -E '"(@react-navigation/native|react-native-navigation)"' package.json

# Detect state management (Redux → breadcrumb integration available)
grep -E '"(redux|@reduxjs/toolkit|zustand|mobx)"' package.json

# Check for existing Sentry initialization
grep -r "Sentry.init" src/ app/ App.tsx App.js _layout.tsx 2>/dev/null | head -5

# Detect Hermes (affects source map handling)
cat android/app/build.gradle 2>/dev/null | grep -i hermes
cat ios/Podfile 2>/dev/null | grep -i hermes

# Detect Expo Router
ls app/_layout.tsx app/_layout.js 2>/dev/null

# Detect backend for cross-link
ls backend/ server/ api/ 2>/dev/null
find . -maxdepth 3 \( -name "go.mod" -o -name "requirements.txt" -o -name "Gemfile" -o -name "package.json" \) 2>/dev/null | grep -v node_modules | head -10
```

**What to determine:**

| Question | Impact |
|----------|--------|
| `expo` in `package.json`? | Expo path (config plugin + `getSentryExpoConfig`) vs bare/vanilla RN path |
| Expo SDK ≥50? | `@sentry/react-native` directly; older = `sentry-expo` (legacy, do not use) |
| `app.json` has `"expo"` key? | Managed Expo — wizard is simplest; config plugin handles all native config |
| `app/_layout.tsx` present? | Expo Router project — init goes in `_layout.tsx` |
| `@sentry/react-native` already in `package.json`? | Skip install, jump to feature config |
| `@react-navigation/native` present? | Recommend `reactNavigationIntegration` for screen tracking |
| `react-native-navigation` present? | Recommend `reactNativeNavigationIntegration` (Wix) |
| Backend directory detected? | Trigger Phase 4 cross-link |

---

## Phase 2: Recommend

Present a concrete recommendation based on what you found. Don't ask open-ended questions — lead with a proposal:

**Recommended (core coverage — always set up these):**
- ✅ **Error Monitoring** — captures JS exceptions, native crashes (iOS + Android), ANRs, and app hangs
- ✅ **Tracing** — mobile performance is critical; auto-instruments navigation, app start, network requests
- ✅ **Session Replay** — mobile replay captures screenshots and touch events for debugging user issues

**Optional (enhanced observability):**
- ⚡ **Profiling** — CPU profiling on iOS (JS profiling cross-platform); low overhead in production
- ⚡ **Logging** — structured logs via `Sentry.logger.*`; links to traces for full context
- ⚡ **User Feedback** — collect user-submitted bug reports directly from your app

**Recommendation logic:**

| Feature | Recommend when... |
|---------|------------------|
| Error Monitoring | **Always** — non-negotiable baseline for any mobile app |
| Tracing | **Always for mobile** — app start, navigation, and network latency matter |
| Session Replay | User-facing production app; debug user-reported issues visually |
| Profiling | Performance-sensitive screens, startup time concerns, or production perf investigations |
| Logging | App uses structured logging, or you want log-to-trace correlation in Sentry |
| User Feedback | Beta or customer-facing app where you want user-submitted bug reports |

Propose: *"For your [Expo managed / bare RN] app, I recommend setting up Error Monitoring + Tracing + Session Replay. Want me to also add Profiling and Logging?"*

---


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Phase 3: Guide](references/extended-guidance.md#phase-3-guide)
- [Configuration Reference](references/extended-guidance.md#configuration-reference)
- [Environment Variables](references/extended-guidance.md#environment-variables)
- [Source Maps & Debug Symbols](references/extended-guidance.md#source-maps-debug-symbols)
- [Default Integrations (Auto-Enabled)](references/extended-guidance.md#default-integrations-auto-enabled)
- [Expo Config Plugin Reference](references/extended-guidance.md#expo-config-plugin-reference)
- [Production Settings](references/extended-guidance.md#production-settings)
- [Verification](references/extended-guidance.md#verification)
- [Phase 4: Cross-Link](references/extended-guidance.md#phase-4-cross-link)
- [Troubleshooting](references/extended-guidance.md#troubleshooting)

