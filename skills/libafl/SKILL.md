---
name: libafl
metadata:
  type: fuzzer
description: >
  LibAFL is a modular fuzzing library for building custom fuzzers. Use for
  advanced fuzzing needs, custom mutators, or non-standard fuzzing targets.
---

# LibAFL

LibAFL is a modular fuzzing library that implements features from AFL-based fuzzers like AFL++. Unlike traditional fuzzers, LibAFL provides all functionality in a modular and customizable way as a Rust library. It can be used as a drop-in replacement for libFuzzer or as a library to build custom fuzzers from scratch.

## When to Use

| Fuzzer | Best For | Complexity |
|--------|----------|------------|
| libFuzzer | Quick setup, single-threaded | Low |
| AFL++ | Multi-core, general purpose | Medium |
| LibAFL | Custom fuzzers, advanced features, research | High |

**Choose LibAFL when:**
- You need custom mutation strategies or feedback mechanisms
- Standard fuzzers don't support your target architecture
- You want to implement novel fuzzing techniques
- You need fine-grained control over fuzzing components
- You're conducting fuzzing research

## Quick Start

LibAFL can be used as a drop-in replacement for libFuzzer with minimal setup:

```c++
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // Call your code with fuzzer-provided data
    my_function(data, size);
    return 0;
}
```

Build LibAFL's libFuzzer compatibility layer:
```bash
git clone https://github.com/AFLplusplus/LibAFL
cd LibAFL/libafl_libfuzzer_runtime
./build.sh
```

Compile and run:
```bash
clang++ -DNO_MAIN -g -O2 -fsanitize=fuzzer-no-link libFuzzer.a harness.cc main.cc -o fuzz
./fuzz corpus/
```

## Installation

### Prerequisites

- Clang/LLVM 15-18
- Rust (via rustup)
- Additional system dependencies

### Linux/macOS

Install Clang:
```bash
apt install clang
```

Or install a specific version via apt.llvm.org:
```bash
wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh 15
```

Configure environment for Rust:
```bash
export RUSTFLAGS="-C linker=/usr/bin/clang-15"
export CC="clang-15"
export CXX="clang++-15"
```

Install Rust:
```bash
installer="$(mktemp)"
curl --proto '=https' --tlsv1.2 -fsSLo "$installer" https://sh.rustup.rs
# Review the script and verify its publisher-provided checksum before execution.
${PAGER:-less} "$installer"
sh "$installer"
rm -f "$installer"
```

Install additional dependencies:
```bash
apt install libssl-dev pkg-config
```

For libFuzzer compatibility mode, install nightly Rust:
```bash
rustup toolchain install nightly --component llvm-tools
```

### Verification

Build LibAFL to verify installation:
```bash
cd LibAFL/libafl_libfuzzer_runtime
./build.sh
# Should produce libFuzzer.a
```

## Writing a Harness

LibAFL harnesses follow the same pattern as libFuzzer when using drop-in replacement mode:

```c++
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // Your fuzzing target code here
    return 0;
}
```

When building custom fuzzers with LibAFL as a Rust library, harness logic is integrated directly into the fuzzer. See the "Writing a Custom Fuzzer" section below for the full pattern.

> **See Also:** For detailed harness writing techniques, see the **harness-writing** technique skill.

## Usage Modes

LibAFL supports two primary usage modes:

### 1. libFuzzer Drop-in Replacement

Use LibAFL as a replacement for libFuzzer with existing harnesses.

**Compilation:**
```bash
clang++ -DNO_MAIN -g -O2 -fsanitize=fuzzer-no-link libFuzzer.a harness.cc main.cc -o fuzz
```

**Running:**
```bash
./fuzz corpus/
```

**Recommended for long campaigns:**
```bash
./fuzz -fork=1 -ignore_crashes=1 corpus/
```

### 2. Custom Fuzzer as Rust Library

Build a fully customized fuzzer using LibAFL components.

**Create project:**
```bash
cargo init --lib my_fuzzer
cd my_fuzzer
cargo add libafl@0.13 libafl_targets@0.13 libafl_bolts@0.13 libafl_cc@0.13 \
  --features "libafl_targets@0.13/libfuzzer,libafl_targets@0.13/sancov_pcguard_hitcounts"
```

**Configure Cargo.toml:**
```toml
[lib]
crate-type = ["staticlib"]
```

## Writing a Custom Fuzzer

> **See Also:** For detailed harness writing techniques, patterns for handling complex inputs,
> and advanced strategies, see the **fuzz-harness-writing** technique skill.

### Fuzzer Components

A LibAFL fuzzer consists of modular components:

1. **Observers** - Collect execution feedback (coverage, timing)
2. **Feedback** - Determine if inputs are interesting
3. **Objective** - Define fuzzing goals (crashes, timeouts)
4. **State** - Maintain corpus and metadata
5. **Mutators** - Generate new inputs
6. **Scheduler** - Select which inputs to mutate
7. **Executor** - Run the target with inputs

### Basic Fuzzer Structure

