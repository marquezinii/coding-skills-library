<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Sanitizer Integration

### AddressSanitizer (ASan)

AddressSanitizer is automatically integrated when using the provided Docker environment or when compiling with appropriate flags.

For local setup:
```bash
export CFLAGS="-fsanitize=address,fuzzer-no-link"
export CXXFLAGS="-fsanitize=address,fuzzer-no-link"
```

Configure ASan behavior:
```bash
export ASAN_OPTIONS="allocator_may_return_null=1,detect_leaks=0"
```

### LD_PRELOAD Configuration

For native extension fuzzing:
```bash
export LD_PRELOAD="$(python -c 'import atheris; import os; print(os.path.join(os.path.dirname(atheris.__file__), "asan_with_fuzzer.so"))')"
```

> **See Also:** For detailed sanitizer configuration, common issues, and advanced flags,
> see the **address-sanitizer** and **undefined-behavior-sanitizer** technique skills.

### Common Sanitizer Issues

| Issue | Solution |
|-------|----------|
| `LD_PRELOAD` not set | Export `LD_PRELOAD` to point to `asan_with_fuzzer.so` |
| Memory allocation failures | Set `ASAN_OPTIONS=allocator_may_return_null=1` |
| Leak detection noise | Set `ASAN_OPTIONS=detect_leaks=0` |
| Missing symbolizer | Set `ASAN_SYMBOLIZER_PATH` to `llvm-symbolizer` |

## Advanced Usage

### Tips and Tricks

| Tip | Why It Helps |
|-----|--------------|
| Use `atheris.instrument_imports()` early | Ensures all imports are instrumented for coverage |
| Start with small `max_len` | Faster initial fuzzing, gradually increase |
| Use dictionaries for structured formats | Helps fuzzer understand format tokens |
| Run multiple parallel instances | Better coverage exploration |

### Custom Instrumentation

Fine-tune what gets instrumented:
```python
import atheris

# Instrument only specific modules
with atheris.instrument_imports():
    import target_module
# Don't instrument test harness code

def test_one_input(data: bytes):
    target_module.parse(data)
```

### Performance Tuning

| Setting | Impact |
|---------|--------|
| `-max_len=N` | Smaller values = faster execution |
| `-workers=N -jobs=N` | Parallel fuzzing for faster coverage |
| `ASAN_OPTIONS=fast_unwind_on_malloc=0` | Better stack traces, slower execution |

### UndefinedBehaviorSanitizer (UBSan)

Add UBSan to catch additional bugs:
```bash
export CFLAGS="-fsanitize=address,undefined,fuzzer-no-link"
export CXXFLAGS="-fsanitize=address,undefined,fuzzer-no-link"
```

Note: Modify flags in Dockerfile if using containerized setup.

## Real-World Examples

### Example: Pure Python Parser

```python
import sys
import atheris
import json

@atheris.instrument_func
def test_one_input(data: bytes):
    try:
        # Fuzz Python's JSON parser
        json.loads(data.decode('utf-8', errors='ignore'))
    except (ValueError, UnicodeDecodeError):
        pass

def main():
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
```

### Example: HTTP Request Parsing

```python
import sys
import atheris

with atheris.instrument_imports():
    from urllib3 import HTTPResponse
    from io import BytesIO

def test_one_input(data: bytes):
    try:
        # Fuzz HTTP response parsing
        fake_response = HTTPResponse(
            body=BytesIO(data),
            headers={},
            preload_content=False
        )
        fake_response.read()
    except Exception:
        pass

def main():
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| No coverage increase | Poor seed corpus or target not instrumented | Add better seeds, verify `instrument_imports()` |
| Slow execution | ASan overhead or large inputs | Reduce `max_len`, use `ASAN_OPTIONS=fast_unwind_on_malloc=1` |
| Import errors | Modules imported before instrumentation | Move imports inside `instrument_imports()` context |
| Segfault without ASan output | Missing `LD_PRELOAD` | Set `LD_PRELOAD` to `asan_with_fuzzer.so` path |
| Build failures | Wrong compiler or missing flags | Verify `CC`, `CFLAGS`, and clang version |

## Related Skills

### Technique Skills

| Skill | Use Case |
|-------|----------|
| **fuzz-harness-writing** | Detailed guidance on writing effective harnesses |
| **address-sanitizer** | Memory error detection during fuzzing |
| **undefined-behavior-sanitizer** | Catching undefined behavior in C extensions |
| **coverage-analysis** | Measuring and improving code coverage |
| **fuzzing-corpus** | Building and managing seed corpora |

### Related Fuzzers

| Skill | When to Consider |
|-------|------------------|
| **hypothesis** | Property-based testing with type-aware generation |
| **python-afl** | AFL-style fuzzing for Python when Atheris isn't available |

## Resources

### Key External Resources

**[Atheris GitHub Repository](https://github.com/google/atheris)**
Official repository with installation instructions, examples, and documentation for fuzzing both pure Python and native extensions.

**[Native Extension Fuzzing Guide](https://github.com/google/atheris/blob/master/native_extension_fuzzing.md)**
Comprehensive guide covering compilation flags, LD_PRELOAD setup, sanitizer configuration, and troubleshooting for Python C extensions.

**[Continuously Fuzzing Python C Extensions](https://blog.trailofbits.com/2024/02/23/continuously-fuzzing-python-c-extensions/)**
Trail of Bits blog post covering CI/CD integration, ClusterFuzzLite setup, and real-world examples of fuzzing Python C extensions in continuous integration pipelines.

**[ClusterFuzzLite Python Integration](https://google.github.io/clusterfuzzlite/build-integration/python-lang/)**
Guide for integrating Atheris fuzzing into CI/CD pipelines using ClusterFuzzLite for automated continuous fuzzing.

### Video Resources

Videos and tutorials are available in the main Atheris documentation and libFuzzer resources.
