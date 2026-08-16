---
name: batch-files
description: 'Expert-level Windows batch file (.bat/.cmd) skill for writing, debugging, and maintaining CMD scripts. Use when asked to "create a batch file", "write a .bat script", "automate a Windows task", "CMD scripting", "batch automation", "scheduled task script", "Windows shell script", or when working with .bat/.cmd files in the workspace. Covers cmd.exe syntax, environment variables, control flow, string processing, error handling, and integration with system tools.'
---

# Batch Files

A comprehensive skill for creating, editing, debugging, and maintaining Windows batch files (.bat/.cmd) using cmd.exe. Applies to CLI tool development, system administration automation, scheduled tasks, file operations scripting, and PATH-based executable scripts.

## When to Use This Skill

- Creating or editing `.bat` or `.cmd` files
- Automating Windows tasks (file operations, deployments, backups)
- Building CLI tools intended for a `bin/` folder on PATH
- Writing scheduled task scripts (SCHTASKS, Task Scheduler)
- Debugging batch script issues (variable expansion, error levels, quoting)
- Integrating batch scripts with external tools (curl, git, Node.js, Python)
- Scaffolding new batch-based projects with structured templates

## Prerequisites

- Windows NT-based OS (Windows 7 or later)
- cmd.exe (built-in)
- Optional: a `bin/` directory on PATH for distributing scripts as commands
- Optional: PATHEXT configured to include `.BAT;.CMD` (default on Windows)

## Command Interpretation

cmd.exe processes each line through four stages in order:

1. **Variable substitution** — `%VAR%` tokens are replaced with environment variable values. `%0`–`%9` reference batch arguments. `%*` expands to all arguments.
2. **Quoting and escaping** — Caret `^` escapes special characters (`& | < > ^`). Quotation marks prevent interpretation of enclosed special characters. In batch files, `%%` yields a literal `%`.
3. **Syntax parsing** — Lines are split into pipelines (`|`), compound commands (`&`, `&&`, `||`), and parenthesized groups `( )`.
4. **Redirection** — `>` overwrites, `>>` appends, `<` reads input, `2>` redirects stderr, `2>&1` merges stderr into stdout, `>NUL` discards output.

## Variables

### Environment Variables

```bat
set _MY_VAR=Hello World
echo %_MY_VAR%
set _MY_VAR=
```

- `set` with no arguments lists all variables
- `set _PREFIX` lists variables starting with `_PREFIX`
- No spaces around `=` — `set name = val` sets variable `"name "` to `" val"`

### Special Variables

| Variable | Value |
|----------|-------|
| `%CD%` | Current directory |
| `%DATE%` | System date (locale-dependent) |
| `%TIME%` | System time HH:MM:SS.mm |
| `%RANDOM%` | Pseudorandom number 0–32767 |
| `%ERRORLEVEL%` | Exit code of last command |
| `%USERNAME%` | Current user name |
| `%USERPROFILE%` | Current user profile path |
| `%TEMP%` / `%TMP%` | Temporary file directory |
| `%PATHEXT%` | Executable extensions list |
| `%COMSPEC%` | Path to cmd.exe |

### Scoping with SETLOCAL / ENDLOCAL

```bat
setlocal
set _LOCAL_VAR=scoped value
endlocal
REM _LOCAL_VAR is no longer defined here
```

To return a value from a scoped block:

```bat
endlocal & set _RESULT=%_LOCAL_VAR%
```

### Delayed Expansion

Variables inside parenthesized blocks are expanded at parse time. Use delayed expansion for runtime evaluation:

```bat
setlocal EnableDelayedExpansion
set _COUNT=0
for /l %%i in (1,1,5) do (
    set /a _COUNT+=1
    echo !_COUNT!
)
endlocal
```

- `!VAR!` expands at execution time (delayed)
- `%VAR%` expands at parse time (immediate)

## Control Flow

### Conditional Execution

```bat
if exist "output.txt" echo File found
if not defined _MY_VAR echo Variable not set
if "%_STATUS%"=="ready" (echo Go) else (echo Wait)
if %ERRORLEVEL% neq 0 echo Command failed
```

