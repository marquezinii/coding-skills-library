---
name: c-review
description: Review C code for memory safety, undefined behavior, integer and bounds errors, ownership mistakes, concurrency hazards, portability problems, and maintainability regressions. Use for C diffs, native libraries, embedded code, parsers, protocol handlers, and security-sensitive C. Produce evidence-backed findings with file and line locations; do not use for C++-only reviews.
license: MIT
---

# C review

Perform a focused, behavior-aware review of the requested C scope. Prefer concrete defects over style commentary and never claim a tool result that was not run.

## 1. Establish scope

- Identify the diff, files, build system, supported compilers, target platforms, and language standard.
- Read nearby tests, public headers, ownership contracts, error conventions, and important call sites.
- Separate pre-existing problems from regressions introduced by the reviewed change.
- Treat external input, binary parsing, privileges, concurrency, and cryptography as high-risk boundaries.

## 2. Run available checks

Use the repository's own commands first. When configured and relevant, consider:

```sh
cc -Wall -Wextra -Wpedantic -Wconversion -Wshadow -fsyntax-only path/to/file.c
clang-tidy path/to/file.c -- <project compile flags>
cppcheck --enable=warning,performance,portability --project=<compile_commands.json>
```

For tests or a reproducible harness, prefer sanitizer builds:

```sh
cc -fsanitize=address,undefined -fno-omit-frame-pointer ...
```

Do not invent compile flags or run broad commands that bypass the project's build configuration. If a tool is unavailable, continue with manual analysis and state the gap.

## 3. Review checklist

### Memory and lifetime

- Out-of-bounds reads/writes, off-by-one lengths, and unterminated strings.
- Use-after-free, double free, leaks, dangling pointers, invalid aliasing, and lifetime escape.
- Allocation overflow, zero-size allocation assumptions, partial initialization, and cleanup on every error path.
- Correct pairing of allocator/deallocator and explicit ownership transfer.

### Undefined behavior and arithmetic

- Signed overflow, invalid shifts, divide-by-zero, lossy narrowing, and size multiplication overflow.
- Uninitialized reads, strict-aliasing violations, invalid pointer arithmetic, and misaligned access.
- Incorrect format specifiers, variadic argument mismatches, and unsafe macro evaluation.

### API and input safety

- Return values, `errno`, short reads/writes, partial results, and retry semantics.
- Length validation before indexing, copying, decoding, or allocating.
- NUL handling, path traversal, command construction, integer-to-size conversions, and attacker-controlled resource use.
- Stable ABI/layout expectations, visibility, calling convention, and public-header compatibility.

### Concurrency and portability

- Data races, lock ordering, atomic ordering, signal-safety, cancellation, and cleanup.
- Endianness, width assumptions, platform APIs, compiler extensions, and implementation-defined behavior.
- Thread-safe initialization and ownership of shared state.

### Maintainability and tests

- Invariants are explicit and enforced near the boundary.
- Error paths are testable and do not duplicate fragile cleanup logic.
- Tests cover boundary lengths, malformed input, allocation failure where practical, and regression cases.

## 4. Report

List findings by severity. Each finding must include:

1. exact file and narrow line range;
2. the failing input/state and execution path;
3. concrete impact;
4. the smallest safe correction;
5. a regression test or validation command when practical.

If no actionable defect is found, say so and list the checks actually performed plus any unverified high-risk area.
