"""Pipeline orchestrator for the AgroMarin lint tools."""

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


def _read_files(files):
    """Read file contents for modification detection."""
    contents = {}
    for f in files:
        path = Path(f)
        if path.exists():
            contents[f] = path.read_bytes()
    return contents


def run_fix(files):
    """Run auto-fix pipeline on files.

    Returns 1 if any file was modified, 0 otherwise.
    """
    if not files:
        return 0

    py_files = [f for f in files if f.endswith('.py')]
    if not py_files:
        return 0

    before = _read_files(py_files)

    # 1. Run custom AgroMarin fixers
    for fixer in ALL_FIXERS:
        for filepath in py_files:
            fixer(filepath)

    # 2. Run third-party auto-fix tools
    for name, tool in FIX_PIPELINE:
        tool.run(py_files)

    # Detect if any file was modified
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
