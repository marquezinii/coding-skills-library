---
name: turborepo
description: |
  Turborepo monorepo build system guidance. Triggers on: turbo.json, task pipelines,
  dependsOn, caching, remote cache, the "turbo" CLI, --filter, --affected, CI optimization, environment
  variables, internal packages, monorepo structure/best practices, and boundaries.

  Use when user: configures tasks/workflows/pipelines, creates packages, sets up
  monorepo, shares code between apps, runs changed/affected packages, debugs cache,
  or has apps/packages directories.
metadata:
  version: 2.10.9-canary.1
---

# Turborepo Skill

Build system for JavaScript/TypeScript monorepos. Turborepo caches task outputs and runs tasks in parallel based on dependency graph.

## IMPORTANT: Package Tasks, Not Root Tasks

**Prefer package tasks over Root Tasks.**

When creating tasks/scripts/pipelines, you MUST default to package tasks:

1. Add the script to each relevant package's `package.json`
2. Register the task in root `turbo.json`
3. Root `package.json` only delegates via `turbo run <task>`

**DO NOT** put task logic in root `package.json` when it can live in packages. This defeats Turborepo's parallelization.

```json
// DO THIS: Scripts in each package
// apps/web/package.json
{ "scripts": { "build": "next build", "lint": "eslint .", "test": "vitest" } }

// apps/api/package.json
{ "scripts": { "build": "tsc", "lint": "eslint .", "test": "vitest" } }

// packages/ui/package.json
{ "scripts": { "build": "tsc", "lint": "eslint .", "test": "vitest" } }
```

```json
// turbo.json - register tasks
{
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "lint": {},
    "test": { "dependsOn": ["build"] }
  }
}
```

```json
// Root package.json - ONLY delegates, no task logic
{
  "scripts": {
    "build": "turbo run build",
    "lint": "turbo run lint",
    "test": "turbo run test"
  }
}
```

```json
// DO NOT DO THIS - defeats parallelization
// Root package.json
{
  "scripts": {
    "build": "cd apps/web && next build && cd ../api && tsc",
    "lint": "eslint apps/ packages/",
    "test": "vitest"
  }
}
```

Root Tasks (`//#taskname`) are ONLY for tasks that truly cannot exist in packages, such as Vitest Projects' `//#test`, repo-wide release scripts, or tooling that does not invoke `turbo` itself.

## Secondary Rule: `turbo run` vs `turbo`

**Always use `turbo run` when the command is written into code:**

```json
// package.json - ALWAYS "turbo run"
{
  "scripts": {
    "build": "turbo run build"
  }
}
```

```yaml
# CI workflows - ALWAYS "turbo run"
- run: turbo run build --affected
```

**The shorthand `turbo <tasks>` is ONLY for one-off terminal commands** typed directly by humans or agents. Never write `turbo build` into package.json, CI, or scripts.

## Quick Decision Trees

### "I need to configure a task"

```
Configure a task?
├─ Define task dependencies → references/configuration/tasks.md
├─ Lint/check-types (parallel + caching) → Use Transit Nodes pattern (see below)
├─ Specify build outputs → references/configuration/tasks.md#outputs
├─ Handle environment variables → references/environment/RULE.md
├─ Set up dev/watch tasks → references/configuration/tasks.md#persistent
├─ Package-specific config → references/configuration/RULE.md#package-configurations
└─ Global settings (cacheDir, daemon) → references/configuration/global-options.md
```

### "My cache isn't working"

```
Cache problems?
├─ Tasks run but outputs not restored → Missing `outputs` key
├─ Cache misses unexpectedly → references/caching/gotchas.md
├─ Need to debug hash inputs → Use --summarize or --dry
├─ Want to skip cache entirely → Use --force or cache: false
├─ Remote cache not working → references/caching/remote-cache.md
└─ Environment causing misses → references/environment/gotchas.md
```

### "I want to run only changed packages"

```
Run only what changed?
├─ Changed packages + dependents (RECOMMENDED) → turbo run build --affected
├─ Custom base branch → TURBO_SCM_BASE=origin/develop turbo run build --affected
├─ Manual git comparison → --filter=...[origin/main]
└─ See all filter options → references/filtering/RULE.md
```

**`--affected` is the primary way to run only changed packages.** It compares against `main` (falling back to `master`) — not the repo's configured default branch — and includes dependents. Set `TURBO_SCM_BASE` for any other base branch.

### "I want to filter packages"

```
Filter packages?
├─ Only changed packages → --affected (see above)
├─ By package name → --filter=web
├─ By directory → --filter=./apps/*
├─ Package + dependencies → --filter=web...
├─ Package + dependents → --filter=...web
└─ Complex combinations → references/filtering/patterns.md
```

### "Environment variables aren't working"

```
Environment issues?
├─ Vars not available at runtime → Strict mode filtering (default)
├─ Cache hits with wrong env → Var not in `env` key
├─ .env changes not causing rebuilds → .env not in `inputs`
├─ CI variables missing → references/environment/gotchas.md
└─ Framework vars (NEXT_PUBLIC_*) → Auto-included via inference
```

### "I need to set up CI"

```
CI setup?
├─ GitHub Actions → references/ci/github-actions.md
├─ Vercel deployment → references/ci/vercel.md
├─ Remote cache in CI → references/caching/remote-cache.md
├─ Only build changed packages → --affected flag
├─ Skip unnecessary builds → turbo-ignore (references/cli/commands.md)
└─ Skip container setup when no changes → turbo-ignore
```

### "I want to watch for changes during development"

```
Watch mode?
├─ Re-run tasks on change → turbo watch (references/watch/RULE.md)
├─ Dev servers with dependencies → Use `with` key (references/configuration/tasks.md#with)
├─ Restart dev server on dep change → Use `interruptible: true`
└─ Persistent dev tasks → Use `persistent: true`
```

### "I need to create/structure a package"

```
Package creation/structure?
├─ Create an internal package → references/best-practices/packages.md
├─ Repository structure → references/best-practices/structure.md
├─ Dependency management → references/best-practices/dependencies.md
├─ Best practices overview → references/best-practices/RULE.md
├─ JIT vs Compiled packages → references/best-practices/packages.md#compilation-strategies
└─ Sharing code between apps → references/best-practices/RULE.md#package-types
```

### "How should I structure my monorepo?"

```
Monorepo structure?
├─ Standard layout (apps/, packages/) → references/best-practices/RULE.md
├─ Package types (apps vs libraries) → references/best-practices/RULE.md#package-types
├─ Creating internal packages → references/best-practices/packages.md
├─ TypeScript configuration → references/best-practices/structure.md#typescript-configuration
├─ ESLint configuration → references/best-practices/structure.md#eslint-configuration
├─ Dependency management → references/best-practices/dependencies.md
└─ Enforce package boundaries → references/boundaries/RULE.md
```

### "I want to enforce architectural boundaries"

```
Enforce boundaries?
├─ Check for violations → turbo boundaries
├─ Tag packages → references/boundaries/RULE.md#tags
├─ Restrict which packages can import others → references/boundaries/RULE.md#rule-types
└─ Prevent cross-package file imports → references/boundaries/RULE.md
```


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Critical Anti-Patterns](references/extended-guidance.md#critical-anti-patterns)
- [Common Task Configurations](references/extended-guidance.md#common-task-configurations)
- [Reference Index](references/extended-guidance.md#reference-index)
- [Source Documentation](references/extended-guidance.md#source-documentation)