```rust
use libafl::prelude::*;
use libafl_bolts::prelude::*;
use libafl_targets::{libfuzzer_test_one_input, std_edges_map_observer};

#[no_mangle]
pub extern "C" fn libafl_main() {
    let mut run_client = |state: Option<_>, mut restarting_mgr, _core_id| {
        // 1. Setup observers
        let edges_observer = HitcountsMapObserver::new(
            unsafe { std_edges_map_observer("edges") }
        ).track_indices();
        let time_observer = TimeObserver::new("time");

        // 2. Define feedback
        let mut feedback = feedback_or!(
            MaxMapFeedback::new(&edges_observer),
            TimeFeedback::new(&time_observer)
        );

        // 3. Define objective
        let mut objective = feedback_or_fast!(
            CrashFeedback::new(),
            TimeoutFeedback::new()
        );

        // 4. Create or restore state
        let mut state = state.unwrap_or_else(|| {
            StdState::new(
                StdRand::new(),
                InMemoryCorpus::new(),
                OnDiskCorpus::new(&output_dir).unwrap(),
                &mut feedback,
                &mut objective,
            ).unwrap()
        });

        // 5. Setup mutator
        let mutator = StdScheduledMutator::new(havoc_mutations());
        let mut stages = tuple_list!(StdMutationalStage::new(mutator));

        // 6. Setup scheduler
        let scheduler = IndexesLenTimeMinimizerScheduler::new(
            &edges_observer,
            QueueScheduler::new()
        );

        // 7. Create fuzzer
        let mut fuzzer = StdFuzzer::new(scheduler, feedback, objective);

        // 8. Define harness
        let mut harness = |input: &BytesInput| {
            let buf = input.target_bytes().as_slice();
            libfuzzer_test_one_input(buf);
            ExitKind::Ok
        };

        // 9. Setup executor
        let mut executor = InProcessExecutor::with_timeout(
            &mut harness,
            tuple_list!(edges_observer, time_observer),
            &mut fuzzer,
            &mut state,
            &mut restarting_mgr,
            timeout,
        )?;

        // 10. Load initial inputs
        if state.must_load_initial_inputs() {
            state.load_initial_inputs(
                &mut fuzzer,
                &mut executor,
                &mut restarting_mgr,
                &input_dir
            )?;
        }

        // 11. Start fuzzing
        fuzzer.fuzz_loop(&mut stages, &mut executor, &mut state, &mut restarting_mgr)?;
        Ok(())
    };

    // Launch fuzzer
    Launcher::builder()
        .run_client(&mut run_client)
        .cores(&cores)
        .build()
        .launch()
        .unwrap();
}
```

## Compilation

### Verbose Mode

Manually specify all instrumentation flags:

```bash
clang++-15 -DNO_MAIN -g -O2 \
  -fsanitize-coverage=trace-pc-guard \
  -fsanitize=address \
  -Wl,--whole-archive target/release/libmy_fuzzer.a -Wl,--no-whole-archive \
  main.cc harness.cc -o fuzz
```

### Compiler Wrapper (Recommended)

Create a LibAFL compiler wrapper to handle instrumentation automatically.

**Create `src/bin/libafl_cc.rs`:**
```rust
use libafl_cc::{ClangWrapper, CompilerWrapper, Configuration, ToolWrapper};

pub fn main() {
    let args: Vec<String> = env::args().collect();
    let mut cc = ClangWrapper::new();
    cc.cpp(is_cpp)
      .parse_args(&args)
      .link_staticlib(&dir, "my_fuzzer")
      .add_args(&Configuration::GenerateCoverageMap.to_flags().unwrap())
      .add_args(&Configuration::AddressSanitizer.to_flags().unwrap())
      .run()
      .unwrap();
}
```

**Compile and use:**
```bash
cargo build --release
target/release/libafl_cxx -DNO_MAIN -g -O2 main.cc harness.cc -o fuzz
```

> **See Also:** For detailed sanitizer configuration, common issues, and advanced flags,
> see the **address-sanitizer** and **undefined-behavior-sanitizer** technique skills.

## Running Campaigns

### Basic Run

```bash
./fuzz --cores 0 --input corpus/
```

### Multi-Core Fuzzing

```bash
./fuzz --cores 0,8-15 --input corpus/
```

This runs 9 clients: one on core 0, and 8 on cores 8-15.

### With Options

```bash
./fuzz --cores 0-7 --input corpus/ --output crashes/ --timeout 1000
```

### Text User Interface (TUI)

Enable graphical statistics view:

```bash
./fuzz -tui=1 corpus/
```

### Interpreting Output

| Output | Meaning |
|--------|---------|
| `corpus: N` | Number of interesting test cases found |
| `objectives: N` | Number of crashes/timeouts found |
| `executions: N` | Total number of target invocations |
| `exec/sec: N` | Current execution throughput |
| `edges: X%` | Code coverage percentage |
| `clients: N` | Number of parallel fuzzing processes |

The fuzzer emits two main event types:
- **UserStats** - Regular heartbeat with current statistics
- **Testcase** - New interesting input discovered


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Advanced Usage](references/extended-guidance.md#advanced-usage)
- [Real-World Examples](references/extended-guidance.md#real-world-examples)
- [Troubleshooting](references/extended-guidance.md#troubleshooting)
- [Related Skills](references/extended-guidance.md#related-skills)
- [Resources](references/extended-guidance.md#resources)