Comparison operators: `equ`, `neq`, `lss`, `leq`, `gtr`, `geq`. Use `/i` for case-insensitive string comparison.

### Compound Commands

```bat
command1 & command2        & REM Always run both
command1 && command2       & REM Run command2 only if command1 succeeds
command1 || command2       & REM Run command2 only if command1 fails
```

### FOR Loops

```bat
REM Iterate over a set of values
for %%i in (alpha beta gamma) do echo %%i

REM Numeric range: start, step, end
for /l %%i in (1,1,10) do echo %%i

REM Files in a directory
for %%f in (*.txt) do echo %%f

REM Recursive file search
for /r %%f in (*.log) do echo %%f

REM Directories only
for /d %%d in (*) do echo %%d

REM Parse command output
for /f "tokens=1,2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do echo %%b

REM Parse file lines
for /f "usebackq tokens=*" %%a in ("data.txt") do echo %%a
```

### GOTO and Labels

```bat
goto :main_logic
:usage
echo Usage: %~nx0 [options]
exit /b 1

:main_logic
echo Running main logic...
goto :eof
```

`goto :eof` exits the current batch or subroutine. Labels start with `:`.

## Command-Line Arguments

| Syntax | Value |
|--------|-------|
| `%0` | Script name as invoked |
| `%1`–`%9` | Positional arguments |
| `%*` | All arguments (unaffected by SHIFT) |
| `%~1` | Argument 1 with enclosing quotes removed |
| `%~f1` | Full path of argument 1 |
| `%~d1` | Drive letter of argument 1 |
| `%~p1` | Path (without drive) of argument 1 |
| `%~n1` | File name (no extension) of argument 1 |
| `%~x1` | Extension of argument 1 |
| `%~dp0` | Drive and path of the batch file itself |
| `%~nx0` | File name with extension of the batch file |
| `%~z1` | File size of argument 1 |
| `%~$PATH:1` | Search PATH for argument 1 |

### Argument Parsing Pattern

```bat
:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="--help" goto :usage
if /i "%~1"=="--output" (
    set "_OUTPUT_DIR=%~2"
    shift
)
shift
goto :parse_args
:args_done
```

## String Processing

### Substrings

```bat
set _STR=Hello World
echo %_STR:~0,5%       & REM "Hello"
echo %_STR:~6%         & REM "World"
echo %_STR:~-5%        & REM "World"
echo %_STR:~0,-6%      & REM "Hello"
```

### Search and Replace

```bat
set _STR=Hello World
echo %_STR:World=Earth%       & REM "Hello Earth"
echo %_STR:Hello=%            & REM " World" (remove "Hello")
```

### Substring Containment Test

```bat
if not "%_STR:World=%"=="%_STR%" echo Contains "World"
```

## Functions

Functions use labels, CALL, and SETLOCAL/ENDLOCAL:

```bat
@echo off
call :greet "Jane Doe"
echo Result: %_GREETING%
exit /b 0

:greet
setlocal
set "_MSG=Hello, %~1"
endlocal & set "_GREETING=%_MSG%"
exit /b 0
```

- `call :label args` invokes a function
- `exit /b` returns from the function (not the script)
- Use the `endlocal & set` trick to pass values out of a scoped block

## Arithmetic

`set /a` performs 32-bit signed integer arithmetic:

```bat
set /a _RESULT=10 * 5 + 3
set /a _COUNTER+=1
set /a _REMAINDER=14 %% 3       & REM Use %% for modulo in batch files
set /a _BITS="255 & 0x0F"       & REM Bitwise AND
```

Supported operators: `+ - * / %% ( )` and bitwise `& | ^ ~ << >>`.

Hexadecimal (`0xFF`) and octal (`077`) literals are supported.

## Error Handling

### Error Level Conventions

- `0` = success
- Non-zero = failure (typically `1`)

```bat
mycommand.exe
if %ERRORLEVEL% neq 0 (
    echo ERROR: mycommand failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
```

### Fail-Fast Pattern

```bat
command1 || (echo command1 failed & exit /b 1)
command2 || (echo command2 failed & exit /b 1)
```

### Setting Exit Codes

```bat
exit /b 0        & REM Return success from a batch/function
exit /b 1        & REM Return failure
cmd /c "exit /b 42"   & REM Set ERRORLEVEL to 42 inline
```

