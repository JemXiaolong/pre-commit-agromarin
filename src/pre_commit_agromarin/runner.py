"""Pipeline orchestrator for the AgroMarin lint tools."""

import sys
from pathlib import Path

from .fixers import ALL_FIXERS
from .tools import autoflake_tool, black_tool, flake8_tool, isort_tool, pyupgrade_tool

# Tools run in this order for auto-fix mode
FIX_PIPELINE = [
    ("autoflake", autoflake_tool),
    ("pyupgrade", pyupgrade_tool),
    ("isort", isort_tool),
    ("black", black_tool),
]

# Tools run in this order for check mode
CHECK_PIPELINE = [
    ("flake8", flake8_tool),
]

# All step names in order for the report
_ALL_STEPS = ["agromarin-fixers"] + [name for name, _ in FIX_PIPELINE]


def _read_files(files):
    """Read file contents for modification detection."""
    contents = {}
    for f in files:
        path = Path(f)
        if path.exists():
            contents[f] = path.read_bytes()
    return contents


def _print_report(file_steps, py_files):
    """Print a coverage report showing what each step did to each file."""
    modified_count = 0
    unchanged_count = 0

    sys.stderr.write("\n\033[1m=== AgroMarin Fix Report ===\033[0m\n\n")

    for f in py_files:
        steps = file_steps.get(f, {})
        file_modified = any(steps.values())

        if file_modified:
            modified_count += 1
        else:
            unchanged_count += 1

        short_name = f
        sys.stderr.write(f"\033[1m  {short_name}\033[0m\n")

        for step in _ALL_STEPS:
            changed = steps.get(step, False)
            if changed:
                sys.stderr.write(f"    \033[33m*\033[0m {step:<20s} \033[33mmodified\033[0m\n")
            else:
                sys.stderr.write(f"    \033[32m-\033[0m {step:<20s} \033[32mno changes\033[0m\n")

        sys.stderr.write("\n")

    sys.stderr.write(
        f"\033[1mSummary:\033[0m "
        f"\033[33m{modified_count} modified\033[0m, "
        f"\033[32m{unchanged_count} unchanged\033[0m "
        f"({modified_count + unchanged_count} files total)\n\n"
    )


def run_fix(files):
    """Run auto-fix pipeline on files.

    Returns 1 if any file was modified, 0 otherwise.
    """
    if not files:
        return 0

    py_files = [f for f in files if f.endswith('.py')]
    if not py_files:
        return 0

    # Track changes per file per step: {filepath: {step: bool}}
    file_steps = {f: {} for f in py_files}

    before = _read_files(py_files)

    # 1. Run custom AgroMarin fixers
    for fixer in ALL_FIXERS:
        for filepath in py_files:
            fixer(filepath)

    snapshot = _read_files(py_files)
    for f in py_files:
        file_steps[f]["agromarin-fixers"] = before.get(f) != snapshot.get(f)

    # 2. Run third-party auto-fix tools (track each step)
    for name, tool in FIX_PIPELINE:
        before_step = _read_files(py_files)
        tool.run(py_files)
        after_step = _read_files(py_files)
        for f in py_files:
            file_steps[f][name] = before_step.get(f) != after_step.get(f)

    # Print the report
    _print_report(file_steps, py_files)

    # Detect if any file was modified overall
    after = _read_files(py_files)
    for f in py_files:
        if before.get(f) != after.get(f):
            return 1

    return 0


def run_check(files):
    """Run lint check pipeline on files.

    Returns non-zero if any linter found issues.
    """
    if not files:
        return 0

    py_files = [f for f in files if f.endswith('.py')]
    if not py_files:
        return 0

    exit_code = 0
    for name, tool in CHECK_PIPELINE:
        result = tool.run(py_files)
        if result != 0:
            exit_code = 1

    return exit_code
