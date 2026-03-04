"""CLI entry points for AgroMarin pre-commit hooks."""

import sys

from .po_format import fix_file as fix_po_file
from .runner import run_check, run_fix


def fix_main():
    """Entry point for agromarin-fix hook.

    Runs all auto-fixers: custom fixers + autoflake + pyupgrade + isort + black.
    Returns 1 if any file was modified, 0 otherwise.
    """
    return run_fix(sys.argv[1:])


def check_main():
    """Entry point for agromarin-check hook.

    Runs linters: flake8 (with bugbear).
    Returns non-zero if any issue found.
    """
    return run_check(sys.argv[1:])


def po_format_main():
    """Entry point for agromarin-po-format hook.

    Formats .po files: sort by msgid, clear redundant translations.
    Returns 1 if any file was modified, 0 otherwise.
    """
    files = sys.argv[1:]
    ret = 0
    for filepath in files:
        if fix_po_file(filepath):
            ret = 1
    return ret
