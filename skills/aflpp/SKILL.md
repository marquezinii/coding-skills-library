---
name: aflpp
metadata:
  type: fuzzer
description: >
  AFL++ is a fork of AFL with better fuzzing performance and advanced features.
  Use for multi-core fuzzing of C/C++ projects.
---

# AFL++

AFL++ is a fork of the original AFL fuzzer that offers better fuzzing performance and more advanced features while maintaining stability. A major benefit over libFuzzer is that AFL++ has stable support for running fuzzing campaigns on multiple cores, making it ideal for large-scale fuzzing efforts.

## When to Use

| Fuzzer | Best For | Complexity |
|--------|----------|------------|
| AFL++ | Multi-core fuzzing, diverse mutations, mature projects | Medium |
| libFuzzer | Quick setup, single-threaded, simple harnesses | Low |
| LibAFL | Custom fuzzers, research, advanced use cases | High |

**Choose AFL++ when:**
- You need multi-core fuzzing to maximize throughput
- Your project can be compiled with Clang or GCC
- You want diverse mutation strategies and mature tooling
- libFuzzer has plateaued and you need more coverage
- You're fuzzing production codebases that benefit from parallel execution

## Quick Start

```c++
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // Call your code with fuzzer-provided data
    check_buf((char*)data, size);
    return 0;
}
```

Compile and run:
```bash
# Setup AFL++ wrapper script first (see Installation)
./afl++ docker afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
mkdir seeds && echo "aaaa" > seeds/minimal_seed
./afl++ docker afl-fuzz -i seeds -o out -- ./fuzz
```

## Installation

AFL++ has many dependencies including LLVM, Python, and Rust. We recommend using a current Debian or Ubuntu distribution for fuzzing with AFL++.

| Method | When to Use | Supported Compilers |
|--------|-------------|---------------------|
| Ubuntu/Debian repos | Recent Ubuntu, basic features only | Ubuntu 23.10: Clang 14 & GCC 13<br>Debian 12: Clang 14 & GCC 12 |
| Docker (from Docker Hub) | Specific AFL++ version, Apple Silicon support | As of 4.35c: Clang 19 & GCC 11 |
| Docker (from source) | Test unreleased features, apply patches | Configurable in Dockerfile |
| From source | Avoid Docker, need specific patches | Adjustable via `LLVM_CONFIG` env var |

### Ubuntu/Debian

Prior to installing afl++, check the clang version dependency of the packge with `apt-cache show afl++`, and install the matching `lld` version (e.g., `lld-17`).


```bash
apt install afl++ lld-17
```


### Docker (from Docker Hub)

```bash
docker pull aflplusplus/aflplusplus:stable
```

### Docker (from source)

```bash
git clone --depth 1 --branch stable https://github.com/AFLplusplus/AFLplusplus
cd AFLplusplus
docker build -t aflplusplus .
```

### From source

