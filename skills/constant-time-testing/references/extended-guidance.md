<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Common Vulnerabilities

| Vulnerability | Description | Detection | Severity |
|---------------|-------------|-----------|----------|
| Secret-dependent branch | `if (secret_bit) { ... }` | dudect, Timecop | CRITICAL |
| Secret-dependent array access | `table[secret_index]` | Timecop, Binsec | HIGH |
| Variable-time division | `result = x / secret` | Timecop | MEDIUM |
| Variable-time shift | `result = x << secret` | Timecop | MEDIUM |
| Montgomery reduction leak | Extra reduction when intermediate > N | dudect | HIGH |

### Secret-Dependent Branch: Deep Dive

**The vulnerability:**
Execution time differs based on whether branch is taken. Common in optimized modular exponentiation (square-and-multiply).

**How to detect with dudect:**
```c
uint8_t do_one_computation(uint8_t *data) {
    uint64_t base = ((uint64_t*)data)[0];
    uint64_t exponent = ((uint64_t*)data)[1]; // Secret!
    return mod_exp(base, exponent, MODULUS);
}

void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {
    for (size_t i = 0; i < c->number_measurements; i++) {
        classes[i] = randombit();
        uint64_t *input = (uint64_t*)(input_data + i * c->chunk_size);
        input[0] = rand(); // Random base
        input[1] = (classes[i] == 0) ? FIXED_EXPONENT : rand(); // Fixed vs random
    }
}
```

**How to detect with Timecop:**
```c
poison(&exponent, sizeof(exponent));
result = mod_exp(base, exponent, modulus);
unpoison(&exponent, sizeof(exponent));
```

Valgrind will report:
```
Conditional jump or move depends on uninitialised value(s)
  at 0x40115D: mod_exp (example.c:14)
```

**Related skill:** **dudect**, **timecop**

## Case Studies

### Case Study: OpenSSL RSA Timing Attack

Brumley and Boneh (2005) extracted RSA private keys from OpenSSL over a network. The vulnerability exploited Montgomery multiplication's variable-time reduction step.

**Attack vector:** Timing differences in modular exponentiation
**Detection approach:** Statistical analysis (precursor to dudect)
**Impact:** Remote key extraction

**Tools used:** Custom timing measurement
**Techniques applied:** Statistical analysis, chosen-ciphertext queries

### Case Study: KyberSlash

Post-quantum algorithm Kyber's reference implementation contained timing vulnerabilities in polynomial operations. Division operations leaked secret coefficients.

**Attack vector:** Secret-dependent division timing
**Detection approach:** Dynamic analysis and statistical testing
**Impact:** Secret key recovery in post-quantum cryptography

**Tools used:** Timing measurement tools
**Techniques applied:** Differential timing analysis

## Advanced Usage

### Tips and Tricks

| Tip | Why It Helps |
|-----|--------------|
| Pin dudect to isolated CPU core (`taskset -c 2`) | Reduces OS noise, improves signal detection |
| Test multiple compilers (gcc, clang, MSVC) | Optimizations may introduce or remove leaks |
| Run dudect for extended periods (hours) | Increases statistical confidence |
| Minimize non-crypto code in harness | Reduces noise that masks weak signals |
| Check assembly output (`objdump -d`) | Verify compiler didn't introduce branches |
| Use `-O3 -march=native` in testing | Matches production optimization levels |

### Common Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---------|----------------|------------------|
| Only testing one input distribution | May miss leaks visible with other patterns | Test fixed-vs-random, fixed-vs-fixed-different, etc. |
| Short dudect runs (< 1 minute) | Insufficient measurements for weak signals | Run 5-10+ minutes, longer for high assurance |
| Ignoring compiler optimization levels | `-O0` may hide leaks present in `-O3` | Test at production optimization level |
| Not testing on target architecture | x86 vs ARM have different timing characteristics | Test on deployment platform |
| Marking too much as secret in Timecop | False positives, unclear results | Mark only true secrets (keys, not public data) |

## Related Skills

### Tool Skills

| Skill | Primary Use in Constant-Time Analysis |
|-------|---------------------------------------|
| **dudect** | Statistical detection of timing differences via Welch's t-test |
| **timecop** | Dynamic tracing to pinpoint exact location of timing leaks |

### Technique Skills

| Skill | When to Apply |
|-------|---------------|
| **coverage-analysis** | Ensure test inputs exercise all code paths in crypto function |
| **ci-integration** | Automate constant-time testing in continuous integration pipeline |

### Related Domain Skills

| Skill | Relationship |
|-------|--------------|
| **crypto-testing** | Constant-time analysis is essential component of cryptographic testing |
| **fuzzing** | Fuzzing crypto code may trigger timing-dependent paths |

## Skill Dependency Map

```
                    ┌─────────────────────────┐
                    │  constant-time-analysis │
                    │     (this skill)        │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
    ┌───────────────────┐           ┌───────────────────┐
    │      dudect       │           │     timecop       │
    │  (statistical)    │           │    (dynamic)      │
    └────────┬──────────┘           └────────┬──────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   Supporting Techniques      │
              │ coverage, CI integration     │
              └──────────────────────────────┘
```

## Resources

### Key External Resources

**[These results must be false: A usability evaluation of constant-time analysis tools](https://www.usenix.org/system/files/sec24fall-prepub-760-fourne.pdf)**
Comprehensive usability study of constant-time analysis tools. Key findings: developers struggle with false positives, need better error messages, and benefit from tool integration. Evaluates FaCT, ct-verif, dudect, and Memsan across multiple cryptographic implementations. Recommends improved tooling UX and better documentation.

**[List of constant-time tools - CROCS](https://crocs-muni.github.io/ct-tools/)**
Curated catalog of constant-time analysis tools with tutorials. Covers formal tools (ct-verif, FaCT), dynamic tools (Memsan, Timecop), symbolic tools (Binsec), and statistical tools (dudect). Includes practical tutorials for setup and usage.

**[Paul Kocher: Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems](https://paulkocher.com/doc/TimingAttacks.pdf)**
Original 1996 paper introducing timing attacks. Demonstrates attacks on modular exponentiation in RSA and Diffie-Hellman. Essential historical context for understanding timing vulnerabilities.

**[Remote Timing Attacks are Practical (Brumley & Boneh)](https://crypto.stanford.edu/~dabo/papers/ssl-timing.pdf)**
Demonstrates practical remote timing attacks against OpenSSL. Shows network-level timing differences are sufficient to extract RSA keys. Proves timing attacks work in realistic network conditions.

**[Cache-timing attacks on AES](https://cr.yp.to/antiforgery/cachetiming-20050414.pdf)**
Shows AES implementations using lookup tables are vulnerable to cache-timing attacks. Demonstrates practical attacks extracting AES keys via cache timing side channels.

**[KyberSlash: Division Timings Leak Secrets](https://eprint.iacr.org/2024/1049.pdf)**
Recent discovery of timing vulnerabilities in Kyber (NIST post-quantum standard). Shows division operations leak secret coefficients. Highlights that constant-time issues persist even in modern post-quantum cryptography.

### Video Resources

- [Trail of Bits: Constant-Time Programming](https://www.youtube.com/watch?v=vW6wqTzfz5g) - Overview of constant-time programming principles and tools
