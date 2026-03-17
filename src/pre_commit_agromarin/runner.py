"""Pipeline orchestrator for the AgroMarin lint tools."""

import sys
from datetime import datetime
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

# ANSI color helpers
_BOLD = "\033[1m"
_RESET = "\033[0m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_DIM = "\033[2m"


def _read_files(files):
    """Read file contents for modification detection."""
    contents = {}
    for f in files:
        path = Path(f)
        if path.exists():
            contents[f] = path.read_bytes()
    return contents


def _bar(ratio, width=10):
    """Render a progress bar string from a 0.0-1.0 ratio."""
    filled = round(ratio * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def _print_report(file_steps, py_files, has_modifications):
    """Print an executive coverage report."""
    w = sys.stderr.write
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(py_files)

    # Classify files
    modified_files = []
    clean_files = []
    for f in py_files:
        if any(file_steps.get(f, {}).values()):
            modified_files.append(f)
        else:
            clean_files.append(f)

    modified_count = len(modified_files)
    clean_count = len(clean_files)

    # ── Header ──
    w(f"\n{_BOLD}")
    w("\u2554" + "\u2550" * 62 + "\u2557\n")
    w(f"\u2551{'AgroMarin Pre-commit Report':^62s}\u2551\n")
    w(f"\u2551{now:^62s}\u2551\n")
    w("\u255a" + "\u2550" * 62 + "\u255d\n")
    w(_RESET)

    # ── Summary ──
    if has_modifications:
        status = f"{_YELLOW}FIXES APPLIED{_RESET} (re-run to verify)"
    else:
        status = f"{_GREEN}ALL CLEAN{_RESET}"

    w(f"\n{_DIM}\u250c\u2500 Summary \u2500" + "\u2500" * 51 + f"\u2510{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}  Files scanned: {_BOLD}{total}{_RESET}")
    w(f"    Modified: {_YELLOW}{modified_count}{_RESET}")
    w(f"    Clean: {_GREEN}{clean_count}{_RESET}")
    padding = 62 - 48 - len(str(total)) - len(str(modified_count)) - len(str(clean_count))
    w(" " * max(padding, 1) + f"{_DIM}\u2502{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}  Status: {status}")
    w(f"\n{_DIM}\u2514" + "\u2500" * 62 + f"\u2518{_RESET}\n")

    if not has_modifications:
        # ── Acceptance Table (all clean) ──
        _print_acceptance(w, total)
    else:
        # ── Tool Effectiveness + Details (has fixes) ──
        _print_tool_effectiveness(w, file_steps, py_files, total)
        _print_details_by_module(w, file_steps, py_files)


def _print_acceptance(w, total):
    """Print acceptance seal when all files pass clean."""
    step_count = len(_ALL_STEPS)
    bar_width = 42
    full_bar = "\u2588" * bar_width

    w(f"\n{_DIM}\u250c\u2500 Acceptance \u2500" + "\u2500" * 49 + f"\u2510{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}\n")

    for step in _ALL_STEPS:
        w(f"{_DIM}\u2502{_RESET}    {_GREEN}\u2713{_RESET} {step:<22s} {_GREEN}PASSED{_RESET}\n")

    w(f"{_DIM}\u2502{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}    {_GREEN}{full_bar}{_RESET}  {_BOLD}{step_count}/{step_count} PASSED{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}{'':>14s}{_BOLD}{_GREEN}\u2705 APPROVED FOR COMMIT{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}{'':>14s}{_DIM}({total} files verified){_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}\n")
    w(f"{_DIM}\u2514" + "\u2500" * 62 + f"\u2518{_RESET}\n\n")


def _print_tool_effectiveness(w, file_steps, py_files, total):
    """Print tool effectiveness table with progress bars."""
    tool_counts = {}
    for step in _ALL_STEPS:
        tool_counts[step] = sum(
            1 for f in py_files if file_steps.get(f, {}).get(step, False)
        )

    w(f"\n{_DIM}\u250c\u2500 Tool Effectiveness \u2500" + "\u2500" * 41 + f"\u2510{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}  {'Tool':<22s} {'Fixed':>5s}    {'Coverage':<16s}     {_DIM}\u2502{_RESET}\n")
    w(f"{_DIM}\u2502{_RESET}  " + "\u2500" * 22 + " " + "\u2500" * 5 + "    " + "\u2500" * 16 + "     " + f"{_DIM}\u2502{_RESET}\n")

    for step in _ALL_STEPS:
        count = tool_counts[step]
        ratio = count / total if total > 0 else 0
        pct = f"{ratio * 100:.0f}%"
        bar = _bar(ratio)
        if count > 0:
            w(f"{_DIM}\u2502{_RESET}  {_YELLOW}{step:<22s} {count:>5d}{_RESET}    {bar}  {pct:>4s}     {_DIM}\u2502{_RESET}\n")
        else:
            w(f"{_DIM}\u2502{_RESET}  {_DIM}{step:<22s} {count:>5d}    {bar}  {pct:>4s}{_RESET}     {_DIM}\u2502{_RESET}\n")

    w(f"{_DIM}\u2514" + "\u2500" * 62 + f"\u2518{_RESET}\n")


def _print_details_by_module(w, file_steps, py_files):
    """Print per-file details grouped by Odoo module."""
    modules = {}
    for f in py_files:
        parts = Path(f).parts
        module = parts[0] if parts else "."
        modules.setdefault(module, []).append(f)

    w(f"\n{_DIM}\u250c\u2500 Details by Module \u2500" + "\u2500" * 42 + f"\u2510{_RESET}\n")

    for module, mod_files in sorted(modules.items()):
        w(f"{_DIM}\u2502{_RESET}\n")
        w(f"{_DIM}\u2502{_RESET}  {_BOLD}{_CYAN}{module}/{_RESET}\n")

        for idx, f in enumerate(sorted(mod_files)):
            steps = file_steps.get(f, {})
            is_last = idx == len(mod_files) - 1
            connector = "\u2514\u2500\u2500" if is_last else "\u251c\u2500\u2500"
            sub_connector = "   " if is_last else "\u2502  "

            rel = str(Path(f).relative_to(module)) if module != "." else f
            fix_count = sum(1 for v in steps.values() if v)

            if fix_count > 0:
                label = f"{_YELLOW}{fix_count} fix{'es' if fix_count != 1 else ''} applied{_RESET}"
            else:
                label = f"{_GREEN}\u2713 clean{_RESET}"

            w(f"{_DIM}\u2502{_RESET}  {_DIM}{connector}{_RESET} {rel:<40s} {label}\n")

            if fix_count > 0:
                tools_used = [s for s in _ALL_STEPS if steps.get(s, False)]
                tools_str = "  ".join(f"{_YELLOW}*{_RESET} {t}" for t in tools_used)
                w(f"{_DIM}\u2502{_RESET}  {_DIM}{sub_connector}{_RESET} {tools_str}\n")

    w(f"{_DIM}\u2502{_RESET}\n")
    w(f"{_DIM}\u2514" + "\u2500" * 62 + f"\u2518{_RESET}\n\n")


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

    # Detect if any file was modified overall
    after = _read_files(py_files)
    has_modifications = any(
        before.get(f) != after.get(f) for f in py_files
    )

    # Print the executive report
    _print_report(file_steps, py_files, has_modifications)

    return 1 if has_modifications else 0


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