Refer to the [Dockerfile](https://github.com/AFLplusplus/AFLplusplus/blob/stable/Dockerfile) for Ubuntu version requirements and dependencies. Set `LLVM_CONFIG` to specify Clang version (e.g., `llvm-config-18`).

### Wrapper Script Setup

Create a wrapper script to run AFL++ on host or Docker:

```bash
cat <<'EOF' > ./afl++
#!/bin/sh
AFL_VERSION="${AFL_VERSION:-"stable"}"
case "$1" in
   host)
        shift
        bash -c "$*"
        ;;
    docker)
        shift
        /usr/bin/env docker run -ti \
            --privileged \
            -v ./:/src \
            --rm \
            --name afl_fuzzing \
            "aflplusplus/aflplusplus:$AFL_VERSION" \
            bash -c "cd /src && bash -c \"$*\""
        ;;
    *)
        echo "Usage: $0 {host|docker}"
        exit 1
        ;;
esac
EOF
chmod +x ./afl++
```

**Security Warning:** The `afl-system-config` and `afl-persistent-config` scripts require root privileges and disable OS security features. Do not fuzz on production systems or your development environment. Use a dedicated VM instead.

### System Configuration

Run after each reboot for up to 15% more executions per second:

```bash
./afl++ <host/docker> afl-system-config
```

For maximum performance, disable kernel security mitigations (requires grub bootloader, not supported in Docker):

```bash
./afl++ host afl-persistent-config
update-grub
reboot
./afl++ <host/docker> afl-system-config
```

Verify with `cat /proc/cmdline` - output should include `mitigations=off`.

## Writing a Harness

### Harness Structure

AFL++ supports libFuzzer-style harnesses:

```c++
#include <stdint.h>
#include <stddef.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 1. Validate input size if needed
    if (size < MIN_SIZE || size > MAX_SIZE) return 0;

    // 2. Call target function with fuzz data
    target_function(data, size);

    // 3. Return 0 (non-zero reserved for future use)
    return 0;
}
```

### Harness Rules

| Do | Don't |
|----|-------|
| Reset global state between runs | Rely on state from previous runs |
| Handle edge cases gracefully | Exit on invalid input |
| Keep harness deterministic | Use random number generators |
| Free allocated memory | Create memory leaks |
| Validate input sizes | Process unbounded input |

> **See Also:** For detailed harness writing techniques, patterns for handling complex inputs,
> and advanced strategies, see the **fuzz-harness-writing** technique skill.

## Compilation

AFL++ offers multiple compilation modes with different trade-offs.

### Compilation Mode Decision Tree

Choose your compilation mode:
- **LTO mode** (`afl-clang-lto`): Best performance and instrumentation. Try this first.
- **LLVM mode** (`afl-clang-fast`): Fall back if LTO fails to compile.
- **GCC plugin** (`afl-gcc-fast`): For projects requiring GCC.

### Basic Compilation (LLVM mode)

```bash
./afl++ <host/docker> afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
```

### GCC Compilation

```bash
./afl++ <host/docker> afl-g++-fast -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
```

**Important:** GCC version must match the version used to compile the AFL++ GCC plugin.

### With Sanitizers

```bash
./afl++ <host/docker> AFL_USE_ASAN=1 afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
```

> **See Also:** For detailed sanitizer configuration, common issues, and advanced flags,
> see the **address-sanitizer** and **undefined-behavior-sanitizer** technique skills.

### Build Flags

Note that `-g` is not necessary, it is added by default by the AFL++ compilers.

| Flag | Purpose |
|------|---------|
| `-DNO_MAIN=1` | Skip main function when using libFuzzer harness |
| `-O2` | Production optimization level (recommended for fuzzing) |
| `-fsanitize=fuzzer` | Enable libFuzzer compatibility mode and adds the fuzzer runtime when linking executable |
| `-fsanitize=fuzzer-no-link` | Instrument without linking fuzzer runtime (for static libraries and object files) |

## Corpus Management

### Creating Initial Corpus

AFL++ requires at least one non-empty seed file:

```bash
mkdir seeds
echo "aaaa" > seeds/minimal_seed
```

For real projects, gather representative inputs:
- Download example files for the format you're fuzzing
- Extract test cases from the project's test suite
- Use minimal valid inputs for your file format

### Corpus Minimization

After a campaign, minimize the corpus to keep only unique coverage:

```bash
./afl++ <host/docker> afl-cmin -i out/default/queue -o minimized_corpus -- ./fuzz
```

> **See Also:** For corpus creation strategies, dictionaries, and seed selection,
> see the **fuzzing-corpus** technique skill.

## Running Campaigns

### Basic Run

```bash
./afl++ <host/docker> afl-fuzz -i seeds -o out -- ./fuzz
```

### Setting Environment Variables

```bash
./afl++ <host/docker> AFL_FAST_CAL=1 afl-fuzz -i seeds -o out -- ./fuzz
```

### Interpreting Output

The AFL++ UI shows real-time fuzzing statistics:

| Output | Meaning |
|--------|---------|
| **execs/sec** | Execution speed - higher is better |
| **cycles done** | Number of queue passes completed |
| **corpus count** | Number of unique test cases in queue |
| **saved crashes** | Number of unique crashes found |
| **stability** | % of stable edges (should be near 100%) |

### Output Directory Structure

```text
out/default/
├── cmdline          # How was the SUT invoked?
├── crashes/         # Inputs that crash the SUT
│   └── id:000000,sig:06,src:000002,time:286,execs:13105,op:havoc,rep:4
├── hangs/           # Inputs that hang the SUT
├── queue/           # Test cases reproducing final fuzzer state
│   ├── id:000000,time:0,execs:0,orig:minimal_seed
│   └── id:000001,src:000000,time:0,execs:8,op:havoc,rep:6,+cov
├── fuzzer_stats     # Campaign statistics
└── plot_data        # Data for plotting
```

### Analyzing Results

View live campaign statistics:

```bash
./afl++ <host/docker> afl-whatsup out
```

Create coverage plots:

```bash
apt install gnuplot
./afl++ <host/docker> afl-plot out/default out_graph/
```

### Re-executing Test Cases

```bash
./afl++ <host/docker> ./fuzz out/default/crashes/<test_case>
```

### Fuzzer Options

| Option | Purpose |
|--------|---------|
| `-G 4000` | Maximum test input length (default: 1048576 bytes) |
| `-t 1000` | Timeout in milliseconds for each test case (default: 1000ms) |
| `-m 1000` | Memory limit in megabytes (default: 0 = unlimited) |
| `-x ./dict.dict` | Use dictionary file to guide mutations |

## Environment Variables That Matter

AFL++ has [many environment variables](https://aflplus.plus/docs/env_variables/), but most are niche. These are the ones that matter in practice.

### Always Set These

```bash
# Every campaign should use tmpfs — SSDs will thank you, and it's faster
AFL_TMPDIR=/dev/shm
```

`AFL_TMPDIR` is a free performance win with no downsides — not setting it wears out your SSD and slows fuzzing.

### Slow Targets

```bash
# Speeds up calibration ~2.5x — use when targets are slow (e.g., >10 ms/exec)
AFL_FAST_CAL=1
```

`AFL_FAST_CAL` reduces calibration time with negligible precision loss. Recommended specifically for slow targets where calibration would otherwise take a long time.

### Multi-Core Campaigns

```bash
# On the primary (-M) instance only — needed for afl-cmin, not for fuzzing itself
AFL_FINAL_SYNC=1

# On all instances — cache test cases in memory (default: 50 MB, good range: 50-250 MB)
AFL_TESTCACHE_SIZE=100
```

`AFL_FINAL_SYNC` tells the primary instance to do a final import from all secondaries when stopping. This does not affect the fuzzing process itself — it only matters when you later run `afl-cmin` for corpus minimization, ensuring the primary's queue has the full combined corpus. `AFL_TESTCACHE_SIZE` caches test cases in memory to reduce disk I/O; the default is 50 MB and values between 50-250 MB work well for most campaigns.

### CI/Automated Fuzzing

```bash
# Fail fast if fuzzing isn't finding anything
AFL_EXIT_ON_TIME=3600  # 1 hour with no new paths = stop

# Or run until "done" (all queue entries processed)
AFL_EXIT_WHEN_DONE=1

# Headless environments
AFL_NO_UI=1
```

Unbounded fuzzing in CI wastes resources. Set time limits or use exit conditions.

### Variables to Avoid

| Variable | Why Skip It |
|----------|-------------|
| `AFL_NO_ARITH` | Can hurt coverage on binary formats, but may be useful for text-based targets |
| `AFL_SHUFFLE_QUEUE` | Only for exotic setups, usually harmful |
| `AFL_DISABLE_TRIM` | Trimming is valuable, don't disable without reason |


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Multi-Core Fuzzing](references/extended-guidance.md#multi-core-fuzzing)
- [Coverage Analysis](references/extended-guidance.md#coverage-analysis)
- [CMPLOG](references/extended-guidance.md#cmplog)
- [Sanitizer Integration](references/extended-guidance.md#sanitizer-integration)
- [Advanced Usage](references/extended-guidance.md#advanced-usage)
- [Troubleshooting](references/extended-guidance.md#troubleshooting)
- [Related Skills](references/extended-guidance.md#related-skills)
- [Resources](references/extended-guidance.md#resources)