## Essential Commands Reference

### File Operations

| Command | Purpose |
|---------|---------|
| `DIR` | List directory contents |
| `COPY` | Copy files |
| `XCOPY` | Extended copy with subdirectories (legacy) |
| `ROBOCOPY` | Robust copy with retry, mirror, logging |
| `MOVE` | Move or rename files |
| `DEL` | Delete files |
| `REN` | Rename files |
| `MD` / `MKDIR` | Create directories |
| `RD` / `RMDIR` | Remove directories |
| `MKLINK` | Create symbolic or hard links |
| `ATTRIB` | View or set file attributes |
| `TYPE` | Print file contents |
| `MORE` | Paginated file display |
| `TREE` | Display directory structure |
| `REPLACE` | Replace files in destination with source |
| `COMPACT` | Show or set NTFS compression |
| `EXPAND` | Extract from .cab files |
| `MAKECAB` | Create .cab archives |
| `TAR` | Create or extract tar archives |

### Text Search and Processing

| Command | Purpose |
|---------|---------|
| `FIND` | Search for literal strings |
| `FINDSTR` | Search with limited regular expressions |
| `SORT` | Sort lines alphabetically |
| `CLIP` | Copy piped input to clipboard |
| `FC` | Compare two files |
| `COMP` | Binary file comparison |
| `CERTUTIL` | Encode/decode Base64, compute hashes |

### System Information

| Command | Purpose |
|---------|---------|
| `SYSTEMINFO` | Full system configuration |
| `HOSTNAME` | Display computer name |
| `VER` | Windows version |
| `WHOAMI` | Current user and group info |
| `TASKLIST` | List running processes |
| `TASKKILL` | Terminate processes |
| `WMIC` | WMI queries (drives, OS, memory) |
| `SC` | Service control (query, start, stop) |
| `DRIVERQUERY` | List installed drivers |
| `REG` | Registry operations (query, add, delete) |
| `SETX` | Set persistent environment variables |

### Network

| Command | Purpose |
|---------|---------|
| `PING` | Test network connectivity |
| `IPCONFIG` | IP configuration |
| `NSLOOKUP` | DNS lookup |
| `NETSTAT` | Network connections and ports |
| `TRACERT` | Trace route to host |
| `NET USE` | Map/disconnect network drives |
| `NET USER` | Manage user accounts |
| `NETSH` | Network configuration utility |
| `ARP` | ARP cache management |
| `ROUTE` | Routing table management |
| `CURL` | HTTP requests (Windows 10+) |
| `SSH` | Secure shell (Windows 10+) |

### Scheduling and Automation

| Command | Purpose |
|---------|---------|
| `SCHTASKS` | Create and manage scheduled tasks |
| `TIMEOUT` | Wait N seconds (Vista+) |
| `START` | Launch programs asynchronously |
| `RUNAS` | Run as different user |
| `SHUTDOWN` | Shutdown or restart |
| `FORFILES` | Find files by date and execute commands |

### Shell Utilities

| Command | Purpose |
|---------|---------|
| `WHERE` | Locate executables in PATH |
| `DOSKEY` | Create command macros |
| `CHOICE` | Prompt for single-key input |
| `MODE` | Configure console size and ports |
| `SUBST` | Map folder to drive letter |
| `CHCP` | Get or set console code page |
| `COLOR` | Set console colors |
| `TITLE` | Set console window title |
| `ASSOC` / `FTYPE` | File type associations |


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Shell Syntax and Expressions](references/extended-guidance.md#shell-syntax-and-expressions)
- [Writing Production-Quality Batch Files](references/extended-guidance.md#writing-production-quality-batch-files)
- [Debugging and Troubleshooting](references/extended-guidance.md#debugging-and-troubleshooting)
- [Cross-Platform and Extended Tools](references/extended-guidance.md#cross-platform-and-extended-tools)
- [CMD Keyboard Shortcuts](references/extended-guidance.md#cmd-keyboard-shortcuts)
- [Reference Files](references/extended-guidance.md#reference-files)
- [Asset Templates](references/extended-guidance.md#asset-templates)

