<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

## Shell Syntax and Expressions

### Parentheses for Grouping

Parentheses turn compound commands into a single unit for redirection or conditional execution:

```bat
(echo Line 1 & echo Line 2) > output.txt
if exist "data.csv" (
    echo Processing...
    call :process "data.csv"
) else (
    echo No data found.
)
```

### Escape Characters

The caret `^` escapes the next character:

```bat
echo Total ^& Summary          & REM Outputs: Total & Summary
echo 100%% complete            & REM Outputs: 100% complete (in batch)
echo Line one^
Line two                       & REM Caret escapes the newline
```

After a pipe, triple caret is needed: `echo x ^^^& y | findstr x`

### Wildcards

- `*` matches any sequence of characters
- `?` matches a single character (or zero at end of period-free segment)

```bat
dir *.txt           & REM All .txt files
ren *.jpeg *.jpg    & REM Bulk rename
```

### Redirection Summary

```bat
command > file.txt          & REM Overwrite stdout to file
command >> file.txt         & REM Append stdout to file
command 2> errors.log       & REM Redirect stderr
command > all.log 2>&1      & REM Merge stderr into stdout
command < input.txt         & REM Read stdin from file
command > NUL 2>&1          & REM Discard all output
```

## Writing Production-Quality Batch Files

### Standard Script Structure

```bat
@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  Script: example.bat
REM  Purpose: Describe what this script does
REM ============================================================

call :main %*
exit /b %ERRORLEVEL%

:main
    call :parse_args %*
    if not defined _TARGET (
        echo ERROR: --target is required. 1>&2
        call :usage
        exit /b 1
    )
    echo Processing: %_TARGET%
    exit /b 0

:parse_args
    if "%~1"=="" exit /b 0
    if /i "%~1"=="--target" set "_TARGET=%~2" & shift
    if /i "%~1"=="--help"   call :usage & exit /b 0
    shift
    goto :parse_args

:usage
    echo Usage: %~nx0 --target ^<path^> [--help]
    echo.
    echo Options:
    echo   --target   Path to process (required)
    echo   --help     Show this help message
    exit /b 0
```

### Best Practices

1. **Always start with `@echo off` and `setlocal`** — Prevents noisy output and variable leakage to the caller.
2. **Validate inputs before processing** — Check required arguments and file existence early. Use `if not defined` and `if not exist`.
3. **Quote paths and variables** — Use `"%~1"` and `"%_MY_PATH%"` to handle spaces and special characters safely.
4. **Use `exit /b` instead of `exit`** — Avoids closing the parent console window.
5. **Return meaningful exit codes** — `exit /b 0` for success, non-zero for specific failures.
6. **Use `%~dp0` for script-relative paths** — Ensures the script works regardless of the caller's working directory.
7. **Prefer `ROBOCOPY` over `XCOPY`** — More reliable, supports retry, mirroring, and logging.
8. **Use `EnableDelayedExpansion` when modifying variables inside loops or parenthesized blocks.**
9. **Write errors to stderr** — `echo ERROR: message 1>&2` keeps stdout clean for piping.
10. **Use `REM` for comments** — `::` can cause issues inside `FOR` loop bodies.

### Security Considerations

- **Never store credentials in batch files** — Use environment variables, credential stores, or prompts.
- **Validate user input** — Unquoted variables containing `&`, `|`, or `>` can inject commands. Always quote: `"%_USER_INPUT%"`.
- **Use `SETLOCAL`** — Prevents variable values from leaking to parent processes.
- **Sanitize file paths** — Validate paths before passing to `DEL`, `RD`, or `ROBOCOPY` to prevent unintended deletion.
- **Avoid `SET /P` for sensitive input** — Input is visible and stored in console history. Use a dedicated credential tool when possible.

## Debugging and Troubleshooting

| Technique | How |
|-----------|-----|
| Trace execution | Remove `@echo off` or use `@echo on` temporarily |
| Step through | Add `PAUSE` between sections |
| Check error level | `echo Exit code: %ERRORLEVEL%` after each command |
| Inspect variables | `set _MY_` to list all variables starting with `_MY_` |
| Delayed expansion issues | Variable inside `( )` block not updating? Enable `!VAR!` syntax |
| FOR loop `%%` vs `%` | Use `%%i` in batch files, `%i` on the command line |
| Spaces in SET | `set name=value` not `set name = value` |
| Caret in pipes | After a pipe, use `^^^` to escape special chars |
| Parentheses in SET /A | Escape with `^(` and `^)` inside `if` blocks, or use quotes |
| Double percent for modulo | `set /a r=14 %% 3` in batch files |

## Cross-Platform and Extended Tools

When batch scripting reaches its limits, these tools extend cmd.exe capabilities:

| Tool | Purpose |
|------|---------|
| **Cygwin** | Full POSIX environment on Windows (grep, sed, awk, ssh) |
| **MSYS2** | Lightweight Unix tools and package manager (pacman) |
| **WSL** | Windows Subsystem for Linux — run native Linux binaries |
| **GnuWin32** | Individual GNU utilities as native Windows executables |
| **PowerShell** | Modern Windows scripting with .NET integration |

Use batch when you need: fast startup, simple file operations, PATH-based CLI tools, or Task Scheduler integration. Consider PowerShell or WSL for complex data processing, REST APIs, or object-oriented scripting.

## CMD Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Auto-complete file/folder names |
| `Up` / `Down` | Navigate command history |
| `F7` | Show command history popup |
| `F3` | Repeat last command |
| `Esc` | Clear current line |
| `Ctrl+C` | Cancel running command |
| `Alt+F7` | Clear command history |

## Reference Files

The `references/` folder contains detailed documentation:

| File | Contents |
|------|----------|
| `tools-and-resources.md` | Windows tools, utilities, package managers, terminals |
| `batch-files-and-functions.md` | Example scripts, techniques, best practices links |
| `windows-commands.md` | Comprehensive A-Z Windows command reference |
| `cygwin.md` | Cygwin user guide and FAQ |
| `msys2.md` | MSYS2 installation, packages, and environments |
| `windows-subsystem-on-linux.md` | WSL setup, commands, and documentation |

## Asset Templates

The `assets/` folder contains starter batch file template data, but as text files:

| Template | Purpose |
|----------|---------|
| `executable.txt` | Standalone CLI tool with argument parsing |
| `library.txt` | Reusable function library with CALL-able labels |
| `task.txt` | Scheduled task / automation script |
