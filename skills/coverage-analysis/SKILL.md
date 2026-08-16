---
name: coverage-analysis
metadata:
  type: technique
description: >
  Coverage analysis measures code exercised during fuzzing.
  Use when assessing harness effectiveness or identifying fuzzing blockers.
---

# Coverage Analysis

Coverage analysis is essential for understanding which parts of your code are exercised during fuzzing. It helps identify fuzzing blockers like magic value checks and tracks the effectiveness of harness improvements over time.

## Overview

Code coverage during fuzzing serves two critical purposes:

1. **Assessing harness effectiveness**: Understand which parts of your application are actually executed by your fuzzing harnesses
2. **Tracking fuzzing progress**: Monitor how coverage changes when updating harnesses, fuzzers, or the system under test (SUT)

Coverage is a proxy for fuzzer capability and performance. While coverage [is not ideal for measuring fuzzer performance](https://arxiv.org/abs/1808.09700) in absolute terms, it reliably indicates whether your harness works effectively in a given setup.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Coverage instrumentation** | Compiler flags that track which code paths are executed |
| **Corpus coverage** | Coverage achieved by running all test cases in a fuzzing corpus |
| **Magic value checks** | Hard-to-discover conditional checks that block fuzzer progress |
| **Coverage-guided fuzzing** | Fuzzing strategy that prioritizes inputs that discover new code paths |
| **Coverage report** | Visual or textual representation of executed vs. unexecuted code |

## When to Apply

**Apply this technique when:**
- Starting a new fuzzing campaign to establish a baseline
- Fuzzer appears to plateau without finding new paths
- After harness modifications to verify improvements
- When migrating between different fuzzers
- Identifying areas requiring dictionary entries or seed inputs
- Debugging why certain code paths aren't reached

**Skip this technique when:**
- Fuzzing campaign is actively finding crashes
- Coverage infrastructure isn't set up yet
- Working with extremely large codebases where full coverage reports are impractical
- Fuzzer's internal coverage metrics are sufficient for your needs

## Quick Reference

| Task | Command/Pattern |
|------|-----------------|
| LLVM coverage instrumentation (C/C++) | `-fprofile-instr-generate -fcoverage-mapping` |
| GCC coverage instrumentation | `-ftest-coverage -fprofile-arcs` |
| cargo-fuzz coverage (Rust) | `cargo +nightly fuzz coverage <target>` |
| Generate LLVM profile data | `llvm-profdata merge -sparse file.profraw -o file.profdata` |
| LLVM coverage report | `llvm-cov report ./binary -instr-profile=file.profdata` |
| LLVM HTML report | `llvm-cov show ./binary -instr-profile=file.profdata -format=html -output-dir html/` |
| gcovr HTML report | `gcovr --html-details -o coverage.html` |

## Ideal Coverage Workflow

The following workflow represents best practices for integrating coverage analysis into your fuzzing campaigns:

```
[Fuzzing Campaign]
       |
       v
[Generate Corpus]
       |
       v
[Coverage Analysis]
       |
       +---> Coverage Increased? --> Continue fuzzing with larger corpus
       |
       +---> Coverage Decreased? --> Fix harness or investigate SUT changes
       |
       +---> Coverage Plateaued? --> Add dictionary entries or seed inputs
```

**Key principle**: Use the corpus generated *after* each fuzzing campaign to calculate coverage, rather than real-time fuzzer statistics. This approach provides reproducible, comparable measurements across different fuzzing tools.

## Step-by-Step

### Step 1: Build with Coverage Instrumentation

Choose your instrumentation method based on toolchain:

**LLVM/Clang (C/C++):**
```bash
clang++ -fprofile-instr-generate -fcoverage-mapping \
  -O2 -DNO_MAIN \
  main.cc harness.cc execute-rt.cc -o fuzz_exec
```

**GCC (C/C++):**
```bash
g++ -ftest-coverage -fprofile-arcs \
  -O2 -DNO_MAIN \
  main.cc harness.cc execute-rt.cc -o fuzz_exec_gcov
```

**Rust:**
```bash
rustup toolchain install nightly --component llvm-tools-preview
cargo +nightly fuzz coverage fuzz_target_1
```

### Step 2: Create Execution Runtime (C/C++ only)

For C/C++ projects, create a runtime that executes your corpus:

```cpp
// execute-rt.cc
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <stdint.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size);

void load_file_and_test(const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (file == NULL) {
        printf("Failed to open file: %s\n", filename);
        return;
    }

    fseek(file, 0, SEEK_END);
    long filesize = ftell(file);
    rewind(file);

    uint8_t *buffer = (uint8_t*) malloc(filesize);
    if (buffer == NULL) {
        printf("Failed to allocate memory for file: %s\n", filename);
        fclose(file);
        return;
    }

    long read_size = (long) fread(buffer, 1, filesize, file);
    if (read_size != filesize) {
        printf("Failed to read file: %s\n", filename);
        free(buffer);
        fclose(file);
        return;
    }

    LLVMFuzzerTestOneInput(buffer, filesize);

    free(buffer);
    fclose(file);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        printf("Usage: %s <directory>\n", argv[0]);
        return 1;
    }

    DIR *dir = opendir(argv[1]);
    if (dir == NULL) {
        printf("Failed to open directory: %s\n", argv[1]);
        return 1;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) {
            char filepath[1024];
            snprintf(filepath, sizeof(filepath), "%s/%s", argv[1], entry->d_name);
            load_file_and_test(filepath);
        }
    }

    closedir(dir);
    return 0;
}
```

### Step 3: Execute on Corpus

**LLVM (C/C++):**
```bash
LLVM_PROFILE_FILE=fuzz.profraw ./fuzz_exec corpus/
```

**GCC (C/C++):**
```bash
./fuzz_exec_gcov corpus/
```

**Rust:**
Coverage data is automatically generated when running `cargo fuzz coverage`.

### Step 4: Process Coverage Data

**LLVM:**
```bash
# Merge raw profile data
llvm-profdata merge -sparse fuzz.profraw -o fuzz.profdata

# Generate text report
llvm-cov report ./fuzz_exec \
  -instr-profile=fuzz.profdata \
  -ignore-filename-regex='harness.cc|execute-rt.cc'

# Generate HTML report
llvm-cov show ./fuzz_exec \
  -instr-profile=fuzz.profdata \
  -ignore-filename-regex='harness.cc|execute-rt.cc' \
  -format=html -output-dir fuzz_html/
```

**GCC with gcovr:**
```bash
# Install gcovr (via pip for latest version)
python3 -m venv venv
source venv/bin/activate
pip3 install gcovr

# Generate report
gcovr --gcov-executable "llvm-cov gcov" \
  --exclude harness.cc --exclude execute-rt.cc \
  --root . --html-details -o coverage.html
```

**Rust:**
```bash
# Install required tools
cargo install cargo-binutils rustfilt

# Create HTML generation script
cat <<'EOF' > ./generate_html
#!/bin/sh
if [ $# -lt 1 ]; then
    echo "Error: Name of fuzz target is required."
    echo "Usage: $0 fuzz_target [sources...]"
    exit 1
fi
FUZZ_TARGET="$1"
shift
SRC_FILTER="$@"
TARGET=$(rustc -vV | sed -n 's|host: ||p')
cargo +nightly cov -- show -Xdemangler=rustfilt \
  "target/$TARGET/coverage/$TARGET/release/$FUZZ_TARGET" \
  -instr-profile="fuzz/coverage/$FUZZ_TARGET/coverage.profdata" \
  -show-line-counts-or-regions -show-instantiations \
  -format=html -o fuzz_html/ $SRC_FILTER
EOF
chmod +x ./generate_html

# Generate HTML report
./generate_html fuzz_target_1 src/lib.rs
```

### Step 5: Analyze Results

Review the coverage report to identify:

- **Uncovered code blocks**: Areas that may need better seed inputs or dictionary entries
- **Magic value checks**: Conditional statements with hardcoded values that block progress
- **Dead code**: Functions that may not be reachable through your harness
- **Coverage changes**: Compare against baseline to track improvements or regressions

## Common Patterns

### Pattern: Identifying Magic Values

**Problem**: Fuzzer cannot discover paths guarded by magic value checks.

**Coverage reveals:**
```cpp
// Coverage shows this block is never executed
if (buf == 0x7F454C46) {  // ELF magic number
    // start parsing buf
}
```

**Solution**: Add magic values to dictionary file:
```
# magic.dict
"\x7F\x45\x4C\x46"
```

### Pattern: Handling Crashing Inputs

**Problem**: Coverage generation fails when corpus contains crashing inputs.

**Before:**
```bash
./fuzz_exec corpus/  # Crashes on bad input, no coverage generated
```

**After:**
```cpp
// Fork before executing to isolate crashes
int main(int argc, char **argv) {
    // ... directory opening code ...

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) {
            pid_t pid = fork();
            if (pid == 0) {
                // Child process - crash won't affect parent
                char filepath[1024];
                snprintf(filepath, sizeof(filepath), "%s/%s", argv[1], entry->d_name);
                load_file_and_test(filepath);
                exit(0);
            } else {
                // Parent waits for child
                waitpid(pid, NULL, 0);
            }
        }
    }
}
```

### Pattern: CMake Integration

**Use Case**: Adding coverage builds to CMake projects.

```cmake
project(FuzzingProject)
cmake_minimum_required(VERSION 3.0)

# Main binary
add_executable(program main.cc)

# Fuzzing binary
add_executable(fuzz main.cc harness.cc)
target_compile_definitions(fuzz PRIVATE NO_MAIN=1)
target_compile_options(fuzz PRIVATE -g -O2 -fsanitize=fuzzer)
target_link_libraries(fuzz -fsanitize=fuzzer)

# Coverage execution binary
add_executable(fuzz_exec main.cc harness.cc execute-rt.cc)
target_compile_definitions(fuzz_exec PRIVATE NO_MAIN)
target_compile_options(fuzz_exec PRIVATE -O2 -fprofile-instr-generate -fcoverage-mapping)
target_link_libraries(fuzz_exec -fprofile-instr-generate)
```

Build:
```bash
cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ .
cmake --build . --target fuzz_exec
```


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Advanced Usage](references/extended-guidance.md#advanced-usage)
- [Anti-Patterns](references/extended-guidance.md#anti-patterns)
- [Tool-Specific Guidance](references/extended-guidance.md#tool-specific-guidance)
- [Troubleshooting](references/extended-guidance.md#troubleshooting)
- [Related Skills](references/extended-guidance.md#related-skills)
- [Resources](references/extended-guidance.md#resources)

