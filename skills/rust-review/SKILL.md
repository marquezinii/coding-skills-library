---
name: rust-review
description: Review Rust code for correctness, unsafe-code soundness, ownership and lifetime mistakes, panic and error-handling problems, concurrency hazards, FFI violations, performance regressions, and missing tests. Use for Rust diffs, crates, CLIs, services, embedded targets, and security-sensitive native code. Produce evidence-backed findings with file and line locations.
license: MIT
---

# Rust review

Review the requested Rust scope against its actual contracts and supported toolchain. Prioritize correctness and soundness over cosmetic preferences.

## 1. Establish scope

- Identify the workspace/crate, diff, MSRV/toolchain, enabled features, targets, and public API constraints.
- Read `Cargo.toml`, nearby tests, unsafe invariants, important call sites, and error conventions.
- Distinguish regressions in the change from unrelated existing issues.
- Treat unsafe code, FFI, deserialization, concurrency, cryptography, and untrusted input as high risk.

## 2. Run available checks

Use repository commands when present. Otherwise, narrow checks may include:

```sh
cargo fmt --check
cargo check --workspace --all-targets
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features
```

Run only checks compatible with the repository's documented feature matrix. When relevant and available, consider `cargo miri test`, sanitizer builds, or target-specific checks. Never claim a command passed unless it ran.

## 3. Review checklist

### Correctness and ownership

- Incorrect moves, clones masking ownership design, stale borrows, lifetime escape, and invalid cache/state assumptions.
- Iterator boundary errors, integer conversions, overflow, indexing, slice boundaries, and partial I/O.
- Drop order, cancellation safety, cleanup on `?`, and resources held across `.await`.
- `unwrap`, `expect`, indexing, and panics reachable from ordinary or attacker-controlled input.

### Unsafe and FFI

- Every `unsafe` block has a true safety invariant that callers uphold.
- Raw pointers are aligned, initialized, in bounds, correctly aliased, and valid for the required lifetime.
- `Send`/`Sync` implementations, pinning, transmute, unions, `MaybeUninit`, and `Vec::set_len` are justified.
- FFI layouts use appropriate `repr`, ownership is explicit, callbacks cannot outlive state, and unwind behavior is defined.
- Safe wrappers cannot construct invalid states or violate invariants through public methods.

### Errors, APIs, and compatibility

- Error variants preserve useful context without leaking secrets.
- Retryability, idempotency, partial success, and cancellation are represented deliberately.
- Public APIs avoid accidental breaking changes in traits, features, serialization, and semver-visible types.
- Feature flags compose; optional dependencies and target gates do not leave uncompiled paths.

### Concurrency and async

- Lock ordering, poisoning policy, atomics, memory ordering, channels, and shutdown are correct.
- No blocking operation or lock guard crosses `.await` without a deliberate reason.
- Spawned tasks have ownership, cancellation, error propagation, and bounded lifetime.
- Shared mutable state cannot race or deadlock under failure paths.

### Performance and tests

- Hot paths avoid unintended allocation, cloning, quadratic behavior, and unbounded buffering.
- Tests cover malformed input, boundaries, feature combinations, unsafe invariants, and regression cases.
- Benchmarks are requested only when performance is part of the contract.

## 4. Report

List actionable findings by severity. Each finding must include:

1. exact file and narrow line range;
2. the concrete state/input that triggers it;
3. impact on correctness, soundness, security, or compatibility;
4. the smallest safe fix;
5. a regression test or validation command when practical.

If no defect is found, say so and report which commands/checks ran and what remains unverified.
